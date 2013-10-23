import os
import sys

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

    if input_data == "nil\n":
        print "nil"
        return 0
    else:
        print "Error: invalid program '%s'" % input_data
        return -1

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)
