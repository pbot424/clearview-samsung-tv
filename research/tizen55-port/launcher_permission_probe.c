/* Permission-only probe for Samsung's optional profiling hook. No root action. */
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

static void report(void) {
    int out = open("/tmp/tvmod-vetro55-native.txt", O_WRONLY|O_CREAT|O_EXCL, 0600);
    if (out < 0) return;
    char header[100];
    int length = snprintf(header, sizeof(header), "uid=%u euid=%u pid=%u\n", getuid(), geteuid(), getpid());
    if (length > 0) write(out, header, length);
    int in = open("/proc/self/status", O_RDONLY);
    char buffer[4096];
    if (in >= 0) {
        int count = read(in, buffer, sizeof(buffer));
        if (count > 0) write(out, buffer, count);
        close(in);
    }
    close(out);
}

__attribute__((constructor)) static void loaded(void) { report(); }
__attribute__((visibility("default"))) int dotnet_launcher_inject(void) { report(); return 0; }
