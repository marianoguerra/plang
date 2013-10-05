import os

# https://bitbucket.org/cfbolz/pyrolog/src/f18f2ccc23a4/prolog/interpreter/translatedmain.py
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

