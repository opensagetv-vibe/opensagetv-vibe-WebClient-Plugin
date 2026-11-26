package org.opensagetv.webplayer;
import java.io.*;
import java.util.*;
public final class LiveRolloverSmoke {
    static int checks;
    static void check(boolean b,String why){if(!b)throw new AssertionError(why);checks++;}
    static final class Api implements StockClientPlayback.Api {
        boolean recording=true,tv=true,dvd=false,loaded=true,fail=false;int media=42,seeks,plays;long target;
        public Object call(String m,Object... a){
            if(m.equals("GetUIContextNames"))return new Object[]{"AA:BB:CC:DD:EE:FF"};
            if(m.equals("GetMediaFileID"))return media;
            if(m.equals("IsTVFile"))return tv;
            if(m.equals("IsFileCurrentlyRecording"))return recording;
            throw new AssertionError(m);
        }
        public Object ui(String context,String m,Object... a){
            check(context.equals("AA:BB:CC:DD:EE:FF"),"only exact UI");
            if(m.equals("IsMediaPlayerFullyLoaded"))return loaded;
            if(m.equals("IsCurrentMediaFileDVD"))return dvd;
            if(m.equals("GetCurrentMediaFile"))return "media";
            if(m.equals("GetAvailableSeekingEnd"))return 1795375071347L;
            if(m.equals("Seek")){seeks++;target=((Number)a[0]).longValue();if(fail)throw new IllegalStateException("unknown receipt");return null;}
            if(m.equals("Play")){plays++;return null;}
            throw new AssertionError("unexpected mutation "+m);
        }
    }
    static byte[] follow(boolean nativeSegment)throws Exception {
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        RecordingFollower.copy(new RecordingFollower.Sources(){
            public int segmentCount(){return NativeRecordingSegment.sourceCount(nativeSegment,1,3);}
            public boolean isRecording(){return NativeRecordingSegment.growing(nativeSegment,1,3,true);}
            public SeekableMediaSource open(final int index){return new SeekableMediaSource(){
                int at;public long length(){return 2;}public void seek(long p){at=(int)p;}
                public int read(byte[] b,int o,int n){int count=Math.min(n,2-at);if(count<=0)return -1;Arrays.fill(b,o,o+count,(byte)('A'+index));at+=count;return count;}
                public void close(){}public String mode(){return "test";}public String detail(){return "fixture";}
            };}
        },1,0,out,()->out.size()<4,n->{},r->{});
        return out.toByteArray();
    }
    public static void main(String[] args)throws Exception {
        List<File> files=Arrays.asList(new File("first.ts"),new File("second.ts"),new File("third.ts"));
        check(NativeRecordingSegment.index(files.get(2),files)==2,"later native OPENURL never selects zero");
        try{NativeRecordingSegment.index(files.get(0),Arrays.asList(files.get(0),files.get(0)));throw new AssertionError("duplicate allowed");}catch(IllegalArgumentException expected){checks++;}
        try{NativeRecordingSegment.index(new File("missing.ts"),files);throw new AssertionError("missing allowed");}catch(IllegalArgumentException expected){checks++;}
        check(!NativeRecordingSegment.growing(true,1,3,true),"old piece completes while show still records");
        check(NativeRecordingSegment.growing(true,2,3,true),"current piece follows its writer");
        check(!NativeRecordingSegment.growing(true,2,4,true),"new piece retires previous writer");
        MpegTsSeekIndex.Result tail=new MpegTsSeekIndex.Result(true,188000,11000,25000,25,188,"validated tail anchor");
        check(NativeRecordingSegment.livePrerollMs(true,true,25000,27000,tail)==9000,"live clock ahead of PTS joins proven tail with two-second preroll");
        check(NativeRecordingSegment.livePrerollMs(false,true,25000,27000,tail)==-1,"library seek is unchanged");
        check(NativeRecordingSegment.livePrerollMs(true,false,25000,27000,tail)==-1,"completed seek is unchanged");
        check(NativeRecordingSegment.livePrerollMs(true,true,10000,27000,tail)==-1,"non-live historical seek is unchanged");
        check(NativeRecordingSegment.livePrerollMs(true,true,25000,0,tail)==-1,"unknown live clock never guesses");
        check(Arrays.equals(follow(true),new byte[]{'B','B'}),"native feeder emits only selected piece");
        check(Arrays.equals(follow(false),new byte[]{'B','B','C','C'}),"library concatenation unchanged");
        Api a=new Api();check(StockClientPlayback.goLive(a,"aabbccddeeff",true,42,()->true),"live accepted");
        check(a.seeks==1&&a.plays==1&&a.target==1795375071347L,"one absolute stock live seek and Play");
        a.recording=false;check(!StockClientPlayback.goLive(a,"aabbccddeeff",true,42,()->true),"completed not live");a.recording=true;
        a.media=43;check(!StockClientPlayback.goLive(a,"aabbccddeeff",true,42,()->true),"changed media rejected");a.media=42;
        a.tv=false;check(!StockClientPlayback.goLive(a,"aabbccddeeff",true,42,()->true),"video rejected");a.tv=true;
        a.dvd=true;check(!StockClientPlayback.goLive(a,"aabbccddeeff",true,42,()->true),"DVD unchanged");a.dvd=false;
        check(!StockClientPlayback.goLive(a,"aabbccddeeff",true,42,()->false),"stale generation rejected");
        check(a.seeks==1,"all negative rows do not seek");
        a.fail=true;try{StockClientPlayback.goLive(a,"aabbccddeeff",true,42,()->true);throw new AssertionError("unknown accepted");}catch(IllegalStateException expected){checks++;}
        check(a.seeks==2&&a.plays==1,"unknown submission never retried or followed by Play");
        System.out.println("Live recording rollover/Watch live: "+checks+" PASS");
    }
}
