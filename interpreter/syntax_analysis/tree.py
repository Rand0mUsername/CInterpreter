class AstNode(object):
    """ A node in the abstract syntax tree """
    def __init__(self, line):
        self.line = line


class NoOp(AstNode):
    pass


class Num(AstNode):
    def __init__(self, token, line):
        AstNode.__init__(self, line)
        self.token = token
        # Numeric value
        self.value = token.value


class String(AstNode):
    def __init__(self, token, line):
        AstNode.__init__(self, line)
        self.token = token
        # String value
        self.value = token.value

# TODO: int* a, b, c creates three pointers and int *a, *b is not allowed, FIX
class Type(AstNode):
    def __init__(self, line, c_type):
        AstNode.__init__(self, line)
        self.c_type = c_type


class StructType(AstNode):
    def __init__(self, line, c_type):
        AstNode.__init__(self, line)
        self.c_type = c_type  # struct name


class Var(AstNode):
    def __init__(self, token, line):
        AstNode.__init__(self, line)
        self.token = token
        # Variable name as a string
        self.value = token.value


class BinOp(AstNode):
    def __init__(self, left, token, right, line):
        AstNode.__init__(self, line)
        # Binary operator token
        self.token = token
        # BinOp arguments (AstNodes)
        self.left = left
        self.right = right


class UnOp(AstNode):
    def __init__(self, token, expr, line, prefix=True):
        AstNode.__init__(self, line)
        self.token = token
        # UnOp argument (AstNode)
        self.expr = expr
        # A flag indicating if this is a prefix operator
        self.prefix = prefix


class TerOp(AstNode):
    def __init__(self, condition, true_exp, false_exp, line):
        AstNode.__init__(self, line)
        # A condition to be tested (AstNode)
        self.condition = condition
        # Expressions to return based on the condition (AstNodes)
        self.true_exp = true_exp
        self.false_exp = false_exp


class Assignment(AstNode):
    def __init__(self, left, token, right, line):
        AstNode.__init__(self, line)
        # Variable node (Var)
        self.left = left
        # Assignment token
        self.token = token
        # The expression to be assigned
        self.right = right


class Expression(AstNode):
    def __init__(self, children, line):
        AstNode.__init__(self, line)
        # a list of comma-delimited sub-expressions (AstNodes)
        self.children = children


class FunctionCall(AstNode):
    def __init__(self, name, args, line):
        AstNode.__init__(self, line)
        # string name of the function
        self.name = name
        # a list of Param AstNodes
        self.args = args


class FieldAccess(AstNode):
    def __init__(self, op_type, var, field, line):
        AstNode.__init__(self, line)
        self.op_type = op_type # -> or .
        self.var = var  # Var node
        self.field = field  # Var field


class SwitchStmt(AstNode):
    def __init__(self, expr, children, line):
        AstNode.__init__(self, line)
        # The expression to compare
        self.expr = expr
        # A list of statement/decl_list/case_label AstNodes that are compounded
        self.children = children


class SwitchCaseLabel(AstNode):
    def __init__(self, expr, line):
        AstNode.__init__(self, line)
        # The expression to compare with
        self.expr = expr


class SwitchDefaultLabel(AstNode):
    def __init__(self, line):
        AstNode.__init__(self, line)


class IfStmt(AstNode):
    def __init__(self, condition, true_body, line, false_body=None):
        AstNode.__init__(self, line)
        # the expression AstNode to check
        self.condition = condition
        # the expression AstNodes to execute
        self.true_body = true_body
        self.false_body = false_body

class ForStmt(AstNode):
    def __init__(self, setup, condition, increment, body, line):
        AstNode.__init__(self, line)
        # Three expression AstNodes in for header
        self.setup = setup
        self.condition = condition
        self.increment = increment
        # The expression to execute
        self.body = body

class WhileStmt(AstNode):
    def __init__(self, condition, body, line):
        AstNode.__init__(self, line)
        # the expression AstNode to check
        self.condition = condition
        # the expression AstNode to execute
        self.body = body


class DoWhileStmt(WhileStmt):
    def __init__(self, condition, body, line):
        AstNode.__init__(self, line)
        # the expression AstNode to execute
        self.body = body
        # the expression AstNode to check
        self.condition = condition


class ReturnStmt(AstNode):
    def __init__(self, expression, line):
        AstNode.__init__(self, line)
        # The expression AstNode to return
        self.expression = expression


class BreakStmt(AstNode):
    pass


class ContinueStmt(AstNode):
    pass


class CompoundStmt(AstNode):
    def __init__(self, children, line):
        AstNode.__init__(self, line)
        # A list of statement/decl_list AstNodes that are compounded
        self.children = children


class VarDecl(AstNode):
    def __init__(self, var_node, type_node, line):
        AstNode.__init__(self, line)
        # Variable name and type nodes
        self.var_node = var_node
        self.type_node = type_node


class StructDecl(AstNode):
    def __init__(self, name, fields, line):
        AstNode.__init__(self, line)
        self.name = name  # string
        self.fields = fields  # dict of name->ctype


class IncludeLibrary(AstNode):
    def __init__(self, library_name, line):
        AstNode.__init__(self, line)
        # Library name as a string
        self.library_name = library_name


class Param(AstNode):
    def __init__(self, type_node, var_node, line):
        AstNode.__init__(self, line)
        # Function param: var and type nodes
        self.var_node = var_node
        self.type_node = type_node


class FunctionDecl(AstNode):
    def __init__(self, type_node, func_name, params, body, line):
        AstNode.__init__(self, line)
        # Function return type (AstNode), name(string)
        self.type_node = type_node
        self.func_name = func_name
        # A list of Param nodes
        self.params = params
        # AstNode expression to execute
        self.body = body


class FunctionBody(AstNode):
    # Essentially the same as CompoundStmt but semantic analyzer
    # treats them differently so the parser conforms
    def __init__(self, children, line):
        AstNode.__init__(self, line)
        # A list of statement/decl_list AstNodes that are compounded
        self.children = children


class Program(AstNode):
    def __init__(self, children, line):
        AstNode.__init__(self, line)
        # The whole program, list of declaration AstNodes / includes
        self.children = children