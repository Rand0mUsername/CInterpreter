#include <stdio.h>

int main(){
    char d;
    char a='0', b='0', c='0';

    while((d = getchar()) != '\n'){
        if(d >= '0' && d <= '9'){
            a = b;
            b = c;
            c = d;
        }
    }
    printf("%c%c%c\n", a, b, c);
    return 0;
}
