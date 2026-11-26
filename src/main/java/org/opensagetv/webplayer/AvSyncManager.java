package org.opensagetv.webplayer;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import javax.imageio.ImageIO;

/** Fixed synthetic ball/AC3 source through the SAME StreamCommand audio path.
 * No user paths, recording imports, native clock emulation or global settings.
 * One bounded generator, at most two short-lived result leases. */
final class AvSyncManager {
    static final class Lease {
        final String id;final File directory;final long created=System.currentTimeMillis();
        File output;String encoder="";boolean hardware,hardwareDecode,hardwareFilters;int offset;
        Lease(String id,File directory){this.id=id;this.directory=directory;}
        String json(){return "{\"id\":\""+id+"\",\"playlistUrl\":\"av-sync/"+id+"/stream.m3u8\",\"source\":\"Synthetic MPEG-2 640x360p60 / 48kHz AC-3 stereo\",\"audioOffsetMs\":"+offset+",\"encoder\":\""+HttpUtil.json(encoder)+"\",\"hardwareEncode\":"+hardware+",\"hardwareDecode\":"+hardwareDecode+",\"hardwareFilters\":"+hardwareFilters+",\"physicalCalibrationClaimed\":false}";}
    }
    private static final Map<String,Lease> LEASES=new ConcurrentHashMap<String,Lease>();
    private static final ReentrantLock GENERATOR=new ReentrantLock();
    private static final ScheduledExecutorService REAPER=Executors.newSingleThreadScheduledExecutor(task->{Thread thread=new Thread(task,"webplayer-av-test-cleanup");thread.setDaemon(true);return thread;});
    private static volatile boolean closing;
    static{REAPER.scheduleWithFixedDelay(()->{try{expire();}catch(IOException ignored){}},60,60,TimeUnit.SECONDS);}
    static Lease create(StreamOptions requested)throws IOException{
        if(!GENERATOR.tryLock())throw new IOException("Another A/V test is being generated; try again shortly");
        Lease lease=null;boolean ready=false;
        try{
            if(closing)throw new IOException("A/V test service is stopping");
            expire();if(LEASES.size()>=2)throw new IOException("Two A/V tests are active; close a test before starting another");
            File executable=TranscoderManager.findExecutable();if(executable==null)throw new IOException("Required FFmpeg Plugin transcoder is unavailable");
            String id=UUID.randomUUID().toString().replace("-","");File directory=new File(root(),id);Files.createDirectory(directory.toPath());lease=new Lease(id,directory);
            File ball=new File(directory,"ball.png");BufferedImage image=new BufferedImage(32,32,BufferedImage.TYPE_INT_ARGB);
            Graphics2D graphics=image.createGraphics();try{graphics.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);graphics.setColor(Color.WHITE);graphics.fillOval(1,1,30,30);}finally{graphics.dispose();}
            ImageIO.write(image,"png",ball);
            File source=new File(directory,"source.ts");run(sourceCommand(executable,ball,source),35);
            StreamOptions options=requested.forDvdTranscode(); // H264/AAC compatibility, selected encoder/quality/offset retained.
            MediaProbe.Info info=new MediaProbe.Info();MediaProbe.Track video=new MediaProbe.Track();video.index=0;video.type="video";video.codec="mpeg2video";video.width=640;video.height=360;video.field="progressive";video.rate="60/1";info.tracks.add(video);
            MediaProbe.Track audio=new MediaProbe.Track();audio.index=1;audio.type="audio";audio.codec="ac3";audio.channels=2;info.tracks.add(audio);
            StreamPlan plan=new StreamPlan(options,info);TranscoderManager.Probe detected=TranscoderManager.forStream(plan);
            if(!detected.available)throw new IOException(detected.detail);
            IOException last=null;
            for(int stage=0;stage<3;stage++){
                if(closing)throw new IOException("A/V test service is stopping");
                if(stage>0&&!options.allowFallback)break;
                if(stage==1&&!detected.hardwareDecode||stage==2&&!detected.hardware)continue;
                TranscoderManager.Probe probe=stage==0?detected:stage==1?TranscoderManager.encodeOnlyFallback(detected,"A/V test hardware decode failed"):TranscoderManager.softwareFallback(detected,"A/V test hardware encode failed");
                File out=new File(directory,"attempt"+stage);Files.createDirectory(out.toPath());
                try{
                    run(StreamCommand.build(probe,source,false,false,0,out,plan),35);
                    if(!new File(out,"stream.m3u8").isFile())throw new IOException("A/V test produced no playlist");
                    lease.output=out;lease.encoder=probe.videoEncoder;lease.hardware=probe.hardware;lease.hardwareDecode=probe.hardwareDecode;lease.hardwareFilters=StreamCommand.usesGpuFilters(probe,plan);lease.offset=options.audioOffsetMs;
                    LEASES.put(id,lease);ready=true;return lease;
                }catch(IOException failure){last=failure;}
            }
            throw last==null?new IOException("A/V test conversion unavailable"):last;
        }finally{if(lease!=null&&!ready)remove(lease.directory);GENERATOR.unlock();}
    }
    static List<String> sourceCommand(File executable,File ball,File source){
        String filter="[1:v]drawbox=x=0:y=300:w=iw:h=3:color=blue:t=fill,drawbox=x=0:y=300:w=iw:h=3:color=red:t=fill:enable='between(mod(t,2),1.5,1.7)',drawbox=x=5:y=5:w=630:h=350:color=yellow:t=2[bg];[bg][0:v]overlay=x=(W-w)/2:y='40+230*pow(min(mod(t,2)/1.5,1),2)':shortest=1[v]";
        return Arrays.asList(executable.getAbsolutePath(),"-hide_banner","-loglevel","error","-y","-loop","1","-framerate","60","-i",ball.getAbsolutePath(),"-f","lavfi","-i","color=c=black:s=640x360:r=60:d=12","-f","lavfi","-i","aevalsrc=if(between(mod(t\\,2)\\,1.5\\,1.515)\\,0.7*sin(2*PI*1000*t)\\,0):s=48000:d=12","-filter_complex",filter,"-map","[v]","-map","2:a:0","-c:v","mpeg2video","-q:v","3","-g","30","-bf","0","-pix_fmt","yuv420p","-c:a","ac3","-b:a","192k","-ar","48000","-ac","2","-t","12","-f","mpegts",source.getAbsolutePath());
    }
    static File media(String path)throws IOException{
        expire();String[] parts=path==null?new String[0]:path.split("/");
        if(parts.length!=3||!parts[1].matches("[a-f0-9]{32}")||!(parts[2].equals("stream.m3u8")||parts[2].matches("seg_[0-9]{5}\\.ts")))throw new IOException("Unknown A/V test file");
        Lease lease=LEASES.get(parts[1]);if(lease==null)throw new IOException("A/V test expired");File file=new File(lease.output,parts[2]);
        if(Files.isSymbolicLink(file.toPath())||!file.isFile()||file.length()>16L*1024L*1024L)throw new IOException("Invalid A/V test artifact");return file;
    }
    static void stop(String id)throws IOException{if(id==null||!id.matches("[a-f0-9]{32}"))throw new IllegalArgumentException("Invalid A/V test lease");Lease lease=LEASES.remove(id);if(lease!=null)remove(lease.directory);}
    static void expire()throws IOException{
        long limit=System.currentTimeMillis()-15L*60L*1000L;
        for(Lease lease:LEASES.values())if(lease.created<limit)stop(lease.id);
        File[] abandoned=root().listFiles();if(abandoned!=null)for(File directory:abandoned)
            if(directory.getName().matches("[a-f0-9]{32}")&&!LEASES.containsKey(directory.getName())&&directory.lastModified()<limit)remove(directory);
    }
    static void close(){closing=true;REAPER.shutdownNow();for(String id:new ArrayList<String>(LEASES.keySet()))try{stop(id);}catch(IOException ignored){}}
    private static File root()throws IOException{File tmp=new File(System.getProperty("java.io.tmpdir")).getCanonicalFile();File root=new File(tmp,"sagetv-webplayer-av-sync");if(Files.isSymbolicLink(root.toPath()))throw new IOException("Invalid A/V test root");Files.createDirectories(root.toPath());return root;}
    private static void remove(File directory)throws IOException{
        Path path=directory.toPath().toAbsolutePath().normalize(),base=root().toPath().toAbsolutePath().normalize();
        if(!path.getParent().equals(base)||!path.getFileName().toString().matches("[a-f0-9]{32}")||Files.isSymbolicLink(path))throw new IOException("Unsafe A/V test cleanup target");
        if(!Files.exists(path))return;
        Files.walkFileTree(path,new SimpleFileVisitor<Path>(){public FileVisitResult visitFile(Path file,BasicFileAttributes attrs)throws IOException{Files.delete(file);return FileVisitResult.CONTINUE;}public FileVisitResult postVisitDirectory(Path dir,IOException failure)throws IOException{if(failure!=null)throw failure;Files.delete(dir);return FileVisitResult.CONTINUE;}});
    }
    private static void run(List<String> command,int seconds)throws IOException{ProcessCapture.Result result=ProcessCapture.run(command,seconds,64*1024);if(result.exit!=0)throw new IOException("A/V test FFmpeg failed: "+result.text.substring(0,Math.min(1000,result.text.length())));}
    private AvSyncManager(){}
}
