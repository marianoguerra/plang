import os
import sys

import rply.parser

import edn
from ptypes import *

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
    env = Env({"__lang_version__": Str("0.0.1")})
    identity = Resolver()

    try:
        input_parsed = edn.loads(input_data)
        print Cc(input_parsed, identity, env, None).run().to_str()
    # catching two exceptions here makes pypy fail with a weird error
    except rply.parser.ParsingError as error:
        pos = error.getsourcepos()
        print "Error reading code at line: %d column: %d" % (pos.lineno, pos.colno)
        return -1
    except rply.errors.LexingError as error:
        pos = error.getsourcepos()
        print "Error reading code at line: %d column: %d" % (pos.lineno, pos.colno)
        return -1
    except PError as error:
        print error.to_str()
        return -1

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
