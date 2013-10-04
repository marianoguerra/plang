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

    def __str__(self):
        return "nil"

nil = Nil(None)

class Fn(Type):
    def call(self, args, cc):
        print "Called fn with args:", args.__str__()
        return cc.resolve(Int(42))

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


class RightPairResolver(ResultHandler):
    def __init__(self, left_val, cc):
        ResultHandler.__init__(self, left_val)
        self.cc = cc

    def on_result(self, right_val):
        return self.cc.resolve(Pair(self.value, right_val))

class LeftPairResolver(ResultHandler):
    def __init__(self, pair, cc):
        ResultHandler.__init__(self)
        self.pair = pair
        self.cc = cc

    def on_result(self, left_val):
        right_resolver = RightPairResolver(left_val, self.cc)
        return Cc(self.pair.next, right_resolver, self.cc.env)

    def run(self):
        return Cc(self.pair.value, self, self.cc.env)

class Pair(Type):
    def __init__(self, left, right=nil):
        Type.__init__(self)
        self.value = left
        self.next = right

    def __str__(self):
        return "(%s . %s)" % (self.value.__str__(), self.next.__str__())

    def eval(self, cc):
        resolver = LeftPairResolver(self, cc)
        return resolver.run()

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
    def __init__(self, value, cont, env):
        self.value = value
        self.cont = cont
        self.env = env

    def step(self):
        return self.value.eval(self)

    def run(self):
        result = self.step()
        while isinstance(result, Cc):
            result = result.step()

        return result

    def resolve(self, value):
        return self.cont.on_result(value)

def entry_point(argv):
    print_result = ResultHandler()

    root = Env({"name": Keyword("bob")})
    env = Env({"answer": Int(42)}, root)
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

    ccp = Cc(Pair(Int(1), Pair(Symbol("answer"), Pair(Symbol("name"), nil))),
            print_result, env)
    ccp.run()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
