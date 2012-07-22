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

    def run(self, context):
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

    def run(self, context):
        for op in self.body:
            op.run(context)


class BlockExpression(Expression):
    def __init__(self):
        self.body = None

    def push(self, node):
        self.body = node

    def run(self, context):
        if self.body is not None:
            return self.body.run(context)
        return 0


class FirstExprBlockOperation(BlockOperation):
    def __init__(self):
        self.first = None
        self.body = []

    def push(self, operation):
        if self.first is None:
            self.first = operation
            return
        return super(FirstExprBlockOperation, self).push(operation)


@oper("L")
class LoopBlock(FirstExprBlockOperation):
    def run(self, context):
        for i in range(self.first.run(context)):
            super(ConditionalBlock, self).run(context)


@oper("i")
class ConditionalBlock(FirstExprBlockOperation):
    def run(self, context):
        if self.first.run(context) != 0:
            super(ConditionalBlock, self).run(context)


class ExecutableOperation(BlockOperation):
    def execute(self, context):
        for o in self.body:
            o.run(context)


@oper("@")
class LambdaBlock(ExecutableOperation):
    def run(self, context):
        context.funcs[context._next_id()] = self


@oper("{")
class FunctionBlock(FirstExprBlockOperation, ExecutableOperation):
    def run(self, context):
        id = self.first.run(context)
        if id in context.funcs:
            raise Exception("Function %d already defined" % id)
        context.funcs[id] = self


@oper("T")
class AnyBlock(BlockOperation):
    def run(self, context):
        for op in self.body:
            out = op.run(context)
            if out != 0:
                return out
        return 0


@oper("A")
class AllBlock(BlockOperation):
    def run(self, context):
        return 1 if all(o.run(context) for o in self.body) else 0


@oper("U")
class SumBlock(BlockOperation):
    def run(self, context):
        try:
            return sum(o.run(context) for o in self.body)
        except ValueError:
            raise Exception("Invalid values summed.")


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

    def run(self, context):
        return tuple(self.value)


class Literal(Operation):
    def __init__(self, value):
        self.value = value

    def run(self, context):
        return self.value
