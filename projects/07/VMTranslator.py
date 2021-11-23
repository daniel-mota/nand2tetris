from posixpath import join
import sys, os

pwd = os.path.dirname(__file__)
path = os.path.join(pwd, sys.argv[1])
path2Write = path[:len(path) - 2] + 'asm'

file = open(path, 'r')
asm = open(path2Write, 'w')

locAdr = {
    'constant': 'SP',
    'local': 'LCL',
}

def main(file):
    # go thru all file
    for line in file:
        if line[0] == '/' or line[0] == '\r':
            continue
        lastChar = line.find('\r')
        line = line[0:lastChar]
        asm.write('//' + line + '\n');
        for l in parser(line):
            asm.write(l + '\n');


def parser(line):
    # parse line and return it
    split = line.split()

    if split[0] == 'push' or split[0] == 'pop':
        # do push or pop operation
        return p_encoder(split[0], split[1], split[2]);
    else:
        return a_encoder(split[0])

num = 0
def comp_comm(comm, instr):
    global num
    instr.append('@SP')
    instr.append('AM=M-1')
    instr.append('D=M')
    instr.append('M=0')
    instr.append('A=A-1')
    instr.append('D=M-D')
    instr.append('M=0')
    instr.append('@TRUE' + str(num))
    instr.append('D;' + comm)
    instr.append('@CONTINUE' + str(num))
    instr.append('0;JMP')
    instr.append('(TRUE' + str(num) + ')')
    instr.append('@SP')
    instr.append('A=M-1')
    instr.append('M=-1')
    instr.append('(CONTINUE' + str(num) + ')')
    num += 1

def bool_comm(comm, instr):
    instr.append('@0')
    instr.append('AM=M-1')
    instr.append('D=M')
    instr.append('M=0')
    instr.append('A=A-1')
    instr.append('M=M' + comm + 'D')

def p_encoder(comm, store, i):
    # encodes each line and returns it
    asmInstruct = []
    if comm == 'push':
        # @i, d=a
        asmInstruct.append('@' + i)
        asmInstruct.append('D=A')
        asmInstruct.append('@SP')
        asmInstruct.append('A=M')
        asmInstruct.append('M=D')
        asmInstruct.append('@SP')
        asmInstruct.append('M=M+1')
    return asmInstruct

def a_encoder(comm):
    asmInstruct = []
    if comm == 'add':
        asmInstruct.append('@0')
        asmInstruct.append('A=M-1')
        asmInstruct.append('D=M')
        asmInstruct.append('M=0')
        asmInstruct.append('A=A-1')
        asmInstruct.append('M=D+M')
        asmInstruct.append('@0')
        asmInstruct.append('M=M-1')
    elif comm == 'sub':
        asmInstruct.append('@0')
        asmInstruct.append('M=M-1')
        asmInstruct.append('A=M')
        asmInstruct.append('D=M')
        asmInstruct.append('M=0')
        asmInstruct.append('A=A-1')
        asmInstruct.append('M=M-D')
    elif comm == 'neg':
        asmInstruct.append('@0')
        asmInstruct.append('A=M-1')
        asmInstruct.append('M=-M')
    elif comm == 'not':
        asmInstruct.append('@0')
        asmInstruct.append('A=M-1')
        asmInstruct.append('M=!M')
    elif comm == 'and':
        bool_comm('&', asmInstruct)
    elif comm == 'or':
        bool_comm('|', asmInstruct)
    elif comm == 'eq':
        comp_comm('JEQ', asmInstruct)
    elif comm == 'gt':
        comp_comm('JGT', asmInstruct)
    elif comm == 'lt':
        comp_comm('JLT', asmInstruct)
    return asmInstruct

        
main(file)
