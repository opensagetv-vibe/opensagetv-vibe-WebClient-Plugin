package org.opensagetv.webplayer;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;

public class StreamHealthSmoke {
    static int checks;
    static void check(boolean yes,String why){if(!yes)throw new AssertionError(why);checks++;}
    static String state(boolean alive,boolean ready,long age,long inputAge,long outputAge,String stage,long feedback,boolean paused,long buffer){
        return StreamHealthDiagnostics.classify(false,alive,ready,false,false,age,inputAge,outputAge,stage,feedback,paused,false,buffer);
    }
    public static void main(String[] args)throws Exception{
        Path dir=Files.createTempDirectory("web121-health-");
        System.setProperty("sagetv.webplayer.streamDiagnostics.dir",dir.toString());
        try{
            check(state(true,false,5000,5000,5000,"write",0,false,0).equals("starting"),"startup grace");
            check(state(true,true,20000,20000,15000,"waiting-source",0,false,0).equals("waiting-source-growth"),"source stops growing");
            check(state(true,true,20000,15000,15000,"write",0,false,0).equals("encoder-input-backpressure"),"stdin blocked");
            check(state(true,true,20000,2000,15000,"fed",0,false,0).equals("encoder-output-stalled"),"input advances output stopped");
            check(state(true,true,20000,0,0,"fed",0,false,0).equals("browser-buffer-empty"),"browser depletion with producer output");
            check(state(true,true,20000,0,0,"fed",0,true,0).equals("paused"),"intentional pause not depletion");
            check(state(true,true,20000,0,0,"fed",20000,false,0).equals("browser-feedback-missing"),"missing feedback not proven network fault");
            check(StreamHealthDiagnostics.classify(false,false,true,true,false,20000,0,0,"input-complete",0,false,false,5000).equals("producer-complete"),"read ahead EOF not browser EOS");
            check(StreamHealthDiagnostics.classify(false,false,false,false,true,20000,0,0,"read",0,false,false,0).equals("producer-failed"),"failure distinguishable");
            check(StreamHealthDiagnostics.classify(true,false,false,false,true,20000,0,0,"read",0,false,false,0).equals("stopped"),"explicit stop not encoder failure");
            HlsSessionManager.Session s=new HlsSessionManager.Session("owned",42,3,0,10,0,true,dir.toFile());
            MiniClientSession client=new MiniClientSession("health-test","127.0.0.1","020000000098",640,360,false);
            java.lang.reflect.Field field=MiniClientMediaBridge.class.getDeclaredField("hls");field.setAccessible(true);field.set(client.media(),s);
            client.media().reportStreamHealth("old",30,0,1,2,false,false,false,6);
            check(s.healthBrowserAt==0,"stale feedback cannot overwrite current producer");
            client.media().reportStreamHealth("owned",30,2500,3,2,false,false,true,2);
            check(s.healthBrowserAt>0&&s.healthBufferAheadMs==2500&&s.healthSeeking&&s.healthRecoveryAttempts==2,"current feedback recorded");
            check(s.bytesInput==0&&!s.stopRequested,"feedback causes no production action");
            client.media().reportPlaybackRevision("owned","web121.3");client.media().reportPlaybackRevision("old","web1.0");
            check(s.healthBrowserRevision.equals("web121.3"),"exact-owner loaded revision retained");
            client.media().reportPlaybackRevision("owned","secret URL/path");check(s.healthBrowserRevision.equals("unknown"),"revision rejects arbitrary content");
            client.media().recordNativeTransportFailure(new IOException("Broken pipe: secret URL/path"));
            check(s.healthNativeError.equals("broken-pipe")&&s.healthNativeErrorAt>0,"broken pipe evidence survives before UI cleanup");
            check(!StreamHealthDiagnostics.json("owned").contains("secret"),"transport metadata excludes raw error content");
            check(StreamHealthDiagnostics.transportFailure(new java.net.SocketTimeoutException()).equals("timeout")&&StreamHealthDiagnostics.transportFailure(new EOFException()).equals("eof"),"native timeout and EOF distinguished");
            client.media().reportStreamHealth("owned",30,Long.MAX_VALUE,50,90,false,false,false,999);
            check(s.healthBufferAheadMs==-1&&s.healthReadyState==-1&&s.healthNetworkState==-1&&s.healthRecoveryAttempts==100,"untrusted numeric feedback bounded");
            check(!StreamHealthDiagnostics.snapshot(s,System.currentTimeMillis()).contains("127.0.0.1"),"no address/url/content journaled");
            s.bytesInput=99;s.healthSourceLength=100;s.healthSourcePosition=99;s.healthInputStage="waiting-source";
            StreamHealthDiagnostics.sample(s,true);s.stopRequested=true;StreamHealthDiagnostics.sample(s,true);
            check(StreamHealthDiagnostics.json("owned").contains("\"state\":\"stopped\""),"closed owner retained");
            check(!StreamHealthDiagnostics.json("other").contains("\"session\":\"owned\""),"exact filter");
            for(int i=0;i<120;i++)StreamHealthDiagnostics.sample(s,true);
            String history=StreamHealthDiagnostics.json("owned");
            check(history.split("\"atMs\":",-1).length-1==StreamHealthDiagnostics.MAX_SAMPLES,"bounded per owner");
            StreamHealthDiagnostics.flush();check(Files.size(dir.resolve("stream-health.jsonl"))>0,"automatic persistence");
            for(int i=0;i<18;i++)StreamHealthDiagnostics.sample(new HlsSessionManager.Session("owner"+i,42,0,0,0,0,false,dir.toFile()),true);
            check(!StreamHealthDiagnostics.json("owned").contains("\"atMs\""),"bounded retained owners");
            byte[] max=new byte[StreamHealthDiagnostics.MAX_FILE_BYTES-2];Arrays.fill(max,(byte)' ');Files.write(dir.resolve("stream-health.jsonl"),max);
            StreamHealthDiagnostics.append(dir,"{\"rotate\":true}");
            check(Files.size(dir.resolve("stream-health.previous.jsonl"))==max.length,"rotate exact owned file");
            check(Files.size(dir.resolve("stream-health.jsonl"))<100,"bounded replacement");
            check(StreamHealthDiagnostics.journal().length<=2*StreamHealthDiagnostics.MAX_FILE_BYTES,"bounded journal download");
            try{StreamHealthDiagnostics.append(dir,String.join("",Collections.nCopies(17000,"x")));throw new AssertionError("oversize accepted");}catch(IOException expected){checks++;}
            Path link=dir.resolve("link");try{Files.createSymbolicLink(link,dir);try{StreamHealthDiagnostics.append(link,"{}");throw new AssertionError("symlink accepted");}catch(IOException expected){checks++;}}catch(UnsupportedOperationException|java.nio.file.FileSystemException unsupported){}
            System.setProperty("sagetv.webplayer.streamDiagnostics.enabled","false");
            StreamHealthDiagnostics.sample(new HlsSessionManager.Session("disabled",1,0,0,0,0,false,dir.toFile()),true);
            check(!StreamHealthDiagnostics.json("disabled").contains("\"atMs\""),"opt out");
            System.setProperty("sagetv.webplayer.streamDiagnostics.enabled","true");
            byte[] zip=DiagnosticSupport.zip("{}","null","null","{}","null");boolean found=false;
            try(ZipInputStream z=new ZipInputStream(new ByteArrayInputStream(zip))){ZipEntry e;while((e=z.getNextEntry())!=null)if(e.getName().equals("stream-health.json"))found=true;}
            check(found,"normal export contains retained server history");
            System.out.println("PASS StreamHealthSmoke "+checks);
        }finally{try(java.util.stream.Stream<Path> paths=Files.walk(dir)){for(Path p:(Iterable<Path>)paths.sorted(Comparator.reverseOrder())::iterator)Files.deleteIfExists(p);}}
    }
}
