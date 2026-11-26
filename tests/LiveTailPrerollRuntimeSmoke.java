package org.opensagetv.webplayer;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** CPU FFmpeg/index proof for a native live clock ahead of captured video PTS. */
public final class LiveTailPrerollRuntimeSmoke {
    static String run(List<String> args,byte[] input)throws Exception {
        Process p=new ProcessBuilder(args).redirectErrorStream(true).start();
        try{
            try(OutputStream out=p.getOutputStream()){if(input!=null)out.write(input);}
            ByteArrayOutputStream log=new ByteArrayOutputStream();
            Thread reader=new Thread(()->{try{byte[] b=new byte[4096];int n;while((n=p.getInputStream().read(b))>=0)log.write(b,0,n);}catch(IOException ignored){}});
            reader.start();if(!p.waitFor(15,TimeUnit.SECONDS))throw new AssertionError("FFmpeg bounded runtime timeout");reader.join(2000);
            if(p.exitValue()!=0)throw new AssertionError(log.toString("UTF-8"));
            return log.toString("UTF-8");
        }finally{if(p.isAlive())p.destroyForcibly();}
    }
    static int frames(String ffmpeg,byte[] source,long offset,long residual)throws Exception {
        String text=run(Arrays.asList(ffmpeg,"-hide_banner","-loglevel","error","-f","mpegts","-i","pipe:0","-ss",String.format(Locale.ROOT,"%.3f",residual/1000.0),"-an","-frames:v","1","-f","framehash","pipe:1"),Arrays.copyOfRange(source,(int)offset,source.length));
        int count=0;for(String line:text.split("\n"))if(line.matches("^0,.*"))count++;return count;
    }
    public static void main(String[] args)throws Exception {
        String ffmpeg=args.length>0?args[0]:"/usr/bin/ffmpeg";Path temp=Files.createTempDirectory("web120-tail-");File source=temp.resolve("fixture.ts").toFile();
        try{
            run(Arrays.asList(ffmpeg,"-hide_banner","-loglevel","error","-f","lavfi","-i","testsrc2=size=320x240:rate=25","-t","8","-an","-c:v","mpeg2video","-g","12","-f","mpegts",source.getPath()),null);
            MpegTsSeekIndex.Sources sources=new MpegTsSeekIndex.Sources(){public int segmentCount(){return 1;}public SeekableMediaSource open(int index)throws IOException{return new DirectFileSource(source);}};
            MpegTsSeekIndex.Result old=MpegTsSeekIndex.resolve(sources,20000);
            long preroll=NativeRecordingSegment.livePrerollMs(true,true,20000,21000,old);
            if(preroll<0)throw new AssertionError("Known live-tail gap was not recognized");
            MpegTsSeekIndex.Result corrected=MpegTsSeekIndex.resolve(sources,preroll);byte[] data=Files.readAllBytes(source.toPath());
            int baseline;
            try{baseline=frames(ffmpeg,data,old.absoluteByte,old.residualMs);}
            catch(AssertionError noPicture){
                if(!noPicture.getMessage().contains("Output file does not contain any stream"))throw noPicture;
                baseline=0; // a tail without another PAT/GOP is also a proven no-picture baseline
            }
            if(baseline!=0)throw new AssertionError("Baseline unexpectedly has a frame beyond captured tail");
            if(frames(ffmpeg,data,corrected.absoluteByte,0)!=1)throw new AssertionError("Corrected live preroll has no decoded picture");
            System.out.println("Live tail CPU runtime: baseline zero pictures; bounded proven-PTS preroll decodes picture PASS");
            Path empty=Files.createDirectory(temp.resolve("empty"));
            String receipt=run(Arrays.asList(ffmpeg,"-hide_banner","-ss","20","-i",source.getPath(),"-an","-c:v","libx264","-f","hls",empty.resolve("stream.m3u8").toString()),null);
            HlsSessionManager.Session exhausted=new HlsSessionManager.Session("cpu-empty",1,0,0,20,30000,false,empty.toFile(),StreamOptions.defaults().hlsFallback());
            exhausted.nativeSegment=true;exhausted.exitCode=0;exhausted.stderrTail=receipt;
            exhausted.sourceInfo=new MediaProbe.Info();MediaProbe.Track video=new MediaProbe.Track();video.type="video";exhausted.sourceInfo.tracks.add(video);
            HlsSessionManager.refreshMetrics(exhausted);
            if(exhausted.playlistReady||!NativeRecordingSegment.exhaustedSeek(exhausted))throw new AssertionError("Actual FFmpeg clean empty-seek receipt not distinguished: "+receipt);
            System.out.println("Completed tail CPU runtime: clean empty seek has no playable segment and qualifies decoder EOF PASS");
        }finally{try(java.util.stream.Stream<Path> paths=Files.walk(temp)){for(Path p:(Iterable<Path>)paths.sorted(Comparator.reverseOrder())::iterator)Files.deleteIfExists(p);}}
    }
}
