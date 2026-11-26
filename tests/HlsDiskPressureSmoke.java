package org.opensagetv.webplayer;

import java.io.*;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** Production monitor, real FFmpeg and real private tmpfs; no server or mocks. */
public final class HlsDiskPressureSmoke {
    static final long MIB=1024L*1024L;
    static final List<Process> owned=new ArrayList<Process>();
    static Method monitor,stderr;
    static int checks;
    static void check(boolean okay,String message){if(!okay)throw new AssertionError(message);checks++;}
    static void fill(Path file,long bytes)throws Exception{
        byte[] block=new byte[1024*1024];
        try(OutputStream out=Files.newOutputStream(file,StandardOpenOption.CREATE_NEW)){
            for(long n=0;n<bytes;){int count=(int)Math.min(block.length,bytes-n);out.write(block,0,count);n+=count;}
        }
    }
    static HlsSessionManager.Session launch(Path root,int seconds)throws Exception{
        Path dir=Files.createTempDirectory(root,"producer-");
        HlsSessionManager.Session s=new HlsSessionManager.Session(UUID.randomUUID().toString().replace("-",""),1,0,0,0,seconds*1000,false,dir.toFile());
        Process p=new ProcessBuilder("/usr/bin/ffmpeg","-hide_banner","-loglevel","warning","-nostdin","-re",
            "-f","lavfi","-i","testsrc2=size=160x90:rate=10","-t",String.valueOf(seconds),
            "-c:v","libx264","-preset","ultrafast","-threads","1","-g","10","-pix_fmt","yuv420p",
            "-f","hls","-hls_time","1","-hls_list_size","0","-hls_flags","temp_file",
            "-hls_segment_filename",dir.resolve("seg_%05d.ts").toString(),dir.resolve("stream.m3u8").toString())
            .redirectOutput(new File("/dev/null")).start();
        owned.add(p);s.process=p;s.running=true;s.launchedAt=System.currentTimeMillis();
        stderr.invoke(null,s);monitor.invoke(null,s,null,null,false);
        long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(12);
        while(s.segments==0&&p.isAlive()&&System.nanoTime()<end)Thread.sleep(30);
        check(s.segments>0&&p.isAlive(),"Healthy real HLS producer must publish before pressure: "+s.stderrTail);
        return s;
    }
    static long stopped(HlsSessionManager.Session s,Process p,String reason,Process unrelated)throws Exception{
        long start=System.nanoTime(),end=start+TimeUnit.SECONDS.toNanos(6);
        while((s.running||p.isAlive()||s.process!=null)&&System.nanoTime()<end)Thread.sleep(20);
        long elapsed=TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-start);
        check(s.stopRequested&&s.error.contains(reason),"Explicit resource error: "+s.error);
        check(!s.running&&!p.isAlive()&&s.process==null&&!s.processStopIncomplete,"Exact owned producer retires");
        s.monitorThread.join(1500);s.stderrThread.join(1500);
        check(!s.monitorThread.isAlive()&&!s.stderrThread.isAlive(),"No orphan monitor or stderr reader");
        check(elapsed<6000,"Bounded resource retirement");
        check(unrelated.isAlive(),"Unrelated owned sentinel survives resource stop");
        return elapsed;
    }
    public static void main(String[] args)throws Exception{
        if(args.length!=1||!args[0].equals("/scratch"))throw new IllegalArgumentException("Private /scratch mount only");
        Path root=Paths.get(args[0]).toRealPath();FileStore store=Files.getFileStore(root);
        check(root.toString().equals("/scratch")&&store.type().equals("tmpfs"),"Refuse real disk or unexpected scratch path");
        check(store.getTotalSpace()>=180*MIB&&store.getTotalSpace()<=200*MIB,"Only bounded192MiB private tmpfs");
        check(root.toFile().getUsableSpace()>180*MIB,"Require unused private mount");
        check(OwnedProcessControlBridge.available(),"Actual optional FFmpeg process provider required");
        monitor=HlsSessionManager.class.getDeclaredMethod("startMonitor",HlsSessionManager.Session.class,SageApiBridge.class,Object.class,boolean.class);
        stderr=HlsSessionManager.class.getDeclaredMethod("startStderrReader",HlsSessionManager.Session.class);
        monitor.setAccessible(true);stderr.setAccessible(true);
        Process unrelated=new ProcessBuilder("/bin/sleep","65").start();owned.add(unrelated);
        try{
            HlsSessionManager.Session low=launch(root,60);Process lowProcess=low.process;
            long freeBefore=root.toFile().getUsableSpace();Path pressure=root.resolve("owned-pressure.bin");fill(pressure,96*MIB);
            long freeDuring=root.toFile().getUsableSpace();
            check(freeBefore>128*MIB&&freeDuring<128*MIB,"Actual filesystem crosses production free-space threshold");
            long lowStop=stopped(low,lowProcess,"protect server disk space",unrelated);
            Files.delete(pressure);
            check(root.toFile().getUsableSpace()>180*MIB,"Releasing exact pressure file restores private capacity");
            System.setProperty("sagetv.webplayer.streamMaxBytes",String.valueOf(64*MIB));
            HlsSessionManager.Session quota=launch(root,60);Process quotaProcess=quota.process;
            Path extra=quota.directory.toPath().resolve("captions.bin");fill(extra,64*MIB+1);
            long quotaStop=stopped(quota,quotaProcess,"Session output limit reached",unrelated);
            Files.delete(extra);System.clearProperty("sagetv.webplayer.streamMaxBytes");
            HlsSessionManager.Session healthy=launch(root,4);Process healthyProcess=healthy.process;
            check(healthyProcess.waitFor(9,TimeUnit.SECONDS),"Recovered producer reaches natural end");
            healthy.monitorThread.join(2000);healthy.stderrThread.join(2000);
            check(healthyProcess.exitValue()==0&&!healthy.running&&healthy.endList&&healthy.error.isEmpty(),"Healthy successor completes after test pressure is released");
            check(unrelated.isAlive(),"Recovery never kills unrelated process");
            System.out.println("{\"passed\":true,\"checks\":"+checks+",\"realPrivateTmpfs\":true,\"realFfmpeg\":true,\"freeBefore\":"+freeBefore+",\"freeDuring\":"+freeDuring+",\"lowSpaceStopMs\":"+lowStop+",\"outputLimitStopMs\":"+quotaStop+",\"physicalBrowser\":false,\"serverMutation\":false}");
        }finally{
            System.clearProperty("sagetv.webplayer.streamMaxBytes");
            for(Process p:owned)if(p.isAlive()){
                check(OwnedProcessControlBridge.stop(p,2000),"Exact disposable child cleanup");
                p.waitFor(2,TimeUnit.SECONDS);
            }
        }
    }
}
