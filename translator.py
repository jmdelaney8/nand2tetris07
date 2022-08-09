import sys

from code_writer import *
from parser import Parser
from parser import *





if __name__ == '__main__':
    infile = sys.argv[1]
    writer = CodeWriter(infile)
    parser = Parser(infile)

    count = 0
    while parser.hasMoreLines():
        print('Command {}'.format(count))
        parser.advance()
        print('command code = {}'.format(parser.commandType()))
        if parser.commandType() == C_ARITHMETIC:
            writer.writeArithmetic(parser.arg1())
        elif parser.commandType() in [C_PUSH, C_POP]:
            writer.writePushPop(parser.commandType(), parser.arg1(), parser.arg2())
        elif parser.commandType() == C_LABEL:
            writer.writeLabel(parser.arg1())
        elif parser.commandType() == C_GOTO:
            writer.writeGoto(parser.arg1())
        elif parser.commandType() == C_IF:
            writer.writeIf(parser.arg1())
        count += 1
    writer.loop()
    writer.close()