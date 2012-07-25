import sys

from contexts import Context
from parser import Parser, ParserError


def main(f):
    with open(f) as file_:
        return run(file_.read())

def run(data):
    p = Parser(data)
    try:
        block = p.run()
    except ParserError as e:
        print "Block Stack:"
        print "\n".join(map(repr, p.blocks))
        print "\nExpressions:"
        print "\n".join(map(repr, p.expressions))
        print "\nBuffer: %s" % p.buffer
        print "%s (at position %d)" % (e, p.position)
        return

    context = Context()
    block.run(context)

    return context


if __name__ == "__main__":
    context = main(sys.argv[1])
    output = sys.argv[2] if len(sys.argv) >= 3 else "/tmp/out.png"
    context.canvas.save(output)

