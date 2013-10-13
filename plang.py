import sys

class Type(object):
    def __init__(self, value):
        self.value = value

    def to_str(self):
        return "%s" % self.value

class Int(Type):
    # if not redefined int acts as a float
    def __init__(self, value):
        self.value = value

    def to_str(self):
        return "%s" % self.value

class Float(Type):
    pass

class Bool(Type):
    def to_str(self):
        if self.value:
            return "true"
        else:
            return "false"

class Nil(Type):
    def to_str(self):
        return "nil"

true = Bool(True)
false = Bool(False)
nil = Nil(None)

def entry_point(argv):
    print Int(42).to_str()
    print Float(42.3).to_str()
    print true.to_str()
    print false.to_str()
    print nil.to_str()
    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
