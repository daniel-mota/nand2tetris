from posixpath import dirname
import sys, os, glob, re

class TableVariable():
    """
    handling table variables
    """
    def __init__(self, KindOf, TypeOf, IndexOf, Name):
        self.Name = Name
        self.kind_of = KindOf
        self.type_of = TypeOf
        self.index_of = IndexOf


class SymbolTable():
    """
    keeping track of variables thru symbol table
    """
    static_count = 0
    field_count = 0
    arg_count = 0
    var_count = 0
    local_count = 0
    def __init__(self, type):
        self.type = type
        self.table = []
    
    def define(self, KindOf, TypeOf, Name):
        index = 0
        if KindOf == 'static':
            index = self.static_count
            self.static_count += 1
        elif KindOf == 'this':
            index = self.field_count
            self.field_count += 1
        elif KindOf == 'argument':
            index = self.arg_count
            self.arg_count += 1
        elif KindOf == 'var':
            index = self.var_count
            self.var_count += 1
        elif KindOf == 'local':
            index = self.local_count
            self.local_count += 1
        var = TableVariable(KindOf, TypeOf, index, Name)
        self.table.append(var)
    

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

    
class VMWriter():
    """
    for interacting with output file
    """
    previous_output = ''
    previous_previous = ''
    def __init__(self, input_file):
        self.output_file = open(self._output_file_name(input_file), 'w')

    def _output_file_name(self, input_file):
        return input_file.split('.')[0] + '.vm'

    def previous(self):
        self.previous_previous = self.previous_output
    
    def write_push(self, seg, index):
        self.output_file.write('push ' + seg + " " + str(index) + '\n')
        self.previous()
        self.previous_output = 'push ' + seg + " " + str(index)
    
    def write_pop(self, seg, index):
        self.output_file.write('pop ' + seg + " " + str(index) + '\n')
        self.previous()
        self.previous_output = 'pop ' + seg + " " + str(index)
    
    def write_arithmetic(self, command):
        self.output_file.write(command + '\n')
        self.previous()
        self.previous_output = command
    
    def write_label(self, label):
        self.output_file.write('label ' + label + '\n')
        self.previous()
        self.previous_output = 'label ' + label

    def write_if(self, label):
        self.output_file.write('if-goto ' + label + '\n')
        self.previous()
        self.previous_output = 'if-goto ' + label

    def write_goto(self, label):
        self.output_file.write('goto ' + label + '\n')
        self.previous()
        self.previous_output = 'goto ' + label
    
    def write_call(self, name, nArgs):
        self.output_file.write('call ' + name + ' '+ str(nArgs) + '\n')
        self.previous()
        self.previous_output = 'call ' + name + ' '+ str(nArgs)
    
    def write_function(self, name, nArgs):
        self.output_file.write('function ' + name + ' '+ str(nArgs) + '\n')
        self.previous()
        self.previous_output = 'function ' + name + ' ' + str(nArgs)
    def write_return(self):
        self.output_file.write('return\n')
        self.previous()
        self.previous_output = 'return'
    
    def close_file(self):
        self.output_file.close()

class CompilationEngine():
    """
    for compiling and outputting to xml file
    """
    while_count = 0
    if_count = 0
    else_count = 0
    else_stack = []
    while_stack = []
    if_stack = []
    is_constructor = False
    is_method = 0
    is_void = True
    built_in_classes = ['Array', 'Keyboard', 'Math', 'Memory', 'Output', 'Screen', 'String', 'Sys']


    def __init__(self, input_file, jack_file):
        self.writer = CompilationWriter(input_file)
        self.vm_writer = VMWriter(input_file)
        self.tokenizer = self._init_tokenizer(jack_file)
        self.class_table = SymbolTable("class")
        self.subrou_table = SymbolTable("subroutine")
        self.var_type = ''
        self.var_kind = ''
        self.var_scope = 'class'
        self.var_class_type = ''
        self.nArgs = 0
    
    def _look_for_vars(self, var_name):
        match = [var for var in self.subrou_table.table if var.Name == var_name]
        if not match:
            match = [var for var in self.class_table.table if var.Name == var_name]
            if not match: 
                return (None, None)
        return (match[0].kind_of, match[0].index_of)

    def _is_class_var(self, var_name):
        match = [var for var in self.subrou_table.table if var.Name == var_name]
        if not match:
            match = [var for var in self.class_table.table if var.Name == var_name]
            if match: 
                return True
        return False
    
    def _type_var(self, var_name):
        match = [var for var in self.subrou_table.table if var.Name == var_name]
        if not match:
            match = [var for var in self.class_table.table if var.Name == var_name]
        return (match[0].type_of)
    
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
        self.var_kind = self.tokenizer.current_token.word
        # static / field
        self._write("keyword")
        self.tokenizer.advance_token()
        # type of var
        self.var_type = self.tokenizer.current_token.word
        self._write("keyword")
        self.tokenizer.advance_token()
        if self.var_kind == 'field':
            self.var_kind = 'this'
        # add var to class table
        self.class_table.define(self.var_kind, self.var_type, self.tokenizer.current_token.word)
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
            if self.var_scope == 'class':
                self.class_table.define(self.var_kind, self.var_type, self.tokenizer.current_token.word)
            else:
                self.subrou_table.define(self.var_kind, self.var_type, self.tokenizer.current_token.word)
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
        elif self.tokenizer.current_token.type == 'keyword' or self.tokenizer.current_token.word == 'Array':
            # set symbol type
            self.var_type = self.tokenizer.current_token.word
            self._write("keyword")
            self.tokenizer.advance_token()
            self._compile_paramlist()
        
        # if not, varname
        else:
            # define in symbol table
            self.subrou_table.define( 'argument',self.var_type, self.tokenizer.current_token.word)
            self._write("identifier")
            self.tokenizer.advance_token()
            self._compile_paramlist()


    def _compile_vardec(self):
        if self.tokenizer.current_token.word != 'var':
            return
        # symbol table local
        self.var_kind = 'local'
        self._write("keyword")
        self.tokenizer.advance_token()
        # set symbol table type
        self.var_type = self.tokenizer.current_token.word
        self._write(self.tokenizer.current_token.type)
        self.tokenizer.advance_token()
        # write local var to table
        self.subrou_table.define(self.var_kind, self.var_type, self.tokenizer.current_token.word)
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
        # look for variable in symbol table
        (var_kind, var_index) = self._look_for_vars(self.tokenizer.current_token.word)
        self.tokenizer.advance_token()
        is_array = False
        if self.tokenizer.current_token.word == '[':
            # write [
            self._write("symbol")
            self.tokenizer.advance_token()
            self._compile_expression()
            # write ]
            self._write("symbol")
            self.tokenizer.advance_token()
            self.vm_writer.write_push(var_kind, var_index)
            self.vm_writer.write_arithmetic('add')
            is_array = True
        # write =
        self._write("symbol")
        self.tokenizer.advance_token()
        self._compile_expression()
        if not is_array:
            # compile pop
            self.vm_writer.write_pop(var_kind, var_index)
        else:
            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        is_array = False
        # write ;
        self._write("symbol")
        self.tokenizer.advance_token()
    
    def _compile_else(self):
        # check if else
        if self.tokenizer.current_token.word != 'else':
            self.vm_writer.write_label("IFEND" + str(self.if_stack[-1]))
            self.if_stack.pop()
            return
        # check if condition valid
        self.else_stack.append(self.else_count)
        self.else_count += 1
        self.vm_writer.write_goto("ELSEEND" + str(self.else_stack[-1]))
        self.vm_writer.write_label("IFEND" + str(self.if_stack[-1]))
        self.if_stack.pop()
        self.vm_writer.write_label("ELSE" + str(self.else_stack[-1]))
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
        self.vm_writer.write_label("ELSEEND" + str(self.else_stack[-1]))
        self.else_stack.pop()


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
        # check if condition valid
        self.if_stack.append(self.if_count)
        self.if_count += 1
        self.vm_writer.write_if("IF" + str(self.if_stack[-1]))
        self.vm_writer.write_goto("IFEND" + str(self.if_stack[-1]))
        self.vm_writer.write_label("IF" + str(self.if_stack[-1]))
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
        self.while_stack.append(self.while_count)
        self.while_count += 1
        self.vm_writer.write_label("WHILESTART" + str(self.while_stack[-1]))
        # write (
        self._write("symbol")
        self.tokenizer.advance_token()
        self._compile_expression();
        # write )
        self._write("symbol")
        self.tokenizer.advance_token()
        # check if condition valid
        self.vm_writer.write_if("WHILE" + str(self.while_stack[-1]))
        self.vm_writer.write_goto("WHILEEND" + str(self.while_stack[-1]))
        # write {
        self._write("symbol")
        self.tokenizer.advance_token()
        self.vm_writer.write_label("WHILE" + str(self.while_stack[-1]))
        
        # compile statements
        self._compile_statements()
        
        # write }
        self._write("symbol")
        self.vm_writer.write_goto("WHILESTART" + str(self.while_stack[-1]))
        self.vm_writer.write_label("WHILEEND" + str(self.while_stack[-1]))
        self.while_stack.pop()
        self.tokenizer.advance_token()
    
    def _compile_subroutinecall(self):
        # write subroutine class name
        self._write("identifier")
        # subroutine class name
        class_name = self.tokenizer.current_token.word
        self.tokenizer.advance_token()
        if self.tokenizer.current_token.word == '(':
            # write (
            self._write("symbol")
            self.tokenizer.advance_token()
            self.vm_writer.write_push('pointer', 0)
            # compile expressionList
            self._compile_expressionList()
            self.vm_writer.write_call(self.var_class_type + '.' + class_name, str(self.nArgs + 1))
        else:
            if class_name not in self.built_in_classes:
                # check if class is really object
                (var_kind, var_index) = self._look_for_vars(class_name)
                if var_kind and var_index is not None:
                    self.vm_writer.write_push(var_kind, var_index)
                    class_name = self._type_var(class_name)
                    self.nArgs += 1
            # write .
            self._write("symbol")
            self.tokenizer.advance_token()
            # write subroutine name
            self._write("identifier")
            subru_name = self.tokenizer.current_token.word
            self.tokenizer.advance_token()
            # write (
            self._write("symbol")
            self.tokenizer.advance_token()
            # compile expressionList
            self._compile_expressionList()
            if self.vm_writer.previous_output.split()[0] == 'label':
                self.vm_writer.write_push('constant', 0)
            self.vm_writer.write_call(class_name + "." + subru_name, str(self.nArgs))
            self.nArgs = 0
        self.vm_writer.write_pop('temp', 0)
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
        # check if constructor
        if self.is_constructor:
            # self.vm_writer.write_push("pointer", 0)
            self.is_constructor = False
        # write ;
        if self.vm_writer.previous_output.split()[0] != 'push' and self.vm_writer.previous_output != 'add' and self.vm_writer.previous_output != 'call':
            self.vm_writer.write_push("constant", 0)
        self.vm_writer.write_return()
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
        # declare function after num of local vars
        self.vm_writer.write_function(self.var_class_type + "." + self.func_name, self.subrou_table.local_count)
        if self.is_method == 1:
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop('pointer', 0)
        self.is_method = 0
        if self.is_constructor:
                self.vm_writer.write_push('constant', self.class_table.field_count)
                self.vm_writer.write_call("Memory.alloc", 1)
                self.vm_writer.write_pop('pointer', 0)
        self._compile_statements()
        self._write("symbol")
        self.tokenizer.advance_token()

    def _compile_subroutinedec(self):
        # first keyword has to be constructor, function or method
        if self.tokenizer.current_token.word != 'constructor' and self.tokenizer.current_token.word != 'function' and self.tokenizer.current_token.word != 'method':
            return
        else:
            self.subrou_table = SymbolTable("subroutine")
            self.nArgs = 0
            if self.tokenizer.current_token.word == 'method':
                # if method, pass in self
                self.subrou_table.define( 'argument',self.var_class_type, 'this')
                self.is_method = 1
            if self.tokenizer.current_token.word == 'constructor':
                self.is_constructor = True
            
            # print const func or method
            self._write("keyword")
            self.tokenizer.advance_token()
            # void or type
            self._write(self.tokenizer.current_token.type)
            self.tokenizer.advance_token()
            # func name
            self.func_name = self.tokenizer.current_token.word
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
        if self.tokenizer.current_token.word != ')':
            # increase number of args in expression list
            self.nArgs += 1
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
        op_vm_translation = {
            "+": "add",
            "-":"sub",
            ">": "gt",
            "<":"lt",
            "&": "and",
            "=": "eq",
            "|": "or",
            "!": "not",
            "~": "neg",
        }
        # write term
        self._compile_termEXP()
        if self.tokenizer.current_token.word in ops:
            # write op then term
            self.writer.write("<symbol> " + op_translation[self.tokenizer.current_token.word] + ' </symbol>\n')
            op = self.tokenizer.current_token.word
            self.tokenizer.advance_token()
            self._compile_termEXP()
            # after terms, compile op
            if op is not "*" and op is not '/':
                self.vm_writer.write_arithmetic(op_vm_translation[op])
            elif op == '/':
                self.vm_writer.write_call('Math.divide', 2)
            else:
                self.vm_writer.write_call("Math.multiply", 2)
            


    def _compile_termEXP(self):
        valid_types = ['integerConstant', 'stringConstant', 'identifier']
        terminal_types = ['integerConstant', 'stringConstant']
        kwords = ['true', 'false', 'null', 'this']
        unary_ops = ['-', '~']
        unary_translations = {
            '~': "not",
            "-": "neg"
        }
        if self.tokenizer.current_token.type not in valid_types and self.tokenizer.current_token.word not in kwords and self.tokenizer.current_token.word != '(' and self.tokenizer.current_token.word not in unary_ops:
            return

        # check if string, int or keyword const
        if self.tokenizer.current_token.type in terminal_types or self.tokenizer.current_token.word in kwords:
            if self.tokenizer.current_token.word not in kwords:
                if self.tokenizer.current_token.type == 'stringConstant':
                    # make new string object
                    self.vm_writer.write_push('constant', len(self.tokenizer.current_token.word))
                    self.vm_writer.write_call('String.new', 1)
                    for letter in self.tokenizer.current_token.word:
                        # write every char of token
                        self.vm_writer.write_push('constant', ord(letter))
                        self.vm_writer.write_call('String.appendChar', 2)
                else:
                    self.vm_writer.write_push("constant", self.tokenizer.current_token.word)
            if self.tokenizer.current_token.word in kwords:
                if self.tokenizer.current_token.word == 'true':
                    self.vm_writer.write_push("constant" , 0)
                    self.vm_writer.write_arithmetic("not")
                elif self.tokenizer.current_token.word == 'false':
                    self.vm_writer.write_push('constant', 0)
                elif self.tokenizer.current_token.word == 'this':
                    self.vm_writer.write_push('pointer', 0)
                elif self.tokenizer.current_token.word == 'null':
                    self.vm_writer.write_push('pointer', 0)
            # write terminal term
            self._write(self.tokenizer.current_token.type)
            self.tokenizer.advance_token()
        
        # check if terminal varname
        elif self.tokenizer.current_token.type == 'identifier' and self.tokenizer.next_token.word != '[' and self.tokenizer.next_token.word != '.':
            # look for var in table
            (var_kind, var_index) = self._look_for_vars(self.tokenizer.current_token.word)
            self.vm_writer.write_push(var_kind, var_index)
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
            # look for variable in symbol table
            (var_kind, var_index) = self._look_for_vars(self.tokenizer.current_token.word)
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
            self.vm_writer.write_push(var_kind, var_index)
            self.vm_writer.write_arithmetic('add')
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('that', 0)
        elif self.tokenizer.current_token.word in unary_ops:
            # write unary op
            unary = self.tokenizer.current_token.word
            self._write("symbol")
            self.tokenizer.advance_token()
            self._compile_termEXP()
            self.vm_writer.write_arithmetic(unary_translations[unary])
        # if all else fails, must be subroutine call
        elif self.tokenizer.current_token.type == 'identifier' and (self.tokenizer.next_token.word == '(' or self.tokenizer.next_token.word == '.'):
            # look for variable in symbol table
            (var_kind, var_index) = self._look_for_vars(self.tokenizer.current_token.word)
            # write subroutine/class/var name
            self._write("identifier")
            subclass_name = self.tokenizer.current_token.word
            self.tokenizer.advance_token()
            if self.tokenizer.current_token.word == '(':
                # write (
                self._write("symbol")
                self.tokenizer.advance_token()
                self._compile_expressionList()
                # write )
                self._write("symbol")
                self.tokenizer.advance_token()
            else:
                # write .
                self._write("symbol")
                self.tokenizer.advance_token()
                # write subroutine name
                self._write("identifier")
                subrou_name = self.tokenizer.current_token.word
                # pass object to method
                if self.tokenizer.current_token.word != 'new' and subclass_name not in self.built_in_classes and var_kind:
                    if var_kind == 'this':
                        self.vm_writer.write_push(var_kind, var_index)    
                    else:
                        self.vm_writer.write_push('pointer', 0)
                if self._is_class_var(subclass_name):
                    subclass_name = self._type_var(subclass_name)
                    self.nArgs += 1
                self.tokenizer.advance_token()
                # write (
                self._write("symbol")
                self.tokenizer.advance_token()
                self._compile_expressionList()
                # write )
                self.vm_writer.write_call(subclass_name + "." + subrou_name, self.nArgs)
                self.nArgs = 0
                self._write("symbol")
                self.tokenizer.advance_token()
        
            
    def _compile_class(self):
        self.writer.write('<keyword> ')
        self.writer.write(self.tokenizer.current_token.word)
        self.writer.write('</keyword>\n')
        self.tokenizer.advance_token()
        # set class type variable
        self.var_class_type = self.tokenizer.current_token.word
        self._compile_term()
        self.writer.write('<symbol> ' + self.tokenizer.current_token.word + ' </symbol>\n')
        self.tokenizer.advance_token()
        self._compile_classvardec()
        self.var_scope = 'subroutine'
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