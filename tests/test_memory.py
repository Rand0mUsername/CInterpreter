import unittest
from interpreter.interpreter.memory import Memory
from interpreter.interpreter.types import Number, Pointer


class TestMemory(unittest.TestCase):

    def test_memory(self):
        memory = Memory()
        memory.declare('int', 'a')
        memory['a'] = Number('int', 1)
        self.assertEqual(memory['a'], Number('int', 1))
        memory.declare('int', 'b')
        memory['b'] = Number('int', 1)
        memory['a'] = Number('int', 1)
        self.assertEqual(memory['a'], Number('int', 1))
        memory.declare('int', 'z')
        memory['z'] = Number('int', 1)
        memory.new_frame('main')
        memory.declare('int', 'a')
        memory['a'] = Number('int', 1)
        memory.declare('int', 'b')
        memory['b'] = Number('int', 1)
        memory['a'] = Number('int', 1)
        self.assertEqual(memory['a'], Number('int', 1))
        memory.new_scope()
        memory.declare('int', 'a')
        memory['a'] = Number('int', 1)
        self.assertEqual(memory['a'], Number('int', 1))
        memory.new_frame('test')
        memory.declare('int', 'a')
        memory['a'] = Number('int', 1)
        self.assertEqual(memory['a'], Number('int', 1))
        memory.del_frame()
        self.assertEqual(memory['a'], Number('int', 1))
        memory.del_scope()
        self.assertEqual(memory['a'], Number('int', 1))
        memory.del_frame()
        self.assertTrue(memory.stack.is_empty())

    def test_pointers(self):
        memory = Memory()
        memory.declare('int', 'a')
        memory.declare('double*', 'b')
        memory['a'] = Number('int', 1)
        memory['b'] = memory['b'].from_number(Number('int', memory.get_address('a')))
        self.assertEqual(memory['b'], Pointer('double*', memory.get_address('a')))
        old_b = memory['b']
        memory['b'] += Number('int', 1)
        self.assertEqual(memory['b'].address-old_b.address, 8)


if __name__ == '__main__':
    unittest.main()