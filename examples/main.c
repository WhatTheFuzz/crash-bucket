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

#ifdef STDIN
int main(__attribute__((unused)) int argc, __attribute__((unused)) char ** argv) {
#else
int main(int argc, char ** argv) {
#endif
    char buf[256];
    FILE  * fp;

#ifdef STDIN
    fp = stdin;
#else
    /* Check the number of arguments.*/
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    /* Open the file. */
    if ((fp = fopen(argv[1], "r")) == NULL) {
        perror("fopen");
        exit(EXIT_FAILURE);
    }
#endif

    fgets(buf, sizeof(buf)-1, fp);

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