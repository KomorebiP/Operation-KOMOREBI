/* Compatibility adapter for Lean's executable self-location in this runtime.
 * Only the current process's numeric exe link is mapped to /proc/self/exe.
 * Other paths, permissions, and all Lean proof checking remain untouched. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
ssize_t readlink(const char *path, char *buf, size_t size) {
    ssize_t (*actual)(const char *,char *,size_t) = dlsym(RTLD_NEXT, "readlink");
    char own[64];
    snprintf(own, sizeof(own), "/proc/%d/exe", (int)getpid());
    return actual(strcmp(path, own) == 0 ? "/proc/self/exe" : path, buf, size);
}
