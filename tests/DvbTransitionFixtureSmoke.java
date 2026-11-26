package org.opensagetv.webplayer;

import java.nio.file.*;
import java.util.*;

/** Generated real A/V transport through the actual DVB decoder, not field proof. */
public final class DvbTransitionFixtureSmoke {
    static int phase(byte[] data,int pos){
        int pid=((data[pos+1]&31)<<8)|(data[pos+2]&255);
        if(pid!=4096||(data[pos+1]&0x40)==0)return -1;
        int p=pos+4;if((data[pos+3]&0x20)!=0)p+=1+(data[p]&255);
        p+=1+(data[p]&255);return (data[p+5]>>1)&31;
    }
    static byte[] check(int phase,DvbSubtitleSession d,PlaybackSessionContext c,PlaybackSessionContext.Token token)throws Exception{
        int[] counts={2,1,0,2};
        if(d.services().length!=counts[phase])throw new AssertionError("Phase "+phase+" inventory "+d.services().length);
        byte[] color=null;
        for(SubtitleCue q:c.cues().drainDue(token,d.latestMediaMs(),256))if(q.kind==SubtitleCue.Kind.BITMAP&&q.width>0){
            if(q.width!=240||q.height!=2||q.x!=100||q.y!=400)throw new AssertionError("Visible fixture geometry");
            if(q.payload.length!=240*2*4)throw new AssertionError("RGBA extent");
            color=Arrays.copyOf(q.payload,4);
        }
        if(phase!=2&&color==null)throw new AssertionError("No selected real DVB pixels in phase "+phase+" "+d.diagnosticsJson());
        if(phase==2&&(d.selectedTrack()!=-1||color!=null))throw new AssertionError("No phantom image on removed service");
        System.out.println("PASS generated phase="+phase+" services="+counts[phase]+" selected="+d.selectedTrack()+" rgba="+Arrays.toString(color));
        return color;
    }
    public static void main(String[] args)throws Exception{
        byte[] data=Files.readAllBytes(Paths.get("artifacts/test-media/VIBE_CAPTION_PMT/VibeCaptions-English-Spanish-PMT.ts"));
        PlaybackSessionContext c=new PlaybackSessionContext();PlaybackSessionContext.Token t=c.beginSource();
        DvbSubtitleSession d=new DvbSubtitleSession(c,t,0);d.configure(true,336,1,"eng");
        int previous=0;byte[] english=null,spanish=null;
        for(int pos=0;pos<data.length;pos+=188){
            int version=phase(data,pos);
            boolean entering=version>=0&&version!=previous;
            if(entering){
                byte[] color=check(previous,d,c,t);if(previous==0)english=color;if(previous==1)spanish=color;
                previous=version;
            }
            d.observe("generated-continuous-source",pos,data,pos,188);
            if(entering&&version==1&&!d.selectService(337,2,"spa"))throw new AssertionError("Explicit language/PID/page unavailable");
        }
        check(previous,d,c,t);
        if(previous!=3||english==null||spanish==null||Arrays.equals(english,spanish))throw new AssertionError("Independent language pictures/phase restoration");
        System.out.println("PASS generated English->Spanish->none->restored source PMT/real RGBA; not physical field acceptance");
    }
}
