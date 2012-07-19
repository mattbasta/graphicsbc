import sys

from parser import Parser


def main(f):
    with open(f) as file_:
        data = file_.read()
    p = Parser(data)
    p.run()


if __name__ == "__main__":
    main(sys.argv[0])
