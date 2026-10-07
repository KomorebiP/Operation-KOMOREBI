#define _GNU_SOURCE
#include <unistd.h>
#include <dlfcn.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
/* Supply a configured executable path without reading process metadata.
   All other readlink calls use libc unchanged. No proof code is modified. */
ssize_t readlink(const char *path, char *buf, size_t size) {
    char own[80];
    snprintf(own, sizeof own, "/proc/%d/exe", (int)getpid());
    const char *configured = getenv("PRSC_RUNTIME_EXECUTABLE");
    if (configured && strcmp(path, own) == 0) {
        size_t n = strlen(configured);
        if (n > size) n = size;
        memcpy(buf, configured, n);
        return n;
    }
    ssize_t (*original)(const char *, char *, size_t) = dlsym(RTLD_NEXT, "readlink");
    return original(path, buf, size);
}
