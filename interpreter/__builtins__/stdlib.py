"""
Supports basic functions from stdlib.h library.
"""

import random
from ..common.utils import definition

RAND_MAX = 32767
NULL = 0

@definition(return_type='int', arg_types=None)
def rand():
    return random.randint(0, RAND_MAX)


@definition(return_type='int', arg_types=['unsigned int'])
def srand(seed):
    random.seed(seed)


@definition(return_type='int', arg_types=['int'])
def abs(num):
    if num < 0:
        return -num
    return num

# TODO: maybe memory as a singleton after all
# add arg type checking later

@definition(return_type='int', arg_types=['int'])
def malloc(*args):
    sz, memory = args
    address = memory.allocate(sz)
    memory.dyn_alloc_addr.add(address)
    return address

@definition(return_type=None, arg_types=None)
def free(*args):
    address, memory = args
    # if allocated kill it
    if address in memory.dyn_alloc_addr:
        memory.dyn_alloc_addr.remove(address)
        del memory.raw_memory[address]
    else:
        raise RuntimeError("Can't free memory that was not dynamically allocated")


