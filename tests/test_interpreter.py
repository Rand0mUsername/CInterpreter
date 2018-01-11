import unittest
import os
from interpreter.interpreter.interpreter import Interpreter

class InterpreterTestCase(unittest.TestCase):
    def interpret(self, text):
        return Interpreter.run(text)

    def test_files(self):
        to_test = 'ex8_stdlib.c'
        for filename in os.listdir('./testdata'):
            # temporary fix to test only one files
            if to_test is not None and filename != to_test:
                continue
            # open the file, read the source and test
            with open(os.path.join('./testdata', filename), 'r') as file:
                print(">>>>> Running " + filename + ":")
                code = file.read()
                self.assertEqual(self.interpret(code), 0)
                print(">>>>> " + filename + " finished running.")
                print()


if __name__ == '__main__':
    unittest.main()
