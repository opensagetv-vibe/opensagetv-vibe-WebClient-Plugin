package org.opensagetv.webplayer;
import java.io.File;
import java.lang.reflect.Field;
import java.util.*;

/** Isolated real-bridge policy only: no encoder, network, Core or field claim. */
public final class CopyFallbackPolicySmoke {
    static int checks;
    static void check(boolean v,String why){if(!v)throw new AssertionError(why);checks++;System.out.println("PASS "+why);}
    static void set(Object o,String key,Object v)throws Exception{Field f=o.getClass().getDeclaredField(key);f.setAccessible(true);f.set(o,v);}
    static Object get(Object o,String key)throws Exception{Field f=o.getClass().getDeclaredField(key);f.setAccessible(true);return f.get(o);}
    static StreamOptions options(String player,String mode,boolean allow){Map<String,String> m=new HashMap<>();m.put("player",player);m.put("videoMode",mode);m.put("allowFallback",String.valueOf(allow));return StreamOptions.fromMap(m);}
    static MiniClientSession owner(){return new MiniClientSession("copy-policy","127.0.0.1","020000000069",640,360,false);}
    static MiniClientMediaBridge seed(MiniClientSession owner,StreamOptions options)throws Exception{
        MiniClientMediaBridge b=owner.media();b.configure(options);set(b,"activeOptions",options);
        // mediaId intentionally zero: accepted policy cannot launch a producer.
        HlsSessionManager.Session s=new HlsSessionManager.Session("synthetic-copy",0,0,0,0,90000,false,new File("build/no-copy-policy-files"),options);
        s.streamPlan=new StreamPlan(options,MediaProbe.parse("streams.stream.0.index=0\nstreams.stream.0.codec_type=video\nstreams.stream.0.codec_name=h264\n"));set(b,"hls",s);return b;
    }
    static void rejects(MiniClientMediaBridge b,boolean decode)throws Exception{try{b.fallback("synthetic-copy",1200,decode);throw new AssertionError("Expected rejection");}catch(IllegalArgumentException expected){}}
    public static void main(String[] args)throws Exception{
        MiniClientSession s=owner();
        try{
            StreamOptions copy=options("mpegts","copy",true);MiniClientMediaBridge b=seed(s,copy);
            check(!b.fallback("retired-source",1200,true)&&get(b,"activeOptions")==copy,"stale codec fallback cannot change active options");
            check(b.fallback("synthetic-copy",1200,true),"confirmed TS Copy codec fallback is accepted by the real bridge policy");
            StreamOptions active=(StreamOptions)get(b,"activeOptions");
            check(active.videoMode.equals("transcode")&&active.player.equals("hls")&&get(b,"configured")==copy,"replacement changes only active representation, not configured defaults");
            rejects(b,true);check(get(b,"activeOptions")==active,"one-shot budget rejects a second codec fallback");
        }finally{s.close();}
        s=owner();try{MiniClientMediaBridge b=seed(s,options("mpegts","copy",true));check(b.fallback("synthetic-copy",1200)&&((StreamOptions)get(b,"activeOptions")).videoMode.equals("copy"),"older default caller preserves TS-to-HLS Copy semantics");}finally{s.close();}
        s=owner();try{StreamOptions strict=options("mpegts","copy",false);MiniClientMediaBridge b=seed(s,strict);rejects(b,true);check(get(b,"activeOptions")==strict&&!((Boolean)get(b,"transportFallback")),"strict Copy refuses codec fallback before consuming budget or mutating options");}finally{s.close();}
        s=owner();try{StreamOptions transcode=options("hls","transcode",true);MiniClientMediaBridge b=seed(s,transcode);rejects(b,true);check(get(b,"activeOptions")==transcode,"codec flag cannot create an extra HLS transcode fallback");}finally{s.close();}
        System.out.println("Copy fallback policy: "+checks+" PASS (isolated policy; no actual producer)");
    }
}
