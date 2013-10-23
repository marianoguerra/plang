from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox

from ptypes import *

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
lg.ignore(r";.*\n")

lexer = lg.build()

pg = ParserGenerator(["nil", "true", "false", "float", "number", "string",
    "symbol", "olist", "clist"])

class State(object):
    def __init__(self):
        pass

class ValueList(BaseBox):
    def __init__(self, value):
        self.value = value

    def getitems(self):
        return self.value

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

@pg.production("items : value")
def value_items_more(state, p):
    return ValueList([p[0]])

@pg.production("items : value items")
def value_items_more(state, p):
    return ValueList([p[0]] + p[1].getitems())

@pg.production("value : olist items clist")
def value_list(state, p):
    return pair_from_iter(p[1].getitems())

def pair_from_iter(iterable):
    items = list(iterable)
    cur = Pair(items[-1], nil)

    for item in reversed(items[:-1]):
        cur = Pair(item, cur)

    return cur

parser = pg.build()

def loads(code):
    state = State()
    return parser.parse(lexer.lex(code), state)

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

