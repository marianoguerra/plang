from ptypes import *

class FnDisplay(Applicative):
    def __init__(self):
        Callable.__init__(self, "display")

    def handle(self, args, cc):
        print args.to_str()
        return cc.resolve(nil)

GROUND = {
    "__lang_version__": Str("0.0.1"),
    "display": FnDisplay()
}
