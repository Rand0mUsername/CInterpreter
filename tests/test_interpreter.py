import unittest
import os
from interpreter.interpreter.interpreter import Interpreter

class InterpreterTestCase(unittest.TestCase):
    def interpret(self, text):
        return Interpreter.run(text)

    def test_helloworld(self):
        self.interpret("""
        #include <stdio.h>

        int main(){
            printf("Hello World!");
            return 0;
        }

        """)

    def test_files(self):
        for filename in os.listdir('./testdata'):
            with open(os.path.join('./testdata', filename), 'r') as file:
                print(">>>>> Running " + filename + ":")
                code = file.read()
                self.assertEqual(self.interpret(code), 0)
                print(">>>>> " + filename + " finished running with exit code 0.")
                print()


if __name__ == '__main__':
    unittest.main()
