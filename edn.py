from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox

SYMBOL_RE = r"[<>\.\*\/\+\!\-\_\?\$%&=a-zA-Z][<>\.\*\+\!\-\_\?\$%&=a-zA-Z0-9:#]*"

lg = LexerGenerator()
lg.add("nil", r"nil")
lg.add("true", r"true")
lg.add("false", r"false")
lg.add("float", r"\d+\.\d+")
lg.add("number", r"\d+")
lg.add("string", r'"(\\\^.|\\.|[^\"])*"')
lg.add("symbol", SYMBOL_RE)
lg.add("olist", r"\(")
lg.add("clist", r"\)")

lg.ignore(r"[\s,\r\n\t]+")

lexer = lg.build()

pg = ParserGenerator(["nil", "true", "false", "float", "number", "string",
    "symbol", "olist", "clist"])

class State(object):
    def __init__(self):
        pass

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

    def eval(self, env):
        return self

    def to_str(self):
        return "nil"

class Bool(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, env):
        return self

    def to_str(self):
        if self.value:
            return "true"
        else:
            return "false"

class Int(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, env):
        return self

    def to_str(self):
        return "%d" % self.value

class Float(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, env):
        return self

    def to_str(self):
        return "%f" % self.value

class Str(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, env):
        return self

    def to_str(self):
        return '%s' % self.value

class Symbol(Type):
    def __init__(self, value):
        Type.__init__(self)
        self.value = value

    def eval(self, env):
        return env.get(self.value)

    def to_str(self):
        return self.value

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

@pg.production("value : string")
def value_string(state, p):
    return Str(p[0].getstr())

@pg.production("value : symbol")
def value_symbol(state, p):
    return Symbol(p[0].getstr())

@pg.production("value : olist clist")
def value_empty_list(state, p):
    return nil

parser = pg.build()

def loads(code):
    state = State()
    return parser.parse(lexer.lex(code), state)

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

