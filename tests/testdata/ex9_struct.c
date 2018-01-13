#include <stdio.h>
struct S {
    int a, b;
    char c;
};

int main() {
    int a = 2;
    int b = 3;
    struct S z;
    z.a = 4;
    z.b = b;
    printf("%d %d\n", a+z.a, b*z.b); // 6 9
    return 0;
}