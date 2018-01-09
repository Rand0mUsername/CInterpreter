"""
Supports basic functions from stdio.h library.
"""

from ..common.utils import definition
from ..interpreter.number import Number

import re

@definition(return_type='int', arg_types=None)
def printf(*args):
    fmt, *params = args
    message = fmt % tuple([param.value for param in params])
    result = len(message)
    print(message, end='')
    return result

@definition(return_type='int', arg_types=None)
def scanf(*args):
    def get_type_name(flag):
        """ Takes a type specifier and returns the type name. """
        if flag[-1] == 'd':
            return 'int'
        raise Exception('You are not allowed to use \'{}\' as a type'.format(flag))

    # unpack args
    fmt, *params, memory = args

    # Extract type specifiers from the format string
    fmt = re.sub(r'\s+', '', fmt)
    specifiers = re.findall('%[^%]*[dfi]', fmt)
    if len(specifiers) != len(params):
        raise Exception('Format of scanf function takes {} positional arguments but {} were given'.format(
            len(specifiers),
            len(params)
        ))

    # Scan the appropriate number of tokens
    tokens = []
    while len(tokens) < len(specifiers):
        line = input()
        tokens.extend(line.split())
        # Note: this can easily fail because it always reads the whole line

    # Cast tokens and perform assignments
    for spec, param, val in zip(specifiers, params, tokens):
        memory[param] = Number(get_type_name(spec), val)

    return len(tokens)

@definition(return_type='char', arg_types=[])
def getchar():
    import sys
    return ord(sys.stdin.read(1))


