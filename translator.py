import sys
from os import path
import os

from code_writer import *
from parser import *

# GLOBALS
writer = None

def translateFile(infile):
    parser = Parser(infile)

    file_base = path.basename(path.splitext(infile)[0])
    writer.setFileName(file_base)

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
        elif parser.commandType() == C_FUNCTION:
            writer.writeFunction(parser.arg1(), int(parser.arg2()))
        elif parser.commandType() == C_CALL:
            writer.writeCall(parser.arg1(), int(parser.arg2()))
        elif parser.commandType() == C_RETURN:
            writer.writeReturn()
        count += 1

if __name__ == '__main__':
    inpath = sys.argv[1]
    outpath = path.splitext(inpath)[0]
    
    writer = CodeWriter(outpath)

    if path.isdir(inpath):
        files = [f for f in os.listdir(inpath)
                 if path.isfile(path.join(inpath, f)) and path.splitext(f)[1] == '.vm']
        for infile in files:
            translateFile(path.join(inpath, infile))
    else:
        translateFile(inpath)


    
    writer.loop()
    writer.close()