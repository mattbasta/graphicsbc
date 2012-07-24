import sys

from contexts import Context
from parser import Parser, ParserError


def main(f):
    with open(f) as file_:
        data = file_.read()
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

    output = sys.argv[2] if len(sys.argv) >= 3 else "/tmp/out.png"
    context.canvas.save(output)


if __name__ == "__main__":
    main(sys.argv[1])
