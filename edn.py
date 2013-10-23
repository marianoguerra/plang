from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox

lg = LexerGenerator()
lg.add("nil", r"nil")
lg.ignore(r"[\s,\r\n\t]+")

lexer = lg.build()

pg = ParserGenerator(["nil"])

class State(object):
    def __init__(self):
        pass

class Nil(BaseBox):
    # without this pypy doesn't compile
    def __init__(self):
        BaseBox.__init__(self)

    def to_str(self):
        return "nil"

nil = Nil()

@pg.production("main : value")
def main(state, p):
    return p[0]

@pg.production("value : nil")
def value_nil(state, p):
    return nil

parser = pg.build()

def loads(code):
    state = State()
    return parser.parse(lexer.lex(code), state)

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

