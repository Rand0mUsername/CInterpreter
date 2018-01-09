from ..lexical_analysis.token_type import NUM_TYPE_TOKENS
from ..syntax_analysis.parser import INTEGER_CONST, CHAR_CONST, REAL_CONST, AMPERSAND, OR_OP, XOR_OP
from .table import *
from ..common.utils import get_functions, MessageColor
from ..common.visitor import Visitor


class SemanticError(Exception):
    pass


class TypeWarning(UserWarning):
    pass


class SemanticAnalyzer(Visitor):

    class CType(object):
        # Maps type names to python types
        types_py = {'char': int, 'int': int, 'float': float, 'double': float}

        # Represents the type hierarchy
        order = ('char', 'int', 'float', 'double')

        # The type as a string
        def __init__(self, type_name):
            self.type_name = type_name

        def combine_with(self, other):
            """ Combines this CType with another one, return a 'broader' type """
            left_order = SemanticAnalyzer.CType.order.index(self.type_name)
            right_order = SemanticAnalyzer.CType.order.index(other.type_name)
            return SemanticAnalyzer.CType(SemanticAnalyzer.CType.order[max(left_order, right_order)])

        def __eq__(self, other):
            """ Checks for equality of python types """
            return SemanticAnalyzer.CType.types_py[self.type_name] == SemanticAnalyzer.CType.types_py[other.type_name]

        def __repr__(self):
            return '{}'.format(self.type_name)

        def __str__(self):
            return self.__repr__()

    def __init__(self):
        """ Initializes the analyzer, there is no scope"""
        self.current_scope = None

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
        # TODO: test void foo(int a) {int a;}
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
        self.visit(node.increment)
        self.visit(node.body)

    def visit_WhileStmt(self, node):
        """ while(condition) body """
        self.visit(node.condition)
        self.visit(node.body)

    def visit_DoWhileStmt(self, node):
        """ do body while (condition) """
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ReturnStmt(self, node):
        """ return expression """
        return self.visit(node.expression)

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

        # Return a resulting type
        return left_type.combine_with(right_type)

    def visit_UnOp(self, node):
        """ op expr """
        # If the operator is the type this is a cast
        # In both cases, return the resulting CType
        if node in NUM_TYPE_TOKENS:
            self.visit(node.expr)
            return SemanticAnalyzer.CType(node.op.value)
        return self.visit(node.expr)

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

    def visit_Assignment(self, node):
        """ right = left """
        # Visit both sides, don't allow assignment with different types
        right = self.visit(node.right)
        left = self.visit(node.left)
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