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


class NoParamStatement(Operation):
    pass


class InfixOperation(Operation):
    def __init__(self, left):
        self.left = left
        self.right = None

    def push(self, operation):
        self.right = operation


@oper(",")
class Continuation(Operation):
    def __init__(self):
        self.value = []

    def push(self, operation):
        if isinstance(operation, Continuation):
            self.value += operation.value
            return
        self.value.append(operation)

    def run(self):
        return tuple(self.value)


class Literal(Operation):
    def __init__(self, value):
        self.value = value

    def run(self):
        return self.value
