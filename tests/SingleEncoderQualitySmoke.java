package org.opensagetv.webplayer;

import java.io.*;
import java.util.concurrent.TimeUnit;

/** WEB-052 single-producer custody, without FFmpeg or a SageTV JVM. */
public final class SingleEncoderQualitySmoke {
    static final class Producer extends Process {
        boolean alive=true;
        final boolean ignoresStop;
        Producer(boolean ignoresStop){this.ignoresStop=ignoresStop;}
        public OutputStream getOutputStream(){return new ByteArrayOutputStream();}
        public InputStream getInputStream(){return new ByteArrayInputStream(new byte[0]);}
        public InputStream getErrorStream(){return new ByteArrayInputStream(new byte[0]);}
        public int waitFor(){return 0;}
        public boolean waitFor(long timeout,TimeUnit unit){return !alive;}
        public int exitValue(){if(alive)throw new IllegalThreadStateException();return 0;}
        public void destroy(){if(!ignoresStop)alive=false;}
        public Process destroyForcibly(){destroy();return this;}
        public boolean isAlive(){return alive;}
    }
    static HlsSessionManager.Session session(Process process){
        HlsSessionManager.Session s=new HlsSessionManager.Session("quality-test",1,0,0,0,8000,false,new File("unused-quality-test"));
        s.process=process;s.running=true;return s;
    }
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);System.out.println("PASS "+message);}
    public static void main(String[] args)throws Exception{
        Process ordinary=new ProcessBuilder("/bin/sh","-c","exec sleep 30").start();
        HlsSessionManager.Session old=session(ordinary);
        try{HlsSessionManager.quiesceForQuality(old);}
        finally{if(ordinary.isAlive()){ordinary.destroy();ordinary.waitFor(2,TimeUnit.SECONDS);}}
        check(!ordinary.isAlive()&&old.stopRequested&&!old.running,"Quality stops the old producer before replacement");
        check(!old.cleanupQueued,"Quality quiescence does not delete published media");
        Producer stubborn=new Producer(true);
        try{HlsSessionManager.quiesceForQuality(session(stubborn));throw new AssertionError("Unconfirmed stop permitted replacement");}
        catch(IOException expected){check(stubborn.isAlive(),"Unconfirmed termination refuses a second encoder");}
        HlsSessionManager.Session completed=session(null);
        HlsSessionManager.quiesceForQuality(completed);
        check(completed.stopRequested&&!completed.running,"Completed producer needs no second process or termination wait");
        System.out.println("Single encoder quality: 4 PASS");
    }
}
