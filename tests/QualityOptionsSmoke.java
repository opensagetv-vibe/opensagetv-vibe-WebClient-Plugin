package org.opensagetv.webplayer;

import java.util.HashMap;
import java.util.Map;

/** Focused WEB-052 options coverage. No physical playback claim. */
public final class QualityOptionsSmoke {
    public static void main(String[] args){
        Map<String,String> values=new HashMap<String,String>();
        values.put("videoKbps","4000");values.put("resolution","480");
        values.put("captionAuthority","cc1");values.put("captions","608");
        values.put("audioOffsetMs","-400");values.put("audioTrack","2");
        values.put("subtitleTrack","3");values.put("encoder","qsv");
        StreamOptions original=StreamOptions.fromMap(values),reduced=original.reducedQuality(1000,720);
        check(original.videoKbps==4000,"Saved options remain immutable");
        check(reduced.videoKbps==1000&&"480".equals(reduced.resolution),"Bitrate reduces; height never increases");
        check(reduced.audioOffsetMs==-400&&reduced.audioTrack==2&&reduced.subtitleTrack==3,"Track and audio offsets preserved");
        check("cc1".equals(reduced.captionAuthority)&&"608".equals(reduced.captions)&&"qsv".equals(reduced.encoder),"Caption and hardware ownership preserved");
        reject(original,5000,480);reject(original,249,480);reject(original,1000,555);
        StreamOptions recovered=reduced.handoffQuality(2000,1080,original);
        check(recovered.videoKbps==2000&&"480".equals(recovered.resolution),"Recovery stays inside configured bitrate/height ceilings");
        check(recovered.audioOffsetMs==-400&&recovered.audioTrack==2&&recovered.subtitleTrack==3&&"608".equals(recovered.captions),"Recovery preserves tracks/captions/offsets");
        try{reduced.handoffQuality(4500,480,original);throw new AssertionError("Exceeded saved ceiling");}
        catch(IllegalArgumentException expected){System.out.println("PASS recovery above saved ceiling rejected");}
        System.out.println("Quality options: 10 PASS");
    }
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);System.out.println("PASS "+message);}
    static void reject(StreamOptions options,int kbps,int height){
        try{options.reducedQuality(kbps,height);throw new AssertionError("Invalid reduction accepted");}
        catch(IllegalArgumentException expected){System.out.println("PASS invalid reduction rejected");}
    }
}
