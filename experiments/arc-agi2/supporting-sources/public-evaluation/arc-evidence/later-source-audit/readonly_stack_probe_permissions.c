#define _GNU_SOURCE
#include <sys/uio.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Feasibility only: an invalid remote address prevents reading any contents.
 * The caller must reverify the target's host PID and scan-parent relationship.
 * Never substitute a nested namespace PID.  This program writes no target
 * memory, sends no signals, and performs no ptrace/debugger operation. */
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    char *end = NULL;
    long value = strtol(argv[1], &end, 10);
    if (!end || *end || value <= 0) return 2;
    char byte = 0;
    struct iovec local = { .iov_base = &byte, .iov_len = 1 };
    struct iovec remote = { .iov_base = NULL, .iov_len = 1 };
    errno = 0;
    ssize_t result = process_vm_readv((pid_t)value, &local, 1, &remote, 1, 0);
    int error = errno;
    /* Intentionally do not print the local byte, even if a null mapping exists. */
    printf("{\"self_namespace_pid\":%ld,\"verified_host_target_pid\":%ld,"
           "\"remote_address\":\"NULL\",\"requested_bytes\":1,"
           "\"result\":%ld,\"errno\":%d,\"error\":\"%s\","
           "\"memory_contents_emitted\":false}\n",
           (long)getpid(), value, (long)result, error, strerror(error));
    return 0;
}
