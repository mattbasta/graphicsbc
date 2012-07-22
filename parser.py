from operations import *


NUMBERS = ".0123456789"
BLOCK_END = ")"
BLOCKS = "Li@{TAU"
SINGLE_OPERATIONS = "#<"
PREFIX_STATEMENTS = "cCKpdtrSP"
PREFIX_EXPRESSIONS = "nN&|IXsoTEOY_`\"!\\aq"
INFIX_EXPRESSIONS = "+-*/^%~M>g=x"
CONTINUATION = ","
WHITESPACE = " \n\r\t"

STATEMENTS = SINGLE_OPERATIONS + PREFIX_STATEMENTS


class Parser(object):

    def __init__(self, data):
        self.data = data
        self.buffer = ""
        self.blocks = [BlockOperation()]
        self.expressions = []

    def push_block(self, block):
        self.blocks.append(block)

    def pop_block(self):
        block = self.blocks.pop()
        if self.expressions:
            block.push(self.collapse_expressions())
        self.blocks[-1].push(block)
        return block

    def push_to_block(self, node):
        if self.expressions:
            self.push_to_block(self.collapse_expressions())
        self.blocks[-1].push(node)

    def push_to_tip(self, node):
        if self.expressions:
            e = self.expressions[-1]
            if isinstance(e, Literal):
                raise Exception("Cannot push literal to literal")
            if isinstance(e, Continuation):
                e.push(node)
                return
        self.expressions.append(node)

    def collapse_expressions(self, offset=0):
        e = None
        while self.expressions[offset:]:
            e = self.expressions.pop()
            if self.expressions:
                self.expressions[-1].push(e)
        return e

    def run():
        for char in self.data:
            if char not in NUMBERS and self.buffer:
                self.push_to_block(Literal("".join(self.buffer)))
                self.buffer = ""
            elif char in NUMBERS:
                # Don't accept numbers like `10.23.4`
                if char == "." and "." in buffer:
                    raise Exception("Invalid numeric literal.")
                self.buffer += char
                continue

            if char == CONTINUATION:
                if not self.expressions:
                    raise Exception("Continuation inside block")
                e = self.expressions.pop()
                if (not issubclass(type(e), Literal) or
                    not issubclass(type(e), Expression)):
                    raise Exception("Continuation against non-expressive value")
                c = Continuation(e)
                self.push_to_tip(c)
                continue

            if char == BLOCK_END:
                # If we find the end of a block expression, just deal with it
                # and move along.
                found = False
                for index, value in reversed(enumerate(self.expressions)):
                    if not isinstance(value, BlockExpression):
                        continue
                    self.push_to_tip(self.collapse_expressions(index))
                    found = True
                    break
                if found:
                    continue

                # Test that there's a block on the block stack to close.
                if not any(issubclass(type(b), BlockOperation) for
                           b in self.blocks):
                    raise Exception("End of block detected outside of block")

                if self.expressions:
                    self.push_to_block(self.collapse_expressions())

                # Keep popping until we've popped a block.
                p = self.pop_block()
                while not issubclass(type(p), BlockOperation):
                    p = self.pop_block()
                continue

            if char in WHITESPACE:
                if self.expressions:
                    e = self.expressions.pop()
                    if self.expressions:
                        self.expressions[-1].push(e)
                    else:
                        self.push_to_block(e)
                continue

            if char in STATEMENTS:
                if self.expressions:
                    raise Exception("Statements cannot be pushed to "
                                    "expressions.")
                self.push_to_block(OPERATIONS[char]())
            elif char in PREFIX_EXPRESSIONS:
                self.push_to_tip(OPERATIONS[char]())
            elif char in INFIX_EXPRESSIONS:
                if not self.expressions:
                    raise Exception("Infix operation in invalid location.")
                e = self.expressions.pop()
                self.push_to_tip(OPERATIONS[char](e))


        if self.expressions:
            raise Exception("Expressions remaining on the stack at termination.")

        body = self.blocks.pop()
        if self.blocks:
            raise Exception("Unclosed blocks detected at end of program.")

        return body
