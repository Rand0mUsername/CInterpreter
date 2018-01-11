from functools import wraps
import pickle
import importlib
import re


def import_module(libname):
    """ Imports the module with a given name """
    return importlib.import_module(libname)


def get_functions(module):
    """ Returns all functions defined in some module """
    lib = import_module(module)

    for func_name in dir(lib):
        func = getattr(lib, func_name)
        if callable(func) and not func_name.startswith('__') and func.__module__.endswith(module):
            yield func


def get_constants(module):
    """ Returns all constants defined in some module """
    lib = import_module(module)
    for name in dir(lib):
        const = getattr(lib, name)
        if not callable(const) and re.match("^[A-Z][_A-Z]*$", name):
            yield (name, const)

def restorable(fn):
    """ Decorator that resets object state after calling a function """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        state = pickle.dumps(self.__dict__)
        result = fn(self, *args, **kwargs)
        self.__dict__ = pickle.loads(state)
        return result
    return wrapper


def definition(return_type=None, arg_types=[]):
    """ Decorator used for definitions of builtin functions """
    def wrapper_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper.return_type = return_type
        wrapper.arg_types = arg_types
        return wrapper
    return wrapper_decorator

class MessageColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'






