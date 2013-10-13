import sys

class PError(Exception):
    def __init__(self, msg):
        self.msg = msg

class PUnboundError(PError):
    def __init__(self, msg, name, env):
        PError.__init__(self, msg)
        self.name = name
        self.env = env

class PCallableExpectedError(PError):
    def __init__(self, msg, value):
        self.msg = msg
        self.value = value

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

class Type(object):
    def __init__(self):
        pass

class Cc(Type):
    def __init__(self, value, cont, env):
        self.value = value
        self.cont = cont
        self.env = env

    def resolve(self, value):
        return self.cont.resolve(value)

    def step(self):
        return self.value.eval(self)

    def run(self):
        result = self.step()
        while isinstance(result, Cc):
            result = result.step()

        return result

class Env(Type):
    def __init__(self, bindings):
        self.value = None
        self.bindings = bindings

    def get(self, name):
        # dict.get must take the two args
        result = self.bindings.get(name, None)
        if result is None:
            raise PUnboundError("'%s' not bound" % name, name, self)

        return result

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
        return '"%s"' % self.value

true = Bool(True)
false = Bool(False)
nil = Nil()

class Callable(Type):
    def __init__(self, name):
        self.name = name

    def call(self, args, cc):
        return cc.resolve(nil)

class Operative(Callable):
    def __init__(self, name):
        Callable.__init__(self, name)

    def call(self, args, cc):
        return cc.resolve(nil)

class OpDump(Operative):
    def __init__(self):
        Callable.__init__(self, "dump")

    def call(self, args, cc):
        print "dump:", args.to_str()
        return cc.resolve(nil)

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
        return Cc(self.head, CallResolver(self, cc), cc.env)

    def to_str(self):
        return "(%s)" % " ".join([item.to_str() for item in self])

def entry_point(argv):
    identity = Resolver()
    env = Env({"version": Str("0.0.1"), "dump": OpDump()})

    print Cc(Int(42), identity, env).step().to_str()
    print Cc(Float(42.3), identity, env).step().to_str()
    print Cc(true, identity, env).step().to_str()
    print Cc(false, identity, env).step().to_str()
    print Cc(nil, identity, env).step().to_str()
    print Cc(Str("hello world!"), identity, env).step().to_str()
    print Cc(Symbol("version"), identity, env).step().to_str()
    result = Cc(Pair(Symbol("dump"), Int(42)), identity, env).run().to_str()
    print "dump returned:", result

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
