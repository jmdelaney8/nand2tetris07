from parser import *
from os import path

# Segment constants
SP = 0
LCL = 1
ARG = 2
THIS = 3
THAT = 4
TEMP = 5
TEMP_LEN = 8


class CodeWriter:
    def __init__(self, outpath):
        self.filename = None
        self.bool_count = 0
        self.call_counts = {}  # keep track of number of calls in a function
        outfilename = path.basename(outpath) + '.asm'
        self.file = open(path.join(outpath, outfilename), 'w')
        self.writeInitialize()


    def setFileName(self, name):
        self.filename = name


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
        self.writePop('R13')
        self.writePop()
        self.file.write('@R13\n')
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
        self.writePop('R13')
        self.writePop()
        self.file.write('@R13\n')
        self.file.write('D=D-M\n')
        self.file.write('@TRUE{}\n'.format(self.bool_count))
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
        self.file.write('(TRUE{})\n'.format(self.bool_count))
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
        self.file.write('// {} {} {}\n'.format(command, segment, index))

        if op == C_PUSH:
            if segment == 'constant':
                self.file.write('@{}\n'.format(index))
                self.file.write('D=A\n')
            elif segment == 'static':
                self.file.write('@{}.{}\n'.format(self.filename, index))
                self.file.write('D=M\n')
            else:
                self.writeGetPointerAddress(segment, index)
                self.file.write('A=D\n')
                self.file.write('D=M\n')            
            self.writePushD()
        elif op == C_POP:
            if segment == 'static':
                self.writePop('{}.{}'.format(self.filename, index))
            else:
                self.writeGetPointerAddress(segment, index)
                self.file.write('@R13\n')
                self.file.write('M=D\n')
                self.writePop()
                self.file.write('@R13\n')
                self.file.write('A=M\n')
                self.file.write('M=D\n')


    def writeGetPointerAddress(self, segment, index):
        """
        Places address in D register. Assume it's not called
        for constant segment.
        """
        # Find the base address to use
        base = None
        if segment == 'local':
            base = LCL
        elif segment == 'argument':
            base = ARG
        elif segment == 'this':
            base = THIS
        elif segment == 'that':
            base = THAT
        elif segment == 'temp':
            base = TEMP
        elif segment == 'pointer':
            if int(index) == 0:
                base = THIS
                index = 0
            elif int(index) == 1:
                base = THAT
                index = 0
            else:
                print('WARNING bad index {} for pointer'.format(index))
        else:
            print('WARNING bad segment {}'.format(segment))

        self.file.write('@{}\n'.format(index))
        self.file.write('D=A\n')
        self.file.write('@{}\n'.format(base))
        # TODO: Do I need to include pointer with temp?
        if segment in ['temp', 'pointer']:
            self.file.write('D=A+D\n')
        else:
            self.file.write('D=M+D\n'.format(index))                
            

    def loop(self):
        self.file.write('(END)\n')
        self.file.write('@END\n')
        self.file.write('0;JMP\n')


    def writeInitialize(self):
        self.file.write('// initialize\n')
        self.file.write('@256\n')
        self.file.write('D=A\n')
        self.file.write('@SP\n')
        self.file.write('M=D\n')
        self.writeCall('Sys.init', 0)


    def close(self):
        self.file.close()


    def writeLabel(self, label):
        self.file.write('// label {}\n'.format(label))
        self.file.write('({})\n'.format(label))


    def writeGoto(self, label):
        self.file.write('// goto {}\n'.format(label))
        self.file.write('@{}\n'.format(label))
        self.file.write('0; JMP\n')


    def writeIf(self, label):
        self.file.write('// if-goto {}\n'.format(label))
        self.writePop()
        self.file.write('@{}\n'.format(label))
        self.file.write('D;JNE\n')


    def writeFunction(self, name, nVars):
        self.file.write('// function {} {}\n'.format(name, nVars))
        self.file.write('({})\n'.format(name))
        for _ in range(nVars):
            self.file.write('@0\n')
            self.file.write('D=A\n')
            self.writePushD()


    def writeReturn(self):
        self.file.write('// return\n')
        # Store current LCL pointer
        self.file.write('@LCL\n')
        self.file.write('D=M\n')
        self.file.write('@R13\n')
        self.file.write('M=D\n')
        # Store return address
        self.file.write('@R14\n')
        self.file.write('M=D\n')
        self.file.write('@5\n')
        self.file.write('D=A\n')
        self.file.write('@R14\n')
        self.file.write('D=M-D\n')
        self.file.write('A=D\n')
        self.file.write('D=M\n')
        self.file.write('@R14\n')
        self.file.write('M=D\n')
        # Set arg 0 to return value
        self.writePop()
        self.file.write('@ARG\n')
        self.file.write('A=M\n')
        self.file.write('M=D\n')
        # Set the stack pointer to one past arg0
        self.file.write('D=A\n')
        self.file.write('@SP\n')
        self.file.write('M=D+1\n')
        # Restore registers
        self.writeRestoreRegister('THAT', 1)
        self.writeRestoreRegister('THIS', 2)
        self.writeRestoreRegister('ARG', 3)
        self.writeRestoreRegister('LCL', 4)
        # GOTO return address
        self.file.write('@R14\n')
        self.file.write('A=M\n')
        self.file.write('0;JMP\n')

    def writeRestoreRegister(self, register, offset):
        """
        Restore register when returning a function. Offset of the rgister from the local pointer of callee
        being returned.
        """
        self.file.write('@{}\n'.format(offset))
        self.file.write('D=A\n')
        self.file.write('@R13\n')
        self.file.write('D=M-D\n'.format(offset))
        self.file.write('A=D\n')
        self.file.write('D=M\n')
        self.file.write('@{}\n'.format(register))
        self.file.write('M=D\n')

    def writeCall(self, fname, nArgs):
        self.file.write('// call {} {}\n'.format(fname, nArgs))
        # Set up call count if needed
        if not fname in self.call_counts:
            self.call_counts[fname] = 0
        # Push return address label
        return_address = '{}$ret.{}'.format(fname, self.call_counts[fname])
        self.file.write('@{}\n'.format(return_address))
        self.call_counts[fname] += 1
        self.file.write('D=A\n')
        self.writePushD()
        # Push LCL, ARG, THIS, THAT
        self.writePushRegister('LCL')
        self.writePushRegister('ARG')
        self.writePushRegister('THIS')
        self.writePushRegister('THAT')
        # Reposition ARG
        self.file.write('@SP\n')
        self.file.write('D=M\n')
        self.file.write('@5\n')
        self.file.write('D=D-A\n')
        self.file.write('@{}\n'.format(nArgs))
        self.file.write('D=D-A\n')
        self.file.write('@ARG\n')
        self.file.write('M=D\n')
        # Set LCL 
        self.file.write('@SP\n')
        self.file.write('D=M\n')
        self.file.write('@LCL\n')
        self.file.write('M=D\n')
        # goto f
        self.file.write('@{}\n'.format(fname))
        self.file.write('0;JMP\n')
        # Insert return address
        self.file.write('({})\n'.format(return_address))


    def writePushRegister(self, reg):
        self.file.write('@{}\n'.format(reg))
        self.file.write('D=M\n')
        self.writePushD()
        
