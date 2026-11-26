package org.opensagetv.webplayer;

import java.nio.file.*;
import java.util.*;

/** Actual PMT parsing ahead of presentation must emit a source-timed clear. */
public final class DvbPmtTimingSmoke {
    public static void main(String[] args)throws Exception{
        byte[] data=Files.readAllBytes(Paths.get("artifacts/test-media/VIBE_CAPTION_PMT/VibeCaptions-English-Spanish-PMT.ts"));
        int boundary=-1;
        for(int p=0;p<data.length;p+=188)if(DvbTransitionFixtureSmoke.phase(data,p)==1){boundary=p;break;}
        if(boundary<0)throw new AssertionError("Real second PMT missing");
        PlaybackSessionContext c=new PlaybackSessionContext();PlaybackSessionContext.Token t=c.beginSource();
        DvbSubtitleSession d=new DvbSubtitleSession(c,t,0);d.configure(true,336,1,"eng");
        d.observe("continuous",0,data,0,boundary);
        c.cues().drainDue(t,Long.MAX_VALUE,4096);
        long before=d.latestMediaMs();
        d.observe("continuous",boundary,data,boundary,188);
        if(d.selectedTrack()!=-1)throw new AssertionError("English must actually disappear");
        if(before<15000||before>16000)throw new AssertionError("Unexpected actual source PTS "+before);
        List<SubtitleCue> early=c.cues().drainDue(t,11000,256);
        if(!early.isEmpty())throw new AssertionError("PMT read-ahead clears at playback11s instead of source16s");
        List<SubtitleCue> due=c.cues().drainDue(t,16000,256);
        if(due.isEmpty()||!due.get(0).clear)throw new AssertionError("No source-timed removal clear");
        if(!d.stateJson().contains("\"selectionChangedMs\":"+before))throw new AssertionError("Client needs explicit source-time metadata");
        d.configure(false,-1,-1,"");
        if(!d.stateJson().contains("\"selectionChangedMs\":0"))throw new AssertionError("User Off must remain immediate");
        System.out.println("PASS actual PMT read-ahead/timed clear/metadata/explicit Off at source="+before);
    }
}
