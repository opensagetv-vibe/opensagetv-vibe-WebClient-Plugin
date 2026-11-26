package org.opensagetv.webplayer;

import java.io.File;
import java.io.IOException;

/** Source-only captions use recording time, not a transcoded fragment's zero.
 * Resolve on the pump thread; never block the native media-command reader with
 * index I/O. Unsupported/non-TS sources fall back honestly to byte/time zero. */
final class SubtitlePumpPosition {
    final long absoluteByte,anchorMs;
    SubtitlePumpPosition(long offset,long anchor){absoluteByte=offset;anchorMs=anchor;}
    static SubtitlePumpPosition resolve(final HlsSessionManager.Session session,final SageApiBridge sage,final Object mediaFile)throws IOException{
        long target=Math.max(Math.round(session.startSeconds*1000.0),session.broadcastTimeMs);
        if(target<=0)return new SubtitlePumpPosition(0,0);
        MpegTsSeekIndex.Result result=MpegTsSeekIndex.resolve(new MpegTsSeekIndex.Sources(){
            public int segmentCount(){return sage.getNumberOfSegments(mediaFile)-session.firstSegment;}
            public SeekableMediaSource open(int index)throws IOException{
                File file=sage.getFileForSegment(mediaFile,session.firstSegment+index);
                return file==null?null:MediaSourceFactory.open(sage,file);
            }
        },target);
        return new SubtitlePumpPosition(result.validated?result.absoluteByte:0,result.validated?result.anchorMs:0);
    }
    static boolean shouldWait(HlsSessionManager.Session session,long observedMs){
        long presentation=Math.max(Math.round(session.startSeconds*1000.0),session.broadcastTimeMs);
        return observedMs>presentation+5000L||session.playbackContext.cues().size()>=SubtitleLimits.MAX_CUES-256;
    }
    private SubtitlePumpPosition(){this(0,0);}
}
