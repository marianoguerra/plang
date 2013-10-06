from ptypes import Fn, nil, Operative, PFn, Symbol, Pair

class FnPrint(Fn):
    def __init__(self):
        Fn.__init__(self, "println")

    def call(self, args, cc):
        for arg in args:
            print arg,
        print

        return cc.resolve(nil)

class FnList(Fn):
    def __init__(self):
        Fn.__init__(self, "list")

    def call(self, args, cc):
        return cc.resolve(args)

