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

class Env(Type):
    def __init__(self, bindings):
        Type.__init__(self)
        self.bindings = bindings

    def get(self, name):
        # dict.get must take the two args
        result = self.bindings.get(name, None)
        if result is None:
            raise PUnboundError("'%s' not bound" % name, name, self)

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
        return cc.resolve(self)

    def to_str(self):
        return "(%s)" % " ".join([item.to_str() for item in self])

class Resolver(object):
    def resolve(self, value):
        return value

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
