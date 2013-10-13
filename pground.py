from ptypes import *

class OpDump(Operative):
    def __init__(self):
        Operative.__init__(self, "dump")

    def call(self, args, cc):
        print "dump:", args.to_str()
        return cc.resolve(nil)

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

class FnDisplay(Applicative):
    def __init__(self):
        Callable.__init__(self, "display")

    def handle(self, args, cc):
        print "display:", args.to_str()
        return cc.resolve(nil)

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

class NumOp(Applicative):
    def __init__(self, name, zero):
        Applicative.__init__(self, name)
        self.zero = zero

    def handle(self, args, cc):
        result = self.zero
        saw_float = False
        if args is nil:
            return cc.resolve(Int(int(self.zero)))
        elif isinstance(args, Pair):
            if args.length() == 1:
                return cc.resolve(self.handle_one(args.head))

            first = True
            for item in args:
                if isinstance(item, Int):
                    result = self.calculate(result, item.value, first)
                elif isinstance(item, Float):
                    saw_float = True
                    result = self.calculate(result, item.value, first)
                else:
                    msg = "Expected Int or Float, got %s"
                    raise PBadMatchError(msg % item.to_str())

                first = False

            if saw_float:
                return cc.resolve(Float(result))
            else:
                return cc.resolve(Int(int(result)))
        else:
            msg = "Expected Pair, got %s"
            raise PBadMatchError(msg % args.to_str())

class FnAdd(NumOp):
    def __init__(self):
        NumOp.__init__(self, "+", 0.0)

    def calculate(self, actual, new_value, is_first):
        return actual + new_value

    def handle_one(self, value):
        return value

class FnSub(NumOp):
    def __init__(self):
        NumOp.__init__(self, "-", 0.0)

    def calculate(self, actual, new_value, is_first):
        if is_first:
            return new_value
        else:
            return actual - new_value

    def handle_one(self, value):
        if isinstance(value, Int):
            return Int(-value.value)
        elif isinstance(value, Float):
            return Float(-value.value)
        else:
            msg = "Expected Int or Float, got %s"
            raise PBadMatchError(msg % value.to_str())

class FnMul(NumOp):
    def __init__(self):
        NumOp.__init__(self, "*", 1.0)

    def calculate(self, actual, new_value, is_first):
        return actual * new_value

    def handle_one(self, value):
        return value

class FnDiv(NumOp):
    def __init__(self):
        NumOp.__init__(self, "/", 1.0)

    def calculate(self, actual, new_value, is_first):
        if is_first:
            return new_value
        else:
            return actual / new_value

    def handle_one(self, value):
        if isinstance(value, Int):
            return Int(1 / value.value)
        elif isinstance(value, Float):
            return Float(1.0 / value.value)
        else:
            msg = "Expected Int or Float, got %s"
            raise PBadMatchError(msg % value.to_str())

GROUND = {
    "dump": OpDump(),
    "do": OpDo(),
    "def": OpDef(),
    "lambda": OpLambda(),
    "call-cc": FnCallCc(),
    "display": FnDisplay(),
    "+": FnAdd(),
    "-": FnSub(),
    "*": FnMul(),
    "/": FnDiv()
}
