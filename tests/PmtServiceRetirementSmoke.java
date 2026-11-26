package org.opensagetv.webplayer;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;

/** Generated valid-CRC PMT removal through the real per-source decoders. */
public final class PmtServiceRetirementSmoke {
    private static byte[] withoutDescriptor(byte[] source,int tag){
        for(int packet=0;packet+188<=source.length;packet+=188){
            int start=packet+4,afc=(source[packet+3]>>4)&3;
            if(afc==3)start+=1+(source[start]&255);
            if(afc==2||start>=packet+188||(source[packet+1]&0x40)==0)continue;
            start+=1+(source[start]&255);
            if(start+16>packet+188||source[start]!=2)continue;
            int end=start+3+(((source[start+1]&15)<<8)|(source[start+2]&255));
            if(end>packet+188)throw new AssertionError("Expected single-packet fixture PMT");
            byte[] out=Arrays.copyOfRange(source,packet,packet+188);int section=start-packet;
            int pos=section+12+(((out[section+10]&15)<<8)|(out[section+11]&255));boolean removed=false;
            while(pos+5<end-packet-4){
                int d=pos+5,limit=d+(((out[pos+3]&15)<<8)|(out[pos+4]&255));
                while(d+2<=limit){int length=out[d+1]&255;if((out[d]&255)==tag){out[d]=0x52;removed=true;}d+=2+length;}
                pos=limit;
            }
            if(!removed)continue;
            out[3]=(byte)((out[3]&0xf0)|(((out[3]&15)+1)&15));
            out[section+5]=(byte)((out[section+5]&0xc1)|((((out[section+5]>>1)+1)&31)<<1));
            int crc=-1;
            for(int i=section;i<end-packet-4;i++){
                crc^=(out[i]&255)<<24;
                for(int b=0;b<8;b++)crc=(crc<<1)^((crc<0)?0x04c11db7:0);
            }
            for(int i=0;i<4;i++)out[end-packet-4+i]=(byte)(crc>>>(24-i*8));
            return out;
        }
        throw new AssertionError("Fixture descriptor not found");
    }
    public static void main(String[] args)throws Exception{
        byte[] tt=Files.readAllBytes(Paths.get("tests/parity/fixtures/teletext-188.ts"));
        PlaybackSessionContext c=new PlaybackSessionContext();PlaybackSessionContext.Token t=c.beginSource();
        TeletextSubtitleSession teletext=new TeletextSubtitleSession(c,t,0);teletext.configure(true,888,"eng");
        teletext.observe("same",0,tt,0,tt.length);
        if(teletext.services().length!=1)throw new AssertionError("Expected actual initial Teletext descriptor");
        byte[] gone=withoutDescriptor(tt,0x56);teletext.observe("same",tt.length,gone,0,gone.length);
        if(!teletext.stateJson().contains("\"selectedTrack\":-1")||teletext.services().length!=0)
            throw new AssertionError("Actual removed Teletext service must be explicit to the client");
        byte[] db=Files.readAllBytes(Paths.get("tests/parity/fixtures/dvb-2bpp.ts"));
        PlaybackSessionContext d=new PlaybackSessionContext();PlaybackSessionContext.Token dt=d.beginSource();
        DvbSubtitleSession dvb=new DvbSubtitleSession(d,dt,0);dvb.configure(true,336,1,"eng");dvb.observe("same",0,db,0,db.length);
        if(dvb.services().length!=1)throw new AssertionError("Expected actual initial DVB descriptor");
        gone=withoutDescriptor(db,0x59);dvb.observe("same",db.length,gone,0,gone.length);
        if(dvb.selectedTrack()!=-1||dvb.services().length!=0)throw new AssertionError("Removed DVB service must be explicit");
        System.out.println("PASS4 actual decoder PMT discovery/removal states; generated TS, not broadcast field");
    }
}
