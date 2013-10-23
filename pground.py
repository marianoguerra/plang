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

class OpDo(Operative):
    def __init__(self):
        Operative.__init__(self, "do")

    def call(self, args, cc):
        return eval_seq_left(args, cc, cc.env)

class OpDef(Operative):
    def __init__(self):
        Operative.__init__(self, "def")

    def call(self, args, cc):
        if (isinstance(args, Pair) and args.length() == 2 and
                isinstance(args.head, Symbol)):
            sym = args.head
            name = sym.to_str()
            tail = args.tail

            if isinstance(tail, Pair):
                value = peval(tail.head, cc.env)
                cc.env.set(name, value)
                return cc.resolve(value)
            else:
                msg = "expected (symbol value), got %s"
                raise PBadMatchError(msg % args.to_str())

        else:
            msg = "expected (symbol value), got %s"
            raise PBadMatchError(msg % args.to_str())

class FnCallCc(Applicative):
    def __init__(self):
        Callable.__init__(self, "call-cc")

    def handle(self, args, cc):
        if isinstance(args, Pair) and args.length() == 1:
            fn = args.head
            if isinstance(fn, Callable):
                return fn.call(cc, cc)
            else:
                msg = "Expected callable in call-cc, got %s"
                raise PBadMatchError(msg % fn.to_str())
        else:
            msg = "Expected (callable) in call-cc, got %s"
            raise PBadMatchError(msg % args.to_str())

GROUND = {
    "__lang_version__": Str("0.0.1"),
    "display": FnDisplay(),
    "dump": OpDump(),
    "lambda": OpLambda(),
    "do": OpDo(),
    "def": OpDef(),
    "call-cc": FnCallCc()
}
