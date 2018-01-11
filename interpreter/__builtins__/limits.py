"""
Supports basic functions and constants from limits.h library.
"""
from interpreter.common.ctype import CType

CHAR_BIT = CType.from_string('char').size_bytes()
SCHAR_MIN = CType.from_string('signed char').limits()[0]
SCHAR_MAX = CType.from_string('signed char').limits()[1]
UCHAR_MAX = CType.from_string('unsigned char').limits()[1]
CHAR_MIN = CType.from_string('char').limits()[0]
CHAR_MAX = CType.from_string('char').limits()[1]
SHRT_MIN = CType.from_string('short int').limits()[0]
SHRT_MAX = CType.from_string('short int').limits()[1]
USHRT_MAX = CType.from_string('unsigned short int').limits()[1]
INT_MIN = CType.from_string('int').limits()[0]
INT_MAX = CType.from_string('int').limits()[1]
UINT_MAX = CType.from_string('unsigned int').limits()[1]
LONG_MIN = CType.from_string('long int').limits()[0]
LONG_MAX = CType.from_string('long int').limits()[1]
ULONG_MAX = CType.from_string('unsigned long int').limits()[1]
LLONG_MIN = CType.from_string('long long int').limits()[0]
LLONG_MAX = CType.from_string('long long int').limits()[1]
ULLONG_MAX = CType.from_string('unsigned long long int').limits()[1]