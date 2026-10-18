using System;
using System.IO;
using System.Text;
using System.Runtime.InteropServices;

// Temporarily maps one known driver-owned DMA page READ ONLY, restores slot 31.
// No physical memory writes or privilege changes are implemented here.
class DriverMapProbe
{
    [StructLayout(LayoutKind.Sequential)] struct MemInfo { public uint Type, Index, Start, Size; }
    [DllImport("libc.so.6", SetLastError=true)] static extern int open(string path,int flags);
    [DllImport("libc.so.6", SetLastError=true)] static extern int ioctl(int fd,uint request,ref MemInfo value);
    [DllImport("libc.so.6", EntryPoint="ioctl", SetLastError=true)] static extern int ioctl_u32(int fd,uint request,ref uint value);
    [DllImport("libc.so.6", SetLastError=true)] static extern IntPtr mmap(IntPtr address,UIntPtr length,int prot,int flags,int fd,int offset);
    [DllImport("libc.so.6")] static extern int munmap(IntPtr address,UIntPtr length);
    [DllImport("libc.so.6")] static extern int close(int fd);
    static readonly string Log="/tmp/tvmod-driver-map-proof-20261017.txt";
    static readonly StringBuilder Output=new StringBuilder();
    static void Record(string line) { Output.AppendLine(line); File.WriteAllText(Log,Output.ToString()); }
    static void Require(bool ok,string error) { if(!ok) throw new Exception(error+" errno="+Marshal.GetLastWin32Error()); }
    static int Main()
    {
        int fd=-1, dma=-1; bool changed=false; IntPtr map=new IntPtr(-1);
        MemInfo original=new MemInfo {Index=31};
        try {
            fd=open("/dev/ntksys",2);Require(fd>=0,"ntksys open");
            dma=open("/dev/ntkhdma",0);Require(dma>=0,"ntkhdma open");
            Require(ioctl(fd,0xc0107302,ref original)==0,"slot query");
            Require(original.Index==31 && original.Type==0x7fffffff && original.Start==0 && original.Size==0,"slot 31 is not empty");
            uint address=0,value=0;
            Require(ioctl_u32(dma,0x80045a03,ref address)==0,"DMA address");
            Require(address>=0x80000000 && address<0x90000000 && (address&4095)==0,"unexpected DMA address");
            Require(ioctl_u32(dma,0xc0045a04,ref value)==0,"DMA word");
            Record("Original slot 31 empty; DMA physical address="+address.ToString("x8"));
            var mapping=new MemInfo {Type=0,Index=31,Start=address,Size=4096};
            Require(ioctl(fd,0xc0107301,ref mapping)==0,"mapping registration");changed=true;
            Record("Registered temporary slot 31; mapping read-only");
            map=mmap(IntPtr.Zero,new UIntPtr(4096),1,1,fd,31*4096);
            Require(map!=new IntPtr(-1),"mmap");
            uint mapped=unchecked((uint)Marshal.ReadInt32(map));
            Record("DMA ioctl word="+value.ToString("x8")+" mapped word="+mapped.ToString("x8")+" equal="+(value==mapped));
        } catch(Exception error) { Record("ERROR: "+error.Message); }
        finally {
            if(map!=new IntPtr(-1)) Record("munmap="+munmap(map,new UIntPtr(4096)));
            if(changed) {
                Record("restore_ioctl="+ioctl(fd,0xc0107301,ref original));
                var check=new MemInfo {Index=31};
                int result=ioctl(fd,0xc0107302,ref check);
                Record("restored="+(result==0 && check.Type==original.Type && check.Index==original.Index && check.Start==original.Start && check.Size==original.Size));
            }
            if(dma>=0) close(dma);if(fd>=0) close(fd);
        }
        return 0;
    }
}
