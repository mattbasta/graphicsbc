import colorsys
import math
from functools import wraps

import mpmath


class BreakInterrupt(StandardError):
    pass


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
    def __repr__(self):
        return "Statement(%s)>%s" % (self.name, self.body)


class PrefixExpression(Expression, PrefixOperation):
    def __repr__(self):
        return "Expression(%s)>%s" % (self.name, self.body)


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
                    raise Exception("Tuple of invalid length (%s got %d)" %
                                        (length, len(self.body.value)))

            return f(self, context)
        return wrap
    return dec


@oper("n")
class NegateOperation(PrefixExpression):
    name = "Negate"
    def run(self, context):
        return self.body.run(context) * -1


@oper("N")
class NotOperation(PrefixExpression):
    name = "Not"
    def run(self, context):
        return self.body.run(context) == 0


@oper("&")
class AndOperation(PrefixExpression):
    name = "And"
    @expect_continuation(2)
    def run(self, context):
        left, right = self.body.value
        return 0 if left.run(context) == 0 else right.run(context)


@oper("|")
class OrOperation(PrefixExpression):
    name = "Or"
    @expect_continuation(2)
    def run(self, context):
        left, right = self.body.value
        left = left.run(context)
        return left if left != 0 else right.run(context)


@oper("I")
class IffOperation(PrefixExpression):
    name = "Iff"
    @expect_continuation(3)
    def run(self, context):
        condition, left, right = self.body.value
        return left.run(context) if condition else right.run(context)


@oper("X")
class XOROperation(PrefixExpression):
    name = "XOR"
    @expect_continuation(2)
    def run(self, context):
        left, right = self.body.run(context)
        left, right = bool(left), bool(right)
        return left != right


@oper("s")
class SinOperation(PrefixExpression):
    name = "Sin"
    def run(self, context):
        return math.sin(self.body.run(context))


@oper("o")
class CosOperation(PrefixExpression):
    name = "Cos"
    def run(self, context):
        return math.cos(self.body.run(context))


@oper("T")
class TanOperation(PrefixExpression):
    name = "Tan"
    def run(self, context):
        return math.tan(self.body.run(context))


@oper("E")
class SecOperation(PrefixExpression):
    name = "Sec"
    def run(self, context):
        return mpmath.sec(self.body.run(context))


@oper("O")
class CscOperation(PrefixExpression):
    name = "Csc"
    def run(self, context):
        return mpmath.csc(self.body.run(context))


@oper("Y")
class CotOperation(PrefixExpression):
    name = "Cot"
    def run(self, context):
        return mpmath.cot(self.body.run(context))


@oper("!")
class TrigInverterOperation(PrefixExpression):
    name = "Inv"
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
    name = "Floor"
    def run(self, context):
        return math.floor(self.body.run(context))


@oper("`")
class CeilOperation(PrefixExpression):
    name = "Ceil"
    def run(self, context):
        return math.ceil(self.body.run(context))


@oper('"')
class SquareOperation(PrefixExpression):
    name = "Square"
    def run(self, context):
        return self.body.run(context) ** 2


@oper("\\")
class SqRootOperation(PrefixExpression):
    name = "Sqrt"
    def run(self, context):
        out = self.body.run(context)
        if isinstance(out, tuple):
            base, degree = out
            return base ** (1 / degree)
        return math.sqrt(out)


@oper("a")
class AssignOperation(PrefixExpression):
    name = "Assignment"
    def run(self, context):
        out = self.body.run(context)
        if isinstance(out, tuple):
            # An assignment
            id_, value = out
            context.vars_[id_] = value
            #print "%d = %s" % out
            return value

        if out in context.vars_:
            return context.vars_[out]
        return 0


@oper("q")
class CallOperation(PrefixExpression):
    name = "Call"
    def run(self, context):
        out = self.body.run(context)
        if isinstance(out, tuple):
            func, args = out[0], out[1:]
        else:
            func, args = out, []
        if func not in context.funcs:
            raise Exception("Function `%d` not yet defined." % func)

        # Set up the arguments
        args = enumerate(list(reversed(args)))
        for idx, arg in args:
            context.vars_[(idx + 1) * -1] = arg

        out = 0
        for op in context.funcs[func].body:
            out = op.run(context)
        if out is None:
            out = 0
        return out


class BlockOperation(Operation):
    name = "Unknown Block"
    def __init__(self):
        self.body = []

    def push(self, operation):
        self.body.append(operation)

    def run(self, context):
        for op in self.body:
            op.run(context)

    def __repr__(self):
        return "block(%s){%s}" % (self.name,
                                  ",".join(map(repr, self.body)))


class BlockExpression(Expression):
    name = "Unknown Block Expression"
    def __init__(self):
        self.body = None

    def push(self, node):
        self.body = node

    def run(self, context):
        if self.body is not None:
            return self.body.run(context)
        return 0

    def __repr__(self):
        return "block(%s)<<{%s}" % (self.name,
                                    ",".join(map(repr, self.body)))


class FirstExprBlockOperation(BlockOperation):
    def __init__(self):
        self.first = None
        self.body = []

    def push(self, operation):
        if self.first is None:
            self.first = operation
            return
        return super(FirstExprBlockOperation, self).push(operation)

    def __repr__(self):
        return "block(%s)<%s>{%s}" % (self.name,
                                      self.first,
                                      ",".join(map(repr, self.body)))


@oper("L")
class LoopBlock(FirstExprBlockOperation):
    name = "Loop"
    def run(self, context):
        try:
            for i in range(self.first.run(context)):
                super(LoopBlock, self).run(context)
        except BreakInterrupt:
            pass


@oper("i")
class ConditionalBlock(FirstExprBlockOperation):
    name = "Conditional"
    def run(self, context):
        if self.first.run(context) != 0:
            super(ConditionalBlock, self).run(context)


class ExecutableOperation(BlockOperation):
    name = "Executable Block"
    def execute(self, context):
        for o in self.body:
            o.run(context)


@oper("@")
class LambdaBlock(ExecutableOperation):
    name = "Lambda"
    def run(self, context):
        context.funcs[context._next_id()] = self


@oper("{")
class FunctionBlock(FirstExprBlockOperation, ExecutableOperation):
    name = "Function"
    def run(self, context):
        id = self.first.run(context)
        if id in context.funcs:
            raise Exception("Function %d already defined" % id)
        context.funcs[id] = self


@oper("T")
class AnyBlock(BlockOperation):
    name = "Any"
    def run(self, context):
        for op in self.body:
            out = op.run(context)
            if out != 0:
                return out
        return 0


@oper("A")
class AllBlock(BlockOperation):
    name = "All"
    def run(self, context):
        return 1 if all(o.run(context) for o in self.body) else 0


@oper("U")
class SumBlock(BlockOperation):
    name = "Sum"
    def run(self, context):
        try:
            return sum(o.run(context) for o in self.body)
        except ValueError:
            raise Exception("Invalid values summed.")


class NoParamStatement(Statement):
    pass


@oper(";")
class BreakStatement(NoParamStatement):
    def run(self, context):
        raise BreakInterrupt()


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
    name = "RGBA"
    @expect_continuation((3, 4))
    def run(self, context):
        body = self.body.run(context)
        mode = "rgba" if len(body) == 4 else "rgb"
        context.canvas.set_color(mode=mode, *body)


@oper("H")
class HSLStatement(PrefixStatement):
    name = "HSLA"
    @expect_continuation((3, 4))
    def run(self, context):
        values = self.body.run(context)
        a = 255 if len(values) == 3 else values[3]
        print values[:3]
        h, s, l = map(lambda x: float(x) / 255, values[:3])
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        context.canvas.set_color(r, g, b, mode="rgb")


@oper("K")
class CMYKStatement(PrefixStatement):
    name = "CMYK"
    @expect_continuation(4)
    def run(self, context):
        context.canvas.set_color(mode="cmyk", *self.body.run(context))


@oper("p")
class CursorStatement(PrefixStatement):
    name = "Cursor"
    @expect_continuation(2)
    def run(self, context):
        context.canvas.set_cursor(*self.body.run(context))


@oper("t")
class TranslateStatement(PrefixStatement):
    name = "Translate"
    @expect_continuation(2)
    def run(self, context):
        context.canvas.translate(*self.body.run(context))


@oper("r")
class RotateStatement(PrefixStatement):
    name = "Rotate"
    def run(self, context):
        context.canvas.rotate(self.body.run(context))


@oper("S")
class ScaleStatement(PrefixStatement):
    name = "Scale"
    def run(self, context):
        context.canvas.scale(*self.body.run(context))


class InfixOperation(Expression):
    name = "Generic Infix Operation"
    def __init__(self, left):
        self.left = left
        self.right = None

    def push(self, operation):
        self.right = operation

    def run(self, context):
        left, right = self.left.run(context), self.right.run(context)
        return self._run(left, right)

    def __repr__(self):
        return "(%s %s %s)" % (repr(self.left), str(type(self)), repr(self.right))


@oper("+")
class PlusOperation(InfixOperation):
    def _run(self, left, right):
        return left + right


@oper("*")
class MultOperation(InfixOperation):
    def _run(self, left, right):
        return left * right


@oper("/")
class DivOperation(InfixOperation):
    def _run(self, left, right):
        return left / right


@oper("-")
class SubOperation(InfixOperation):
    def _run(self, left, right):
        return left - right


@oper("%")
class ModOperation(InfixOperation):
    def _run(self, left, right):
        return left % right


@oper("^")
class PowOperation(InfixOperation):
    def _run(self, left, right):
        return left ** right


@oper("~")
class IntDivOperation(InfixOperation):
    def _run(self, left, right):
        return math.floor(left / right)


@oper(">")
class GTOperation(InfixOperation):
    def _run(self, left, right):
        return left > right


@oper("g")
class GTOperation(InfixOperation):
    def _run(self, left, right):
        return left >= right


@oper("=")
class GTOperation(InfixOperation):
    def _run(self, left, right):
        return left == right


@oper("x")
class GTOperation(InfixOperation):
    def _run(self, left, right):
        return left != right


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

    def __repr__(self):
        return "[%s]" % ",".join(map(repr, self.value))


class Literal(Operation):
    def __init__(self, value):
        if "." in value:
            value = float(value)
        else:
            value = int(value)
        self.value = value

    def run(self, context):
        return self.value

    def __repr__(self):
        return "[%d]" % self.value
