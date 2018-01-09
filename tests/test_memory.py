import unittest
from interpreter.interpreter.memory import Memory


class TestMemory(unittest.TestCase):

    def test_memory(self):
        memory = Memory()
        memory.declare('int', 'a')
        memory['a'] = 1
        self.assertEqual(memory['a'], 1)
        memory.declare('int', 'b')
        memory['b'] = 2
        memory['a'] = 3
        self.assertEqual(memory['a'], 3)
        memory.declare('int', 'z')
        memory['z'] = 3
        memory.new_frame('main')
        memory.declare('int', 'a')
        memory['a'] = 1
        memory.declare('int', 'b')
        memory['b'] = 2
        memory['a'] = 6
        self.assertEqual(memory['a'], 6)
        memory.new_scope()
        memory.declare('int', 'a')
        memory['a'] = 2
        self.assertEqual(memory['a'], 2)
        memory.new_frame('test')
        memory.declare('int', 'a')
        memory['a'] = 4
        self.assertEqual(memory['a'], 4)
        memory.del_frame()
        self.assertEqual(memory['a'], 2)
        memory.del_scope()
        self.assertEqual(memory['a'], 6)
        memory.del_frame()
        self.assertTrue(memory.stack.is_empty())


if __name__ == '__main__':
    unittest.main()