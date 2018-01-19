#include <stdio.h>
#include <stdlib.h>

int main() {
    int a = 4;
    int* b = &a;
    int* c = &b;
    printf("%d!\n", *&a); // 4
    printf("%d!\n", **&b); // 4
    return 0;
}