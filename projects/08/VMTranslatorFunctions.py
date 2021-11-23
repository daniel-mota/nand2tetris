from posixpath import join
import sys, os

pwd = os.path.dirname(__file__)
path = os.path.join(pwd, sys.argv[1])
path2Write = path[:len(path) - 2] + 'asm'

if os.path.isdir(path):
    dir = os.listdir(path);
    files = []
    for file in dir:
        if file[len(file) - 2:] == 'vm':
            thisFile = os.path.join(path, file)
            files.append(thisFile)
    fileWrite = path.split('/')[-1]
    path2Write = path + '/' + fileWrite + '.asm'
else:
    files = [path]

fileName = path2Write.split('/')
fileName = fileName[-1]
fileName = fileName[:len(fileName) - 4]

asm = open(path2Write, 'w')

locAdr = {
    'constant': 'SP',
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT',
    'temp': 'R5'
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
    elif split[0] == 'label' or split[0] == 'goto' or split[0] == 'if-goto':
        return pf_encoder(split[0], split[1])
    elif split[0] == 'call' or split[0] == 'function':
        return fun_encoder(split[0], split[1], split[2])
    elif split[0] == 'return':
        return fun_encoder(split[0], '', '')
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

foo = 0
def p_encoder(comm, store, i):
    global foo;
    # encodes each line and returns it
    asmInstruct = []
    if comm == 'push':
        if store == 'constant':
        # @i, d=a
            asmInstruct.append('@' + i)
            asmInstruct.append('D=A')
            asmInstruct.append('@SP')
            asmInstruct.append('A=M')
            asmInstruct.append('M=D')
            asmInstruct.append('@SP')
            asmInstruct.append('M=M+1')
        # TODO check for temp
        elif store == 'pointer':
            if i == '0':
                asmInstruct.append('@THIS')
            else:
                asmInstruct.append('@THAT')
            asmInstruct.append('D=M')
            asmInstruct.append('@SP')
            asmInstruct.append('M=M+1')
            asmInstruct.append('A=M-1')
            asmInstruct.append('M=D')
        else:
            if store == 'static':
                asmInstruct.append('@' + fileName + '.' + str(foo))
            else:
                asmInstruct.append('@' + locAdr[store])
            if store == 'temp':
                asmInstruct.append('D=A')
            else:
                asmInstruct.append('D=M')
            asmInstruct.append('@' + i)
            asmInstruct.append('A=D+A')
            asmInstruct.append('D=M')
            asmInstruct.append('@SP')
            asmInstruct.append('AM=M+1')
            asmInstruct.append('A=A-1')
            asmInstruct.append('M=D')
    else:
        if store == 'pointer':
            asmInstruct.append('@SP')
            asmInstruct.append('AM=M-1')
            asmInstruct.append('D=M')
            if i == '0':
                asmInstruct.append('@THIS')
            else:
                asmInstruct.append('@THAT')
            asmInstruct.append('M=D')
        else:
            # implement pop
            if store == 'static':
                    asmInstruct.append('@' + fileName + '.' + str(foo))
            else:
                asmInstruct.append('@' + locAdr[store])
            if store == 'temp':
                asmInstruct.append('D=A')
            else:
                asmInstruct.append('D=M')
            asmInstruct.append('@' + i)
            asmInstruct.append('D=A+D')
            asmInstruct.append('@R13')
            asmInstruct.append('M=D')
            asmInstruct.append('@SP')
            asmInstruct.append('AM=M-1')
            asmInstruct.append('D=M')
            asmInstruct.append('@R13')
            asmInstruct.append('A=M')
            asmInstruct.append('M=D')

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

def pf_encoder(comm, label):
    asmInstruct = []
    if comm == 'label':
        asmInstruct.append('(' + label + ')')
    elif comm == 'goto':
        asmInstruct.append('@' + label)
        asmInstruct.append('0;JMP')
    elif comm == 'if-goto':
        asmInstruct.append('@SP')
        asmInstruct.append('AM=M-1')
        asmInstruct.append('D=M')
        asmInstruct.append('@' + label)
        asmInstruct.append('D;JNE')
    return asmInstruct

retNum = 0
def fun_encoder(comm, fun, nArgs):
    asmInstruct = []
    global retNum
    if comm == 'call':
        # push retrAdress
        asmInstruct.append('@' + fun + '$ret.' + str(retNum))
        asmInstruct.append('D=A')
        asmInstruct.append('@SP')
        asmInstruct.append('AM=M+1')
        asmInstruct.append('A=A-1')
        asmInstruct.append('M=D')
        # push LCL
        asmInstruct.append('@LCL')
        asmInstruct.append('D=M')
        asmInstruct.append('@SP')
        asmInstruct.append('AM=M+1')
        asmInstruct.append('A=A-1')
        asmInstruct.append('M=D')
        # push ARG
        asmInstruct.append('@ARG')
        asmInstruct.append('D=M')
        asmInstruct.append('@SP')
        asmInstruct.append('AM=M+1')
        asmInstruct.append('A=A-1')
        asmInstruct.append('M=D')
        # push THIS
        asmInstruct.append('@THIS')
        asmInstruct.append('D=M')
        asmInstruct.append('@SP')
        asmInstruct.append('AM=M+1')
        asmInstruct.append('A=A-1')
        asmInstruct.append('M=D')
        # push THAT
        asmInstruct.append('@THAT')
        asmInstruct.append('D=M')
        asmInstruct.append('@SP')
        asmInstruct.append('AM=M+1')
        asmInstruct.append('A=A-1')
        asmInstruct.append('M=D')
        # reposition arg
        asmInstruct.append('@SP')
        asmInstruct.append('D=M')
        asmInstruct.append('@5')
        asmInstruct.append('D=D-A')
        asmInstruct.append('@' + nArgs)
        asmInstruct.append('D=D-A')
        asmInstruct.append('@ARG')
        asmInstruct.append('M=D')
        # lcl = sp
        asmInstruct.append('@SP')
        asmInstruct.append('D=M')
        asmInstruct.append('@LCL')
        asmInstruct.append('M=D')
        # goto function
        asmInstruct.append('@' + fun)
        asmInstruct.append('0;JMP')
        # (retAddrLabel)
        asmInstruct.append('(' + fun + '$ret.' + str(retNum) + ')')
        retNum += 1

    elif comm == 'function':
        asmInstruct.append('(' + fun + ')')
        # push nArgs local variables
        for i in range(int(nArgs)):
            asmInstruct.append('@1')
            asmInstruct.append('D=A')
            asmInstruct.append('@SP')
            asmInstruct.append('AM=M+1')
            asmInstruct.append('A=A-1')
            asmInstruct.append('M=0')
            

    elif comm == 'return':
        asmInstruct.append('@LCL')
        asmInstruct.append('D=M')
        asmInstruct.append('@R15') # ! R15 storing endFrame
        asmInstruct.append('M=D')
        asmInstruct.append('@5')
        asmInstruct.append('AD=D-A') # setting return address (endframe - 5)
        asmInstruct.append('D=M')
        asmInstruct.append('@R14')
        asmInstruct.append('M=D')
        # returns return value
        asmInstruct.append('@SP')
        asmInstruct.append('A=M-1')
        asmInstruct.append('D=M')
        asmInstruct.append('@ARG')
        asmInstruct.append('A=M')
        asmInstruct.append('M=D')
        # reposition SP
        asmInstruct.append('D=A+1')
        asmInstruct.append('@SP')
        asmInstruct.append('M=D')
        # restore that
        asmInstruct.append('@R15')
        asmInstruct.append('D=M')
        asmInstruct.append('@1')
        asmInstruct.append('D=D-A')
        asmInstruct.append('A=D')
        asmInstruct.append('D=M')
        asmInstruct.append('@THAT')
        asmInstruct.append('M=D')
        # restore THIS
        asmInstruct.append('@R15')
        asmInstruct.append('D=M')
        asmInstruct.append('@2')
        asmInstruct.append('D=D-A')
        asmInstruct.append('A=D')
        asmInstruct.append('D=M')
        asmInstruct.append('@THIS')
        asmInstruct.append('M=D')
        # restore ARG
        asmInstruct.append('@R15')
        asmInstruct.append('D=M')
        asmInstruct.append('@3')
        asmInstruct.append('D=D-A')
        asmInstruct.append('A=D')
        asmInstruct.append('D=M')
        asmInstruct.append('@ARG')
        asmInstruct.append('M=D')
        # restore LCL
        asmInstruct.append('@R15')
        asmInstruct.append('D=M')
        asmInstruct.append('@4')
        asmInstruct.append('D=D-A')
        asmInstruct.append('A=D')
        asmInstruct.append('D=M')
        asmInstruct.append('@LCL')
        asmInstruct.append('M=D')
        # goto return address
        asmInstruct.append('@R14')
        asmInstruct.append('A=M')
        asmInstruct.append('0;JMP')
    return asmInstruct


for path2File in files:
    retNum = 0
    file = open(path2File, 'r')
    main(file)
