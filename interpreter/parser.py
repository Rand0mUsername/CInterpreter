""" SCI - Simple C Interpreter """

###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################
from .lexer import *
from .tree import *
from .utils import *


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self, expected=None, obtained=None):
        if not expected and not obtained:
            raise Exception('Invalid syntax')
        else:
            raise Exception('Expected token <{}> but found <{}> at line {}.'.format(
                expected, obtained, self.lexer.line
            ))

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(token_type, self.current_token.type)

    def program(self):
        """
        program         : declarations
        """
        root = Program(self.declarations())
        return root

    def declarations(self):

        declarations = []

        while self.current_token.type == TYPE:
            if self.is_function_declaration():
                declarations.append(self.function_declaration())
            else:
                declarations.extend(self.var_declaration_list())
                self.eat(SEMICOLON)
        return declarations

    def function_declaration(self):
        """
        function_declaration  : type_spec ID LPAREN parameters RPAREN block
        """
        type_node = self.type_spec()
        func_name = self.current_token.value
        self.eat(ID)
        self.eat(LPAREN)
        params = self.parameters()
        self.eat(RPAREN)
        return FunctionDecl(
            type_node=type_node,
            func_name=func_name,
            params=params,
            block_node=self.block()
        )

    def var_declaration_list(self):
        """
        var_declarations  : type_spec var (ASSIGN expr)? (COMMA var (ASSIGN expr)?)* SEMICOLON
        """
        declarations = []

        type_node = self.type_spec()
        var_node = self.variable()

        declarations.extend(self.var_initialization(type_node, var_node))

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_node = self.variable()
            declarations.extend(self.var_initialization(type_node, var_node))

        return declarations

    def var_initialization(self, type_node, var_node):
        declarations = list()

        declarations.append(VarDecl(
            type_node=type_node,
            var_node=var_node
        ))

        if self.current_token.type == ASSIGN:
            token = self.current_token
            self.eat(ASSIGN)
            declarations.append(Assign(
                left=var_node,
                op=token,
                right=self.expr()
            ))
        return declarations

    def parameters(self):
        """
        parameters      : empty
                        | param
                        | param COMMA parameters

        param           : type_spec variable
        """

        if self.current_token.type == RPAREN:
            return []

        nodes = [Param(self.type_spec(), self.variable())]
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            nodes.append(Param(self.type_spec(), self.variable()))
        return nodes

    def is_function_declaration(self):
        """Look ahead to check declaration type"""
        pos, curr_char, token = (
            self.lexer.pos,
            self.lexer.current_char,
            self.current_token
        )   # save current state

        self.eat(TYPE)
        self.eat(ID)
        result = self.current_token.type == LPAREN

        self.lexer.pos, self.lexer.current_char, self.current_token = (
            pos,
            curr_char,
            token
        )   # restore state

        return result

    def block(self):
        """block : LBRACKET statement_list RBRACKET"""
        self.eat(LBRACKET)
        node = Block(self.statement_list())
        self.eat(RBRACKET)
        return node

    def statement_list(self):
        """
        statement_list : statement
                       | statement SEMI statement_list
        """
        node = self.statement()

        results = node

        while self.current_token.type == SEMICOLON:
            self.eat(SEMICOLON)
            results.extend(self.statement())

        return results

    @multi
    def statement(self):
        """
        statement : compound_statement
                  | assignment_statement
                  | empty
        """
        if self.current_token.type == ID:
            node = self.assignment_statement()
        elif self.current_token.type == TYPE:
            node = self.var_declaration_list()
        elif self.current_token.type == IF:
            node = self.if_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        node = Assign(left, token, self.expr())
        return node

    def if_statement(self):
        self.eat(IF)
        self.eat(LPAREN)
        cond_node = self.expr()
        self.eat(RPAREN)
        if_block = self.block()
        else_block = self.empty()
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            else_block = self.block()
        return IfStmt(
            condition=cond_node,
            if_block=if_block,
            else_block=else_block
        )

    def type_spec(self):
        """type_spec : TYPE
        """
        token = self.current_token
        self.eat(TYPE)
        node = Type(token)
        return node

    def variable(self):
        """
        variable : ID
        """
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def expr(self):
        """
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | INT_NUMBER
                  | LPAREN expr RPAREN
                  | variable
        """
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INT_NUMBER:
            self.eat(INT_NUMBER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def parse(self):

        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node