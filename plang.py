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
    def __init__(self, bindings):
        self.bindings = bindings

    def get(self, name):
        result = self.bindings.get(name, None)

        if result is None:
            raise UnboundVariable(name)
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

    def run(self):
        return self.value.eval(self)

    def resolve(self, value):
        return self.cont(value)

def print_result(result):
    print "result:", result.__str__()

def entry_point(argv):
    env = Env({"answer": Int(42)})
    val_i = Int(42)
    val_f = Float(42.1)

    cci = Cc(val_i, print_result, env)
    cci.run()

    ccf = Cc(val_f, print_result, env)
    ccf.run()

    ccb = Cc(true, print_result, env)
    ccb.run()

    ccs = Cc(Str("hi there"), print_result, env)
    ccs.run()

    cck = Cc(Keyword("hi-there"), print_result, env)
    cck.run()

    ccs = Cc(Symbol("answer"), print_result, env)
    ccs.run()

    try:
        ccs = Cc(Symbol("not_there"), print_result, env)
        ccs.run()
    except UnboundVariable as error:
        print "Error:", error.__str__()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
