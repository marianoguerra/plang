import sys

class PError(Exception):
    def __init__(self, msg):
        self.msg = msg

class PUnboundError(PError):
    def __init__(self, msg, name, env):
        PError.__init__(self, msg)
        self.name = name
        self.env = env

class Resolver(object):
    def resolve(self, value):
        return value

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

def entry_point(argv):
    identity = Resolver()
    env = Env({"version": Str("0.0.1")})

    print Cc(Int(42), identity, env).step().to_str()
    print Cc(Float(42.3), identity, env).step().to_str()
    print Cc(true, identity, env).step().to_str()
    print Cc(false, identity, env).step().to_str()
    print Cc(nil, identity, env).step().to_str()
    print Cc(Str("hello world!"), identity, env).step().to_str()
    print Cc(Symbol("version"), identity, env).step().to_str()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
