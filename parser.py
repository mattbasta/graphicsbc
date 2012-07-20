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


class Parser(object):

    def __init__(self, data):
        self.data = data
        self.buffer = ""
        self.blocks = [BlockOperation()]

    def push_block(self, block):
        self.blocks.append(block)

    def pop_block(self):
        block = self.blocks.pop()
        self.blocks[-1].push(block)
        return block

    def push_to_block(self, node):
        self.blocks[-1].push(node)

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

            if char == BLOCK_END:
                # Test that there's a block on the block stack to close.
                if not any(issubclass(type(b), BlockOperation) for
                           b in self.blocks):
                    raise Exception("End of block detected outside of block")

                # Keep popping until we've popped a block.
                p = self.pop_block()
                while not issubclass(type(p), BlockOperation):
                    p = self.pop_block()
                continue

            if char in WHITESPACE:
                # Whitespace should pop any non-block operation.
                while not issubclass(type(self.blocks[-1]), BlockOperation):
                    self.pop_block()
                continue

        body = self.blocks.pop()
        if self.blocks:
            raise Exception("Unclosed blocks detected at end of program.")
