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

class OpDef(Operative):

    def __init__(self):
        Operative.__init__(self, "def")

    def call(self, args, cc):
        arglist = list(args)
        arglen = len(arglist)

        if arglen < 2:
            raise TypeError("%s expected at least 2 arguments, got %d" % (
                self.name, arglen))
        else:
            name = arglist[0]
            funargs = arglist[1]
            body = arglist[2:]

            if not isinstance(name, Symbol):
                raise TypeError("function name expected to be a symbol, got %s" % (name.__str__()))

            if not isinstance(funargs, Pair):
                raise TypeError("function args expected to be a list, got %s of type %s" % (funargs.__str__(), type(funargs)))

            namestr = name.__str__()
            fn = PFn(namestr, funargs, body)

            cc.env.set(namestr, fn)
            return cc.resolve(fn)
