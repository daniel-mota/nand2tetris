//push constant 111
@111
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 333
@333
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 888
@888
D=A
@SP
A=M
M=D
@SP
M=M+1
//pop static 8
@StaticTest.0
D=M
@8
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//pop static 3
@StaticTest.0
D=M
@3
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//pop static 1
@StaticTest.0
D=M
@1
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//push static 3
@StaticTest.0
D=M
@3
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//push static 1
@StaticTest.0
D=M
@1
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//sub
@0
M=M-1
A=M
D=M
M=0
A=A-1
M=M-D
//push static 8
@StaticTest.0
D=M
@8
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//add
@0
A=M-1
D=M
M=0
A=A-1
M=D+M
@0
M=M-1