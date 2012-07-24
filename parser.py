from operations import *


NUMBERS = ".0123456789"
BLOCK_END = ")"
BLOCK_STATEMENTS = "Li@{"
BLOCK_EXPRESSIONS = "(TAU"
SINGLE_OPERATIONS = "#<dP"
PREFIX_STATEMENTS = "CHKptrS"
PREFIX_EXPRESSIONS = "nN&|IXsoTEOY_`\"!\\aq"
INFIX_EXPRESSIONS = "+-*/^%~M>g=x"
CONTINUATION = ","
WHITESPACE = " \n\r\t"

STATEMENTS = SINGLE_OPERATIONS + PREFIX_STATEMENTS


class ParserError(Exception):
    pass


class Parser(object):

    def __init__(self, data):
        self.data = data
        self.buffer = ""
        self.blocks = [BlockOperation()]
        self.expressions = []
        self.position = 0

    def push_block(self, block):
        print "Pushing block"
        self.blocks.append(block)

    def pop_block(self):
        print "Popping block"
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
                raise ParserError("Cannot push expression to literal")
            if isinstance(node, Literal) and isinstance(e, Continuation):
                e.push(node)
                return
        self.expressions.append(node)

    def collapse_expressions(self, offset=0):
        e = None
        print "Collapsing expressions"
        while self.expressions[offset:]:
            e = self.expressions.pop()
            if self.expressions:
                self.expressions[-1].push(e)
        return e

    def run(self):
        for char in self.data:
            self.position += 1
            if char not in NUMBERS and self.buffer:
                value = "".join(self.buffer)
                print "Flushing buffer: %s" % value
                self.push_to_tip(Literal(value))
                self.buffer = ""
            elif char in NUMBERS:
                # Don't accept numbers like `10.23.4`
                if char == "." and "." in self.buffer:
                    raise ParserError("Invalid numeric literal.")
                self.buffer += char
                continue

            if char == CONTINUATION:
                if not self.expressions:
                    raise ParserError("Continuation inside block")
                print "Popping expression for continuation"
                e = self.expressions.pop()
                if not (issubclass(type(e), Literal) or
                        issubclass(type(e), Expression)):
                    raise ParserError("Continuation against non-expressive "
                                      "value (%s)." % e)
                c = Continuation(e)
                self.push_to_tip(c)
                continue

            if char == BLOCK_END:
                # If we find the end of a block expression, just deal with it
                # and move along.
                found = False
                for index, value in reversed(list(enumerate(self.expressions))):
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
                    raise ParserError("End of block detected outside of block")

                if self.expressions:
                    self.push_to_block(self.collapse_expressions())

                # Keep popping until we've popped a block.
                p = self.pop_block()
                while not issubclass(type(p), BlockOperation):
                    p = self.pop_block()
                continue

            if char in WHITESPACE:
                if self.expressions:
                    print "Dealing with whitespace in an expression"
                    e = self.expressions.pop()
                    print "  ", e
                    if isinstance(e, Continuation):
                        print "  Continuation"
                        self.expressions[-1].push(e)
                        e = self.expressions.pop()

                    if self.expressions:
                        print "  Pushing to expression", self.expressions[-1]
                        self.expressions[-1].push(e)
                    else:
                        print "  Pushing to block"
                        self.push_to_block(e)
                continue

            if char in STATEMENTS:
                if self.expressions:
                    self.push_to_block(self.collapse_expressions())
                print "Pushing %s to tip" % char
                self.push_to_tip(OPERATIONS[char]())
            elif char in PREFIX_EXPRESSIONS:
                print "Prefix expression", char
                self.push_to_tip(OPERATIONS[char]())
            elif char in INFIX_EXPRESSIONS:
                print "Infix expression", char
                if not self.expressions:
                    raise ParserError("Infix operation in invalid location.")
                e = self.expressions.pop()
                self.push_to_tip(OPERATIONS[char](e))
            elif char in BLOCK_STATEMENTS:
                print "Block Statement", char
                if self.expressions:
                    self.push_to_block(self.collapse_expressions())
                self.push_block(OPERATIONS[char]())
            elif char in BLOCK_EXPRESSIONS:
                print "Block expression", char
                self.push_to_tip(OPERATIONS[char]())

        if self.expressions:
            raise ParserError("Expressions remaining on the stack at termination.")

        body = self.blocks.pop()
        if self.blocks:
            raise ParserError("Unclosed blocks detected at end of program.")

        return body
