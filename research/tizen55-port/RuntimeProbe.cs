using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Diagnostics;
class RuntimeProbe {
    [DllImport("libc.so.6")] static extern uint getuid();
    [DllImport("libc.so.6")] static extern uint geteuid();
    [DllImport("/home/owner/share/tmp/sdk_tools/heaptrack/libheaptrack_inject.so")]
    static extern int dotnet_launcher_inject();
    static int Main(string[] args) {
        var output = "uid=" + getuid() + " euid=" + geteuid() + "\n";
        output += "runtime=" + Environment.Version + "\n";
        foreach (var line in File.ReadAllLines("/proc/self/status"))
            if (line.StartsWith("Cap") || line.StartsWith("NoNewPrivs:")) output += line + "\n";
        output += "smack=" + File.ReadAllText("/proc/self/attr/current") + "\n";
        var start = new ProcessStartInfo("/bin/true");
        start.ArgumentList.Add("probe-only-no-process-launched");
        using (var hmac = new HMACSHA256(new byte[32]))
            output += "hmac_bytes=" + hmac.ComputeHash(new byte[0]).Length + "\n";
        if (args.Length == 1 && args[0] == "loadnative") {
            try { output += "native_result=" + dotnet_launcher_inject() + "\n"; }
            catch (Exception e) { output += "native_error=" + e + "\n"; }
        }
        File.WriteAllText("/tmp/tvmod-vetro55-runtime.txt", output);
        return 0;
    }
}
