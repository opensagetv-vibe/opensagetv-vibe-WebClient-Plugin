package org.opensagetv.webplayer;

import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.util.*;

/** WEB-045: bounded process-local cache for explicitly completed local sources.
 * Only embedded probe metadata is cached. Transport-service/sidecar discovery
 * runs again per caller; consumers always receive independent mutable tracks.
 * Active files and remote samples must never enter this cache.
 */
final class MediaProbeCache {
    interface Reader { MediaProbe.Info read(); }
    private static final class Entry {
        final String signature; final MediaProbe.Info info;
        Entry(String signature,MediaProbe.Info info){this.signature=signature;this.info=copy(info);}
    }
    private final int capacity;
    private final LinkedHashMap<String,Entry> entries=new LinkedHashMap<String,Entry>(16,.75f,true);
    MediaProbeCache(int capacity){this.capacity=Math.max(1,Math.min(128,capacity));}

    MediaProbe.Info read(File source,String encoder,String probe,Reader reader){
        String key=null,before=null;
        try{key=source.getCanonicalPath();before=signature(source,encoder,probe);}catch(Exception ignored){}
        if(before!=null){synchronized(entries){Entry e=entries.get(key);if(e!=null&&before.equals(e.signature)){MediaProbe.Info hit=copy(e.info);hit.probeCacheHit=true;return hit;}entries.remove(key);}}
        MediaProbe.Info result=reader.read();
        // Never turn an incomplete/failed/fallback inventory into durable truth.
        if(before!=null&&"ffprobe".equals(result.probeMethod)&&result.warning.isEmpty()&&
                result.video()!=null&&result.video().width>0&&result.video().height>0){
            try{if(before.equals(signature(source,encoder,probe))){synchronized(entries){
                entries.put(key,new Entry(before,result));
                while(entries.size()>capacity)entries.remove(entries.keySet().iterator().next());
            }}}catch(Exception ignored){}
        }
        return result;
    }
    private static String signature(File source,String encoder,String probe)throws Exception{
        if(encoder==null||probe==null||!new File(encoder).isFile()||!new File(probe).isFile())return null;
        MessageDigest hash=MessageDigest.getInstance("SHA-256");
        BasicFileAttributes a=Files.readAttributes(source.toPath(),BasicFileAttributes.class);
        if(!a.isRegularFile()||a.size()==0)return null;
        try(RandomAccessFile f=new RandomAccessFile(source,"r")){
            byte[] b=new byte[4096];int n=f.read(b);if(n>0)hash.update(b,0,n);
            if(a.size()>4096){f.seek(Math.max(4096,a.size()-4096));n=f.read(b);if(n>0)hash.update(b,0,n);}
        }
        return attributes(source)+"|"+attributes(new File(encoder))+"|"+attributes(new File(probe))+"|"+Arrays.toString(hash.digest());
    }
    private static String attributes(File file)throws IOException{
        Path path=file.toPath().toRealPath();BasicFileAttributes a=Files.readAttributes(path,BasicFileAttributes.class);
        return path+":"+a.fileKey()+":"+a.size()+":"+a.lastModifiedTime();
    }
    private static MediaProbe.Info copy(MediaProbe.Info source){
        MediaProbe.Info result=new MediaProbe.Info();result.warning=source.warning;result.probeMethod=source.probeMethod;
        for(MediaProbe.Track track:source.tracks)result.tracks.add(track.copy());
        return result;
    }
}
