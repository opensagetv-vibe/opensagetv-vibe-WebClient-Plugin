package org.opensagetv.webplayer;

import java.io.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Bounded original A/53 service inventory. Never exports caption text/payload. */
public final class OriginalCaptionInventory {
    static final class Inventory {
        final long[] text608=new long[4],controls608=new long[4],blocks708=new long[64],bytes708=new long[64];
        final int[] channel={0,0};final byte[] dtvcc=new byte[127];
        int length,expected;long records,pairs608,triples708,packets708,truncated;
        void packet(long pts,byte[] data){
            records++;
            for(int p=0;p+2<data.length;p+=3){
                int flags=data[p]&255;if((flags&4)==0)continue;
                int type=flags&3,a=data[p+1]&255,b=data[p+2]&255;
                if(type<=1){
                    pairs608++;a&=127;b&=127;
                    if(a>=16&&a<=31){channel[type]=(a&8)==0?0:1;controls608[type*2+channel[type]]++;}
                    else if(a>=32||b>=32)text608[type*2+channel[type]]++;
                }else{
                    triples708++;
                    if(type==3){if(expected>0&&length<expected)truncated++;length=0;int size=a&63;expected=2*(size==0?64:size)-1;append(b);}
                    else if(expected>0){append(a);append(b);}
                }
            }
        }
        void append(int value){
            if(expected<=0||length>=expected)return;
            dtvcc[length++]=(byte)value;
            if(length==expected){
                packets708++;int p=0;
                while(p<length){
                    int h=dtvcc[p++]&255,service=h>>5,size=h&31;
                    if(service==7){if(p>=length){truncated++;break;}service=dtvcc[p++]&63;}
                    if(p+size>length){truncated++;break;}
                    if(service>0&&size>0){blocks708[service]++;bytes708[service]+=size;}
                    p+=size;
                }
                length=expected=0;
            }
        }
    }
    static void selfTest(){
        Inventory i=new Inventory();
        for(int field=0;field<2;field++)for(int channel=0;channel<2;channel++)
            i.packet(0,new byte[]{(byte)(0xfc+field),(byte)(channel==0?0x14:0x1c),0x20,(byte)(0xfc+field),'A','B'});
        i.packet(0,new byte[]{(byte)0xff,2,0x22,(byte)0xfe,'H','I',(byte)0xff,0x42,(byte)0xe1,(byte)0xfe,9,'Z'});
        for(long n:i.text608)if(n!=1)throw new AssertionError("608 field/channel routing");
        if(i.blocks708[1]!=1||i.bytes708[1]!=2||i.blocks708[9]!=1||i.bytes708[9]!=1||i.truncated!=0)
            throw new AssertionError("708 packet/service/extended-service assembly");
        System.out.println("PASS inventory608CC1-4/708service1+extended9; synthetic parser test only");
    }
    public static void main(String[] args)throws Exception{
        if(args.length==1&&"--self-test".equals(args[0])){selfTest();return;}
        if(args.length!=0)throw new IllegalArgumentException("Only bounded stdin or --self-test");
        Inventory i=new Inventory();A53CaptionTap.Parser parser=new A53CaptionTap.Parser(i::packet);
        MessageDigest hash=MessageDigest.getInstance("SHA-256");byte[] buffer=new byte[32768];long bytes=0;int n;
        while((n=System.in.read(buffer))!=-1){bytes+=n;if(bytes>20L*1024*1024)throw new IOException("Original sample exceeds bound");hash.update(buffer,0,n);parser.push(buffer,0,n);}
        parser.finish();StringBuilder sha=new StringBuilder();for(byte b:hash.digest())sha.append(String.format("%02x",b&255));
        StringBuilder services=new StringBuilder("[");boolean first=true;
        for(int s=1;s<64;s++)if(i.blocks708[s]>0){if(!first)services.append(',');first=false;services.append("{\"service\":").append(s).append(",\"blocks\":").append(i.blocks708[s]).append(",\"bytes\":").append(i.bytes708[s]).append('}');}
        services.append(']');
        System.out.println("{\"sourceBytes\":"+bytes+",\"sha256\":\""+sha+"\",\"records\":"+i.records+
            ",\"valid608Pairs\":"+i.pairs608+",\"textPairs608\":"+Arrays.toString(i.text608)+
            ",\"controlPairs608\":"+Arrays.toString(i.controls608)+",\"valid708Triples\":"+i.triples708+
            ",\"packets708\":"+i.packets708+",\"services708\":"+services+",\"incompletePacketsOrBlocks\":"+i.truncated+
            ",\"exportsCaptionPayload\":false,\"physicalAcceptance\":false}");
    }
}
