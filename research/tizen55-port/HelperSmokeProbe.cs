using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
class HelperSmokeProbe {
    [DllImport("libc")] static extern uint getuid();
    static int Main() {
        var report = new StringWriter();
        Console.SetOut(report); Console.SetError(report);
        try { Console.WriteLine("libc_uid=" + getuid()); }
        catch(Exception e) { Console.WriteLine("libc_error=" + e.Message); }
        string root = "/home/owner/share/tmp/sdk_tools/vetro55-smoke/";
        foreach(var name in new[] {"TvState","SamsungTvArchiveRoot","SamsungTvRootAgent","SamsungTvRemoteInputAgent"}) {
            try {
                var assembly = Assembly.LoadFrom(root + name + ".dll");
                var entry = assembly.EntryPoint;
                // Invalid/no arguments exercise guards, not privileged operations.
                object[] args = entry.GetParameters().Length == 0 ? null : new object[] {new string[0]};
                Console.WriteLine("helper=" + name);
                Console.WriteLine("return=" + entry.Invoke(null, args));
                if (name == "SamsungTvArchiveRoot") {
                    // A valid-shaped name reaches its capability gate. It must
                    // reject SDK context before unshare/mount or any launcher.
                    Console.WriteLine("archive_capability_gate_return=" + entry.Invoke(null,
                        new object[] {new[] {"archive-root-0000000000000000"}}));
                }
            } catch(Exception e) { Console.WriteLine(name + " error=" + e); }
        }
        File.WriteAllText("/tmp/tvmod-vetro55-helpers.txt",report.ToString());
        return 0;
    }
}
