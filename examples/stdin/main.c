/* Compile with:
** clang -glldb -Og -fno-omit-frame-pointer -fno-inline-functions main.c -o main
*/

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdnoreturn.h>

int a(void);
int b(void);
int c(void);
int d(void);

int a(void) {
    puts("Called a.");
    return 0;
}

int b(void) {
    puts("Called b.");
    return 0;
}

int c(void) {
    puts("Called c.");
    return 0;
}

noreturn int d(void) {
    abort();
}

int main(int argc, char ** argv) {

    /* Read from stdin. */
    char buf[256];
    fgets(buf, sizeof(buf)-1, stdin);

    /* Check what the buffer starts with. */
    if (strchr(buf, 'a') != NULL){
        a();
    }
    if (strchr(buf, 'b') != NULL){
        b();
    }
    if (strchr(buf, 'c') != NULL){
        c();
    }
    if (strchr(buf, 'd') != NULL){
        d();
    }
}