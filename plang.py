import os
import sys

from ptypes import *
import rply.parser

import edn

def readinput():
    result = []
    while True:
        s = os.read(0, 1)
        result.append(s)
        if s == '':
            if len(result) > 1:
                break
            raise SystemExit
    return "".join(result)

def entry_point(argv):
    input_data = readinput()
    try:
        input_parsed = edn.loads(input_data)
    except rply.parser.ParsingError as error:
        pos = error.getsourcepos()
        print "Error reading code at line: %d column: %d" % (pos.lineno, pos.colno)
        return -1

    env = Env({
        "version": Str("0.0.1"),
        "dump": OpDump(),
        "do": OpDo(),
        "def": OpDef(),
        "lambda": OpLambda(),
        "display": FnDisplay()
    })


    print Cc(input_parsed, identity, env).run().to_str()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
