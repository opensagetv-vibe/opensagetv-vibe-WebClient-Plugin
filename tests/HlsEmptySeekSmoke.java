package org.opensagetv.webplayer;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** WEB-121 empty-manifest reproduction; generated metadata is not picture proof. */
public final class HlsEmptySeekSmoke {
    static int checks;
    static void check(boolean value,String why){if(!value)throw new AssertionError(why);checks++;}
    static void field(Object o,String name,Object value)throws Exception{java.lang.reflect.Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);f.set(o,value);}
    static void eligible(HlsSessionManager.Session s){
        s.nativeSegment=true;s.running=false;s.activeRecording=false;s.stopRequested=false;s.endList=true;s.exitCode=0;
        s.segments=0;s.hlsSeconds=0;s.error="";s.healthInputError="none";s.dvdSource=null;
        s.sourceInfo=new MediaProbe.Info();MediaProbe.Track v=new MediaProbe.Track();v.type="video";s.sourceInfo.tracks.add(v);
        s.stderrTail="Output file is empty, nothing was encoded (check -ss / -t / -frames parameters if used)";
    }
    public static void main(String[] args)throws Exception{
        Path dir=Files.createTempDirectory("web121-empty-");
        MiniClientSession owner=new MiniClientSession("empty-test","127.0.0.1","020000000091",640,360,false);
        try{
            HlsSessionManager.Session s=new HlsSessionManager.Session("empty",1,0,0,10,20000,false,dir.toFile(),StreamOptions.defaults().hlsFallback());
            String manifest="#EXTM3U\n#EXT-X-TARGETDURATION:1\n#EXTINF:0.000000,\nseg_00000.ts\n#EXT-X-ENDLIST\n";
            Files.write(s.playlist.toPath(),manifest.getBytes(StandardCharsets.UTF_8));
            HlsSessionManager.refreshMetrics(s);check(!s.playlistReady&&s.segments==0,"missing output file is not a playable segment");
            Files.write(dir.resolve("seg_00000.ts"),new byte[0]);Thread.sleep(120);HlsSessionManager.refreshMetrics(s);
            check(!s.playlistReady&&s.segments==0,"zero-byte segment cannot suppress encoder startup fallback");
            Files.write(dir.resolve("seg_00000.ts"),new byte[188]);Files.write(s.playlist.toPath(),manifest.replace("0.000000","0.041711").getBytes(StandardCharsets.UTF_8));
            Thread.sleep(120);HlsSessionManager.refreshMetrics(s);check(s.playlistReady&&s.segments==1,"nonempty one-picture duration remains playable");
            MiniClientMediaBridge b=owner.media();field(b,"hls",s);field(b,"mediaId",1);field(b,"browserTimeMs",10000L);
            eligible(s);check(MiniClientSession.readInt(b.handle(17,new byte[0]),0)==-1,"clean completed empty seek returns real decoder EOF without nonexistent browser frame");
            for(String reason:Arrays.asList("ordinary","recording","running","stopped","failed","unknown","open","input-error","error","metadata","stderr","picture","dvd")){
                eligible(s);
                if(reason.equals("ordinary"))s.nativeSegment=false;if(reason.equals("recording"))s.activeRecording=true;
                if(reason.equals("running"))s.running=true;if(reason.equals("stopped"))s.stopRequested=true;
                if(reason.equals("failed"))s.exitCode=69;if(reason.equals("unknown"))s.exitCode=Integer.MIN_VALUE;
                if(reason.equals("open"))s.endList=false;if(reason.equals("input-error"))s.healthInputError="broken-pipe";
                if(reason.equals("error"))s.error="decode failed";if(reason.equals("metadata"))s.sourceInfo=null;
                if(reason.equals("stderr"))s.stderrTail="";if(reason.equals("picture"))s.hlsSeconds=.04;
                if(reason.equals("dvd"))s.dvdSource=new DvdNativeSession();
                check(MiniClientSession.readInt(b.handle(17,new byte[0]),0)==10000,"empty-seek EOS rejects "+reason);
            }
            System.out.println("Empty native seek/manifest: "+checks+" PASS");
        }finally{owner.close();try(java.util.stream.Stream<Path> paths=Files.walk(dir)){for(Path p:(Iterable<Path>)paths.sorted(Comparator.reverseOrder())::iterator)Files.deleteIfExists(p);}}
    }
}
