// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

    // jump to skip comparisons
    @8
    0;JMP

(END_EQ)
    @0
    A=M
    M=-1
    @R15
    A=M
    0;JMP

    @23
    D=A
    @R15
    M=D
    @0
    M=M-1
    M=M-1
    A=M
    D=M
    M=0
    A=A+1
    D=D-M
    M=0
    
    @END_EQ
    D;JEQ
    @SP
    M=M+1
