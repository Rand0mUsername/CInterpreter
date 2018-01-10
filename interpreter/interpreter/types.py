import random


def sizeof(type_name):
    """ Returns sizes of datatypes. """
    if type_name[-1] == '*':
        return 4   # 32bit system
    elif type_name == 'char':
        return 1
    elif type_name == 'int':
        return 4
    elif type_name == 'float':
        return 4
    elif type_name == 'double':
        return 8
    elif type_name == 'c_function' or type_name == 'py_function':
        # we also need to store functions in memory, implementing function pointers
        # is an overkill so we are storing them directly and assuming fixed size of 32
        return 32


class Pointer(object):
    """ A pointer class used by the interpreter """

    # null pointer
    NULL = 0

    def from_number(self, number):
        """ self = number """
        # The type names are almost the same, semantic analysis
        return Pointer(self.type_name, number.value)

    def __init__(self, type_name, address=NULL):
        # one of the four pointer types
        self.type_name = type_name
        # a target address
        self.address = address

    def __add__(self, other_number):
        """ self + other_number """
        return Pointer(self.type_name, self.address + other_number.value * sizeof(self.type_name[:-1]))

    def __sub__(self, other_number):
        """ self - other_number """
        return Pointer(self.type_name, self.address - other_number.value * sizeof(self.type_name[:1]))

    def __gt__(self, other_ptr):
        """ self > other_ptr """
        return Number('int', self.address > other_ptr.address)

    def __ge__(self, other_ptr):
        """ self >= other_ptr """
        return Number('int', self.address >= other_ptr.address)

    def __lt__(self, other_ptr):
        """ self < other_ptr """
        return Number('int', self.address < other_ptr.address)

    def __le__(self, other_ptr):
        """ self <= other_ptr """
        return Number('int', self.address <= other_ptr.address)

    def __eq__(self, other_ptr):
        """ self == other_ptr """
        return Number('int', self.address == other_ptr.address)

    def __ne__(self, other_ptr):
        """ self != other_ptr """
        return Number('int', self.address != other_ptr.address)

    def __iadd__(self, other_number):
        """ self += other_number """
        return Pointer(self.type_name, self.address + other_number.value * sizeof(self.type_name[:-1]))

    def __isub__(self, other_number):
        """ self -= other_number """
        return Pointer(self.type_name, self.address - other_number.value * sizeof(self.type_name[:-1]))

    def __bool__(self):
        return bool(self.address)

    def __repr__(self):
        return '{} ({})'.format(
            self.type_name,
            self.address
        )

    def __str__(self):
        return self.__repr__()


# Maps type names to python types used to evaluate
types_py = {'char': int,
            'int': int,
            'float': float,
            'double': float,
            'char*': Pointer,
            'int*': Pointer,
            'float*': Pointer,
            'double*': Pointer
            }


class Number(object):
    """ A number class used by the interpreter """

    # Represents the base type hierarchy
    order = ('char', 'int', 'float', 'double')

    def __init__(self, type_name, value=random.randint(0, 2**32)):
        # save the type name as a string
        self.type_name = type_name

        # cast the value to appropriate python type
        self.value = types_py[type_name](value)

    def _combine_types(self, other):
        """ Combines the type of this Number with another Number and returns a (type_name, type_py) tuple """
        left_order = Number.order.index(self.type_name)
        right_order = Number.order.index(other.type_name)
        type_name = Number.order[max(left_order, right_order)]
        return type_name, types_py[type_name]

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
        type_py = types_py[self.type_name]
        result = self + other
        return Number(self.type_name, type_py(result.value))

    def __isub__(self, other):
        """ self -= other """
        type_py = types_py[self.type_name]
        result = self - other
        return Number(self.type_name, type_py(result.value))

    def __imul__(self, other):
        """ self *= other """
        type_py = types_py[self.type_name]
        result = self * other
        return Number(self.type_name, type_py(result.value))

    def __itruediv__(self, other):
        """ self /= other """
        type_py = types_py[self.type_name]
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