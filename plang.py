import sys
from rply.token import BaseBox

class Type(BaseBox):

    def __init__(self):
        pass

    def __str__(self):
        return "<Type>"

    def eval(self, cc):
        return cc.resolve(self)

class Error(Exception):
    pass

class UnboundVariable(Error):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '(UnboundVariable "%s")' % self.name

class TypeError(Error):
    def __init__(self, reason, value):
        self.reason = reason
        self.value = value

    def __str__(self):
        return '(TypeError "%s" %s)' % (self.reason, self.value)

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

nil = Nil(None)

class Fn(Type):
    def __init__(self, name="<lambda>"):
        Type.__init__(self)
        self.name = name

    def call(self, args, cc):
        print "Called fn with args:", args.__str__()
        return cc.resolve(Int(42))

    def __str__(self):
        return '(fn %s)' % self.name

class FnPrint(Fn):
    def __init__(self):
        Fn.__init__(self, "println")

    def call(self, args, cc):
        print args.__str__()
        return cc.resolve(nil)

class FnList(Fn):
    def __init__(self):
        Fn.__init__(self, "list")

    def call(self, args, cc):
        return cc.resolve(args)

class CallableExpected(Error):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '(CallableExpected %s)' % self.value.__str__()

class ResultHandler(object):
    def __init__(self, value=nil):
        self.value = value

    def on_result(self, result):
        print "result:", result.__str__()

class PairResolver(ResultHandler):
    pass

class RightPairResolver(PairResolver):
    def __init__(self, left_val, cc):
        PairResolver.__init__(self, left_val)
        self.cc = cc

    def on_result(self, right_val):
        return self.cc.resolve(Pair(self.value, right_val))

class LeftPairResolver(PairResolver):
    def __init__(self, pair, cc):
        PairResolver.__init__(self)
        self.pair = pair
        self.cc = cc

    def on_result(self, left_val):
        right_resolver = RightPairResolver(left_val, self.cc)
        return Cc(self.pair.next, right_resolver, self.cc.env)

    def step(self):
        return Cc(self.pair.value, self, self.cc.env)

class PairRunner(ResultHandler):
    def __init__(self, cc):
        ResultHandler.__init__(self)
        self.cc = cc

    def on_result(self, pair):
        if isinstance(pair, Pair):
            fn = pair.value
            if isinstance(fn, Fn):
                return fn.call(pair.next, self.cc)
            else:
                raise CallableExpected(fn)
        else:
            raise TypeError("Expected pair", pair)

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
            run_cc = Cc(None, PairRunner(cc), cc.env)
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

    def extend(self, iterable):
        cur = nil
        for item in reversed(iterables):
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

class Cc(Type):
    def __init__(self, value, cont, env, do_run=False):
        self.value = value
        self.cont = cont
        self.env = env
        self.do_run = do_run

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

def entry_point(argv):
    print_result = ResultHandler()

    root = Env({"name": Keyword("bob")})
    env = Env({"answer": Int(42), "println": FnPrint(), "list": FnList()},
            root)
    val_i = Int(42)
    val_f = Float(42.1)

    cci = Cc(val_i, print_result, env)
    cci.run()

    ccf = Cc(val_f, print_result, env)
    ccf.run()

    ccb = Cc(true, print_result, env)
    ccb.run()

    ccn = Cc(nil, print_result, env)
    ccn.run()

    ccs = Cc(Str("hi there"), print_result, env)
    ccs.run()

    cck = Cc(Keyword("hi-there"), print_result, env)
    cck.run()

    ccs = Cc(Symbol("answer"), print_result, env)
    ccs.run()

    ccs1 = Cc(Symbol("name"), print_result, env)
    ccs1.run()

    try:
        ccs2 = Cc(Symbol("not_there"), print_result, env)
        ccs2.run()
    except UnboundVariable as error:
        print "Error:", error.__str__()

    ccp1 = Cc(
            Pair(Symbol("println"),
                Pair(Int(1),
                    Pair(Symbol("answer"),
                        Pair(Symbol("name"),
                            nil)))),
            print_result, env, True)
    ccp1.run()

    ccp2 = Cc(
            Pair(Symbol("list"),
                Pair(Int(1),
                    Pair(Symbol("answer"),
                        Pair(Symbol("name"),
                            nil)))),
            print_result, env, True)
    ccp2.run()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
