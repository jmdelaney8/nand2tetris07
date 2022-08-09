C_ARITHMETIC = 1
C_PUSH = 2
C_POP = 3
C_LABEL = 4
C_GOTO = 5
C_IF = 6
C_FUNCTION = 7
C_RETURN = 8
C_CALL = 9

class Parser:
    _command_type = None
    _arg1 = None
    _arg2 = None
    def __init__(self, infile):
        self.file = open(infile, 'r')
        self.command = None  # Assume a new line will be read to initialize 

    
    def hasMoreLines(self):
        self.command = self.file.readline()
        if not self.command:
            return False
        return True


    def advance(self):
        self.parse()


    def parse(self):
        # Parse op
        command = self.command.split('\n')[0]
        op = command.split(' ')[0]
        print('op = {}'.format(op))
        if op in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            self._command_type = C_ARITHMETIC
        elif op == 'push':
            self._command_type = C_PUSH
        elif op == 'pop':
            self._command_type = C_POP
        else:
            # Must be comment or empty line
            self._command_type = None
            self._arg1 = None
            self._arg2 = None
            return
        #TODO: parse label, if, function, goto, return, and call ops

        # Parse arg1
        if self._command_type == C_ARITHMETIC:
            self._arg1 = op
        elif self._command_type == C_RETURN:
            self._arg1 = None
        else:
            self._arg1 = self.command.split(' ')[1]

        # Parse arg2
        if self._command_type in [C_PUSH, C_POP, C_FUNCTION, C_CALL]:
            self._arg2 = self.command.split(' ')[2]
        else:
            self._arg2 = None


    def commandType(self):
        return self._command_type


    def arg1(self):
        return self._arg1


    def arg2(self):
        return self._arg2

