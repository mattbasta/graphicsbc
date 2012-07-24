import math
from functools import wraps

import mpmath


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


class PrefixOperation(Statement):
    def __init__(self):
        self.body = None

    def push(self, node):
        self.body = node


class PrefixStatement(PrefixOperation):
    pass


class PrefixExpression(PrefixOperation):
    pass


def expect_continuation(len_=None):
    def dec(f):
        def wrap(self, context):
            if not self.body:
                raise Exception("Tuple not passed to prefix statement")
            if not isinstance(self.body, Continuation):
                raise Exception("Expected tuple, got non-tuple")

            if len_ is not None:
                length = (len_, ) if not isinstance(len_, tuple) else len_
                if len(self.body.value) not in length:
                    raise Exception("Tuple of invalid length")

            return f(self, context)
        return wrap
    return dec


@oper("n")
class NegateOperation(PrefixExpression):
    def run(self, context):
        return self.body.run(context) * -1


@oper("N")
class NotOperation(PrefixExpression):
    def run(self, context):
        return self.body.run(context) == 0


@oper("&")
class AndOperation(PrefixExpression):
    @expect_continuation(2)
    def run(self, context):
        left, right = self.body.value
        return 0 if left.run(context) == 0 else right.run(context)


@oper("|")
class OrOperation(PrefixExpression):
    @expect_continuation(2)
    def run(self, context):
        left, right = self.body.value
        left = left.run(context)
        return left if left != 0 else right.run(context)


@oper("I")
class IffOperation(PrefixExpression):
    @expect_continuation(3)
    def run(self, context):
        condition, left, right = self.body.value
        return left.run(context) if condition else right.run(context)


@oper("X")
class XOROperation(PrefixExpression):
    @expect_continuation(2)
    def run(self, context):
        left, right = self.body.run(context)
        left, right = bool(left), bool(right)
        return left != right


@oper("s")
class SinOperation(PrefixExpression):
    def run(self, context):
        return math.sin(self.body.run(context))


@oper("o")
class CosOperation(PrefixExpression):
    def run(self, context):
        return math.cos(self.body.run(context))


@oper("T")
class TanOperation(PrefixExpression):
    def run(self, context):
        return math.tan(self.body.run(context))


@oper("E")
class SecOperation(PrefixExpression):
    def run(self, context):
        return mpmath.sec(self.body.run(context))


@oper("O")
class CscOperation(PrefixExpression):
    def run(self, context):
        return mpmath.csc(self.body.run(context))


@oper("Y")
class CotOperation(PrefixExpression):
    def run(self, context):
        return mpmath.cot(self.body.run(context))


@oper("!")
class TrigInverterOperation(PrefixExpression):
    def run(self, context):
        if isinstance(self.body, SinOperation):
            return math.asin(self.body.body.run(context))
        if isinstance(self.body, CosOperation):
            return math.acos(self.body.body.run(context))
        if isinstance(self.body, TanOperation):
            return math.atan(self.body.body.run(context))
        if isinstance(self.body, SecOperation):
            return mpmath.asec(self.body.body.run(context))
        if isinstance(self.body, CscOperation):
            return mpmath.acsc(self.body.body.run(context))
        if isinstance(self.body, CotOperation):
            return mpmath.acot(self.body.body.run(context))

        raise Exception("Unsupported inversion operation.")


@oper("_")
class FloorOperation(PrefixExpression):
    def run(self, context):
        return math.floor(self.body.run(context))


@oper("`")
class CeilOperation(PrefixExpression):
    def run(self, context):
        return math.ceil(self.body.run(context))


@oper('"')
class SquareOperation(PrefixExpression):
    def run(self, context):
        return self.body.run(context) ** 2


@oper("\\")
class SqRootOperation(PrefixExpression):
    def run(self, context):
        out = self.body.run(context)
        if isinstance(out, tuple):
            base, degree = out
            return base ** (1 / degree)
        return math.sqrt(out)


@oper("a")
class AssignOperation(PrefixExpression):
    def run(self, context):
        out = self.body.run(context)
        if isinsatnce(out, tuple):
            # An assignment
            id_, value = out
            context.vars_[id_] = value
            return value

        if out in context.vars_:
            return context.vars_[out]
        return 0


@oper("q")
class CallOperation(PrefixExpression):
    @expect_continuation()
    def run(self, context):
        out = self.body.run(context)
        func, args = out[0], out[1:]
        if func not in context.funcs:
            raise Exception("Function `%d` not yet defined." % func)

        # Set up the arguments
        args = enumerate(list(reversed(args)))
        for idx, arg in args:
            context.vars_[(idx + 1) * -1] = arg

        out = 0
        for op in context.funcs[func]:
            out = op.run(context)
        if out is None:
            out = 0
        return out


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
            super(LoopBlock, self).run(context)


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


@oper("#")
class ClearMatStatement(NoParamStatement):
    def run(self, context):
        context.canvas.clear_transforms()


@oper("<")
class PopMatStatement(NoParamStatement):
    def run(self, context):
        context.canvas.pop()


@oper("d")
class DotStatement(NoParamStatement):
    def run(self, context):
        context.canvas.dot()


@oper("P")
class PathStatement(NoParamStatement):
    def run(self, context):
        context.canvas.line()


@oper("C")
class RGBStatement(PrefixStatement):
    # TODO: This should support RGBA, as well.
    @expect_continuation((3, 4))
    def run(self, context):
        mode = "rgba" if len(self.body) == 4 else "rgb"
        context.canvas.set_color(mode=mode, *self.body.run(context))


@oper("K")
class CMYKStatement(PrefixStatement):
    # TODO: This should support RGBA, as well.
    @expect_continuation(4)
    def run(self, context):
        context.canvas.set_color(mode="cmyk", *self.body.run(context))


@oper("p")
class CursorStatement(PrefixStatement):
    @expect_continuation(2)
    def run(self, context):
        context.canvas.set_cursor(*self.body.run(context))


@oper("t")
class TranslateStatement(PrefixStatement):
    @expect_continuation(2)
    def run(self, context):
        context.canvas.translate(*self.body.run(context))


@oper("r")
class RotateStatement(PrefixStatement):
    def run(self, context):
        context.canvas.rotate(self.body.run(context))


@oper("S")
class ScaleStatement(PrefixStatement):
    def run(self, context):
        context.canvas.scale(*self.body.run(context))


class InfixOperation(Expression):
    def __init__(self, left):
        self.left = left
        self.right = None

    def push(self, operation):
        self.right = operation


@oper("+")
class PlusOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) + self.right.run(context)


@oper("*")
class MultOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) * self.right.run(context)


@oper("/")
class DivOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) / self.right.run(context)


@oper("-")
class SubOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) - self.right.run(context)


@oper("%")
class ModOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) % self.right.run(context)


@oper("^")
class PowOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) ** self.right.run(context)


@oper("~")
class IntDivOperation(InfixOperation):
    def run(self, context):
        return math.floor(self.left.run(context) / self.right.run(context))


@oper(">")
class GTOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) > self.right.run(context)


@oper("g")
class GTOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) >= self.right.run(context)


@oper("=")
class GTOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) == self.right.run(context)


@oper("x")
class GTOperation(InfixOperation):
    def run(self, context):
        return self.left.run(context) != self.right.run(context)


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
        return tuple(v.run(context) for v in self.value)


class Literal(Operation):
    def __init__(self, value):
        if "." in value:
            value = float(value)
        else:
            value = int(value)
        self.value = value

    def run(self, context):
        return self.value
