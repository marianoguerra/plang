from rply.token import BaseBox

# if it doesn't inherith from BaseBox it pypy doesn't compile it
class Type(BaseBox):
    def __init__(self):
        pass

    def to_str(self):
        return "<type>"

class PError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def to_str(self):
        return self.msg

class PUnboundError(PError):
    def __init__(self, msg, name, env):
        PError.__init__(self, msg)
        self.name = name
        self.env = env

    def __str__(self):
        return "%s: %s" % (self.msg, self.name)

class PBadMatchError(PError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "%s" % self.msg

class PCallableExpectedError(PError):
    def __init__(self, msg, value):
        self.msg = msg
        self.value = value

    def __str__(self):
        return "%s: %s" % (self.msg, self.value.to_str())

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

class Nil(Type):
    # without this pypy doesn't compile
    def __init__(self):
        Type.__init__(self)

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        return "nil"

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

class Int(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        return "%d" % self.value

class Float(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        return "%f" % self.value

class Str(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(self)

    def to_str(self):
        return '%s' % self.value

class Symbol(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, cc):
        return cc.resolve(cc.env.get(self.value))

    def to_str(self):
        return self.value

nil = Nil()
true = Bool(True)
false = Bool(False)

class Pair(Type):
    def __init__(self, head, tail=nil):
        self.head = head
        self.tail = tail

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
        return cc.resolve(self)

identity = Resolver()

def expand_pair(pair, cc):
    return Cc(pair, identity, cc.env, cc, False).run()

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

class Operative(Callable):
    def __init__(self, name):
        Callable.__init__(self, name)

    def call(self, args, cc):
        return cc.resolve(nil)

    def to_str(self):
        return "<operative %s>" % self.name

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

