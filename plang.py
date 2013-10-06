import sys
import edn
import rply.parser

from ptypes import *
from pground import *
from putils import *

def entry_point(argv):
    input_data = readinput()
    try:
        input_parsed = edn.loads("(do %s)" % input_data)
    except rply.parser.ParsingError as error:
        pos = error.getsourcepos()
        print "Error reading code at line: %d column: %d" % (pos.lineno, pos.colno)
        return -1

    print_result = ResultHandler()

    root = Env({"name": Keyword("bob"), "def": OpDef(), "do": OpDo()})
    env = Env({"answer": Int(42), "println": FnPrint(), "list": FnList()},
            root)

    try:
        print "In:  %s" % input_parsed.__str__()
        cc = Cc(input_parsed, print_result, env)
        cc.run()
    except Exception as error:
        print "Error: %s" % error

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
