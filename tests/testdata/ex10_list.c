#include <stdio.h>
#include <stdlib.h>

struct node {
    int val;
    struct node* next;
};

int main() {
    struct node n1, n2, n3, n4, n5;
    n1.val = 1; n2.val = 2; n3.val = 3; n4.val = 4; n5.val = 5;
    n2.next = &n4;
    n4.next = &n1;
    n1.next = &n5;
    n5.next = &n3;
    n3.next = NULL;
    struct node* curr = &n2;
    while(curr != NULL) {
        printf("%d\n", curr->val);
        curr = curr->next;
    }
    return 0;
}