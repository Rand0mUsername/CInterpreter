
from .number import Number, ConstNumber
from ..common.ctype import CType


class Scope(object):
    """ A scope (block/function) with its address/const table """
    def __init__(self, scope_name, parent_scope=None):
        self.scope_name = scope_name
        # Parent_scope is None if this is a global scope or a function scope (top of the frame)
        self.parent_scope = parent_scope
        self._values = dict()  # addresses/consts

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, item):
        return self._values[item]

    def __contains__(self, key):
        return key in self._values

    def __repr__(self):
        lines = [
            '{}:{}'.format(key, val) for key, val in self._values.items()
        ]
        title = '{}\n'.format(self.scope_name)
        return title + '\n'.join(lines)


class Frame(object):
    """ A single stack frame, contains nested scopes """
    def __init__(self, frame_name):
        self.frame_name = frame_name
        # depth = 00
        self.curr_scope = Scope(
            '{}.scope_00'.format(frame_name),
            None
        )

    def new_scope(self):
        # increase depth
        self.curr_scope = Scope(
            '{}{:02d}'.format(
                self.curr_scope.scope_name[:-2],
                int(self.curr_scope.scope_name[-2:]) + 1
            ),
            self.curr_scope
        )

    def del_scope(self):
        self.curr_scope = self.curr_scope.parent_scope

    def find_key(self, key):
        scope = self.curr_scope
        while scope and key not in scope:
            scope = scope.parent_scope
        return scope

    def _get_scopes(self):
        scopes = []
        curr_scope = self.curr_scope
        while curr_scope is not None:
            scopes.append(curr_scope)
            curr_scope = curr_scope.parent_scope
        return scopes

    def __contains__(self, key):
        return key in self._get_scopes()

    def __repr__(self):
        lines = [
            '{}\n{}'.format(
                scope,
                '-' * 40
            ) for scope in self._get_scopes()
        ]

        title = 'Frame: {}\n{}\n'.format(
            self.frame_name,
            '*' * 40
        )

        return title + '\n'.join(lines)


class Stack(object):
    """ A stack, contains stacked frames """
    def __init__(self):
        # curr_frame is always the last in the list
        self.curr_frame = None
        self.frames = []

    def is_empty(self):
        return self.curr_frame is None

    def new_frame(self, frame_name):
        self.frames.append(Frame(frame_name))
        self.curr_frame = self.frames[-1]

    def del_frame(self):
        self.frames.pop(-1)
        if len(self.frames) == 0:
            self.curr_frame = None
        else:
            self.curr_frame = self.frames[-1]

    def __repr__(self):
        lines = [
            '{}'.format(frame) for frame in self.frames
        ]
        return '\n'.join(lines)


class Memory(object):
    """
        A simulated program memory, contains a raw_memory map that maps addresses to values and a stack with frames.
        Every frame contains nested scopes and each scope maps symbol names to addresses/consts.
        There is also a global scope and a list of dynamically allocated addresses.

        Mapping name->address in scopes and address->val in raw_memory is a way to simulate C memory system in python.
        In reality the raw_memory map would not be necessary since scope members would inherently have addresses.

        Possible values are Number(ctype, value), FunctionDecl(C Fun), <function> (Py Fun)
    """

    # Addresses start from this number and always grow
    STARTING_ADDRESS = int(1e6)

    def __init__(self):
        self.global_scope = Scope('global_scope')
        self.stack = Stack()
        self.raw_memory = dict()
        self.next_free_address = Memory.STARTING_ADDRESS
        self.dyn_alloc_addr = set()

    def declare_constant(self, name, value):
        scope = self._get_curr_scope()
        scope[name] = ConstNumber(CType.from_string('int'), value)

    def allocate(self, block_sz):
        """ Allocates a memory block """
        ret_address = self.next_free_address
        self.next_free_address += block_sz
        return ret_address

    def _get_curr_scope(self):
        if self.stack.is_empty():
            return self.global_scope
        else:
            return self.stack.curr_frame.curr_scope

    def _declare(self, name, size_bytes, initial_value):
        # find the current scope
        scope = self._get_curr_scope()

        # name -> address (just int) / const (Number!, no address)
        scope[name] = self.allocate(size_bytes)  # random fixed fun size

        # address -> random value
        self.raw_memory[scope[name]] = initial_value

    def declare_fun(self, name):
        """ Reserves space for a fun variable """
        # random fixed size for functions
        self._declare(name, 32, None)

    def declare_num(self, c_type, name):
        """ Reserves space for a num variable """
        self._declare(name, c_type.size_bytes(), Number(c_type))

    def find_key(self, key):
        """ Returns the scope with the given key starting from the current scope """
        if self.stack.is_empty():
            return self.global_scope
        # Look in the current frame
        scope = self.stack.curr_frame.find_key(key)
        if scope is not None:
            return scope
        # If nothing try in the global scope
        if key in self.global_scope:
            return self.global_scope
        # Semantic analysis should ensure the key exists, this should never happen
        raise RuntimeError("Failed to find {} in the current scope".format(key))

    def get_value_in_scope(self, key):
        scope = self.find_key(key)
        return scope[key]

    def set_at_address(self, address, value):
        self.raw_memory[address] = value
        if value is None:
            raise RuntimeError()

    def get_at_address(self, address):
        if address not in self.raw_memory:
            # Return a random int number
            self.raw_memory[address] = Number(CType(type_spec='int'))
        return self.raw_memory[address]

    def __setitem__(self, key, value):
        val_in_scope = self.get_value_in_scope(key)
        if isinstance(val_in_scope, ConstNumber):
            raise RuntimeError("Can't reassign const value for const {} ".format(key))
        elif isinstance(val_in_scope, int):
            self.set_at_address(val_in_scope, value)
        else:
            raise RuntimeError("Invalid type for val_in_scope:  (<{}>) ".type(val_in_scope))

    def __getitem__(self, key):
        val_in_scope = self.get_value_in_scope(key)
        if isinstance(val_in_scope, ConstNumber):
            return val_in_scope
        elif isinstance(val_in_scope, int):
            return self.get_at_address(val_in_scope)
        else:
            raise RuntimeError("Invalid type for val_in_scope:  (<{}>) ".type(val_in_scope))

    def new_frame(self, frame_name):
        self.stack.new_frame(frame_name)

    def del_frame(self):
        self.stack.del_frame()

    def new_scope(self):
        self.stack.curr_frame.new_scope()

    def del_scope(self):
        self.stack.curr_frame.del_scope()

    def __repr__(self):
        return "{}\nStack\n{}\n{}".format(
            self.global_scope,
            '=' * 40,
            self.stack
        )

    def __str__(self):
        return self.__repr__()


