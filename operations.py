OPERATIONS = {}
def oper(name):
    def wrap(cls):
        OPERATIONS[name] = cls
        return cls
    return wrap


class Operation(object):
    def has_return_value(self):
        raise NotImplementedError()

    def push(self, operation):
        raise NotImplementedError()

    def run(self):
        pass


class Statement(Operation):
    def has_return_value(self):
        return False


class Expression(Operation):
    def has_return_value(self):
        return True


class BlockOperation(Operation):
    def __init__(self):
        self.body = []

    def push(self, operation):
        self.body.append(operation)

    def run(self):
        for op in self.body:
            op.run()


class FirstExprBlockOperation(BlockOperation):
    def __init__(self):
        self.first = None
        self.body = []

    def push(self, operation):
        if self.first is None:
            self.first = operation
            return
        return super(FirstExprBlockOperation, self).push(operation)


class NoParamStatement(Statement):
    pass


class InfixOperation(Expression):
    def __init__(self, left):
        self.left = left
        self.right = None

    def push(self, operation):
        self.right = operation


@oper(",")
class Continuation(InfixOperation):
    def __init__(self, left):
        if isinstance(left, Continuation):
            self.value = left.value
        else:
            self.value = [left]

    def push(self, operation):
        if isinstance(operation, Continuation):
            self.value = operation.value
            return
        self.value.append(operation)

    def run(self):
        return tuple(self.value)


class Literal(Operation):
    def __init__(self, value):
        self.value = value

    def run(self):
        return self.value
