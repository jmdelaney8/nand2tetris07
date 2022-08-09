from os import path
from translator import *  # For the op enums


class CodeWriter:
    def __init__(self, infile):
        filename = path.splitext(infile)[0]
        self.bool_count = 0
        self.file = open(filename + '.asm', 'w')

    def writeArithmetic(self, op):
        print('writing arith op: {}'.format(op))
        if op in ['add', 'sub', 'and', 'or']:
            self.writeArithOp(op)
        elif op in ['eq', 'gt', 'lt']:
            self.writeCompare(op)
        elif op in ['not', 'neg']:
            self.file.write('// {}\n'.format(op))
            self.writePop()
            if op == 'not':
                self.file.write('D=!D\n')
            elif op == 'neg':
                self.file.write('D=-D\n')
            self.writePushD()
        else:
            print('ERROR did not act on op: {}'.format(op))





    def writeArithOp(self, op):
        # Log
        self.file.write('//{}\n'.format(op))
        self.writePop('R5')
        self.writePop()
        self.file.write('@R5\n')
        if op == 'add':
            self.file.write('D=D+M\n')
        elif op == 'sub':
            self.file.write('D=D-M\n')
        elif op == 'and':
            self.file.write('D=D&M\n')
        elif op == 'or':
            self.file.write('D=D|M\n')
        self.writePushD()



    def writeCompare(self, op):
        self.file.write('//{}\n'.format(op))
        self.writePop('R5')
        self.writePop()
        self.file.write('@R5\n')
        self.file.write('D=D-M\n')
        self.file.write('@true{}\n'.format(self.bool_count))
        if op == 'eq':
            self.file.write('D;JEQ\n')
        elif op == 'lt':
            self.file.write('D;JLT\n')
        elif op == 'gt':
            self.file.write('D;JGT\n')
        self.file.write('@0\n')
        self.file.write('D=A\n')
        self.file.write('@ENDBOOL{}\n'.format(self.bool_count))
        self.file.write('0; JMP\n')
        self.file.write('(true{})\n'.format(self.bool_count))
        self.file.write('@0\n')
        self.file.write('D=A-1\n')
        self.file.write('(ENDBOOL{})\n'.format(self.bool_count))
        self.bool_count+=1
        self.writePushD()
            



    def writePushD(self):
        self.file.write('@SP\n')
        self.file.write('A=M\n')
        self.file.write('M=D\n')
        self.file.write('@SP\n')
        self.file.write('M=M+1\n')    


    def writePop(self, dest=None):
        self.file.write('@SP\n')
        self.file.write('M=M-1\n')
        self.file.write('A=M\n')
        self.file.write('D=M\n')
        if dest is not None:
            self.file.write('@{}\n'.format(dest))
            self.file.write('M=D\n')


    def writePushPop(self, op, segment, index):
        print('writing PushPop op: {}'.format(op))

        # logging
        command = None
        if op == C_PUSH:
            command = 'push'
        else:
            command = 'pop'
        self.file.write('// {} {} {}'.format(command, segment, index))
        
        # Translation
        if op == C_PUSH:
            self.file.write('@{}'.format(index))
            self.file.write('D=A\n')
            self.writePushD()
        elif op == C_POP:
            self.writePop()

    def loop(self):
        self.file.write('(END)\n')
        self.file.write('@END\n')
        self.file.write('0;JMP\n')

    def close(self):
        self.file.close()

