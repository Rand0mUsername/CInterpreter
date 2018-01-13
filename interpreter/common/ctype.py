import random


class StructCType:
    def __init__(self, name):
        self.name = name


class CType:

    # groups of text specifiers
    type_specifiers = ['char', 'int', 'float', 'double']
    len_specifiers = ['short', 'long']
    sign_specifiers = ['unsigned', 'signed']

    # all possible str(CType) ordered by strength
    all_types = ['char', 'unsigned char', 'short int', 'unsigned short int', 'int', 'unsigned int', 'long int',
                 'unsigned long int', 'long long int', 'unsigned long long int', 'float', 'double', 'long double']

    def __init__(self, len_spec=None, sign_spec=None, type_spec='int', pointer=False):
        # all strings
        self.len_spec = len_spec  # short, long, long long, None
        self.sign_spec = sign_spec  # signed, unsigned, None
        self.type_spec = type_spec  # int, char, float, double, None
        self.pointer = pointer  # True, False

    def py_type(self):
        if self.pointer:
            return int
        elif self.type_spec in ['float', 'double']:
            return float
        else:
            return int

    def random_value(self):
        py_type = self.py_type()
        if py_type == float:
            return random.uniform(*self.limits())
        elif py_type == int:
            return random.randint(*self.limits())
        else:
            raise RuntimeError("Unknown py type {}".format(str(py_type)))

    def limits(self):
        size_bits = 8 * self.size_bytes()
        if self.sign_spec == 'unsigned':
            return 0, 2**size_bits-1
        else:
            mid = 2**(size_bits-1)
            return -mid, mid-1

    def size_bytes(self):
        if self.pointer:
            return 4  # assuming 32bit architecture
        if self.type_spec == 'char':
            return 1
        if self.len_spec == 'short':
            return 2
        if self.len_spec == 'long long':
            return 8
        if self.type_spec == 'int':
            return 4
        if self.type_spec == 'float':
            return 4
        if self.type_spec == 'double':
           if self.len_spec == 'long':
               return 8
           else:
               return 4
        raise RuntimeError('Failed to return size of a CType {}'.format(str(self)))

    def dereference(self):
        assert self.pointer
        return CType(self.len_spec, self.sign_spec, self.type_spec, False)

    def __repr__(self):
        # canonical representation
        # (signed|unsigned) (short|long|long long)? (int|char|float|double) (*)?
        specs = []
        if self.sign_spec == 'unsigned':
            specs.append(self.sign_spec)
        if self.len_spec is not None:
            specs.append(self.len_spec)
        if self.type_spec is not None:
            specs.append(self.type_spec)
        if self.pointer:
            specs.append('*')
        return ' '.join(specs)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        """ Checks for equality of types """
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def from_string(type_str):
        # Collect all specifiers
        type_spec = None
        len_spec = None
        sign_spec = None
        pointer = False
        spec_strs = type_str.split(' ')
        idx = 0
        while idx < len(spec_strs):
            spec = spec_strs[idx]
            if spec in CType.type_specifiers:
                if type_spec is not None:
                    raise RuntimeError("Multiple type specifiers")
                type_spec = spec
                if idx+1 < len(spec_strs) and spec_strs[idx+1] == '*':
                    pointer = True
                    idx += 1
            elif spec in CType.len_specifiers:
                if len_spec is not None:
                    raise RuntimeError("Multiple len specifiers")
                len_spec = spec
                if spec == 'long' and idx+1 < len(spec_strs) and spec_strs[idx+1] == 'long':
                    len_spec = 'long long'
                    idx += 1
            elif spec in CType.sign_specifiers:
                if sign_spec is not None:
                    raise RuntimeError("Multiple sign specifiers")
                sign_spec = spec
            else:
                raise RuntimeError("Unrecognized spec '{}' ".format(spec))
            idx += 1

        # Check one case to allow defaults
        if len_spec is None and type_spec is None:
            raise RuntimeError("No len and no type spec")

        return CType(len_spec, sign_spec, type_spec, pointer)

    @staticmethod
    def combine_types(a, b):
        """ Combines this Type with another one, return a 'stronger' type """
        assert(not a.pointer and not b.pointer)
        order_a = CType.all_types.index(str(a))
        order_b = CType.all_types.index(str(b))
        order_result = max(max(order_a, order_b), 4)  # max with 4 for 'int'
        return CType.from_string(CType.all_types[order_result])
