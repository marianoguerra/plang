import sys
import edn

from ptypes import *
from pground import *
from putils import *

def entry_point(argv):
    input_data = readinput()
    input_parsed = edn.loads(input_data)

    print_result = ResultHandler()

    root = Env({"name": Keyword("bob"), "def": OpDef()})
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
