from ..common.ctype import CType


class Number(object):
    """ A number class used by the interpreter """

    def __init__(self, c_type, value=None):
        # save the c type
        self.c_type = c_type

        # get a random default value and cast to the type
        if value is None:
            value = c_type.random_value()

        # TODO now it works with Number/int but remove Number later
        if isinstance(value, Number):
            value = value.value

        value = c_type.py_type()(value)

        # check the limits, this should be the only place this is needed
        lo, hi = c_type.limits()
        value = (value - lo) % (hi - lo + 1) + lo

        # finally assign
        self.value = value

    @staticmethod
    def cast(c_type, num):
        return Number(c_type, c_type.py_type()(num))

    def assign(self, other):
        return CType.cast(self.c_type, other)

    def __add__(self, other):
        """ self + other """
        if self.c_type.pointer:
            # ptr + int
            data_size = self.c_type.dereference().size_bytes()
            return Number(self.c_type, self.value + other.value * data_size)
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(res_c_type, res_py_type(self.value) + res_py_type(other.value))

    def __sub__(self, other):
        """ self - other """
        if self.c_type.pointer:
            # ptr - int
            data_size = self.c_type().dereference().size_bytes()
            return Number(self.c_type, self.value - other.value * data_size)
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(res_c_type, res_py_type(self.value) - res_py_type(other.value))

    def __mul__(self, other):
        """ self * other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(res_c_type, res_py_type(self.value) * res_py_type(other.value))

    def __truediv__(self, other):
        """ self / other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        if res_py_type == int:
            return Number(res_c_type, res_py_type(self.value) // res_py_type(other.value))
        return Number(res_c_type, res_py_type(self.value) / res_py_type(other.value))

    def __mod__(self, other):
        """ self % other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()

        if res_py_type != int:
            raise TypeError("invalid operands of types '{}' and '{}' to binary ‘operator %’".format(
                str(self.c_type),
                str(other.c_type)
            ))
        return Number(res_c_type, res_py_type(self.value) % res_py_type(other.value))

    def __gt__(self, other):
        """ self > other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(CType(type_spec='int'), res_py_type(self.value) > res_py_type(other.value))

    def __ge__(self, other):
        """ self >= other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(CType(type_spec='int'), res_py_type(self.value) >= res_py_type(other.value))

    def __lt__(self, other):
        """ self < other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(CType(type_spec='int'), res_py_type(self.value) < res_py_type(other.value))

    def __le__(self, other):
        """ self <= other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(CType(type_spec='int'), res_py_type(self.value) <= res_py_type(other.value))

    def __eq__(self, other):
        """ self == other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(CType(type_spec='int'), res_py_type(self.value) == res_py_type(other.value))

    def __ne__(self, other):
        """ self != other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(CType(type_spec='int'), res_py_type(self.value) != res_py_type(other.value))

    def __iadd__(self, other):
        """ self += other """
        return Number(self.c_type, self.c_type.py_type()(self+other))

    def __isub__(self, other):
        """ self -= other """
        return Number(self.c_type, self.c_type.py_type()(self-other))

    def __imul__(self, other):
        """ self *= other """
        return Number(self.c_type, self.c_type.py_type()(self*other))

    def __itruediv__(self, other):
        """ self /= other """
        return Number(self.c_type, self.c_type.py_type()(self/other))

    def __and__(self, other):
        """ self & other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(res_c_type, res_py_type(self.value) & res_py_type(other.value))

    def __or__(self, other):
        """ self | other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(res_c_type, res_py_type(self.value) | res_py_type(other.value))

    def __xor__(self, other):
        """ self ^ other """
        res_c_type = CType.combine_types(self.c_type, other.c_type)
        res_py_type = res_c_type.py_type()
        return Number(res_c_type, res_py_type(self.value) ^ res_py_type(other.value))

    def __bool__(self):
        return bool(self.value)

    def log_neg(self):
        if self.value:
            return Number(CType(type_spec='int'), 1)
        else:
            return Number(CType(type_spec='int'), 0)

    def __repr__(self):
        return '{} ({})'.format(
            str(self.c_type),
            self.value
        )

    def __str__(self):
        return self.__repr__()