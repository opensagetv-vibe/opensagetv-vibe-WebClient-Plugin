package org.opensagetv.webplayer;
import java.io.File;
import java.util.HashMap;
import java.util.Map;

/** No Sage.jar fixture: proves the plugin's epoch, pacing and policy boundary. */
public final class CaptionSelectionSmoke {
    static void check(boolean value,String reason){if(!value)throw new AssertionError(reason);}
    static StreamOptions options(String... pairs){Map<String,String> values=new HashMap<String,String>();for(int i=0;i<pairs.length;i+=2)values.put(pairs[i],pairs[i+1]);return StreamOptions.fromMap(values);}
    public static void main(String[] args)throws Exception{
        PlaybackSessionContext context=new PlaybackSessionContext();PlaybackSessionContext.Token old=context.beginSource();
        context.fileCues().offer(SubtitleCue.text(old,SubtitleCue.Owner.LOCAL_FILE,1000,500,"file",false,false));
        context.cues().offer(SubtitleCue.text(old,SubtitleCue.Owner.LOCAL_BROADCAST,1000,0,"old CC",false,false));
        PlaybackSessionContext.Token current=context.beginCaptionSelection();
        check(context.isCurrent(old),"caption selection must not invalidate A/V or ordinary subtitle work");
        check(context.fileCues().drainDue(current,2000,10).size()==1,"file cue must survive");
        check(!context.cues().offer(SubtitleCue.text(old,SubtitleCue.Owner.LOCAL_BROADCAST,1200,0,"stale",false,false)),"retired decoder must not clear/repopulate new CC");
        check(context.cues().offer(SubtitleCue.text(current,SubtitleCue.Owner.LOCAL_BROADCAST,1200,0,"new CC",false,false)),"current caption accepted");
        check(context.cues().drainDue(current,2000,10).size()==1,"only current CC delivered");
        HlsSessionManager.Session session=new HlsSessionManager.Session("caption-test",1,0,0,20,60000,false,new File("build/manual/caption-test"),StreamOptions.defaults(),context,current);
        check(!SubtitlePumpPosition.shouldWait(session,25000),"five-second source lead allowed");
        check(SubtitlePumpPosition.shouldWait(session,25001),"source reader must not race through whole recording");
        session.broadcastTimeMs=30000;check(!SubtitlePumpPosition.shouldWait(session,25001),"reader resumes from proven browser recording clock");
        long generation=context.token().captionGeneration;
        check(!HlsSessionManager.selectBroadcast(session,"dvb",100,1,"eng"),"missing source rejects before mutation");
        check(context.token().captionGeneration==generation,"failed selection cannot retire current captions");
        check(!HlsSessionManager.selectBroadcast(session,"invalid",-1,-1,""),"unknown selection fails closed");
        check(HlsSessionManager.selectBroadcast(session,"off",-1,-1,""),"Off works without source decoder");
        check(context.token().captionGeneration==generation+1,"successful caption-only epoch");
        check(!options("player","native","nativeHlsSupported","true").ts(),"native browser uses HLS conversion");
        check(!options("player","auto","nativeHlsSupported","true").ts(),"automatic Apple path avoids an unnecessary failed TS attempt");
        check(options("player","auto").ts(),"existing desktop automatic transport retained");
        boolean rejected=false;try{options("player","native");}catch(IllegalArgumentException expected){rejected=true;}check(rejected,"unsupported native decoder cannot be advertised as available");
        System.out.println("PASS caption-only epochs/source pacing/selection rejection/native-HLS policy (18 assertions)");
    }
}
