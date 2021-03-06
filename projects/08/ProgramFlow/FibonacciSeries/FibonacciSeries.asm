//push argument 1
@ARG
D=M
@1
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//pop pointer 1           // that = argument[1]
@SP
AM=M-1
D=M
@THAT
M=D
//push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
//pop that 0              // first element in the series = 0
@THAT
D=M
@0
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
//pop that 1              // second element in the series = 1
@THAT
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
//push argument 0
@ARG
D=M
@0
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
//sub
@0
M=M-1
A=M
D=M
M=0
A=A-1
M=M-D
//pop argument 0          // num_of_elements -= 2 (first 2 elements are set)
@ARG
D=M
@0
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//label MAIN_LOOP_START
(MAIN_LOOP_START)
//push argument 0
@ARG
D=M
@0
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//if-goto COMPUTE_ELEMENT // if num_of_elements > 0, goto COMPUTE_ELEMENT
@SP
AM=M-1
D=M
@COMPUTE_ELEMENT
D;JNE
//goto END_PROGRAM        // otherwise, goto END_PROGRAM
@END_PROGRAM
0;JMP
//label COMPUTE_ELEMENT
(COMPUTE_ELEMENT)
//push that 0
@THAT
D=M
@0
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//push that 1
@THAT
D=M
@1
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
//pop that 2              // that[2] = that[0] + that[1]
@THAT
D=M
@2
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//push pointer 1
@THAT
D=M
@SP
M=M+1
A=M-1
M=D
//push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
//add
@0
A=M-1
D=M
M=0
A=A-1
M=D+M
@0
M=M-1
//pop pointer 1           // that += 1
@SP
AM=M-1
D=M
@THAT
M=D
//push argument 0
@ARG
D=M
@0
A=D+A
D=M
@SP
AM=M+1
A=A-1
M=D
//push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
//sub
@0
M=M-1
A=M
D=M
M=0
A=A-1
M=M-D
//pop argument 0          // num_of_elements--
@ARG
D=M
@0
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//goto MAIN_LOOP_START
@MAIN_LOOP_START
0;JMP
//label END_PROGRAM
(END_PROGRAM)
