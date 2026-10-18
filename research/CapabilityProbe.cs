using System;
using System.IO;
using System.Runtime.InteropServices;

class CapabilityProbe
{
    [DllImport("libc.so.6")] static extern uint getuid();
    [DllImport("libc.so.6")] static extern uint geteuid();
    static int Main(string[] args)
    {
        string output = "uid=" + getuid() + " euid=" + geteuid() + "\n";
        foreach (string line in File.ReadAllLines("/proc/self/status"))
            if (line.StartsWith("Cap") || line.StartsWith("NoNewPrivs:")) output += line + "\n";
        output += "smack=" + File.ReadAllText("/proc/self/attr/current") + "\n";
        File.WriteAllText("/tmp/tvmod-capability-proof-20261017.txt", output);
        return 0;
    }
}
