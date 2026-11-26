package org.opensagetv.webplayer;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.regex.*;

/** Real generated software encode using the production planner/command.
 * Not a GPU, physical receiver or field-broadcast qualification. */
public final class P12QualityRuntimeSmoke {
    private static String ffmpeg,ffprobe;
    public static void main(String[] args) throws Exception {
        if(args.length!=2)throw new IllegalArgumentException("ffmpeg and NEW explicit artifact directory required");
        ffmpeg=args[0];ffprobe=new File(new File(ffmpeg).getParentFile(),"ffprobe").getPath();
        Path root=new File("artifacts/active/WP12-005").getCanonicalFile().toPath();
        Path out=new File(args[1]).getCanonicalFile().toPath();
        if(!out.startsWith(root)||Files.exists(out))throw new IllegalArgumentException("Preserve existing paths; use a new WP12-005 run directory");
        Files.createDirectories(out);
        File input=out.resolve("interlaced-source.ts").toFile();
        run(Arrays.asList(ffmpeg,"-hide_banner","-loglevel","error","-n","-f","lavfi","-i",
            "testsrc2=size=1280x720:rate=60000/1001:duration=8","-f","lavfi","-i",
            "sine=frequency=880:sample_rate=48000:duration=8","-vf","tinterlace=mode=interleave_top",
            "-c:v","mpeg2video","-flags","+ilme+ildct","-top","1","-q:v","3","-c:a","ac3","-b:a","192k","-shortest",input.getPath()));
        MediaProbe.Info info=MediaProbe.read(input,ffmpeg);
        check(info.video()!=null&&info.video().interlaced(),"actual source is interlaced MPEG2");
        Result low=encode(input,info,out,"yadif-low",800,"480","29.97",1,0,"yadif",false);
        Result high=encode(input,info,out,"bwdif-high",1600,"720","23.976",3,2,"bwdif",false);
        check(high.videoBytes>low.videoBytes*1.2,"higher configured bitrate raises actual video payload on this pattern");
        Result copy=encode(out.resolve("bwdif-high/stream.ts").toFile(),
            MediaProbe.read(out.resolve("bwdif-high/stream.ts").toFile(),ffmpeg),out,"copy",12345,"source","source",7,3,"auto",true);
        check(copy.videoHash.equals(high.videoHash),"Copy preserves complete compressed video packets despite unrelated bitrate/GOP/B-frame knobs");
        System.out.println("P12 generated quality runtime: 3 production plans PASS; no GPU/receiver claim");
    }
    private static Result encode(File input,MediaProbe.Info info,Path out,String name,int kbps,String height,String fps,int gop,int bf,String filter,boolean copy)throws Exception{
        Path dir=Files.createDirectory(out.resolve(name));
        Map<String,String> m=new HashMap<String,String>();
        m.put("profileSchemaVersion","7");m.put("player","mpegts");m.put("videoMode",copy?"copy":"transcode");
        m.put("encoder","software");m.put("videoKbps",String.valueOf(kbps));m.put("resolution",height);m.put("fps",fps);
        m.put("keyFrameSeconds",String.valueOf(gop));m.put("bFrames",String.valueOf(bf));
        m.put("deinterlace",copy?"off":"on");m.put("deinterlaceFilter",filter);m.put("captions","off");
        m.put("audioCodec",copy?"copy":"aac");m.put("audioChannels",copy?"source":"2");
        StreamPlan plan=new StreamPlan(StreamOptions.fromMap(m),info);
        TranscoderManager.Probe probe=new TranscoderManager.Probe(true,ffmpeg,"generated","libx264",false,false,"software","generated software runtime");
        List<String> command=StreamCommand.build(probe,input,false,false,0,dir.toFile(),plan);
        run(command);
        File video=dir.resolve("stream.ts").toFile();MediaProbe.Info decoded=MediaProbe.read(video,ffmpeg);
        MediaProbe.Track t=decoded.video();check(t!=null&&"h264".equals(t.codec),name+" real H264 output");
        if(!copy){
            check(t.height==Integer.parseInt(height)&&!t.interlaced(),name+" real progressive height "+height);
            String[] rat=t.rate.split("/");double actual=Double.parseDouble(rat[0])/(rat.length==2?Double.parseDouble(rat[1]):1);
            check(Math.abs(actual-Double.parseDouble(fps))<.01,name+" actual FPS "+actual);
        }else check(plan.copyVideo&&plan.copyAudio,"actual Copy plan");
        String frameText=run(Arrays.asList(ffprobe,"-v","error","-select_streams","v:0","-show_entries","frame=key_frame,pict_type,best_effort_timestamp_time","-of","flat",video.getPath()));
        Map<Integer,Map<String,String>> frames=new TreeMap<Integer,Map<String,String>>();
        Matcher matcher=Pattern.compile("(?m)^frames\\.frame\\.(\\d+)\\.(\\w+)=(.*)$").matcher(frameText);
        while(matcher.find()){int id=Integer.parseInt(matcher.group(1));Map<String,String> f=frames.get(id);if(f==null){f=new HashMap<String,String>();frames.put(id,f);}f.put(matcher.group(2),matcher.group(3).replace("\"",""));}
        int b=0;List<Double> keys=new ArrayList<Double>();
        for(Map<String,String> f:frames.values()){if("B".equals(f.get("pict_type")))b++;if("1".equals(f.get("key_frame")))keys.add(Double.parseDouble(f.get("best_effort_timestamp_time")));}
        if(!copy){
            check(bf==0?b==0:b>0,name+" actual B-frame selection "+b);
            check(keys.size()>=2,name+" multiple real keyframes");
            for(int i=1;i<keys.size();i++)check(keys.get(i)-keys.get(i-1)<=gop+.09,name+" bounded keyframe interval");
        }
        String packets=run(Arrays.asList(ffprobe,"-v","error","-select_streams","v:0","-show_entries","packet=size","-of","csv=p=0",video.getPath()));
        long bytes=0;for(String line:packets.split("\\R")){String n=line.split(",",2)[0].trim();if(n.matches("\\d+"))bytes+=Long.parseLong(n);}
        String hash=run(Arrays.asList(ffmpeg,"-hide_banner","-loglevel","error","-i",video.getPath(),"-map","0:v:0","-c:v","copy","-f","hash","-hash","sha256","-" )).trim();
        check(hash.startsWith("SHA256="),name+" actual packet digest");
        System.out.println(name+": height="+t.height+" fps="+t.rate+" frames="+frames.size()+" B="+b+" keyframes="+keys+" videoBytes="+bytes+" "+hash);
        return new Result(bytes,hash);
    }
    private static String run(List<String> c)throws Exception{ProcessCapture.Result r=ProcessCapture.run(c,60,1024*1024);if(r.exit!=0)throw new AssertionError("Tool failed "+r.exit+": "+r.text);return r.text;}
    private static void check(boolean ok,String s){if(!ok)throw new AssertionError(s);}
    private static final class Result{final long videoBytes;final String videoHash;Result(long b,String h){videoBytes=b;videoHash=h;}}
}
