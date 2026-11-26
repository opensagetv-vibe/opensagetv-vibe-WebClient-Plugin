package org.opensagetv.webplayer;
import java.io.File;
import java.util.*;
import java.util.regex.*;

/** Generated FFmpeg/media proof, not physical receiver/phone calibration. */
public final class AvSyncRuntimeSmoke {
    static AvSyncManager.Lease create(int offset)throws Exception{
        Map<String,String> values=new HashMap<String,String>();values.put("player","hls");values.put("encoder","software");values.put("audioOffsetMs",String.valueOf(offset));values.put("deinterlace","off");
        return AvSyncManager.create(StreamOptions.fromMap(values));
    }
    static double onset(String ffmpeg,AvSyncManager.Lease lease)throws Exception{
        File playlist=AvSyncManager.media("/"+lease.id+"/stream.m3u8");
        ProcessCapture.Result result=ProcessCapture.run(Arrays.asList(ffmpeg,"-hide_banner","-i",playlist.getAbsolutePath(),"-map","0:a:0","-af","silencedetect=noise=-30dB:d=0.05","-f","null","-"),30,128*1024);
        if(result.exit!=0)throw new AssertionError(result.text);
        Matcher matcher=Pattern.compile("silence_end: ([0-9.]+)").matcher(result.text);if(!matcher.find())throw new AssertionError("No click onset");return Double.parseDouble(matcher.group(1));
    }
    public static void main(String[] args)throws Exception{
        String ffmpeg=args.length>0?args[0]:"/usr/bin/ffmpeg";System.setProperty("sagetv.webplayer.transcoder",ffmpeg);
        try{
            double[] starts=new double[3];int[] offsets={-500,0,500};
            for(int index=0;index<offsets.length;index++){
                AvSyncManager.Lease lease=create(offsets[index]);
                try{starts[index]=onset(ffmpeg,lease);if(lease.offset!=offsets[index]||lease.hardware)throw new AssertionError("Offset/Hardware truth");}
                finally{AvSyncManager.stop(lease.id);}
            }
            if(Math.abs(starts[1]-starts[0]-.5)>.12||Math.abs(starts[2]-starts[1]-.5)>.12)throw new AssertionError(Arrays.toString(starts));
            boolean rejected=false;try{AvSyncManager.media("/../../Sage.properties");}catch(Exception expected){rejected=true;}if(!rejected)throw new AssertionError("Path traversal");
            System.out.println("PASS real generated MPEG2/AC3 ball→H264/AAC shared audio-filter path; -500/0/+500ms click onsets="+Arrays.toString(starts)+"; lease/path cleanup guarded");
        }finally{AvSyncManager.close();}
    }
}
