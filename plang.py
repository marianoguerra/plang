import sys
from rply.token import BaseBox

class Type(BaseBox):

    def __init__(self):
        pass

    def __str__(self):
        return str(self.value)

    def eval(self, cc):
        return cc.resolve(self)


class Int(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

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
    val = Int(42)
    cc = Cc(val, print_result)
    cc.run()
    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
