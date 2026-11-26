package org.opensagetv.webplayer;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Generated context guards; optional genuine external IDX/SUB/IFO worker gate. */
public final class VobSubPaletteSmoke {
    static int assertions;
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);assertions++;}
    static void rejects(File idx,String expected)throws Exception {
        try{VobSubPalette.configure(new ArrayList<String>(),idx);throw new AssertionError("Accepted "+expected);}
        catch(IOException expectedError){check(expectedError.getMessage().contains(expected),"Fixed context error: "+expected);}
    }
    public static void main(String[] args)throws Exception {
        Path dir=Files.createTempDirectory("vibe-vobsub-context-");
        File idx=dir.resolve("movie.idx").toFile(),sub=dir.resolve("movie.sub").toFile(),ifo=dir.resolve("movie.ifo").toFile();
        try {
            Files.write(sub.toPath(),new byte[]{0});Files.write(idx.toPath(),"size: 720x480\n".getBytes(StandardCharsets.UTF_8));
            rejects(idx,"palette unavailable");
            File movie=dir.resolve("movie.ts").toFile();Files.write(movie.toPath(),new byte[]{0});
            try{MediaProbe.Info missing=new MediaProbe.Info();MediaProbe.discoverSidecars(missing,movie);check(missing.ordinarySubtitles().isEmpty()&&missing.warning.contains("palette unavailable"),"Missing palette is not advertised as a working sidecar");}finally{Files.delete(movie.toPath());}
            Files.write(idx.toPath(),"palette: ffffff\n".getBytes(StandardCharsets.UTF_8));rejects(idx,"Invalid VobSub IDX palette");
            String palette="000000,ffffff,112233,334455,556677,778899,99aabb,bbccdd,ddeeff,101010,202020,303030,404040,505050,606060,707070";
            Files.write(idx.toPath(),("palette: "+palette+"\n").getBytes(StandardCharsets.UTF_8));
            List<String> options=new ArrayList<String>();VobSubPalette.configure(options,idx);
            check(options.equals(Arrays.asList("-palette",palette)),"Exact sixteen RGB colors supplied explicitly");
            Files.write(idx.toPath(),("palette: "+palette+"\npalette: "+palette).getBytes(StandardCharsets.UTF_8));rejects(idx,"Ambiguous");
            Files.write(idx.toPath(),"size: 720x480\n".getBytes(StandardCharsets.UTF_8));
            Files.write(ifo.toPath(),new byte[0xd0]);rejects(idx,"VTS IFO required");
            try(RandomAccessFile out=new RandomAccessFile(ifo,"rw")) {
                out.setLength(4096);out.write("DVDVIDEO-VTS".getBytes(StandardCharsets.US_ASCII));out.seek(0xcc);out.writeInt(1);
                out.seek(2048);out.writeShort(1);out.writeShort(0);out.writeInt(2047);out.seek(2060);out.writeInt(16);
            }
            options.clear();VobSubPalette.configure(options,idx);
            check(options.equals(Arrays.asList("-ifo_palette",ifo.getCanonicalPath())),"Bounded associated first-PGC IFO accepted");
            try(RandomAccessFile out=new RandomAccessFile(ifo,"rw")){out.seek(2060);out.writeInt(0x7fffffff);}
            rejects(idx,"palette region unavailable");
            try(RandomAccessFile out=new RandomAccessFile(ifo,"rw")){out.seek(0xcc);out.writeInt(-1);}
            rejects(idx,"PGC table");
            Files.write(idx.toPath(),new byte[256*1024+1]);rejects(idx,"context limit");
            MediaProbe.Track track=new MediaProbe.Track();track.type="subtitle";track.codec="dvd_subtitle";track.index=128;track.language="eng";
            MediaProbe.Info info=new MediaProbe.Info();info.tracks.add(track);Map<String,String> requested=new HashMap<String,String>();requested.put("subtitleMode","auto");requested.put("subtitleForcedOnly","true");requested.put("subtitleLanguage","eng");StreamOptions optionsForPlan=StreamOptions.fromMap(requested);
            check(new StreamPlan(optionsForPlan,info).subtitle==track,"Auto forced-only allows per-packet-filtered DVD track");
            track.codec="hdmv_pgs_subtitle";check(new StreamPlan(optionsForPlan,info).subtitle==track,"Auto forced-only allows per-packet-filtered PGS track");
            track.codec="subrip";check(new StreamPlan(optionsForPlan,info).subtitle==null,"Auto forced-only does not promote unforced text");
            if(args.length>=2)external(new File(args[0]),args[1],args.length>2?Paths.get(args[2]):null);
            System.out.println("VobSubPaletteSmoke PASS assertions="+assertions+" genuineExternal="+(args.length>=2));
        } finally {
            for(File file:new File[]{idx,sub,ifo})Files.deleteIfExists(file.toPath());Files.delete(dir);
        }
    }
    static void external(File idx,String ffmpeg,Path witness)throws Exception {
        MediaProbe.Track track=new MediaProbe.Track();track.type="subtitle";track.codec="dvd_subtitle";track.sourceKind="sidecar";
        track.sidecarFormat="idx";track.sidecarFile=idx;track.sidecarSubstream=0;track.language="eng";
        List<String> options=new ArrayList<String>();VobSubPalette.configure(options,idx);
        check(options.get(0).equals("-ifo_palette"),"Genuine old IDX obtains paired authored IFO palette");
        PlaybackSessionContext context=new PlaybackSessionContext();PlaybackSessionContext.Token token=context.beginSource();
        OrdinarySubtitleSession session=OrdinarySubtitleSession.start(context,token,track,idx,ffmpeg,100000,0);
        check("0:i:0".equals(session.mapSpec()),"IDX physical substream ID mapping, not a container ordinal");
        SubtitleCue image=null,clear=null;long deadline=System.currentTimeMillis()+20000;
        try {
            while(System.currentTimeMillis()<deadline){
                for(SubtitleCue cue:context.fileCues().drainDue(token,116000,128)) {
                    if(image==null&&cue.kind==SubtitleCue.Kind.BITMAP&&cue.payload.length>0)image=cue;
                    else if(image!=null&&clear==null&&cue.clear&&cue.payload.length==0&&cue.ptsMs>image.ptsMs)clear=cue;
                }
                if(clear!=null||!session.running)break;Thread.sleep(20);
            }
            check(session.error.isEmpty(),"Genuine production worker has no error: "+session.error);
            check(image!=null&&image.owner==SubtitleCue.Owner.LOCAL_FILE,"Genuine external bitmap decoded as LOCAL_FILE");
            int visible=0;for(int i=3;i<image.payload.length;i+=4)if((image.payload[i]&255)>0)visible++;
            check(visible>100,"Genuine authored palette has visible straight-alpha pixels");
            check(Math.abs(image.ptsMs-103603)<=1,"First genuine cue retains original file time, not seek origin");
            check(clear!=null&&Math.abs(clear.ptsMs-104501)<=1,"Genuine authored clear retains original file time");
            if(witness!=null)Files.write(witness,("{\"cue\":"+image.json()+",\"clear\":"+clear.json()+"}\n").getBytes(StandardCharsets.UTF_8),StandardOpenOption.CREATE_NEW);
        } finally {session.stop();}
        for(int delay:new int[]{-1000,1000}) {
            token=context.beginSeek();session=OrdinarySubtitleSession.start(context,token,track,idx,ffmpeg,100000,delay);
            SubtitleCue delayed=null;long end=System.currentTimeMillis()+15000;
            try {
                while(System.currentTimeMillis()<end) {
                    for(SubtitleCue cue:context.fileCues().drainDue(token,116000,128))if(delayed==null&&cue.payload.length>0)delayed=cue;
                    if(delayed!=null||!session.running)break;Thread.sleep(20);
                }
                check(session.error.isEmpty()&&delayed!=null&&Math.abs(delayed.ptsMs-(103603+delay))<=1,"Real file bitmap signed offset "+delay);
            } finally {session.stop();}
        }
        token=context.beginSeek();session=OrdinarySubtitleSession.start(context,token,track,idx,ffmpeg,100000,0,true);
        try {
            long end=System.currentTimeMillis()+15000;while(session.running&&System.currentTimeMillis()<end)Thread.sleep(20);
            check(!session.running&&session.error.isEmpty(),"Genuine forced-only decoder completes without an error");
            // This sample's normal cues are not marked forced. A zero-cue result
            // is filtering, not a fabricated forced-subtitle positive.
            check(session.cues==0,"Unforced genuine sample produces no forced-only bitmap");
        } finally {session.stop();}
    }
}
