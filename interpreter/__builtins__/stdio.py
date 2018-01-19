"""
Supports basic functions and constants from stdio.h library.
"""

from ..common.utils import definition
from ..interpreter.number import Number
from ..common.ctype import CType


import re
import sys

@definition(return_type='int', arg_types=None)
def printf(*args):
    fmt, *params = args
    message = fmt % tuple([param for param in params])
    result = len(message)
    print(message, end='')
    return result

@definition(return_type='int', arg_types=None)
def scanf(*args):
    def get_type_name(flag):
        """ Takes a type specifier and returns the type name. """
        if flag[-1] == 'd':
            return 'int'
        elif flag[-1] == 'f':
            return 'float'
        elif flag[-1] == 'c':
            return 'char'
        raise Exception('\'{}\' not supported as a printf type specifier'.format(flag))

    # unpack args: format string, addresses, memory
    fmt, *addresses, memory = args

    # Extract type specifiers from the format string
    fmt = re.sub(r'\s+', '', fmt)  # Remove whitespace
    specifiers = re.findall('%[^%]*[dfic]', fmt)
    if len(specifiers) != len(addresses):
        raise Exception('Format of scanf function takes {} positional arguments but {} were given'.format(
            len(specifiers),
            len(addresses)
        ))

    # Scan the appropriate number of tokens
    tokens = []
    while len(tokens) < len(specifiers):
        line = input()
        tokens.extend(line.split())
        # Note: this can easily fail because it always reads the whole line

    # Cast tokens and perform assignments
    for spec, address, val in zip(specifiers, addresses, tokens):
        memory.set_at_address(address, Number(CType.from_string(get_type_name(spec)), val))

    return len(tokens)

@definition(return_type='char', arg_types=[])
def getchar():
    return ord(sys.stdin.read(1))


@definition(return_type='char', arg_types=['char'])
def putchar(ch):
    try:
        sys.stdout.write(chr(ch))
        return ch
    except UnicodeEncodeError:
        return 0




