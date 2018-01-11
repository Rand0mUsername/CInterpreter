#include <stdio.h>

int main() {
    int i, j = 0;
    for(i=0; i<5; i++) {
        j += i;
        if (j == 6) {
          break;
        }
    }
    printf("%d %d\n", i, j); // 3 6
    i = 0;
    while(i < 10) {
        ++i;
        if (i >= 5) {
             continue;
        }
        j += i;
    }
    printf("%d %d\n", i, j); // 10 16

    // nested
    i, j = 0;
    int k;
    int t = 0;
    for(i=1; i<=55; i++) {
        if (i == 6) {
          break;
        }
        k = 0;
        while (k < 3) {
            j++;
            k++;
            t++;
            if (k == i) {
                break;
            }
        }
        j += i/2;
    }
    printf("%d %d %d %d\n", i, j, k, t); // 6 18 3 12

    // switch
    int c = 3;
    switch (c+1) {
        case 1:
             printf("1!");
             break;
        case 2+2:
             printf("4!");
        case 5:
             printf("Fallthrough!");
             break;
        default:
             printf("Default");
    } // 4!Fallthrough!
    return 0;
}