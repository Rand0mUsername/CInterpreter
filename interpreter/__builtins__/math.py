"""
Supports basic functions and constants from math.h library.
"""

from ..common.utils import definition
import math

# Trigonometric functions

@definition(return_type='double', arg_types=['double'])
def cos(a):
    return math.cos(a)

@definition(return_type='double', arg_types=['double'])
def sin(a):
    return math.sin(a)

@definition(return_type='double', arg_types=['double'])
def tan(a):
    return math.tan(a)

@definition(return_type='double', arg_types=['double'])
def acos(a):
    return math.acos(a)

@definition(return_type='double', arg_types=['double'])
def asin(a):
    return math.asin(a)

@definition(return_type='double', arg_types=['double'])
def atan(a):
    return math.atan(a)

@definition(return_type='double', arg_types=['double'])
def atan2(a):
    return math.atan2(a)

# Hyperbolic functions

@definition(return_type='double', arg_types=['double'])
def cosh(a):
    return math.cosh(a)

@definition(return_type='double', arg_types=['double'])
def sinh(a):
    return math.sinh(a)

@definition(return_type='double', arg_types=['double'])
def tanh(a):
    return math.tanh(a)

@definition(return_type='double', arg_types=['double'])
def acosh(a):
    return math.acosh(a)

@definition(return_type='double', arg_types=['double'])
def asinh(a):
    return math.asinh(a)

@definition(return_type='double', arg_types=['double'])
def atanh(a):
    return math.atanh(a)

# Exponential and logarithmic functions

@definition(return_type='double', arg_types=['double'])
def exp(a):
    return math.exp(a)

@definition(return_type='double', arg_types=['double'])
def log(a):
    return math.log(a)

@definition(return_type='double', arg_types=['double'])
def log10(a):
    return math.log10(a)

@definition(return_type='double', arg_types=['double', 'double'])
def pow(a, b):
    return math.pow(a, b)

@definition(return_type='double', arg_types=['double'])
def sqrt(a):
    return math.sqrt(a)

# Rounding and remainder functions

@definition(return_type='double', arg_types=['double'])
def ceil(a):
    return math.ceil(a)

@definition(return_type='double', arg_types=['double'])
def floor(a):
    return math.floor(a)

@definition(return_type='double', arg_types=['double'])
def trunc(a):
    return math.trunc(a)

@definition(return_type='double', arg_types=['double'])
def round(a):
    import builtins
    return builtins.round(a)
