import sys
from rply.token import BaseBox

class Type(BaseBox):

    def __init__(self):
        pass

    def __str__(self):
        return str(self.value)

class Int(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

def entry_point(argv):
    val = Int(42)
    print "hello pypy!", val.__str__()
    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
