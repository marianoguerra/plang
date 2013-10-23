from ptypes import *

class OpDump(Operative):
    def __init__(self):
        Operative.__init__(self, "dump")

    def call(self, args, cc):
        print "dump:", args.to_str()
        return cc.resolve(nil)

class FnDisplay(Applicative):
    def __init__(self):
        Callable.__init__(self, "display")

    def handle(self, args, cc):
        print args.to_str()
        return cc.resolve(nil)

GROUND = {
    "__lang_version__": Str("0.0.1"),
    "display": FnDisplay(),
    "dump": OpDump()
}
