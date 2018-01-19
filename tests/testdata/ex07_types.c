#include <stdio.h>

int main() {
    char a = 1;
    int i;
    for(i = 0; i < 1000; i++) {
        a++;
        if(a%10 == 0) {
            printf("%d ", a);
        }
    }
    printf("\n");
    char b = 255; // -1
    unsigned char c = 255; // 255
    printf("%d %d\n", b, c);
    long long int d = 1;
    char deg = 0;
    while(d > 0) {
        deg++;
        d *= 2;
    }
    printf("%d", deg);
    return 0;
}