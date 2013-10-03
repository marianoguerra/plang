import sys
from rply.token import BaseBox

class Type(BaseBox):

    def __init__(self):
        pass

    def __str__(self):
        return "<Type>"

    def eval(self, cc):
        return cc.resolve(self)


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
        return cc.resolve(Int(42))

true = Bool(True)
false = Bool(False)

class Cc(Type):
    def __init__(self, value, cont):
        self.value = value
        self.cont = cont

    def run(self):
        return self.value.eval(self)

    def resolve(self, value):
        return self.cont(value)

def print_result(result):
    print "result:", result.__str__()

def entry_point(argv):
    val_i = Int(42)
    val_f = Float(42.1)

    cci = Cc(val_i, print_result)
    cci.run()

    ccf = Cc(val_f, print_result)
    ccf.run()

    ccb = Cc(true, print_result)
    ccb.run()

    ccs = Cc(Str("hi there"), print_result)
    ccs.run()

    cck = Cc(Keyword("hi-there"), print_result)
    cck.run()

    ccs = Cc(Symbol("answer"), print_result)
    ccs.run()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
