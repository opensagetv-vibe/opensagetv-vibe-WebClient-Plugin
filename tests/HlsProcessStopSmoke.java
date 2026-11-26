package org.opensagetv.webplayer;

import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.opensagetv.vibe.ffmpeg.OwnedProcessControl;

/** Real HLS owner stop plus deterministic incomplete-stop admission refusal. */
public final class HlsProcessStopSmoke {
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
    private static final class Refuses extends Process {
        volatile boolean alive=true;
        public OutputStream getOutputStream(){return new ByteArrayOutputStream();}
        public InputStream getInputStream(){return new ByteArrayInputStream(new byte[0]);}
        public InputStream getErrorStream(){return getInputStream();}
        public int waitFor(){return 0;}
        public boolean waitFor(long time,TimeUnit unit){return !alive;}
        public int exitValue(){if(alive)throw new IllegalThreadStateException();return 0;}
        public void destroy(){throw new AssertionError("unsafe Process.destroy called");}
        public boolean isAlive(){return alive;}
    }
    @SuppressWarnings("unchecked") public static void main(String[] args)throws Exception{
        Path root=Files.createTempDirectory("web097-owner-stop-");
        Field field=HlsSessionManager.class.getDeclaredField("SESSIONS");field.setAccessible(true);
        Map<String,HlsSessionManager.Session> registry=(Map<String,HlsSessionManager.Session>)field.get(null);
        HlsSessionManager.Session normal=new HlsSessionManager.Session(UUID.randomUUID().toString().replace("-",""),1,0,0,0,0,false,root.toFile());
        HlsSessionManager.Session bad=new HlsSessionManager.Session(UUID.randomUUID().toString().replace("-",""),2,0,0,0,0,false,root.toFile());
        final Process owned=new ProcessBuilder("/bin/sh","-c","dd if=/dev/zero bs=32768 count=4096 2>/dev/null & wait").start();
        Process other=new ProcessBuilder("/bin/sh","-c","exec sleep 30").start();
        Refuses refuses=new Refuses();
        Thread writer=new Thread(()->{byte[] b=new byte[32768];try{for(int i=0;i<512;i++)owned.getOutputStream().write(b);}catch(IOException expected){}});
        writer.setDaemon(true);writer.start();normal.process=owned;normal.feederThread=writer;normal.running=true;
        registry.put(normal.id,normal);registry.put(bad.id,bad);
        try{
            Thread.sleep(250);check(writer.isAlive(),"actual input writer blocked");
            long start=System.nanoTime();check(HlsSessionManager.stop(normal.id),"public HLS stop accepted");
            writer.join(1000);check(!writer.isAlive()&&!owned.isAlive(),"owned tree/writer retired");
            check(System.nanoTime()-start<3000000000L,"public HLS stop bounded");
            check(normal.process==null&&!normal.running&&normal.cleanupQueued&&!normal.processStopIncomplete,"verified owner retired");
            check(other.isAlive(),"unrelated process preserved");
            bad.process=refuses;bad.running=true;
            try{HlsSessionManager.stop(bad.id);throw new AssertionError("failed stop reported success");}
            catch(IllegalStateException expected){}
            check(bad.process==refuses&&bad.processStopIncomplete&&!bad.cleanupQueued,"failed stop retains exact Process/session");
            Method admission=HlsSessionManager.class.getDeclaredMethod("requireOwnedProcessControl",HlsSessionManager.Session.class);admission.setAccessible(true);
            try{admission.invoke(null,normal);throw new AssertionError("overlapping replacement admitted");}
            catch(InvocationTargetException expected){check(expected.getCause()instanceof IOException,"explicit failed admission");}
            check(other.isAlive(),"admission refusal does not stop existing unrelated playback");
            refuses.alive=false;Thread.sleep(50);check(HlsSessionManager.stop(bad.id),"later verified stop can retire owner");
            check(bad.process==null&&!bad.processStopIncomplete&&bad.cleanupQueued,"no stuck cleanup flag after real retirement");
            System.out.println("PASS HLS blocked-duplex stop, ownership retention, admission fence, unrelated preservation and verified retry");
        }finally{
            registry.remove(normal.id);registry.remove(bad.id);refuses.alive=false;
            OwnedProcessControl.terminate(owned);OwnedProcessControl.terminate(other);
            owned.waitFor(2,TimeUnit.SECONDS);other.waitFor(2,TimeUnit.SECONDS);
            Files.deleteIfExists(root);
        }
    }
}
