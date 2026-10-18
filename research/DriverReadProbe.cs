using System;
using System.IO;
using System.Text;
using System.Runtime.InteropServices;

class DriverReadProbe
{
    [StructLayout(LayoutKind.Sequential)] struct MemInfo { public uint Type, Index, Start, Size; }
    [DllImport("libc.so.6", SetLastError=true)] static extern int open(string path, int flags);
    [DllImport("libc.so.6", SetLastError=true)] static extern int ioctl(int fd, uint request, ref MemInfo value);
    [DllImport("libc.so.6", EntryPoint="ioctl", SetLastError=true)] static extern int ioctl_u32(int fd, uint request, ref uint value);
    [DllImport("libc.so.6")] static extern int close(int fd);
    static int Main()
    {
        var output = new StringBuilder();
        int fd = open("/dev/ntksys", 0);
        output.AppendLine("ntksys open="+fd+" errno="+Marshal.GetLastWin32Error());
        if (fd >= 0) {
            for(uint i=0;i<32;i++) {
                var info = new MemInfo {Type=0x7fffffff, Index=i};
                int result=ioctl(fd,0xc0107302,ref info);
                output.AppendLine(String.Format("GET_MEM_INFO index={0} result={1} errno={2} type={3:x8} start={4:x8} size={5:x8}",i,result,Marshal.GetLastWin32Error(),info.Type,info.Start,info.Size));
                if(result != 0) break;
            }
            close(fd);
        }
        fd=open("/dev/ntkhdma",0);
        output.AppendLine("ntkhdma open="+fd+" errno="+Marshal.GetLastWin32Error());
        if(fd>=0) {
            uint address=0;
            int result=ioctl_u32(fd,0x80045a03,ref address);
            output.AppendLine(String.Format("GET_BUFF_ADDR result={0} errno={1} address={2:x8}",result,Marshal.GetLastWin32Error(),address));
            close(fd);
        }
        File.WriteAllText("/tmp/tvmod-driver-read-proof-20261017.txt",output.ToString());
        return 0;
    }
}
