from ptypes import *

class FnPrint(Fn):
    def __init__(self):
        Fn.__init__(self, "println")

    def call(self, args, cc):
        arglist = args.to_list()
        for arg in arglist:
            print arg.__str__(),
        print

        return cc.resolve(nil)

class FnList(Fn):
    def __init__(self):
        Fn.__init__(self, "list")

    def call(self, args, cc):
        return cc.resolve(args)

class OpDef(Operative):

    def __init__(self):
        Operative.__init__(self, "def")

    def call(self, args, cc):
        arglist = args.to_list()
        arglen = len(arglist)

        if arglen < 2:
            raise TypeError("%s expected at least 2 arguments, got %d" % (
                self.name, arglen), args)
        else:
            name = arglist[0]
            funargs = arglist[1]
            body = arglist[2:]

            if not isinstance(name, Symbol):
                raise TypeError("function name expected to be a symbol, got %s" % (name.__str__()), name)

            if not isinstance(funargs, Pair):
                raise TypeError("function args expected to be a list, got %s" % funargs.__str__(), funargs)

            namestr = name.__str__()
            fn = PFn(namestr, funargs, body)

            cc.env.set(namestr, fn)
            return cc.resolve(fn)

class OpDo(Operative):
    def __init__(self):
        Operative.__init__(self, "do")

    def call(self, args, cc):
        holder = ResultHolder()
        for expr in args:
            expr_cc = Cc(expr, holder, cc.env)
            expr.eval(cc).run()

        return cc.resolve(holder.result)
