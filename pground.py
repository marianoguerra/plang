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

class OpLambda(Operative):
    def __init__(self):
        Operative.__init__(self, "lambda")

    def call(self, args, cc):
        if isinstance(args, Pair):
            param_names = args.head
            if not isinstance(param_names, Pair):
                msg = "Expected List of symbols as params, got %s"
                raise PBadMatchError(msg % param_names.to_str())

            params = []
            for param_name in param_names:
                if not isinstance(param_name, Symbol):
                    msg = "Expected symbol in lambda param name, got %s"
                    raise PBadMatchError(msg % param_name.to_str())
                else:
                    params.append(param_name.value)

            return cc.resolve(Lambda(params, args.tail))
        else:
            msg = "Expected lambda params to be ((*args) *body), got %s"
            raise PBadMatchError(msg % args.to_str())

GROUND = {
    "__lang_version__": Str("0.0.1"),
    "display": FnDisplay(),
    "dump": OpDump(),
    "lambda": OpLambda(),
}
