
class Error(Exception):
    pass

class UnboundVariable(Error):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '(UnboundVariable "%s")' % self.name

class TypeError(Error):
    def __init__(self, reason, value):
        self.reason = reason
        self.value = value

    def __str__(self):
        return '(TypeError "%s" %s)' % (self.reason, self.value)

class CallableExpected(Error):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '(CallableExpected %s)' % self.value.__str__()

