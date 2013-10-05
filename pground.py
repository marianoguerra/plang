from ptypes import Fn, nil

class FnPrint(Fn):
    def __init__(self):
        Fn.__init__(self, "println")

    def call(self, args, cc):
        print args.__str__()
        return cc.resolve(nil)

class FnList(Fn):
    def __init__(self):
        Fn.__init__(self, "list")

    def call(self, args, cc):
        return cc.resolve(args)

