class Number(object):
    """ A number class used by the interpreter """
    
    # Maps type names to python types_py
    types_py = {'char': int, 'int': int, 'float': float, 'double': float}

    # Represents the type hierarchy
    order = ('char', 'int', 'float', 'double')

    def __init__(self, type_name, value):
        # save the type name as a string
        self.type_name = type_name
        
        # cast the value to appropriate python type
        self.value = Number.types_py[type_name](value)

    def _combine_types(self, other):
        """ Combines the type of this Number with another Number and returns a (type_name, type_py) tuple """
        left_order = Number.order.index(self.type_name)
        right_order = Number.order.index(other.type_name)
        type_name = Number.order[max(left_order, right_order)]
        return type_name, Number.types_py[type_name]

    def __add__(self, other):
        """ self + other """
        type_name, type_py = self._combine_types(other)
        return Number(type_name, type_py(self.value) + type_py(other.value))

    def __sub__(self, other):
        """ self - other """
        type_name, type_py = self._combine_types(other)
        return Number(type_name, type_py(self.value) - type_py(other.value))

    def __mul__(self, other):
        """ self * other """
        type_name, type_py = self._combine_types(other)
        return Number(type_name, type_py(self.value) * type_py(other.value))

    def __truediv__(self, other):
        """ self / other """
        type_name, type_py = self._combine_types(other)
        if type_py == int:
            return Number(type_name, type_py(self.value) // type_py(other.value))
        return Number(type_name, type_py(self.value) / type_py(other.value))

    def __mod__(self, other):
        """ self % other """
        type_name, type_py = self._combine_types(other)

        if type_py != int:
            raise TypeError("invalid operands of types '{}' and '{}' to binary ‘operator %’".format(
                self.type_name,
                other.type
            ))
        return Number(type_name, type_py(self.value) % type_py(other.value))

    def __gt__(self, other):
        """ self > other """
        type_name, type_py = self._combine_types(other)
        return Number('int', int(type_py(self.value) > type_py(other.value)))

    def __ge__(self, other):
        """ self >= other """
        type_name, type_py = self._combine_types(other)
        return Number('int', int(type_py(self.value) >= type_py(other.value)))

    def __lt__(self, other):
        """ self < other """
        type_name, type_py = self._combine_types(other)
        return Number('int', int(type_py(self.value) < type_py(other.value)))

    def __le__(self, other):
        """ self <= other """
        type_name, type_py = self._combine_types(other)
        return Number('int', int(type_py(self.value) <= type_py(other.value)))

    def __eq__(self, other):
        """ self == other """
        type_name, type_py = self._combine_types(other)
        return Number('int', int(type_py(self.value) == type_py(other.value)))

    def __ne__(self, other):
        """ self != other """
        type_name, type_py = self._combine_types(other)
        return Number('int', int(type_py(self.value) != type_py(other.value)))

    def __iadd__(self, other):
        """ self += other """
        type_py = Number.types_py[self.type_name]
        result = self + other
        return Number(self.type_name, type_py(result.value))

    def __isub__(self, other):
        """ self -= other """
        type_py = Number.types_py[self.type_name]
        result = self - other
        return Number(self.type_name, type_py(result.value))

    def __imul__(self, other):
        """ self *= other """
        type_py = Number.types_py[self.type_name]
        result = self * other
        return Number(self.type_name, type_py(result.value))

    def __itruediv__(self, other):
        """ self /= other """
        type_py = Number.types_py[self.type_name]
        result = self / other
        return Number(self.type_name, type_py(result.value))

    def __and__(self, other):
        """ self & other """
        type_name, type_py = self._combine_types(other)
        return Number(type_name, int(type_py(self.value) & type_py(other.value)))

    def __or__(self, other):
        """ self | other """
        type_name, type_py = self._combine_types(other)
        return Number(type_name, int(type_py(self.value) | type_py(other.value)))

    def __xor__(self, other):
        """ self ^ other """
        type_name, type_py = self._combine_types(other)
        return Number(type_name, int(type_py(self.value) ^ type_py(other.value)))

    def __bool__(self):
        return bool(self.value)

    def log_neg(self):
        return Number('int', 0) if self.value else Number('int', 1)

    def __repr__(self):
        return '{} ({})'.format(
            self.type_name,
            self.value
        )

    def __str__(self):
        return self.__repr__()