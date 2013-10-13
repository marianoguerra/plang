from rply.token import BaseBox

class PError(Exception):
    def __init__(self, msg):
        self.msg = msg

class PBadMatchError(PError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "%s" % self.msg

class PUnboundError(PError):
    def __init__(self, msg, name, env):
        PError.__init__(self, msg)
        self.name = name
        self.env = env

    def __str__(self):
        return "%s: %s" % (self.msg, self.name)

class PCallableExpectedError(PError):
    def __init__(self, msg, value):
        self.msg = msg
        self.value = value

    def __str__(self):
        return "%s: %s" % (self.msg, self.value.to_str())

class Resolver(object):
    def resolve(self, value):
        return value

class CallResolver(Resolver):
    def __init__(self, val, cc):
        self.val = val
        self.cc = cc

    def resolve(self, value):
        if isinstance(value, Callable):
            return value.call(self.val.tail, self.cc)
        else:
            raise PCallableExpectedError("Callable expected", value)

class TailResolver(Resolver):
    def __init__(self, val, cc):
        self.val = val
        self.cc = cc

    def resolve(self, tail):
        return self.cc.resolve(Pair(self.val, tail))

class HeadResolver(Resolver):
    def __init__(self, val, cc):
        self.val = val
        self.cc = cc

    def resolve(self, head):
        return Cc(self.val.tail, TailResolver(head, self.cc), self.cc.env,
                self.cc, False)


class Type(BaseBox):
    def __init__(self):
        pass

class Callable(Type):
    def __init__(self, name):
        self.name = name

    def call(self, args, cc):
        return cc.resolve(nil)

class Cc(Callable):
    def __init__(self, value, cont, env, parent, do_run=True):
        self.value = value
        self.cont = cont
        self.env = env
        self.parent = parent
        self.do_run = do_run

    def resolve(self, value):
        return self.cont.resolve(value)

    def step(self):
        return self.value.eval(self)

    def run(self):
        result = self.step()
        while isinstance(result, Cc):
            result = result.step()

        return result

    def eval(self, cc):
        return cc.parent.resolve(self)

    def call(self, args, _cc):
        if isinstance(args, Pair) and args.length() == 1:
            return self.resolve(args.head)
        else:
            msg = "expected on argument in cc, got %s"
            raise PBadMatchError(msg % args.to_str())

class Env(Type):
    def __init__(self, bindings, parent=None):
        self.value = None
        self.bindings = bindings
        self.parent = parent

    def get(self, name):
        # dict.get must take the two args
        result = self.bindings.get(name, None)
        if result is None:
            if self.parent is None:
                raise PUnboundError("'%s' not bound" % name, name, self)
            else:
                return self.parent.get(name)

        return result

    def set(self, name, value):
        self.bindings[name] = value

class Int(Type):
    # if not redefined int acts as a float
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def to_str(self):
        return "%s" % self.value

    def eval(self, cc):
        return cc.resolve(self)


class Float(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        return "%s" % self.value

class Bool(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        if self.value:
            return "true"
        else:
            return "false"

class Nil(Type):
    def __init__(self):
        Type.__init__(self)
        self.value = None

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        return "nil"

    def __iter__(self):
        return iter([])

class Symbol(Type):
    # if not redefined it doesn't compile
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(cc.env.get(self.value))

    def to_str(self):
        return "%s" % self.value

class Str(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        return '%s' % self.value

true = Bool(True)
false = Bool(False)
nil = Nil()

class Operative(Callable):
    def __init__(self, name):
        Callable.__init__(self, name)

    def call(self, args, cc):
        return cc.resolve(nil)

    def to_str(self):
        return "<applicative %s>" % self.name

def expand_pair(pair, cc):
    return Cc(pair, identity, cc.env, cc, False).run()

def peval(value, env):
    return Cc(value, identity, env, None).run()

class Applicative(Callable):
    def __init__(self, name):
        Callable.__init__(self, name)

    def handle(self, args, cc):
        return cc.resolve(args)

    def call(self, args, cc):
        eargs = expand_pair(args, cc)
        return self.handle(eargs, cc)

    def to_str(self):
        return "<applicative %s>" % self.name

class LeftResolver(Resolver):
    def __init__(self, rest, cc, env):
        self.rest = rest
        self.cc = cc
        self.env = env

    def resolve(self, value):
        if self.rest is nil:
            return self.cc.resolve(value)
        else:
            return eval_seq_left(self.rest, self.cc, self.env)


def eval_seq_left(pair, cc, env):
    if pair is nil:
        return cc.resolve(nil)
    elif isinstance(pair, Pair):
        return Cc(pair.head, LeftResolver(pair.tail, cc, env), env, cc)
    else:
        msg = "expected sequence of forms in body, got %s"
        raise PBadMatchError(msg % pair.to_str())

class Lambda(Applicative):
    def __init__(self, argnames, body):
        Applicative.__init__(self, "<lambda>")
        self.body = body
        self.argnames = argnames

    def handle(self, args, cc):
        if not isinstance(args, Pair):
            msg = "Expected sequence for function arguments, got %s"
            raise PBadMatchError(msg % args.to_str())

        env = Env({}, cc.env)

        # pypy doesn't like list(args)
        arglist = [item for item in args]
        args_len = len(arglist)
        argnames_len = len(self.argnames)

        if args_len != argnames_len:
            raise PBadMatchError("expected %d arguments, got %d" % (
                argnames_len, args_len))

        for i in range(args_len):
            argname = self.argnames[i]
            arg = arglist[i]
            env.set(argname, arg)

        return eval_seq_left(self.body, cc, env)

    def call(self, args, cc):
        eargs = expand_pair(args, cc)
        return self.handle(eargs, cc)

    def to_str(self):
        return "<lambda>"

class OpDump(Operative):
    def __init__(self):
        Operative.__init__(self, "dump")

    def call(self, args, cc):
        print "dump:", args.to_str()
        return cc.resolve(nil)

class OpDo(Operative):
    def __init__(self):
        Operative.__init__(self, "do")

    def call(self, args, cc):
        return eval_seq_left(args, cc, cc.env)

class OpDef(Operative):
    def __init__(self):
        Operative.__init__(self, "def")

    def call(self, args, cc):
        if (isinstance(args, Pair) and args.length() == 2 and
                isinstance(args.head, Symbol)):
            sym = args.head
            name = sym.to_str()
            tail = args.tail

            if isinstance(tail, Pair):
                value = peval(tail.head, cc.env)
                cc.env.set(name, value)
                return cc.resolve(value)
            else:
                msg = "expected (symbol value), got %s"
                raise PBadMatchError(msg % args.to_str())

        else:
            msg = "expected (symbol value), got %s"
            raise PBadMatchError(msg % args.to_str())

class OpLambda(Operative):
    def __init__(self):
        Operative.__init__(self, "lambda")

    def call(self, args, cc):
        if isinstance(args, Pair):
            param_names = args.head
            if not isinstance(param_names, Pair):
                msg = "Expected List of symbols as params, got %s"
                raise PBadMatchError(msg % param_names.to_str())

            params = []
            for param_name in param_names:
                if not isinstance(param_name, Symbol):
                    msg = "Expected symbol in lambda param name, got %s"
                    raise PBadMatchError(msg % param_name.to_str())
                else:
                    params.append(param_name.value)

            return cc.resolve(Lambda(params, args.tail))
        else:
            msg = "Expected lambda params to be ((*args) *body), got %s"
            raise PBadMatchError(msg % args.to_str())

class FnDisplay(Applicative):
    def __init__(self):
        Callable.__init__(self, "display")

    def handle(self, args, cc):
        print "display:", args.to_str()
        return cc.resolve(nil)

class FnCallCc(Applicative):
    def __init__(self):
        Callable.__init__(self, "call-cc")

    def handle(self, args, cc):
        if isinstance(args, Pair) and args.length() == 1:
            fn = args.head
            if isinstance(fn, Callable):
                return fn.call(cc, cc)
            else:
                msg = "Expected callable in call-cc, got %s"
                raise PBadMatchError(msg % fn.to_str())
        else:
            msg = "Expected (callable) in call-cc, got %s"
            raise PBadMatchError(msg % args.to_str())

class Pair(Type):
    def __init__(self, head, tail=nil):
        self.head = head
        self.tail = tail
        self._length_calculated = False
        self._size = 0

    def __iter__(self):
        pair = self
        while True:
            cur = pair.head
            yield cur
            if pair.tail == nil:
                break
            else:
                pair = pair.tail
                if not isinstance(pair, Pair):
                    break

    def eval(self, cc):
        if cc.do_run:
            return Cc(self.head, CallResolver(self, cc), cc.env, cc)
        else:
            return Cc(self.head, HeadResolver(self, cc), cc.env, cc)

    def to_str(self):
        return "(%s)" % " ".join([item.to_str() for item in self])

    def _length(self):
        pair = self
        count = 0
        while True:
            cur = pair.head
            count += 1
            if pair.tail == nil:
                break
            else:
                pair = pair.tail
                if not isinstance(pair, Pair):
                    count += 1
                    break

        return count

    def length(self):
        if not self._length_calculated:
            self._size = self._length()
            self._length_calculated = True

        return self._size

identity = Resolver()

def pair_from_iter(iterable):
    items = list(iterable)
    cur = Pair(items[-1], nil)

    for item in reversed(items[:-1]):
        cur = Pair(item, cur)

    return cur
