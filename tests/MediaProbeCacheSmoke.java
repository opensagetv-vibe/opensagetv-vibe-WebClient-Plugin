package org.opensagetv.webplayer;

import java.nio.file.*;
import java.nio.file.attribute.FileTime;
import java.io.*;

/** Deterministic cache identity/ownership tests, not playback certification. */
public final class MediaProbeCacheSmoke {
    static int checks,reads;
    static void ok(boolean condition,String message){if(!condition)throw new AssertionError(message);checks++;System.out.println("PASS "+message);}
    static MediaProbe.Info info(){reads++;MediaProbe.Info i=new MediaProbe.Info();i.probeMethod="ffprobe";MediaProbe.Track v=new MediaProbe.Track();v.type="video";v.width=1920;v.height=1080;v.codec="mpeg2video";i.tracks.add(v);return i;}
    public static void main(String[] args)throws Exception{
        Path root=Files.createTempDirectory("web045-cache-");Path source=root.resolve("source.ts"),tool=root.resolve("tool"),probe=root.resolve("probe");
        try{
            Files.write(source,new byte[]{1,2,3});Files.write(tool,new byte[]{4});Files.write(probe,new byte[]{5});
            String encoder=tool.toString(),prober=probe.toString();MediaProbeCache cache=new MediaProbeCache(2);
            MediaProbe.Info first=cache.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info);
            MediaProbe.Info hit=cache.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info);
            ok(reads==1&&!first.probeCacheHit&&hit.probeCacheHit,"unchanged completed source avoids another probe");
            hit.video().codec="mutated";hit.tracks.clear();first.video().width=5;
            MediaProbe.Info isolated=cache.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info);
            ok(isolated.video().width==1920&&isolated.video().codec.equals("mpeg2video"),"cache and consumers never share mutable tracks");
            FileTime original=Files.getLastModifiedTime(source);Files.write(source,new byte[]{9,2,3});Files.setLastModifiedTime(source,original);
            ok(!cache.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info).probeCacheHit,"edge fingerprint detects same-size preserved-mtime rewrite");
            Files.write(source,new byte[]{9,2,3,4});ok(!cache.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info).probeCacheHit,"source growth invalidates inventory");
            Files.write(tool,new byte[]{6,7});ok(!cache.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info).probeCacheHit,"encoder identity changes invalidate metadata");
            Files.write(probe,new byte[]{7,8});ok(!cache.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info).probeCacheHit,"probe identity changes invalidate metadata");
            MediaProbeCache failed=new MediaProbeCache(2);int start=reads;
            MediaProbeCache.Reader fail=()->{MediaProbe.Info i=info();i.warning="incomplete";return i;};
            failed.read(source.toFile(),encoder,prober,fail);failed.read(source.toFile(),encoder,prober,fail);
            ok(reads==start+2,"failed or incomplete probe results are not cached");
            start=reads;cache.read(source.toFile(),"missing-tool",prober,MediaProbeCacheSmoke::info);cache.read(source.toFile(),"missing-tool",prober,MediaProbeCacheSmoke::info);
            ok(reads==start+2,"unresolved tool identity disables caching");
            MediaProbeCache race=new MediaProbeCache(2);
            race.read(source.toFile(),encoder,prober,()->{try{Files.write(source,new byte[]{1,1,1,1,1});}catch(IOException e){throw new RuntimeException(e);}return info();});
            ok(!race.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info).probeCacheHit,"file changing during probe is never cached");
            Path other=root.resolve("other.ts"),third=root.resolve("third.ts");Files.write(other,new byte[]{1});Files.write(third,new byte[]{2});
            MediaProbeCache lru=new MediaProbeCache(2);lru.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info);
            lru.read(other.toFile(),encoder,prober,MediaProbeCacheSmoke::info);lru.read(third.toFile(),encoder,prober,MediaProbeCacheSmoke::info);
            ok(!lru.read(source.toFile(),encoder,prober,MediaProbeCacheSmoke::info).probeCacheHit,"LRU capacity is bounded and evicts old sources");
            Files.delete(other);Files.delete(third);
        }finally{
            // Only the explicitly-created ordinary test files, never a recursive
            // delete of a computed workspace/user directory.
            for(String name:new String[]{"source.ts","tool","probe","other.ts","third.ts"})Files.deleteIfExists(root.resolve(name));
            Files.delete(root);
        }
        System.out.println("MediaProbe cache: "+checks+" tests PASS");
    }
}
