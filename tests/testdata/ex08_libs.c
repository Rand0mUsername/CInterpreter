#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits.h>

int main() {
    printf("%d %d\n", RAND_MAX, SHRT_MIN);

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

    char s = 'D';
    putchar(s);
    putchar(s);
    putchar('\n');

    // math
    double n1 = pow(cos(0)*3, sqrt(9)); // 27.0
    double n2 = sqrt(n1); // ~5.2
    double n3 = round(n2); // 5.0
    double n4 = ceil(n3+0.1); // 6.0
    printf("%lf %lf %lf %lf\n", n1, n2, n3, n4);

    return 0;
}