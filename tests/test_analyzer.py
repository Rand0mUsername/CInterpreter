import unittest
from interpreter.lexical_analysis.lexer import Lexer
from interpreter.syntax_analysis.parser import Parser
from interpreter.semantic_analysis.analyzer import SemanticAnalyzer, SemanticError

class SemanticAnalyzerTestCase(unittest.TestCase):

    def analyze(self, text):
        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        SemanticAnalyzer.analyze(tree)

    def test_ok(self):
        self.analyze("""
            #include <stdio.h>
            #include <math.h>
            int a, b;
            int test(int a){
            
            }
            int main(int a){
                int b;
                int c = a + b;
                double d;
                scanf("%d %d", &a, &d);
                
                if(a + 5){
                    c = 2;
                }else{
                    b = 2;
                }
                
                int r = test(a);
                printf("%d", c + 2);
                return 0;
            }
            
        """)

    def test_redefinition(self):
        with self.assertRaises(SemanticError):
            self.analyze("int main(int a) { int a = 4; }")

    def test_no_main(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                int a, b;
                int test(int a){
    
                }
            """)

    def test_redefinition_block(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                int main(){
                    int b = 3;
                    int c;
                    int b = 4;
                }
            """)

    def test_redefinition_function(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                int foo(){}
                int foo(){}
                
                int main(){
                    int b;
                }
            """)

    def test_double_param(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                int foo(int a, int b, int a) {}

                int main(){
                    int b;
                }
            """)

    def test_log_op_int(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                int main(){
                    int a = 2;
                    int b = 3;
                    int c = a ^ b;
                    float d = 4;
                    int e = c ^ d;
                }
            """)

    def test_function_inconsistencies(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                   int foo(){}
                   int main(){
                       bar();
                   }
               """)

        with self.assertRaises(SemanticError):
            self.analyze("""
                   int foo(int a, int b) {}
                   int main(){
                       foo(2, 3, 4);
                   }
               """)

        with self.assertRaises(SemanticError):
            self.analyze("""
                   int foo;
                   int main(){
                       foo();
                   }
               """)

    def test_pointers_ok(self):
        self.analyze("""
                        int main(){
                            int a;
                            int* b = &a;
                            char* c = a;
                            char* d = *b;
                            c += a;
                            c += 3;
                            c -= a;
                            c--;
                            --c;
                            ++c;
                            c++;
                            int* e = b;
                        }
                    """)

    def test_pointers(self):
        with self.assertRaises(SemanticError):
            self.analyze("""
                int main(){
                    char a;
                    char* b = a;
                }
            """)

        with self.assertRaises(SemanticError):
            self.analyze("""
                int main(){
                    int a;
                    char* b = &a;
                    int* c = b;
                }
            """)

        with self.assertRaises(SemanticError):
            self.analyze("""
                int main(){
                    int a;
                    int* b = &a;
                    char c;
                    b += c;
                }
            """)



if __name__ == '__main__':
    unittest.main()