package org.opensagetv.webplayer;
import java.nio.file.*;
import java.io.*;

/** Exact newly authored one-picture VOB through production software conversion. */
public final class DvdOnePictureFixtureSmoke {
    static void put(byte[] b,int p,int n){b[p]=(byte)(n>>>24);b[p+1]=(byte)(n>>>16);b[p+2]=(byte)(n>>>8);b[p+3]=(byte)n;}
    static byte[] push(byte[] data,int flags){byte[] b=new byte[data.length+8];put(b,0,data.length);put(b,4,flags);System.arraycopy(data,0,b,8,data.length);return b;}
    public static void main(String[] args)throws Exception {
        System.setProperty("sagetv.webplayer.ffmpeg","/usr/bin/ffmpeg");System.setProperty("sagetv.webplayer.videoEncoder","software");
        Path dir=Files.createTempDirectory("vibe-one-picture-worker-");System.setProperty("sagetv.webplayer.hlsDir",dir.toString());
        DvdNativeSession dvd=new DvdNativeSession();HlsSessionManager.Session hls=null;
        try {
            byte[] data=Files.readAllBytes(Paths.get(args[0]));if(data.length>262144)throw new AssertionError("Fixture exceeds bounded single push");
            dvd.init(1);byte[] selection=new byte[8];put(selection,4,0xbd80);dvd.setStream(selection);
            java.util.Map<String,String> options=new java.util.LinkedHashMap<String,String>();
            for(int i=1;i<args.length;i++){String[] pair=args[i].split("=",2);options.put(pair[0],pair[1]);}
            dvd.push(push(data,0));hls=HlsSessionManager.startDvd(dvd,StreamOptions.fromMap(options));dvd.push(push(new byte[0],0x100));
            long end=System.currentTimeMillis()+20000;
            while(System.currentTimeMillis()<end){HlsSessionManager.refreshMetrics(hls);if(hls.playlistReady)break;Thread.sleep(50);}
            if(!hls.playlistReady)throw new AssertionError("Exact authored one-picture VOB failed: "+hls.error+" / "+hls.stderrTail);
            System.out.println("PASS authored one-picture production worker; bytes="+data.length+", segments="+hls.segments+", duration="+hls.hlsSeconds);
        }finally{if(hls!=null)HlsSessionManager.stop(hls.id);dvd.close();}
    }
}
