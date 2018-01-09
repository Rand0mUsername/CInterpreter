from .memory import *
from .number import Number
from ..lexical_analysis.token_type import NUM_TYPE_TOKENS
from ..lexical_analysis.lexer import Lexer
from ..lexical_analysis.token_type import *
from ..syntax_analysis.parser import Parser
from ..syntax_analysis.tree import *
from ..semantic_analysis.analyzer import SemanticAnalyzer
from ..common.utils import get_functions, MessageColor
from ..common.visitor import Visitor

class Interpreter(Visitor):

    def __init__(self):
        """ Initializes the memory for this run """
        # we can use memory[], new/del_scope, new/del_frame
        # the Memory class takes care of the underlying logic
        self.memory = Memory()

    # Program and its children - interpreted before _init
    # these visits don't return anything

    def visit_Program(self, node):
        """
        Visits the AST root: forwards the call to children
        (IncludeLibrary, FunctionDecl, VarDecl+Assignment)
        """
        for child in node.children:
            assert(isinstance(child, (FunctionDecl, IncludeLibrary, VarDecl)))
            self.visit(child)

    def visit_IncludeLibrary(self, node):
        """ Maps function name to the actual python function """
        functions = get_functions('interpreter.__builtins__.{}'.format(
            node.library_name
        ))
        for func in functions:
            self.memory[func.__name__] = func

    def visit_FunctionDecl(self, node):
        """ Maps function name to FunctionDecl node """
        self.memory[node.func_name] = node

    def visit_VarDecl(self, node):
        """ Declares a new variable """
        self.memory.declare(node.type_node.value, node.var_node.value)

    # functions
    # these visits return function return value (as a Number)

    def visit_FunctionCall(self, node):
        # Evaluate argument expressions
        args = [self.visit(arg) for arg in node.args]
        # Additional fix argument until memory is properly implemented
        if node.name == 'scanf':
            args.append(self.memory)

        """
        Since our library functions are just pure python functions we have
        to treat them as black boxes - they are never parsed so we can't 
        simulate their behaviour, in this case we just return the value
        """
        func = self.memory[node.name]
        if callable(func):
            return Number(func.return_type, func(*args))

        # Otherwise, func is a FunctionDecl AstNode, we can properly simulate

        # Create a new frame
        self.memory.new_frame(func.func_name)

        """
            Declare params in the new frame
             
            Note: In reality param values just get pushed on the stack and the new frame
            works with them using an offset from the frame start. Since we just simulate 
            frames and there is no notion of memory addresses it is acceptable to just declare
            param variables in the new frame. Doing parameter passing on a lower level than the
            whole memory is not very useful and it would also break some design decisions.
        """
        for idx, arg in enumerate(args):
            param = func.params[idx]
            self.memory.declare(param.type_node.value, param.var_node.value)
            self.memory[param.var_node.value] = arg

        # Visit the function body and cast the return value to the appropriate type
        raw_ret_val = self.visit(func.body)
        ret_val = Number(func.type_node.value, raw_ret_val.value)
        # Delete the frame and return
        self.memory.del_frame()
        return ret_val

    def visit_FunctionBody(self, node):
        for child in node.children:
            if isinstance(child, ReturnStmt):
                return self.visit(child)
            self.visit(child)

    # statements
    # these visits don't return anything

    def visit_CompoundStmt(self, node):
        self.memory.new_scope()
        for child in node.children:
            self.visit(child)
        self.memory.del_scope()

    def visit_ReturnStmt(self, node):
        return self.visit(node.expression)

    def visit_IfStmt(self, node):
        if self.visit(node.condition):
            self.visit(node.true_body)
        else:
            self.visit(node.false_body)

    def visit_WhileStmt(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_ForStmt(self, node):
        self.visit(node.setup)
        while self.visit(node.condition):
            self.visit(node.body)
            self.visit(node.increment)

    # expressions
    # these visits return expression value

    def visit_Expression(self, node):
        expr = None
        for child in node.children:
            expr = self.visit(child)
        # return the last comma-delimited child
        return expr

    def visit_Assignment(self, node):
        var_name = node.left.value
        if node.token.type == ADD_ASSIGN:
            self.memory[var_name] += self.visit(node.right)
        elif node.token.type == SUB_ASSIGN:
            self.memory[var_name] -= self.visit(node.right)
        elif node.token.type == MUL_ASSIGN:
            self.memory[var_name] *= self.visit(node.right)
        elif node.token.type == DIV_ASSIGN:
            self.memory[var_name] /= self.visit(node.right)
        else:
            self.memory[var_name] = self.visit(node.right)
        return self.memory[var_name]

    def visit_UnOp(self, node):
        if node.prefix:
            if node.token.type == AMPERSAND:
                return node.expr.value  # address = variable name
            elif node.token.type == INC_OP:
                self.memory[node.expr.value] += Number('int', 1)
                return self.memory[node.expr.value]
            elif node.token.type == DEC_OP:
                self.memory[node.expr.value] -= Number('int', 1)
                return self.memory[node.expr.value]
            elif node.token.type == MINUS:
                return Number('int', -1) * self.visit(node.expr)
            elif node.token.type == PLUS:
                return self.visit(node.expr)
            elif node.token.type == LOG_NEG:
                res = self.visit(node.expr)
                return res.log_neg()
            elif node.token.type in NUM_TYPE_TOKENS:
                # cast
                res = self.visit(node.expr)
                return Number(node.token.value, res.value)
            else:
                print(node.token, NUM_TYPE_TOKENS)
                raise RuntimeError("Unknown prefix operator, earlier stages should catch this")
        else:
            if node.token.type == INC_OP:
                var = self.memory[node.expr.value]
                self.memory[node.expr.value] += Number('int', 1)
                return var
            elif node.token.type == DEC_OP:
                var = self.memory[node.expr.value]
                self.memory[node.expr.value] -= Number('int', 1)
                return var
            else:
                raise RuntimeError("Unknown postfix operator, earlier stages should catch this")

    def visit_BinOp(self, node):
        if node.token.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.token.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.token.type == MUL_OP:
            return self.visit(node.left) * self.visit(node.right)
        elif node.token.type == DIV_OP:
            return self.visit(node.left) / self.visit(node.right)
        elif node.token.type == MOD_OP:
            return self.visit(node.left) % self.visit(node.right)
        elif node.token.type == LT_OP:
            return self.visit(node.left) < self.visit(node.right)
        elif node.token.type == GT_OP:
            return self.visit(node.left) > self.visit(node.right)
        elif node.token.type == LE_OP:
            return self.visit(node.left) <= self.visit(node.right)
        elif node.token.type == GE_OP:
            return self.visit(node.left) >= self.visit(node.right)
        elif node.token.type == EQ_OP:
            return self.visit(node.left) == self.visit(node.right)
        elif node.token.type == NE_OP:
            return self.visit(node.left) != self.visit(node.right)
        elif node.token.type == LOG_AND_OP:
            return self.visit(node.left) and self.visit(node.right)
        elif node.token.type == LOG_OR_OP:
            return self.visit(node.left) or self.visit(node.right)
        elif node.token.type == AMPERSAND:
            return self.visit(node.left) & self.visit(node.right)
        elif node.token.type == OR_OP:
            return self.visit(node.left) | self.visit(node.right)
        elif node.token.type == XOR_OP:
            return self.visit(node.left) ^ self.visit(node.right)

    def visit_Num(self, node):
        if node.token.type == INTEGER_CONST:
            return Number(type_name='int', value=node.value)
        elif node.token.type == CHAR_CONST:
            return Number(type_name='char', value=node.value)
        elif node.token.type == REAL_CONST:
            return Number(type_name='float', value=node.value)
        else:
            raise RuntimeError("Unknown num const, earlier stages should catch this")

    def visit_Var(self, node):
        return self.memory[node.value]

    def visit_String(self, node):
        return node.value

    def visit_NoOp(self, node):
        pass

    def interpret(self, tree):
        """ Interprets a C program from its AST """
        # Visit the AST root (Program) - this will prepare the memory by:
        # loading functions from included libraries, loading local functions and loading global variables
        self.visit(tree)

        # Create a new stack frame and trigger _init that calls main
        self.memory.new_frame('main')
        _init = FunctionCall(
            name='main',
            args=[],
            line=0
        )
        ret_val = self.visit(_init)
        self.memory.del_frame()
        return ret_val.value

    @staticmethod
    def run(program):
        try:
            lexer = Lexer(program)
            parser = Parser(lexer)
            tree = parser.parse()
            SemanticAnalyzer.analyze(tree)
            status = Interpreter().interpret(tree)
        except Exception as message:
            print("{}[{}] {} {}".format(
                MessageColor.FAIL,
                type(message).__name__,
                message,
                MessageColor.ENDC
            ))
            status = -1
        print()
        print(MessageColor.OKBLUE + "Process terminated with status {}".format(status) + MessageColor.ENDC)
        return status


