#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main() {
    int xx = sqrt(4);
    srand(4);
    int a = rand();
    int b = rand();
    int c = -123;
    printf("%d %d %d %d\n", a, b, c, abs(c));

    int* ptr = malloc(4);
    int* x = ptr;
    *x = 4;
    printf("%d %d %d %d\n", &x, &ptr, *x, *ptr);

    free(x);
    // free(x); // RTE
    // free(123); // RTE
    return 0;
}