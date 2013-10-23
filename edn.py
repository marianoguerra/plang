from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox

lg = LexerGenerator()
lg.add("nil", r"nil")
lg.add("true", r"true")
lg.add("false", r"false")
lg.add("float", r"\d+\.\d+")
lg.add("number", r"\d+")

lg.ignore(r"[\s,\r\n\t]+")

lexer = lg.build()

pg = ParserGenerator(["nil", "true", "false", "float", "number"])

class State(object):
    def __init__(self):
        pass

# if it doesn't inherith from BaseBox it pypy doesn't compile it
class Type(BaseBox):
    def __init__(self):
        pass

    def to_str(self):
        return "<type>"

class Nil(Type):
    # without this pypy doesn't compile
    def __init__(self):
        Type.__init__(self)

    def to_str(self):
        return "nil"

class Bool(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def to_str(self):
        if self.value:
            return "true"
        else:
            return "false"

class Int(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def to_str(self):
        return "%d" % self.value

class Float(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def to_str(self):
        return "%f" % self.value

nil = Nil()
true = Bool(True)
false = Bool(False)

@pg.production("main : value")
def main(state, p):
    return p[0]

@pg.production("value : nil")
def value_nil(state, p):
    return nil

@pg.production("value : true")
def value_true(state, p):
    return true

@pg.production("value : false")
def value_false(state, p):
    return false

@pg.production("value : float")
def value_float(state, p):
    return Float(float(p[0].getstr()))

@pg.production("value : number")
def value_integer(state, p):
    return Int(int(p[0].getstr()))

parser = pg.build()

def loads(code):
    state = State()
    return parser.parse(lexer.lex(code), state)

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

