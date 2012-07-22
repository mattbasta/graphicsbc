
class Context(object):
    def __init__(self):
        self.vars_ = {}
        self.funcs = {}
        self.counter = 0

    def _next_id(self):
        c = self.counter
        self.counter += 1
        while c in self.vars_ or c in self.funcs:
            c = self.counter
            self.counter += 1
        return c
