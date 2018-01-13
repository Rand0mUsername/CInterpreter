from collections import OrderedDict

"""
Symbols and tables used for semantic analysis
"""


class Symbol(object):
    def __init__(self, name, c_type=None):
        # string name of the symbol
        self.name = name
        # a CType
        self.c_type = c_type


class VarSymbol(Symbol):
    """ A symbol representing a variable """
    def __init__(self, name, c_type):
        super(VarSymbol, self).__init__(name, c_type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.c_type,
        )

    __repr__ = __str__


class StructSymbol(Symbol):
    """ A symbol representing a struct """
    def __init__(self, c_type, fields):
        super(StructSymbol, self).__init__(c_type.name)
        self.c_type = c_type
        self.fields = fields

    def __str__(self):
        return "<{class_name}(name='{name}' fields='{fields}'))>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            fields=self.fields
        )

    __repr__ = __str__


class ConstSymbol(Symbol):
    """ A symbol representing a constant """
    def __init__(self, name, c_type):
        super(ConstSymbol, self).__init__(name, c_type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.c_type,
        )

    __repr__ = __str__


class FunctionSymbol(Symbol):
    """ A symbol representing a function """
    def __init__(self, name, c_type, params=None):
        super(FunctionSymbol, self).__init__(name, c_type)
        # a list of formal parameter Symbols
        self.params = params if params is not None else []

    def __str__(self):
        return '<{class_name}(type={type}, name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.params,
            type=self.c_type
        )

    __repr__ = __str__


class ScopedSymbolTable(object):
    """ A scope containing a symbol table """
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbol_table = OrderedDict()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
            )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbol_table.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def insert(self, symbol):
        """ Inserts a new symbol in the current table. """
        self._symbol_table[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
        """ Tries to find a symbol with a given name in the current table. """
        symbol = self._symbol_table.get(name)

        # return a symbol if found
        if symbol is not None:
            return symbol

        # if current_scope_only flag is set, don't search in parent scopes
        if current_scope_only:
            return None

        # recursively go up the chain and search for the name in parent scopes
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
