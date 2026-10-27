#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

/* Host compatibility only: numbered /proc/<self-pid>/exe is absent in this
   execution namespace, while /proc/self/exe resolves correctly. Redirect only
   that one pathname. Every other readlink call uses libc unchanged. */
ssize_t readlink(const char *path, char *buf, size_t bufsiz) {
    static ssize_t (*original)(const char *, char *, size_t) = NULL;
    if (!original) original = dlsym(RTLD_NEXT, "readlink");
    if (!original) { errno = ENOSYS; return -1; }
    char expected[64];
    snprintf(expected, sizeof(expected), "/proc/%ld/exe", (long)getpid());
    return original(strcmp(path, expected) == 0 ? "/proc/self/exe" : path, buf, bufsiz);
}
