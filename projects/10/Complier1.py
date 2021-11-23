from posixpath import dirname
import sys, os, glob, re

class CompilationWriter():
    """
    for interacting with output file
    """
    def __init__(self, input_file):
        self.output_file = open(self._output_file_name(input_file), 'w')

    def _output_file_name(self, input_file):
        return input_file.split('.')[0] + '.xml'
    
    def write(self, text):
        self.output_file.write(text)
    
    def close_file(self):
        self.output_file.close()

class CompilationEngine():
    """
    for compiling and outputting to xml file
    """

    def __init__(self, input_file, jack_file):
        self.writer = CompilationWriter(input_file)
        self.tokenizer = self._init_tokenizer(jack_file)
    
    def _init_tokenizer(self, jack_file):
        tokenizer = JackTokenizer(jack_file)
        tokenizer._tokenize_file()
        return tokenizer

    def _compile_file(self):
        self.writer.write('<tokens>\n')
        self.compile_next()
        self.writer.write('</tokens>')
        self.writer.close_file()

    
    def _compile_term(self):
        self.writer.write('<identifier> ')
        self.writer.write(self.tokenizer.current_token.word)
        self.writer.write(' </identifier>\n')
        self.tokenizer.advance_token()

    def _compile_classvardec(self):
        if self.tokenizer.current_token.word != 'static' and self.tokenizer.current_token.word != 'field':
            return
        # static / field
        self._write("keyword")
        self.tokenizer.advance_token()
        # type of var
        self._write("keyword")
        self.tokenizer.advance_token()
        self._compile_term()
        self._additional_vars()
        self.writer.write('<symbol> ' + self.tokenizer.current_token.word + ' </symbol>\n')
        self.tokenizer.advance_token()
        # check if multiple var decs
        if self.tokenizer.current_token.word == 'static' or self.tokenizer.current_token.word == 'field':
            self._compile_classvardec()
    
    def _write(self, type):
        self.writer.write("<" + type + "> " + self.tokenizer.current_token.word +  " </" + type + ">\n")

    
    def _additional_vars(self):
        if self.tokenizer.current_token.word == ';':
            return
        elif self.tokenizer.current_token.word == ',':
            self._write("symbol")
            self.tokenizer.advance_token()
            self._additional_vars()
        else:
            # var name
            self._write("identifier");
            self.tokenizer.advance_token()
            self._additional_vars()

    def _compile_paramlist(self):
        if self.tokenizer.current_token.word == ')':
            return

        # check if comma
        if self.tokenizer.current_token.word == ',':
            self._write("symbol")
            self.tokenizer.advance_token()
            self._compile_paramlist()
        
        # check if keyword
        elif self.tokenizer.current_token.type == 'keyword':
            self._write("keyword")
            self.tokenizer.advance_token()
            self._compile_paramlist()
        
        # if not, varname
        else:
            self._write("identifier")
            self.tokenizer.advance_token()
            self._compile_paramlist()


    def _compile_vardec(self):
        if self.tokenizer.current_token.word != 'var':
            return
        self._write("keyword")
        self.tokenizer.advance_token()
        self._write(self.tokenizer.current_token.type)
        self.tokenizer.advance_token()
        self._write("identifier")
        self.tokenizer.advance_token()
        self._additional_vars()
        self._write("symbol")
        self.tokenizer.advance_token()
        self._compile_vardec()



    def _compile_let(self):
        # write let
        self._write("keyword")
        self.tokenizer.advance_token()
        # write varname
        self._write("identifier")
        self.tokenizer.advance_token()
        if self.tokenizer.current_token.word == '[':
            # write [
            self._write("symbol")
            self.tokenizer.advance_token()
            self._compile_expression()
            # write ]
            self._write("symbol")
            self.tokenizer.advance_token()
        # write =
        self._write("symbol")
        self.tokenizer.advance_token()
        self._compile_expression()
        # write ;
        self._write("symbol")
        self.tokenizer.advance_token()
    
    
    def _compile_else(self):
        # check if else
        if self.tokenizer.current_token.word != 'else':
            return
        # write else
        self._write("keyword")
        self.tokenizer.advance_token()
        # write {
        self._write("symbol")
        self.tokenizer.advance_token()
        # compile statements
        self._compile_statements()
        # write }
        self._write("symbol")
        self.tokenizer.advance_token()

    def _compile_if(self):
        # write if
        self._write("keyword")
        self.tokenizer.advance_token()
        # write (
        self._write("symbol")
        self.tokenizer.advance_token()
        self._compile_expression()
        # write )
        self._write("symbol")
        self.tokenizer.advance_token()
        
        # write {
        self._write("symbol")
        self.tokenizer.advance_token()
        
        # compile statements
        self._compile_statements()
        
        # write }
        self._write("symbol")
        self.tokenizer.advance_token()

        # check if else
        self._compile_else()
    
    
    def _compile_while(self):
        # write while
        self._write("keyword")
        self.tokenizer.advance_token()
        # write (
        self._write("symbol")
        self.tokenizer.advance_token()
        self._compile_expression();
        # write )
        self._write("symbol")
        self.tokenizer.advance_token()
        
        # write {
        self._write("symbol")
        self.tokenizer.advance_token()
        
        # compile statements
        self._compile_statements()
        
        # write }
        self._write("symbol")
        self.tokenizer.advance_token()
    
    def _compile_subroutinecall(self):
        # write subroutine name
        self._write("identifier")
        self.tokenizer.advance_token()
        if self.tokenizer.current_token.word == '(':
            # write (
            self._write("symbol")
            self.tokenizer.advance_token()
            # compile expressionList
            self._compile_expressionList()
        else:
            # write .
            self._write("symbol")
            self.tokenizer.advance_token()
            # write subroutine name
            self._write("identifier")
            self.tokenizer.advance_token()
            # write (
            self._write("symbol")
            self.tokenizer.advance_token()
            # compile expressionList
            self._compile_expressionList()
        # write )
        self._write("symbol")
        self.tokenizer.advance_token()

    def _compile_do(self):
        # write do
        self._write("keyword")
        self.tokenizer.advance_token()

        # compile statements
        self._compile_subroutinecall()
        
        # write ;
        self._write("symbol")
        self.tokenizer.advance_token()
    
    
    def _compile_return(self):
        # write return
        self._write("keyword")
        self.tokenizer.advance_token()
        if self.tokenizer.current_token.word != ";":
            # write term
            self._compile_expression()
        # write ;
        self._write("symbol")
        self.tokenizer.advance_token()

    def _compile_statements(self):
        kwords = ['let', 'do', 'if', 'while', 'return']
        if self.tokenizer.current_token.word not in kwords:
            return
        if self.tokenizer.current_token.word == 'let':
            self._compile_let()
        if self.tokenizer.current_token.word == 'do':
            self._compile_do()
        if self.tokenizer.current_token.word == 'if':
            self._compile_if()
        if self.tokenizer.current_token.word == 'while':
            self._compile_while()
        if self.tokenizer.current_token.word == 'return':
            self._compile_return()
        self._compile_statements()
        

    def _compile_subroutinebody(self):
        self._write("symbol")
        self.tokenizer.advance_token()
        self._compile_vardec()
        self._compile_statements()
        self._write("symbol")
        self.tokenizer.advance_token()

    def _compile_subroutinedec(self):
        # first keyword has to be constructor, function or method
        if self.tokenizer.current_token.word != 'constructor' and self.tokenizer.current_token.word != 'function' and self.tokenizer.current_token.word != 'method':
            return
        else:
            # print const func or method
            self._write("keyword")
            self.tokenizer.advance_token()
            # void or type
            self._write(self.tokenizer.current_token.type)
            self.tokenizer.advance_token()
            # func name
            self._write("identifier")
            self.tokenizer.advance_token()
            # parameter list
            # print first paren
            self._write("symbol")
            self.tokenizer.advance_token();
            self._compile_paramlist()
            self._write("symbol")
            self.tokenizer.advance_token()
            self._compile_subroutinebody();
            self._compile_subroutinedec()

    def _compile_expressionList(self):
        self._compile_expression()
        if self.tokenizer.current_token.word == ',':
            # write ,
            self._write("symbol")
            self.tokenizer.advance_token()
            # write expression
            self._compile_expressionList()

    def _compile_expression(self):
        ops = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        op_translation = {
            "+":"+",
            "-":"-",
            "*":"*",
            "|":"|",
            "<":"&lt;",
            ">":"&gt;",
            "=":"=",
            "&":"&amp;",
            "/":"/"
        }
        # write term
        self._compile_termEXP()
        if self.tokenizer.current_token.word in ops:
            # write op then term
            self.writer.write("<symbol> " + op_translation[self.tokenizer.current_token.word] + ' </symbol>\n')
            self.tokenizer.advance_token()
            self._compile_termEXP()

        

    

    def _compile_termEXP(self):
        valid_types = ['integerConstant', 'stringConstant', 'identifier']
        terminal_types = ['integerConstant', 'stringConstant']
        kwords = ['true', 'false', 'null', 'this']
        unary_ops = ['-', '~']
        if self.tokenizer.current_token.type not in valid_types and self.tokenizer.current_token.word not in kwords and self.tokenizer.current_token.word != '(' and self.tokenizer.current_token.word not in unary_ops:
            return

        # check if string, int or keyword const
        if self.tokenizer.current_token.type in terminal_types or self.tokenizer.current_token.word in kwords:
            # write terminal term
            self._write(self.tokenizer.current_token.type)
            self.tokenizer.advance_token()
        
        # check if terminal varname
        elif self.tokenizer.current_token.type == 'identifier' and self.tokenizer.next_token.word != '[' and self.tokenizer.next_token.word != '.':
            # write terminal varname
            self._write(self.tokenizer.current_token.type)
            self.tokenizer.advance_token()
        
        # check if paren
        elif self.tokenizer.current_token.word == '(':
            # write (
            self._write("symbol")
            self.tokenizer.advance_token()
            # write expression
            self._compile_expression()
            # write )
            self._write("symbol")
            self.tokenizer.advance_token()
        # check if array
        elif self.tokenizer.next_token.word == '[':
            # write varname
            self._write("identifier")
            self.tokenizer.advance_token()
            # write [
            self._write("symbol")
            self.tokenizer.advance_token()
            # write expression
            self._compile_expression()
            # write ]
            self._write("symbol")
            self.tokenizer.advance_token()
        elif self.tokenizer.current_token.word in unary_ops:
            # write unary op
            self._write("symbol")
            self.tokenizer.advance_token()
            self._compile_termEXP()
        # if all else fails, must be subroutine call
        elif self.tokenizer.current_token.type == 'identifier' and (self.tokenizer.next_token.word == '(' or self.tokenizer.next_token.word == '.'):
            # write subroutine/class/var name
            self._write("identifier")
            self.tokenizer.advance_token()
            if self.tokenizer.current_token.word == '(':
                # write (
                self._write("symbol")
                self.tokenizer.advance_token()
                self._compile_expressionlist()
                # write )
                self._write("symbol")
                self.tokenizer.advance_token()
            else:
                # write .
                self._write("symbol")
                self.tokenizer.advance_token()
                # write subroutine name
                self._write("identifier")
                self.tokenizer.advance_token()
                # write (
                self._write("symbol")
                self.tokenizer.advance_token()
                self._compile_expressionList()
                # write )
                self._write("symbol")
                self.tokenizer.advance_token()
        
            
    def _compile_class(self):
        self.writer.write('<keyword> ')
        self.writer.write(self.tokenizer.current_token.word)
        self.writer.write('</keyword>\n')
        self.tokenizer.advance_token()
        self._compile_term()
        self.writer.write('<symbol> ' + self.tokenizer.current_token.word + ' </symbol>\n')
        self.tokenizer.advance_token()
        self._compile_classvardec()
        self._compile_subroutinedec()
        # write }
        self.writer.write('<symbol> ' + self.tokenizer.current_token.word + ' </symbol>\n')
        self.tokenizer.advance_token()
        

    
    def compile_next(self):
        self.tokenizer.advance_token()
        if self.tokenizer.current_token.word == "class":
            self._compile_class()

class JackToken():
    """
    for interacting with words and returning sole tokens
    """
    keywords = ['class', 'constructor','function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

    symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

    keywordConstants = ['true', 'false', 'null', 'this']

    def __init__(self, word):
        self.word = word
        self.type = self._define_type()
    
    def is_empty(self):
        return self.word == ''

    def _define_type(self):
        if self.word in self.keywords:
            return 'keyword'
        elif self.word in self.symbols:
            return 'symbol'
        elif self.word in self.keywordConstants:
            return 'keywordConstant'
        elif self.word.isdigit():
            return 'integerConstant'
        else:
            return 'identifier'
    

class JackLine():
    """
    for interacting with lines and returning them as tokens
    """
    COMMENT_SYMBOL = '//'
    API_COMMENT_SYMBOL = '/*'
    API_COMMENT2_SYMBOL = '*'
    NEWLINE_SYMBOL = '\n'
    EMPTY_SYMBOL = ''

    def __init__(self, line):
        self.raw_line = line
        self.line = self._sanitized_line()
        self.parts = self.line.split(' ')
        self.tokens = []
    
    def _sanitized_line(self):
        line = self.raw_line.strip()
        if self.COMMENT_SYMBOL in line and not self.is_comment():
            line = line[0:line.index('//')]
            line = line.strip()
        return line
    
    def _split_string(self):
        self.parts = re.split('(")', self.line)
        ind = self.parts.index('"') + 1
        str = self.parts[ind]
        self.parts = re.split('(\W)', self.line)
        self.parts = list(filter((" ").__ne__, self.parts))
        self.parts = list(filter(("").__ne__, self.parts))
        start = self.parts.index('"')
        end = self.parts.index('"', start + 1)
        del self.parts[start+1:end]
        self.parts.insert(start+1, str)


    def is_comment(self):
        if len(self.raw_line.strip()) > 2:
            return self.raw_line[0:2] == self.COMMENT_SYMBOL or self.raw_line.strip()[0:2] == self.API_COMMENT_SYMBOL or self.raw_line.strip()[0] == self.API_COMMENT2_SYMBOL
        else:
            if self.raw_line.strip():
                return self.raw_line.strip()[0] == self.API_COMMENT2_SYMBOL
            else:
                return False
                
    
    def is_whitespace(self):
        return self.raw_line == self.NEWLINE_SYMBOL
    
    def is_empty(self):
        return self.raw_line == self.EMPTY_SYMBOL
    
    # tokenize parts
    def _tokenize_parts(self):
        if '"' in self.line and not self.is_comment():
            self._split_string()
        first_quote = False
        string = False
        for part in self.parts:
            if first_quote and string and part == '"':
                # for second quote
                first_quote = False
                string = False

            elif part == '"':
                # first double quotes come thru
                first_quote = True
                string = True
                parts = part
            
            if not first_quote and not string:
                # always will pass except when string
                parts = re.split('(\W)', part)
            
            else: 
                # for when string comes thru
                parts = [part]


            for anotherPart in parts:
                if not anotherPart:
                    continue
                if anotherPart != '"':
                    token = JackToken(anotherPart)
                if first_quote and string and anotherPart != '"':
                    token.type = "stringConstant"
                if anotherPart != '"':
                    self.tokens.append(token)


class JackTokenizer():
    """
    Removes all comments and white space from the input stream
    and breaks it inot Jack-language tokens,as specified by the 
    Jack grammar
    """
    def __init__(self, input_file):
        self.input_file = open(input_file, 'r')
        self.has_more_lines = True
        self.has_more_tokens = True
        self.current_line = None
        self.current_token = None
        self.next_line = None
        self.next_token = None
        self.tokens = []
        self.token_index = 0

    def has_valid_current_line(self):
        return not self.current_line.is_whitespace() and not self.current_line.is_comment()
    
    def _update_has_more_lines(self):
        if self.next_line.is_empty():
            self.has_more_lines = False
    
    def _update_has_more_tokens(self):
        if self.next_token.is_empty():
            self.has_more_tokens = False
    
    def _update_next_line(self):
        line = self.input_file.readline()
        self.next_line = JackLine(line)
    
    def _update_next_token(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.next_token = self.tokens[self.token_index]
        
    def _update_current_line(self):
        # initialization
        if self.current_line == None:
            line = self.input_file.readline()
            self.current_line = JackLine(line)
        else:
            self.current_line = self.next_line
    
    def _update_current_token(self):
        # initialization
        if self.current_token == None:
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = self.next_token

    def advance_line(self):
        self._update_current_line()
        self._update_next_line()
        self._update_has_more_lines()
    
    def advance_token(self):
        self._update_current_token()
        self._update_next_token()
        self._update_has_more_tokens()

    def _tokenize_file(self):
        while self.has_more_lines:
            # initialize
            self.advance_line()

            if self.has_valid_current_line():
                self.current_line._tokenize_parts()
                for token in self.current_line.tokens:
                    self.tokens.append(token)

class JackAnalyzer():
    """
        Main driver of the show
    """

    def __init__(self, input):
        # declare input directory/file
        self.input = input
        self.current_file = None
        # ! DECLARE MODULES AND CLASSES
        # tokenizer
    
    def run_compiler(self):
        if os.path.isfile(self.input):
            # if only one file, input will be file array
            jack_files = [self.input]

            ouput_file_name = input.split('.')[0] + '.vm'
        
        elif os.path.isdir(self.input):
            # get all jack files
            jack_path = os.path.join(self.input, '*.jack')
            jack_files = glob.glob(jack_path)

        
        for jack_file in jack_files:
            self.current_file = jack_file
            # store file tokens in self.tokens
            compilEngine = CompilationEngine(self.current_file, jack_file)
            compilEngine._compile_file()
            


            

if __name__ == "__main__" and len(sys.argv) == 2:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), sys.argv[1]))
    JackAnalyzer(path).run_compiler()