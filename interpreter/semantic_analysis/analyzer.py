from ..lexical_analysis.token_type import *
from ..syntax_analysis.tree import *
from .table import *
from ..common.utils import get_functions, MessageColor
from ..common.visitor import Visitor


class SemanticError(Exception):
    pass


class TypeWarning(UserWarning):
    pass


class SemanticAnalyzer(Visitor):

    class CType(object):
        # Represents the base type hierarchy
        order = ('char', 'int', 'float', 'double')

        # Checks if a CType is a pointer
        @staticmethod
        def is_pointer(c_type):
            return c_type.type_name[-1] == '*'

        # The type as a string
        def __init__(self, type_name):
            self.type_name = type_name

        def combine_with(self, other):
            """ Combines this CType with another one, return a 'broader' type """
            # If 1 pointer just return its type, that's pointer arithmetic
            # 2 pointers / ptr+float etc. should be blocked before this
            if SemanticAnalyzer.CType.is_pointer(self):
                return SemanticAnalyzer.CType(self.type_name)
            elif SemanticAnalyzer.CType.is_pointer(other):
                return SemanticAnalyzer.CType(other.type_name)
            else:
                # Combine non-pointer types
                left_order = SemanticAnalyzer.CType.order.index(self.type_name)
                right_order = SemanticAnalyzer.CType.order.index(other.type_name)
                return SemanticAnalyzer.CType(SemanticAnalyzer.CType.order[max(left_order, right_order)])

        def __eq__(self, other):
            """ Checks for equality of types """
            return self.type_name == other.type_name

        def __repr__(self):
            return '{}'.format(self.type_name)

        def __str__(self):
            return self.__repr__()

    def __init__(self):
        """ Initializes the analyzer, there is no scope"""
        self.current_scope = None
        # the number of nested loops/switches
        self.in_nested_loop = 0
        self.in_nested_switch = 0

    def error(self, message):
        raise SemanticError("SemanticError:" + message)

    def warning(self, message):
        print("SemanticWarning:" + MessageColor.WARNING + message + MessageColor.ENDC)

    def get_next_scope_name(self, name):
        """ Generates next scope name by incrementing the number of the current scope. """
        if name[-2:].isdigit():
            return '{}{:02d}'.format(
                name[:-2],
                int(name[-2:]) + 1
            )
        else:
            return '{}{:02d}'.format(
                name,
                1
            )

    """
        A series of visit functions. Beware of inconsistent return values:
        - visit_Param returns a symbol containing that param
        - visit_Expression and functions alike return a CType with the numeric type
        - the rest of the functions don't return anything
    """

    def visit_Program(self, node):
        # Create a global scope
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope,
        )

        # Only the global scope has builtin types
        global_scope.init_builtins()

        # Set the global scope as the current scope and recurse
        self.current_scope = global_scope
        for child in node.children:
            self.visit(child)
        if not self.current_scope.lookup('main'):
            self.error(
                "Undeclared mandatory function main"
            )
        self.current_scope = self.current_scope.enclosing_scope

    def visit_VarDecl(self, node):
        """ type_node var_node """

        # Get a symbol for this type
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        # Create a symbol for this variable and insert in the current symbol table
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        if self.current_scope.lookup(var_name, current_scope_only=True):
            self.error(
                "Error: Duplicate identifier '{}' found at line {}".format(
                    var_name,
                    node.line
                )
            )

        self.current_scope.insert(var_symbol)

    def visit_IncludeLibrary(self, node):
        """ #include <library_name.h> """

        functions = get_functions('interpreter.__builtins__.{}'.format(
            node.library_name
        ))

        for func in functions:
            # Get function return type
            type_symbol = self.current_scope.lookup(func.return_type)

            func_name = func.__name__
            if self.current_scope.lookup(func_name):
                continue

            # Create function symbol
            func_symbol = FunctionSymbol(func_name, type_symbol=type_symbol)

            if func.arg_types is None:
                func_symbol.params = None
            else:
                # add a symbol for each param
                for i, param_type in enumerate(func.arg_types):
                    type_symbol = self.current_scope.lookup(param_type)
                    var_symbol = VarSymbol('param{:02d}'.format(i + 1), type_symbol)
                    func_symbol.params.append(var_symbol)

            self.current_scope.insert(func_symbol)

    def visit_FunctionDecl(self, node):
        """ type_node  func_name ( params ) body """

        # Get function return type and fetch the type symbol
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        # Create a function symbol and insert it in the current table
        func_name = node.func_name
        if self.current_scope.lookup(func_name):
            self.error(
                "Error: Duplicate identifier '{}' found at line {}".format(func_name, node.line)
            )
        func_symbol = FunctionSymbol(func_name, type_symbol=type_symbol)
        self.current_scope.insert(func_symbol)

        # Create a new scope for the function
        procedure_scope = ScopedSymbolTable(
            scope_name=func_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = procedure_scope

        # Visit function parameters, adding them to the new scope
        # Since visit_Param returns a symbol, add param symbols to the func symbol
        for param in node.params:
            func_symbol.params.append(self.visit(param))

        self.visit(node.body)

        self.current_scope = self.current_scope.enclosing_scope

    def visit_Param(self, node):
        """ type_node var_node, returns a param symbol"""

        # Create a symbol for the param and insert it in the current table
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        if self.current_scope.lookup(var_name, current_scope_only=True):
            self.error(
                "Error: Duplicate identifier '{}' found at line {}".format(
                    var_name,
                    node.line
                )
            )

        self.current_scope.insert(var_symbol)

        # Return the param symbol (!)
        return var_symbol

    def visit_FunctionBody(self, node):
        """ { children } """
        # Visit all sub-statements
        for child in node.children:
            self.visit(child)

    def visit_CompoundStmt(self, node):
        """ { children } """

        # We entered a new block, create a new scope
        block_scope = ScopedSymbolTable(
            scope_name=self.get_next_scope_name(self.current_scope.scope_name),
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )

        # Set it as the current scope and recurse
        self.current_scope = block_scope

        for child in node.children:
            self.visit(child)

        self.current_scope = self.current_scope.enclosing_scope

    def visit_IfStmt(self, node):
        """ if (condition) tbody else fbody """
        self.visit(node.condition)
        self.visit(node.true_body)
        self.visit(node.false_body)

    def visit_ForStmt(self, node):
        """ for(setup condition increment) body"""
        self.visit(node.setup)
        self.visit(node.condition)
        self.in_nested_loop += 1
        self.visit(node.body)
        self.in_nested_loop -= 1
        self.visit(node.increment)

    def visit_WhileStmt(self, node):
        """ while(condition) body """
        self.visit(node.condition)
        self.in_nested_loop += 1
        self.visit(node.body)
        self.in_nested_loop -= 1

    def visit_DoWhileStmt(self, node):
        """ do body while (condition) """
        self.in_nested_loop += 1
        self.visit(node.body)
        self.in_nested_loop -= 1
        self.visit(node.condition)

    def visit_ReturnStmt(self, node):
        """ return expression """
        return self.visit(node.expression)

    def visit_ContinueStmt(self, node):
        """ continue """
        if self.in_nested_loop == 0:
            self.error("Continue statement not in loop at line {}".format(node.line))

    def visit_BreakStmt(self, node):
        """ break """
        if self.in_nested_loop == 0 and self.in_nested_switch == 0:
            self.error("Break statement not in loop/switch at line {}".format(node.line))

    def visit_Expression(self, node):
        # Visit all comma-separated subexpressions and return the CType of the last one
        # All number expressions return their CType (!)
        expr = None
        for child in node.children:
            expr = self.visit(child)
        return expr

    def visit_BinOp(self, node):
        """ left op right """

        # Visit both sides of the binary operation and get their CTypes
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Allow logical operators only on ints
        if node.token.type == AMPERSAND or node.token.type == OR_OP or node.token.type == XOR_OP:
            if left_type.type_name != "int" or right_type.type_name != "int":
                self.error("Unsupported types ltype:<{}> rtype:<{}> at bitwise operator {} at line {}".format(
                    left_type.type_name,
                    right_type.type_name,
                    node.token.type,
                    node.line
                ))

        # Disallow two pointers
        if SemanticAnalyzer.CType.is_pointer(left_type) and SemanticAnalyzer.CType.is_pointer(right_type):
            self.error("Two pointer types (<{}> and <{}>) at binary operator {} at line {}".format(
                    left_type.type_name,
                    right_type.type_name,
                    node.token.type,
                    node.line
                ))

        # If one pointer allow only PLUS and MINUS with int
        if SemanticAnalyzer.CType.is_pointer(left_type):
            if right_type.type_name != "int" or (node.token.type != PLUS and node.token.type != MINUS):
                self.error("Unsupported pointer arithmetic with types (<{}> and <{}>) at bin op {} at line {}".format(
                    left_type.type_name,
                    right_type.type_name,
                    node.token.type,
                    node.line
                ))
        elif SemanticAnalyzer.CType.is_pointer(right_type):
            if left_type.type_name != "int" or (node.token.type != PLUS and node.token.type != MINUS):
                self.error("Unsupported pointer arithmetic with types (<{}> and <{}>) at bin op {} at line {}".format(
                    left_type.type_name,
                    right_type.type_name,
                    node.token.type,
                    node.line
                ))

        # Return the resulting type
        return left_type.combine_with(right_type)

    def visit_UnOp(self, node):
        """ op expr """
        # If the operator is the type this is a cast
        if node in NUM_TYPE_TOKENS:
            self.visit(node.expr)
            return SemanticAnalyzer.CType(node.token.value)

        # Visit the expression
        expr_type = self.visit(node.expr)

        # INC/DEC -> lvalue
        if node.token.type in [INC_OP, DEC_OP] and not self.is_lvalue(node.expr):
            self.error("{} not an lvalue, can't inc/dec at un op {} at line {}".format(
                type(node.expr),
                node.token.type,
                node.line
            ))

        # ASTERISK -> pointer
        if node.token.type == ASTERISK:
            if SemanticAnalyzer.CType.is_pointer(expr_type):
                return SemanticAnalyzer.CType(expr_type.type_name[:-1])
            else:
                self.error(
                    "Can't dereference type ({}) at line {}".format(
                        expr_type,
                        node.line
                    )
                )

        # pointer -> ASTERISK/INC/DEC
        if SemanticAnalyzer.CType.is_pointer(expr_type) and node.token.type not in [INC_OP, DEC_OP, ASTERISK]:
            self.error("Unsupported pointer arithmetic on type (<{}>) at un op {} at line {}".format(
                expr_type.type_name,
                node.token.type,
                node.line
            ))

        # AMPERSAND casts to int
        if node.token.type == AMPERSAND:
            return SemanticAnalyzer.CType('int')
        else:
            return expr_type

    def visit_TerOp(self, node):
        """ condition ? texpression : fexpression """
        # Visit all three expressions and return the resulting CType
        self.visit(node.condition)
        true_exp = self.visit(node.true_exp)
        false_exp = self.visit(node.false_exp)
        if true_exp != false_exp:
            self.warning("Incompatibile types at ternary operator texpr:<{}> fexpr:<{}> at line {}".format(
                true_exp,
                false_exp,
                node.line
            ))
        return true_exp

    def is_lvalue(self, node):
        if isinstance(node, Var):
            return True
        if isinstance(node, UnOp) and node.token.type == ASTERISK and isinstance(node.expr, Var):
            return True

        return False

    def visit_Assignment(self, node):
        """ left = right """
        left = self.visit(node.left)  # primary
        right = self.visit(node.right)  # whatever

        # left is a primary expression but it needs to be an lvalue
        if not self.is_lvalue(node.left):
            self.error("Can't assign to a non-lvalue (<{}>) at ass op {} at line {}".format(
                type(node.left),
                node.token.type,
                node.line
            ))

        # it can be NumVar/PtrVar/*PtrVar

        # Allow only +=int and -=int and =int and =matching_type if it is a pointer
        if SemanticAnalyzer.CType.is_pointer(left):
            if node.token.type == ADD_ASSIGN and right.type_name == 'int':
                return right
            if node.token.type == SUB_ASSIGN and right.type_name == 'int':
                return right
            if node.token.type == ASSIGN and SemanticAnalyzer.CType.is_pointer(right) and \
                    right.type_name == left.type_name:
                return right
            if node.token.type == ASSIGN and right.type_name == 'int':
                return right
            self.error("Unsupported pointer assignment on types (<{}> <{}>) at ass op {} at line {}".format(
                left.type_name,
                right.type_name,
                node.token.type,
                node.line
            ))
        else:
            # Otherwise, don't allow assignment with different types
            if left != right:
                self.warning("Incompatible types when assigning to type <{}> from type <{}> at line {}".format(
                    left,
                    right,
                    node.line
                ))

        # Return the resulting type
        return right

    def visit_Var(self, node):
        """ value """
        # Visit a variable and check if it exists in the current scope
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(
                "Symbol(identifier) not found '{}' at line {}".format(
                    var_name,
                    node.line
                )
            )

        # Get type symbol from var symbol and construct a CType based on its name
        return SemanticAnalyzer.CType(var_symbol.type_symbol.name)

    def visit_Type(self, node):
        # Just return the CType
        return SemanticAnalyzer.CType(node.value)

    def visit_Num(self, node):
        """ value """
        # Branch on token type to return the appropriate CType
        if node.token.type == INTEGER_CONST:
            return SemanticAnalyzer.CType("int")
        elif node.token.type == CHAR_CONST:
            return SemanticAnalyzer.CType("char")
        elif node.token.type == REAL_CONST:
            return SemanticAnalyzer.CType("float")
        else:
            self.error("Unknown num token type: {}".format(node.token.type))

    def visit_String(self, node):
        pass

    def visit_NoOp(self, node):
        pass

    def visit_FunctionCall(self, node):
        # Get function symbol and check if its defined
        func_name = node.name
        func_symbol = self.current_scope.lookup(func_name)
        if func_symbol is None:
            self.error(
                "Function '{}' not found at line {}".format(
                    func_name,
                    node.line
            ))
        if not isinstance(func_symbol, FunctionSymbol):
            self.error(
                "Identifier '{}' cannot be used as a function at line".format(
                    func_name,
                    node.line
                )
            )

        # If function has no params or it is a variadic fn (params is None)
        # just visit the args with no checks and return the return CType
        if func_symbol.params is None:
            for i, arg in enumerate(node.args):
                self.visit(arg)
            return SemanticAnalyzer.CType(func_symbol.type_symbol.name)

        # Check if there is a correct number of arguments
        if len(node.args) != len(func_symbol.params):
            self.error(
                "Function {} takes {} positional arguments but {} were given at line {}".format(
                    func_name,
                    len(node.args),
                    len(func_symbol.params),
                    node.line
                )
            )

        # Check if argument types match parameter types
        param_types = []
        arg_types = []

        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg)
            param_type = SemanticAnalyzer.CType(func_symbol.params[i].type_symbol.name)
            param_types.append(param_type)
            arg_types.append(arg_type)

        if param_types != arg_types:
            self.warning("Incompatibile argument types for function <{}{}> but found <{}{}> at line {}".format(
                func_name,
                str(param_types).replace('[', '(').replace(']', ')'),
                func_name,
                str(arg_types).replace('[', '(').replace(']', ')'),
                node.line
            ))

        # Return the return value CType
        return SemanticAnalyzer.CType(func_symbol.type_symbol.name)

    @staticmethod
    def analyze(tree):
        """ Analyzes the AST and looks for errors/warnings """
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(tree)