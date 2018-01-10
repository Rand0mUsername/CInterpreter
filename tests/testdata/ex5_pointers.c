#include <stdio.h>

int main(){
    int i = 2;
    printf("%d\n", i);  // 2
    int* ptr = &i;
    int* other = ptr;
    printf("%d %d %d\n", i, *ptr, *other); // 2 2 2
    i++;
    printf("%d %d %d\n", i, *ptr, *other); // 3 3 3
    *ptr = 7;
    printf("%d %d %d\n", i, *ptr, *other); // 7 7 7
    *other += *ptr / 2;
    printf("%d %d %d\n", i, *ptr, *other); // 10 10 10
    (*ptr)--;
    --(*ptr);
    printf("%d %d %d\n", i, *ptr, *other); // 8 8 8
    *ptr++;  // after this ptr points to itself
    int j = (((*ptr)));
    printf("%d %d %d %d\n", i, j, *ptr, *other); // 8 ..32 ..32 8
    return 0;
}