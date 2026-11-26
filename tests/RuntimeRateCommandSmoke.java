package org.opensagetv.webplayer;
import java.io.File;
import java.util.*;
/** Test the optional provider's real command selection, not GPU execution. */
public final class RuntimeRateCommandSmoke {
    static int checks;
    static void check(boolean v,String message){if(!v)throw new AssertionError(message);checks++;}
    static List<String> command(Map<String,String> values,String codec,boolean pipe){
        MediaProbe.Info info=new MediaProbe.Info();MediaProbe.Track video=new MediaProbe.Track();
        video.index=0;video.type="video";video.codec="mpeg2video";video.width=1920;video.height=1080;video.rate="30000/1001";info.tracks.add(video);
        TranscoderManager.Probe probe=new TranscoderManager.Probe(true,"/test/plugin-owned-mim","test",codec,true,true,true,"QSV","test","test");
        return StreamCommand.build(probe,new File("/test/source.ts"),false,pipe,0,new File("/test/output"),new StreamPlan(StreamOptions.fromMap(values),info));
    }
    public static void main(String[] args){
        Map<String,String> values=new HashMap<>();values.put("player","hls");values.put("videoMode","transcode");values.put("runtimeBitrateControl","true");
        List<String> c=command(values,"h264_qsv",false);
        check(c.contains("-sagetvruntimebitrate")&&c.indexOf("-readrate")<c.indexOf("-i"),"eligible input must be paced");
        check(c.get(c.indexOf("-readrate_initial_burst")+1).equals("6"),"bounded startup burst");
        for(String mutation:new String[]{"site-off","opt-out","copy","pipe","other-encoder","ts","b-frames"}){
            Map<String,String> v=new HashMap<>(values);String codec="h264_qsv";boolean pipe=false;
            if(mutation.equals("site-off"))System.setProperty("vibe.test.rateDisabled","true");
            if(mutation.equals("opt-out"))v.put("runtimeBitrateControl","false");
            if(mutation.equals("copy"))v.put("videoMode","copy");
            if(mutation.equals("pipe"))pipe=true;
            if(mutation.equals("other-encoder"))codec="h264_vaapi";
            if(mutation.equals("ts"))v.put("player","mpegts");
            if(mutation.equals("b-frames"))v.put("bFrames","1");
            c=command(v,codec,pipe);check(!c.contains("-sagetvruntimebitrate")&&!c.contains("-readrate"),"ordinary path changed: "+mutation);
            System.clearProperty("vibe.test.rateDisabled");
        }
        System.out.println("Runtime rate command: "+checks+" PASS (synthetic provider; no GPU claim)");
    }
}
