using System;
using System.IO;
using System.Text;
using System.Runtime.InteropServices;

// A single driver-owned DMA page, read-only. Never writes physical memory.
class DriverProbe {
    [StructLayout(LayoutKind.Sequential)] struct MemInfo { public uint Type, Index, Start, Size; }
    [DllImport("libc.so.6", SetLastError=true)] static extern int open(string p, int flags);
    [DllImport("libc.so.6", SetLastError=true)] static extern int ioctl(int fd,uint req,ref MemInfo info);
    [DllImport("libc.so.6", EntryPoint="ioctl", SetLastError=true)] static extern int ioctl_u32(int fd,uint req,ref uint info);
    [DllImport("libc.so.6", SetLastError=true)] static extern IntPtr syscall(uint nr, uint addr,uint size,uint prot,uint flags,int fd,uint pgoff);
    [DllImport("libc.so.6")] static extern int munmap(IntPtr addr,UIntPtr length);
    [DllImport("libc.so.6")] static extern int close(int fd);
    static StringBuilder log = new StringBuilder();
    static void Record(string s) { log.AppendLine(s); File.WriteAllText("/tmp/tvmod-vetro55-driver.txt",log.ToString()); }
    static bool Same(MemInfo a,MemInfo b) { return a.Type==b.Type && a.Index==b.Index && a.Start==b.Start && a.Size==b.Size; }
    static void Require(bool ok,string s) { if(!ok) throw new Exception(s+" errno="+Marshal.GetLastWin32Error()); }
    static int Main() {
        int fd=-1,dma=-1; bool changed=false; IntPtr map=new IntPtr(-1);
        MemInfo original=new MemInfo {Index=31};
        try {
            fd=open("/dev/ntksys",2); Require(fd>=0,"open ntksys");
            Require(ioctl(fd,0xc0107302,ref original)==0,"read slot");
            Require(original.Type==0x7fffffff && original.Index==31 && original.Start==0 && original.Size==0,"slot not empty");
            dma=open("/dev/ntkhdma",0); Require(dma>=0,"open DMA");
            uint address=0,word=0;
            Require(ioctl_u32(dma,0x80045a03,ref address)==0,"DMA address");
            Require(address>=0x80000000 && address<0x90000000 && (address&4095)==0,"unexpected DMA address");
            Require(ioctl_u32(dma,0xc0045a04,ref word)==0,"DMA word");
            var temporary=new MemInfo {Type=0,Index=31,Start=address,Size=4096};
            Require(ioctl(fd,0xc0107301,ref temporary)==0,"set slot"); changed=true;
            var readback=new MemInfo {Index=31};
            Require(ioctl(fd,0xc0107302,ref readback)==0 && Same(temporary,readback),"slot readback");
            Record("slot_readback=True; mmap2 pgoff=31; prot=READ; size=4096");
            map=syscall(192,0,4096,1,1,fd,31);
            Require(map!=new IntPtr(-1),"raw mmap2");
            Record("read_matches_dma="+(unchecked((uint)Marshal.ReadInt32(map))==word));
        } catch(Exception error) { Record("ERROR: "+error.Message); }
        finally {
            if(map!=new IntPtr(-1)) Record("munmap="+munmap(map,new UIntPtr(4096)));
            if(changed) {
                int restore=ioctl(fd,0xc0107301,ref original);
                var check=new MemInfo {Index=31};
                int result=ioctl(fd,0xc0107302,ref check);
                Record("restore_ioctl="+restore+"; restored="+(result==0 && Same(original,check)));
            }
            if(dma>=0) close(dma); if(fd>=0) close(fd);
        }
        return 0;
    }
}
