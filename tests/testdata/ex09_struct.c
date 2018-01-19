#include <stdio.h>
struct s {
    int a, b;
    char c;
};

int main() {
    int x = 2;
    int y;
    struct s z;
    z.a = 3;
    struct s * ptr;
    ptr = &z;
    ptr->b = 4;
    printf("%d %d %d\n", x, ptr->a, z.b);
    return 0;
}