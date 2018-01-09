from collections import OrderedDict

"""
Symbols and tables used for semantic analysis
"""


class Symbol(object):
    def __init__(self, name, type_symbol=None):
        # string name of the symbol
        self.name = name
        # a symbol holding the type of this symbol
        self.type_symbol = type_symbol


class VarSymbol(Symbol):
    """ A symbol representing a variable """
    def __init__(self, name, type_symbol):
        super(VarSymbol, self).__init__(name, type_symbol)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__


class BuiltinTypeSymbol(Symbol):
    """ A symbol representing a built in type (char, int, float, double) """
    def __init__(self, name):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
        )


class FunctionSymbol(Symbol):
    """ A symbol representing a function """
    def __init__(self, name, type_symbol, params=None):
        super(FunctionSymbol, self).__init__(name, type_symbol)
        # a list of formal parameter Symbols
        self.params = params if params is not None else []

    def __str__(self):
        return '<{class_name}(type={type}, name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.params,
            type=self.type
        )

    __repr__ = __str__


class ScopedSymbolTable(object):
    """ A scope containing a symbol table """
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbol_table = OrderedDict()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def init_builtins(self):
        """ Inserts built in types in the symbol table. """
        self.insert(BuiltinTypeSymbol('char'))
        self.insert(BuiltinTypeSymbol('int'))
        self.insert(BuiltinTypeSymbol('float'))
        self.insert(BuiltinTypeSymbol('double'))

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
