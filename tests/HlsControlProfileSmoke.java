package org.opensagetv.webplayer;

import java.io.PrintWriter;
import java.io.File;
import java.io.StringWriter;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/** Public HLS validation must happen before any SageTV source/encoder access. */
public final class HlsControlProfileSmoke {
    static int checks;
    static void check(boolean result,String message) {
        if(!result)throw new AssertionError(message);
        checks++;System.out.println("PASS "+message);
    }
    static final class Exchange {
        final Map<String,String> params=new HashMap<>();
        final StringWriter body=new StringWriter();
        int status=200;
        final HttpServletRequest request=(HttpServletRequest)Proxy.newProxyInstance(
            getClass().getClassLoader(),new Class[]{HttpServletRequest.class},(p,m,a)->
                "getParameter".equals(m.getName())?params.get(a[0]):null);
        final HttpServletResponse response=(HttpServletResponse)Proxy.newProxyInstance(
            getClass().getClassLoader(),new Class[]{HttpServletResponse.class},(p,m,a)-> {
                if("setStatus".equals(m.getName()))status=(Integer)a[0];
                if("getWriter".equals(m.getName()))return new PrintWriter(body);
                return null;
            });
        Exchange(){params.put("id","1");params.put("action","start");}
    }
    public static void main(String[] args)throws Exception {
        Exchange invalid=new Exchange();
        invalid.params.put("stream_profileSchemaVersion","999");
        new HlsControlServlet().doPost(invalid.request,invalid.response);
        check(invalid.status==400&&invalid.body.toString().contains("profileSchemaVersion"),
            "invalid marked profile is rejected before SageTV source access");
        Exchange legacy=new Exchange();
        legacy.params.put("stream_videoKbps","nonsense");
        check(HlsControlServlet.requestOptions(legacy.request)==null,
            "unmarked legacy requests retain null-options legacy path");
        Exchange marked=new Exchange();
        marked.params.put("stream_profileSchemaVersion","8");
        marked.params.put("stream_videoMode","transcode");
        marked.params.put("stream_videoKbps","1000");
        marked.params.put("stream_resolution","480");
        marked.params.put("stream_encoder","qsv");
        StreamOptions options=HlsControlServlet.requestOptions(marked.request);
        check(options.videoKbps==1000&&"480".equals(options.resolution)&&"qsv".equals(options.encoder),
            "marked request retains validated bitrate, height and hardware choice");
        check(!options.ts()&&"hls".equals(options.player),"default Auto becomes HLS on playlist endpoint");
        MediaProbe.Info source=new MediaProbe.Info();
        MediaProbe.Track video=new MediaProbe.Track();
        video.index=0;video.type="video";video.codec="mpeg2video";
        video.width=1920;video.height=1080;video.field="tt";video.rate="30000/1001";
        source.tracks.add(video);
        TranscoderManager.Probe qsv=new TranscoderManager.Probe(true,"/usr/bin/ffmpeg","test",
            "h264_qsv",true,true,true,"QSV","Intel Quick Sync","test full hardware");
        List<String> command=StreamCommand.build(qsv,new File("/tmp/source.ts"),false,false,0,
            new File("/tmp/out"),new StreamPlan(options,source));
        check(command.contains("1000k")&&!command.contains("8M"),"production planner uses requested 1Mbps, not legacy 8Mbps");
        check(command.contains("h264_qsv")&&command.contains("qsv")&&command.contains("-forced_idr"),
            "profile retains GPU decode/encode and independently decodable HLS boundaries");
        marked.params.put("stream_player","mpegts");
        marked.params.put("stream_videoMode","copy");marked.params.put("stream_resolution","source");
        marked.params.put("stream_audioCodec","copy");marked.params.put("stream_allowFallback","false");
        options=HlsControlServlet.requestOptions(marked.request);
        check(!options.ts()&&"copy".equals(options.videoMode)&&"copy".equals(options.audioCodec)&&!options.allowFallback,
            "delivery normalization preserves strict Copy and audio policy");
        for(String[] pair:new String[][]{{"stream_videoKbps","249"},{"stream_resolution","999"},
            {"stream_encoder","arbitrary"},{"stream_player","arbitrary"}}) {
            Exchange bad=new Exchange();bad.params.put("stream_profileSchemaVersion","8");
            bad.params.put(pair[0],pair[1]);new HlsControlServlet().doPost(bad.request,bad.response);
            check(bad.status==400,"invalid "+pair[0]+" rejected before producer access");
        }
        Exchange independent=new Exchange();independent.params.put("stream_profileSchemaVersion","8");
        check(HlsControlServlet.requestOptions(independent.request).videoKbps==8000,
            "per-request changes do not alter another request's defaults");
        System.out.println("HLS public profile: "+checks+" PASS");
    }
}
