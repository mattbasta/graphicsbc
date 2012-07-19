OPERATIONS = {}
def oper(name):
    def wrap(cls):
        OPERATIONS[name] = cls
        return cls
    return wrap


class Operation(object):
    def run(self):
        pass


class BlockOperation(Operation):
    def __init__(self):
        self.body = []

    def push(self, operation):
        self.body.append(operation)

    def run(self):
        for op in self.body:
            op.run()


