/* Host compatibility for Lean's own executable-path lookup.
 * Redirect only /proc/<calling process PID>/exe to /proc/self/exe.
 * No other path is changed. This does not edit compiler or proof bytes.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

ssize_t readlink(const char *path, char *buffer, size_t size) {
    static ssize_t (*original)(const char *, char *, size_t);
    if (!original)
        original = dlsym(RTLD_NEXT, "readlink");
    char own_path[64];
    snprintf(own_path, sizeof(own_path), "/proc/%d/exe", (int)getpid());
    return original(strcmp(path, own_path) == 0 ? "/proc/self/exe" : path,
                    buffer, size);
}
