package org.opensagetv.webplayer;

import java.io.File;
import java.util.*;

/** Command-level coverage for full hardware decode+encode attempts on every GPU backend. */
public final class HardwarePipelineSmoke {
    static int n;
    static void ok(boolean v,String m){if(!v)throw new AssertionError(m);n++;System.out.println("PASS "+m);}
    static boolean hasPair(List<String> c,String a,String b){for(int i=0;i+1<c.size();i++)if(a.equals(c.get(i))&&b.equals(c.get(i+1)))return true;return false;}
    static StreamPlan plan(){
        MediaProbe.Info i=new MediaProbe.Info();
        MediaProbe.Track v=new MediaProbe.Track();v.index=0;v.type="video";v.codec="mpeg2video";v.width=1920;v.height=1080;v.field="tt";v.rate="30000/1001";i.tracks.add(v);
        MediaProbe.Track a=new MediaProbe.Track();a.index=1;a.type="audio";a.codec="ac3";a.channels=6;a.language="eng";i.tracks.add(a);
        Map<String,String> m=new HashMap<String,String>();m.put("player","hls");m.put("videoMode","transcode");m.put("resolution","720");m.put("fps","59.94");m.put("deinterlace","auto");m.put("audioCodec","aac");m.put("allowFallback","true");
        return new StreamPlan(StreamOptions.fromMap(m),i);
    }
    static TranscoderManager.Probe p(String enc,String dec,boolean filters,String name){return new TranscoderManager.Probe(true,"/usr/bin/ffmpeg","test",enc,true,true,filters,dec,name,"test full hardware");}
    static List<String> cmd(TranscoderManager.Probe p){return StreamCommand.build(p,new File("/tmp/source.ts"),false,false,0,new File("/tmp/out"),plan());}
    public static void main(String[] args){
        Map<String,String> dvdPrefs=new HashMap<String,String>();dvdPrefs.put("player","mpegts");dvdPrefs.put("videoMode","copy");dvdPrefs.put("encoder","qsv");dvdPrefs.put("audioCodec","copy");
        StreamOptions dvdOptions=StreamOptions.fromMap(dvdPrefs).forDvdTranscode();
        ok("hls".equals(dvdOptions.player)&&"transcode".equals(dvdOptions.videoMode)&&"qsv".equals(dvdOptions.encoder)&&"aac".equals(dvdOptions.audioCodec),"DVD forces H.264/AAC HLS while preserving selected hardware encoder");

        List<String> q=cmd(p("h264_qsv","QSV",true,"Intel Quick Sync"));
        ok(hasPair(q,"-hls_time","1"),"local transcode uses an actual one-second HLS target");
        List<String> pipe=StreamCommand.build(p("h264_qsv","QSV",true,"Intel Quick Sync"),new File("/tmp/source.ts"),false,true,0,new File("/tmp/out"),plan());
        ok(hasPair(pipe,"-hls_time","3"),"DVD/remote pipe preserves its established HLS cadence");
        List<String> concat=StreamCommand.build(p("h264_qsv","QSV",true,"Intel Quick Sync"),new File("/tmp/source.ts"),true,false,0,new File("/tmp/out"),plan());
        ok(hasPair(concat,"-hls_time","3"),"concat input preserves its established HLS cadence");
        ok(hasPair(q,"-hwaccel","qsv")&&hasPair(q,"-hwaccel_output_format","qsv"),"QSV attempts hardware decode surfaces");
        List<String> dvdQsv=TranscoderManager.buildDvdHlsCommand(p("h264_qsv","QSV",true,"Intel Quick Sync"),0xbd80,new File("/tmp/dvd-hls"));
        int dvdInput=dvdQsv.indexOf("-i"),dvdHw=dvdQsv.indexOf("-hwaccel");
        ok(dvdHw>=0&&dvdInput>=0&&dvdHw<dvdInput,"DVD QSV hardware decode options precede the MPEG-PS input");
        ok(hasPair(dvdQsv,"-c:v","h264_qsv")&&hasPair(dvdQsv,"-c:a","aac"),"DVD path always transcodes MPEG-2 video to browser H.264/AAC");
        ok(hasPair(dvdQsv,"-map","0:i:0x80?"),"DVD physical audio mapping is optional for silent menu/still cells");
        ok(q.get(q.indexOf("-vf")+1).contains("vpp_qsv")&&q.get(q.indexOf("-vf")+1).contains("deinterlace=advanced")&&q.get(q.indexOf("-vf")+1).contains("framerate=60000/1001"),"QSV uses hardware VPP deinterlace/scale/FPS");
        ok(hasPair(q,"-c:v","h264_qsv"),"QSV hardware encode remains selected");
        ok(hasPair(q,"-forced_idr","1"),"QSV HLS forced keyframes are IDR segment boundaries");
        List<String> defaultQsv=TranscoderManager.buildHlsCommand(p("h264_qsv","QSV",true,"Intel Quick Sync"),null,false,true,0,0,new File("/tmp/default-hls"));
        ok(hasPair(defaultQsv,"-forced_idr","1"),"default public HLS pipe also requests QSV IDR before growing-file EOF");
        ok(hasPair(defaultQsv,"-hwaccel_output_format","qsv")&&defaultQsv.get(defaultQsv.indexOf("-vf")+1).contains("vpp_qsv"),"default HLS retains GPU decode/filter/encode");

        Map<String,String> tsPrefs=new HashMap<String,String>();tsPrefs.put("player","mpegts");tsPrefs.put("videoMode","transcode");
        StreamPlan tsPlan=new StreamPlan(StreamOptions.fromMap(tsPrefs),plan().source);
        List<String> ts=StreamCommand.build(p("h264_qsv","QSV",true,"Intel Quick Sync"),new File("/tmp/source.ts"),false,false,0,new File("/tmp/out"),tsPlan);
        ok(!ts.contains("-forced_idr"),"continuous MPEG-TS retains its existing keyframe policy");
        Map<String,String> copyPrefs=new HashMap<String,String>();copyPrefs.put("player","hls");copyPrefs.put("videoMode","copy");
        List<String> copy=StreamCommand.build(p("h264_qsv","QSV",true,"Intel Quick Sync"),new File("/tmp/source.ts"),false,false,0,new File("/tmp/out"),new StreamPlan(StreamOptions.fromMap(copyPrefs),plan().source));
        ok(hasPair(copy,"-c:v","copy")&&!copy.contains("-forced_idr"),"Copy never receives an encoder-only IDR option");
        ok(hasPair(copy,"-hls_time","3"),"Copy segment target remains unchanged");

        List<String> nv=cmd(p("h264_nvenc","CUDA/NVDEC",true,"NVIDIA NVENC"));
        ok(hasPair(nv,"-hwaccel","cuda")&&hasPair(nv,"-hwaccel_output_format","cuda"),"NVIDIA attempts NVDEC/CUDA decode surfaces");
        ok(nv.get(nv.indexOf("-vf")+1).contains("yadif_cuda")&&nv.get(nv.indexOf("-vf")+1).contains("scale_cuda"),"NVIDIA uses CUDA deinterlace/scale");
        ok(hasPair(nv,"-c:v","h264_nvenc"),"NVIDIA hardware encode remains selected");

        List<String> va=cmd(p("h264_vaapi","VAAPI",true,"VAAPI"));
        ok(hasPair(va,"-hwaccel","vaapi")&&hasPair(va,"-hwaccel_output_format","vaapi"),"VAAPI attempts hardware decode surfaces");
        ok(va.get(va.indexOf("-vf")+1).contains("deinterlace_vaapi")&&va.get(va.indexOf("-vf")+1).contains("scale_vaapi"),"VAAPI uses hardware deinterlace/scale");
        ok(hasPair(va,"-c:v","h264_vaapi"),"VAAPI hardware encode remains selected");

        List<String> amf=cmd(p("h264_amf","D3D11VA",false,"AMD AMF"));
        ok(hasPair(amf,"-hwaccel","d3d11va"),"AMD AMF path attempts D3D11VA hardware decode");
        ok(amf.get(amf.indexOf("-vf")+1).contains("yadif")&&amf.get(amf.indexOf("-vf")+1).contains("format=nv12"),"AMD keeps software filters only when GPU VPP is unavailable");
        ok(hasPair(amf,"-c:v","h264_amf"),"AMD hardware encode remains selected");

        List<String> vt=cmd(p("h264_videotoolbox","VideoToolbox",false,"Apple VideoToolbox"));
        ok(hasPair(vt,"-hwaccel","videotoolbox"),"VideoToolbox path attempts hardware decode");
        ok(hasPair(vt,"-c:v","h264_videotoolbox"),"VideoToolbox hardware encode remains selected");
        ok(!nv.contains("-forced_idr")&&!va.contains("-forced_idr")&&!amf.contains("-forced_idr")&&!vt.contains("-forced_idr"),"QSV-specific option never reaches other hardware encoders");
        TranscoderManager.Probe software=new TranscoderManager.Probe(true,"/usr/bin/ffmpeg","test","libx264",false,false,false,"","Software","test");
        ok(!cmd(software).contains("-forced_idr"),"Software fallback never receives a QSV-only codec option");

        TranscoderManager.Probe mixed=TranscoderManager.encodeOnlyFallback(p("h264_qsv","QSV",true,"Intel Quick Sync"),"decode startup failed");
        ok(mixed.hardware&&!mixed.hardwareDecode&&"h264_qsv".equals(mixed.videoEncoder),"decode failure falls back to hardware encode before software encode");
        ok(hasPair(TranscoderManager.buildHlsCommand(mixed,null,false,true,0,0,new File("/tmp/default-hls")),"-forced_idr","1"),"default QSV encode-only fallback retains IDR boundaries");
        List<String> mixedCmd=cmd(mixed);ok(!mixedCmd.contains("-hwaccel")&&hasPair(mixedCmd,"-c:v","h264_qsv"),"encode-only retry removes hardware decode but keeps QSV encode");
        Map<String,String> configured=new HashMap<String,String>();configured.put("videoKbps","4500");configured.put("audioOffsetMs","250");configured.put("deinterlaceFilter","bwdif");
        StreamOptions custom=StreamOptions.fromMap(configured);
        List<String> currentDvd=TranscoderManager.buildDvdHlsCommand(mixed,0xbd80,new File("/tmp/dvd-hls"),custom);
        ok(hasPair(currentDvd,"-forced_idr","1"),"current DVD QSV HLS uses independently decodable boundaries even in encode-only fallback");
        ok(hasPair(currentDvd,"-async_depth","1"),"DVD QSV bounds concurrent encoder surfaces without disabling GPU encoding");
        ok(hasPair(TranscoderManager.buildDvdHlsCommand(p("h264_qsv","QSV",true,"Intel Quick Sync"),0xbd80,new File("/tmp/dvd-hls"),custom),"-async_depth","1"),"full-hardware DVD QSV uses the same bounded encoder queue");
        ok(!q.contains("-async_depth")&&!mixedCmd.contains("-async_depth"),"ordinary QSV TV and recording queues stay unchanged");
        for(TranscoderManager.Probe other:Arrays.asList(p("h264_nvenc","CUDA/NVDEC",true,"NVIDIA"),p("h264_vaapi","VAAPI",true,"VAAPI"),software))
            ok(!TranscoderManager.buildDvdHlsCommand(other,0xbd80,new File("/tmp/dvd-hls"),custom).contains("-async_depth"),"non-QSV DVD never receives a QSV surface option: "+other.videoEncoder);
        for(TranscoderManager.Probe other:Arrays.asList(p("h264_nvenc","CUDA/NVDEC",true,"NVIDIA"),p("h264_vaapi","VAAPI",true,"VAAPI"),software))
            ok(!TranscoderManager.buildHlsCommand(other,null,false,true,0,0,new File("/tmp/default-hls")).contains("-forced_idr"),"default non-QSV HLS excludes QSV-only IDR option: "+other.videoEncoder);
        ok(hasPair(currentDvd,"-b:v","4500k")&&currentDvd.get(currentDvd.indexOf("-af")+1).contains("adelay=250"),"DVD uses actual per-client bitrate/audio offset instead of fixed constants");
        ok(currentDvd.get(currentDvd.indexOf("-vf")+1).contains("bwdif")&&!StreamCommand.usesGpuFilters(mixed,TranscoderManager.dvdCommandPlan(custom)),"explicit BWDIF is honestly a Software filter");
        ok(hasPair(currentDvd,"-map","0:i:0x80?"),"new DVD policy preserves optional physical audio mapping");
        List<String> silent=TranscoderManager.buildDvdHlsCommand(mixed,-1,new File("/tmp/dvd-hls"),custom);
        ok(hasPair(silent,"-map","0:a:0?"),"silent DVD menu never requires fabricated audio index");
        System.out.println("Hardware pipeline: "+n+" tests PASS");
    }
}
