
from rply.token import BaseBox
from perrors import *
from putils import *

class Type(BaseBox):

    def __init__(self):
        pass

    def __str__(self):
        return "<Type>"

    def eval(self, cc):
        return cc.resolve(self)

class Env(Type):
    def __init__(self, bindings, parent=None):
        self.bindings = bindings
        self.parent = parent

    def get(self, name):
        result = self.bindings.get(name, None)

        if result is None:
            if self.parent is None:
                raise UnboundVariable(name)
            else:
                return self.parent.get(name)
        else:
            return result

    def set(self, name, value):
        self.bindings[name] = value

    def __str__(self):
        return '<Env>'

class Int(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def __str__(self):
        return str(self.value)

class Float(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def __str__(self):
        return str(self.value)

class Bool(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def __str__(self):
        if self.value:
            return "true"
        else:
            return "false"

class Nil(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = None
        self.next = None

    def __str__(self):
        return "nil"

    def to_list(self):
        return []

nil = Nil(None)

class Operative(Type):
    def __init__(self, name):
        Type.__init__(self)
        self.name = name

    def call(self, args, cc):
        raise NotImplementedError("operative %s not implemented" % self.name)

class Fn(Type):
    def __init__(self, name="<lambda>"):
        Type.__init__(self)
        self.name = name

    def call(self, args, cc):
        raise NotImplementedError("fn %s not implemented" % self.name)

    def __str__(self):
        return '(fn %s)' % self.name

class PFn(Fn):
    def __init__(self, name, arglist, body):
        Fn.__init__(self, name)
        self.arglist = arglist
        self.body = body

    def call(self, args, cc):
        earglist = args.to_list()
        earglen = len(earglist)
        larglist = self.arglist.to_list()
        arglistlen = len(larglist)

        if earglen != arglistlen:
            raise TypeError("Expected %d arguments in %s, got %d" % (
                arglistlen, self.name, earglen), args)
        else:
            for i in range(arglistlen):
                argname = larglist[i]
                argval = earglist[i]
                cc.env.set(argname.__str__(), argval)

            holder = ResultHolder()

            for expr in self.body:
                expr_cc = Cc(expr, holder, cc.env, cc)
                cc1 = expr.eval(expr_cc)

                if cc1 is not None:
                    cc1.run()

            return cc.resolve(holder.result)

class Pair(Type):
    def __init__(self, left, right=nil):
        Type.__init__(self)
        self.value = left
        self.next = right

    def __str__(self):
        #return "(%s . %s)" % (self.value, self.next)
        return "(%s)" % " ".join([item.__str__() for item in self])

    def eval(self, cc):
        if cc.do_run:
            run_cc = Cc(self.next, PairRunner(cc), cc.env, cc)
            resolver = LeftPairResolver(self, run_cc)
            return resolver.step()
        else:
            resolver = LeftPairResolver(self, cc)
            return resolver.step()

    def __iter__(self):
        pair = self
        while True:
            cur = pair.value
            yield cur
            if pair.next == nil:
                break
            else:
                pair = pair.next
                if not isinstance(pair, Pair):
                    break

    def to_list(self):
        return [item for item in self]

def pair_from_iter(iterable):
    items = list(iterable)
    cur = Pair(items[-1], nil)

    for item in reversed(items[:-1]):
        cur = Pair(item, cur)

    return cur

class Str(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def __str__(self):
        return '"%s"' % self.value

class Keyword(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def __str__(self):
        return ':%s' % self.value

class Symbol(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def __str__(self):
        return '%s' % self.value

    def eval(self, cc):
        name = self.value
        return cc.resolve(cc.env.get(name))

true = Bool(True)
false = Bool(False)

class Cc(Fn):
    def __init__(self, value, cont, env, parent, do_run=True):
        self.value = value
        self.cont = cont
        self.env = env
        self.do_run = do_run
        self.parent = parent

    def step(self):
        return self.value.eval(self)

    def run(self):
        result = self.step()
        while isinstance(result, Cc):
            result = result.step()

        return result

    def resolve(self, value):
        return self.cont.on_result(value)

    def __str__(self):
        return '<Cc>'

    def call(self, value, cc):
        if isinstance(value, Pair):
            return cc.resolve(value.value)
        else:
            # shouldn't happen, but pypy doesn't like it
            return cc.resolve(value)

class Tagged(Type):
    def __init__(self, tag, value):
        self._tag = tag
        self._value = value

    def __str__(self):
        return "#{} {}".format(self._tag, str(self._value))

    def __repr__(self):
        return "<tagged {} {}>".format(self._tag, str(self._value))

class ResultHandler(object):
    def __init__(self, value=None):
        self.value = value

    def on_result(self, result):
        pass

class PairResolver(ResultHandler):
    pass

class LeftPairResolver(PairResolver):
    def __init__(self, pair, cc):
        PairResolver.__init__(self)
        self.pair = pair
        self.cc = cc

    def on_result(self, left_val):
        return self.cc.cont.on_result(Pair(left_val, self.pair.next))

    def step(self):
        return Cc(self.pair.value, self, self.cc.env, self.cc)

class PairExpander(PairResolver):
    def __init__(self, pair, cc):
        PairResolver.__init__(self, pair)
        self.cc = cc

    def on_result(self, left_val):
        if self.pair.next == nil:
            return self.cc.resolve(Pair(left_val, nil))
        else:
            return Cc(self.pair.next.value,
                    PairExpander(self.pair.next.next, self.cc),
                    self.cc.env, self.cc, False)

    def step(self):
        return Cc(self.value.value, self, self.cc.env, self.cc)

class ResultHolder(ResultHandler):
    def __init__(self):
        ResultHandler.__init__(self)
        self.result = nil

    def on_result(self, result):
        self.result = result

def expand_pair(pair, env, parent_cc):
    result = []
    holder = ResultHolder()

    while pair != nil:
        # XXX reuse same Cc?
        cc = Cc(pair, holder, env, parent_cc, False)

        if cc is not None:
            cc.run()

        res = holder.result
        # this check is kind of pointless, but trying to make pypy work
        if isinstance(res, Pair):
            left = res.value
            result.append(left)
            pair = pair.next
        else:
            raise TypeError("Expected pair, got %s" % res.__str__(), res)

    epair = nil
    for item in reversed(result):
        epair = Pair(item, epair)

    return epair


class PairRunner(ResultHandler):
    def __init__(self, cc):
        ResultHandler.__init__(self)
        self.cc = cc

    def on_result(self, pair):
        if isinstance(pair, Pair):
            fn = pair.value
            if isinstance(fn, Operative):
                return fn.call(pair.next, self.cc)
            elif isinstance(fn, Fn):
                expanded_pair = expand_pair(pair.next, self.cc.env, self.cc)
                return fn.call(expanded_pair, self.cc)
            else:
                raise CallableExpected(fn)
        else:
            raise TypeError("Expected pair", pair)

# TODO
Char = Str
Set = Pair
Vector = Pair
Map = Pair

NL = Char('\n')
TAB = Char('\t')
RETURN = Char('\r')
SPACE = Char(' ')

