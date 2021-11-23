// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
@SCREEN
D=A
@i
M=D-1


(CHECK)
    @24576
    D=M
    @BLACKEN
    D;JGT
    @WHITEN
    0;JMP

(BLACKEN)
    @24576
    D=A
    @i
    D=D-M
    @CHECK
    D;JEQ

    @i
    D=M
    A=D
    M=-1
    @i
    M=M+1
    @CHECK
    0;JMP

(WHITEN)
    @SCREEN
    D=A-1
    @i
    D=D-M
    @CHECK
    D;JEQ

    @i
    D=M
    A=D
    M=0
    @i
    M=M-1
    @CHECK
    0;JMP


