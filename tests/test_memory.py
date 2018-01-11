import unittest
from interpreter.interpreter.memory import Memory
from interpreter.interpreter.number import Number
from interpreter.common.ctype import CType


class TestMemory(unittest.TestCase):

    def test_memory(self):
        memory = Memory()
        memory.declare_num(CType(type_spec='int'), 'a')
        memory['a'] = Number(CType(type_spec='int'), 1)
        self.assertEqual(memory['a'], Number(CType(type_spec='int'), 1))
        memory.declare_num(CType(type_spec='int'), 'b')
        memory['b'] = Number(CType(type_spec='int'), 1)
        memory['a'] = Number(CType(type_spec='int'), 1)
        self.assertEqual(memory['a'], Number(CType(type_spec='int'), 1))
        memory.declare_num(CType(type_spec='int'), 'z')
        memory['z'] = Number(CType(type_spec='int'), 1)
        memory.new_frame('main')
        memory.declare_num(CType(type_spec='int'), 'a')
        memory['a'] = Number(CType(type_spec='int'), 1)
        memory.declare_num(CType(type_spec='int'), 'b')
        memory['b'] = Number(CType(type_spec='int'), 1)
        memory['a'] = Number(CType(type_spec='int'), 1)
        self.assertEqual(memory['a'], Number(CType(type_spec='int'), 1))
        memory.new_scope()
        memory.declare_num(CType(type_spec='int'), 'a')
        memory['a'] = Number(CType(type_spec='int'), 1)
        self.assertEqual(memory['a'], Number(CType(type_spec='int'), 1))
        memory.new_frame('test')
        memory.declare_num(CType(type_spec='int'), 'a')
        memory['a'] = Number(CType(type_spec='int'), 1)
        self.assertEqual(memory['a'], Number(CType(type_spec='int'), 1))
        memory.del_frame()
        self.assertEqual(memory['a'], Number(CType(type_spec='int'), 1))
        memory.del_scope()
        self.assertEqual(memory['a'], Number(CType(type_spec='int'), 1))
        memory.del_frame()
        self.assertTrue(memory.stack.is_empty())
        
if __name__ == '__main__':
    unittest.main()