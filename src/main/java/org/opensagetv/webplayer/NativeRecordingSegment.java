package org.opensagetv.webplayer;

import java.io.File;
import java.util.List;

/** Stock MiniPlayer opens and clocks one physical segment, not the whole show. */
final class NativeRecordingSegment {
    static int index(File authorized,List<File> files){
        if(authorized==null)throw new IllegalArgumentException("Missing authorized recording segment");
        int found=-1;
        for(int i=0;i<files.size();i++)if(authorized.equals(files.get(i))){
            if(found>=0)throw new IllegalArgumentException("Ambiguous authorized recording segment");
            found=i;
        }
        if(found<0)throw new IllegalArgumentException("Authorized recording segment no longer exists");
        return found;
    }
    static int sourceCount(boolean nativeSegment,int first,int count){return nativeSegment?Math.min(count,first+1):count;}
    static boolean growing(boolean nativeSegment,int first,int count,boolean recording){return recording&&(!nativeSegment||first==count-1);}
    /** A completed physical file can have a wall-clock capture gap. A seek
     * beyond its last sample yields no browser frame. Only a CLEAN demuxer
     * empty-output receipt may signal stock EOF without a browser ended event.
     * Do not turn hardware/decode/input failures into success. */
    static boolean exhaustedSeek(HlsSessionManager.Session s){
        return s!=null&&s.nativeSegment&&!s.activeRecording&&!s.stopRequested&&!s.running&&
            s.dvdSource==null&&!s.isTs()&&s.startSeconds>0&&s.exitCode==0&&s.endList&&
            s.segments==0&&s.hlsSeconds==0&&s.error.isEmpty()&&"none".equals(s.healthInputError)&&
            s.sourceInfo!=null&&s.sourceInfo.video()!=null&&
            s.stderrTail.toLowerCase(java.util.Locale.ROOT).contains("output file is empty");
    }
    static long livePrerollMs(boolean nativeSegment,boolean recording,long requested,long elapsed,MpegTsSeekIndex.Result index){
        // Core's growing segment clock includes tuner startup/dropout time.
        // A live-edge request beyond every observed PTS must not discard future
        // seconds forever. Join just behind the proven tail, never an arbitrary
        // byte estimate, and only within the native current-live clock window.
        if(!nativeSegment||!recording||elapsed<=0||Math.abs(requested-elapsed)>5000||
           index==null||!index.validated||!"validated tail anchor".equals(index.reason)||index.residualMs<=1000)return -1;
        return Math.max(0,index.anchorMs-2000);
    }
}
