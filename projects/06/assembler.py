import sys, os

pwd = os.path.dirname(__file__)
path = os.path.join(pwd, sys.argv[1]);
path2Write = path[:len(path) - 4] + '.hack'

file = open(path, 'r');
hack = open(path2Write, 'w');

predef_symbols = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24576,
}

n = 0;
for line in file:
    if line[0] =='\r' or line[0] == '/':
        continue

    elif line[0] == '(':
        predef_symbols[line[1:len(line)-3]] = n
    else:
        n += 1
file.seek(0)

c_bits_comp = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110001",
    "-M": "1110001",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101",
}

c_bits_dest = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

c_bits_jump = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

n = 16;
def parser(line):
    # find where line ends (either comment or enter)
    if line.find("/") == -1:
        index = line.find('\r')
        # start and end of commands
    else:
        index = line.find('/')

    # a encoder
    if line[0] == '@':
        commands = line[1:index]
        commands = commands.strip();
        return a_encoder(commands);

    # c encoder    
    else:
        commands = line[0:index];

        # parse dest
        if line.find("=") == -1:
            # no dest
            equals = 0
            compI = -1
        else:
            equals = line.find("=")
            compI = 0
        
        # parse jump
        if line.find(';') == -1:
            # no jump
            semi = len(commands);
        else:
            semi = line.find(';');
        
        dest = commands[0:equals];
        dest = dest.rstrip()
        comp = commands[equals+compI+1:semi];
        comp = comp.rstrip();
        jump = commands[semi+1:];
        jump = jump.rstrip();
        return c_encoder(dest, comp, jump)

def a_encoder(instruct):
    global n
    if instruct.isdigit():
        instruct = int(instruct)
    else:
        # check for symbol
        if predef_symbols.get(instruct) is None:
            predef_symbols[instruct] = n
            instruct = n
            n += 1
        else:
            instruct = predef_symbols[instruct]
    encoded = '0'
    max_binary = 16384;
    
    while(max_binary > 0 and instruct >= 0):
        if max_binary <= instruct:
            encoded += '1'
            instruct -= max_binary
            max_binary /= 2
        else:
            encoded += '0'
            max_binary /= 2
    return encoded

def c_encoder(dest, comp, jump):
    encoded = '111'
    encoded += c_bits_comp[comp];
    encoded += c_bits_dest[dest];
    encoded += c_bits_jump[jump];
    return encoded;

for line in file:
    # check for whitespace
    a = line[0]
    if line[0] == '\r' or line[0] == '/' or line[0] == '(':
        continue

    # remove left whitespace
    line = line.lstrip()
    

    hack.write(parser(line) + '\n');
hack.close();

