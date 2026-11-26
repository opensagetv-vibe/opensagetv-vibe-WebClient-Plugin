package org.opensagetv.webplayer;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.Proxy;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.function.BooleanSupplier;

/** Optional FFmpeg/MIM-owned source images, NOT a Web transcoder or playback
 * session. The browser supplies only its current source epoch and a position;
 * the bridge resolves the known SageTV library file. Opaque preview leases
 * stay here and can neither seek nor start an A/V producer. */
final class SharedSourcePreview {
    interface Exchange { Reply call(String method,String path)throws Exception; }
    static final class Reply {
        final int status;final byte[] bytes;final String type,position;
        Reply(int status,byte[] bytes,String type,String position){this.status=status;this.bytes=bytes;this.type=type;this.position=position;}
        String text(){return new String(bytes,StandardCharsets.UTF_8);}
    }
    static final class Image {
        final byte[] jpeg;final long positionMs;
        Image(byte[] jpeg,long positionMs){this.jpeg=jpeg;this.positionMs=positionMs;}
    }
    private static final ThreadPoolExecutor CLEANUP=new ThreadPoolExecutor(0,1,30,TimeUnit.SECONDS,
            new ArrayBlockingQueue<Runnable>(4),task->{Thread t=new Thread(task,"web-preview-retire");t.setDaemon(true);return t;});
    private final Exchange exchange;
    private long generation,expiresAt;
    private String key="",token="";
    private boolean busy;
    SharedSourcePreview(){this(SharedSourcePreview::loopback);}
    SharedSourcePreview(Exchange exchange){this.exchange=exchange;}

    /** No network under a native-media/UI monitor. Provider TTL is the final
     * bound if the finite cleanup queue is already full or its HTTP fails. */
    void reset(){final String previous;synchronized(this){generation++;key="";previous=token;token="";expiresAt=0;}
        if(!previous.isEmpty())try{CLEANUP.execute(()->retire(previous));}catch(java.util.concurrent.RejectedExecutionException full){/* 120s provider expiry. */}
    }
    Image image(String sourceKey,String source,long position,BooleanSupplier current){
        if(sourceKey==null||sourceKey.isEmpty()||source==null||source.isEmpty()||position<0||position>14L*86400000L||!current.getAsBoolean())return null;
        final long epoch;String lease,previous="";
        synchronized(this){
            if(busy)return null;busy=true;
            if(!key.equals(sourceKey)||System.currentTimeMillis()>=expiresAt){generation++;previous=token;token="";key=sourceKey;}
            epoch=generation;lease=token;
        }
        try{
            if(!previous.isEmpty())retire(previous);
            if(lease.isEmpty()){
                Reply caps=exchange.call("GET","/v1/capabilities");
                java.util.regex.Matcher section=java.util.regex.Pattern.compile("\"mimDirect\"\\s*:\\s*(\\{[^{}]*\\})").matcher(caps.text());
                if(caps.status!=200||!section.find())return null;
                String offered=section.group(1).replaceAll("\\s+","");
                if(!offered.matches("(?s).*\"available\":true[,}].*")||!offered.matches("(?s).*\"contractVersion\":1[,}].*")
                        ||!offered.matches("(?s).*\"sourcePreviewLeaseRevision\":1[,}].*"))return null;
                if(!valid(epoch,current))return null;
                Reply reserved=exchange.call("POST","/v1/previews/reserve?source="+URLEncoder.encode(source,"UTF-8"));
                java.util.regex.Matcher match=java.util.regex.Pattern.compile("\"previewToken\"\\s*:\\s*\"([0-9a-f]{64})\"").matcher(reserved.text());
                if(reserved.status!=200||!match.find())return null;
                lease=match.group(1);
                if(!valid(epoch,current)){retire(lease);return null;}
                synchronized(this){if(generation!=epoch){retireAsync(lease);return null;}token=lease;expiresAt=System.currentTimeMillis()+100000;}
            }
            if(!valid(epoch,current))return null;
            Reply reply=exchange.call("POST","/v1/previews/image?previewToken="+lease+"&positionMs="+position);
            if(!valid(epoch,current)||reply.status!=200||!"image/jpeg".equalsIgnoreCase(reply.type)
                    ||reply.position==null||!reply.position.matches("[0-9]{1,12}")||!boundedJpeg(reply.bytes))return null;
            long actual=Long.parseLong(reply.position);if(actual<0||actual>14L*86400000L)return null;
            return new Image(reply.bytes,actual);
        }catch(Exception unavailable){return null;}
        finally{synchronized(this){busy=false;}}
    }
    private boolean valid(long epoch,BooleanSupplier current){boolean ours;synchronized(this){ours=generation==epoch;}return ours&&current.getAsBoolean();}
    private void retireAsync(final String previous){try{CLEANUP.execute(()->retire(previous));}catch(java.util.concurrent.RejectedExecutionException full){/* Provider expiry. */}}
    private void retire(String previous){try{exchange.call("POST","/v1/previews/teardown?previewToken="+previous);}catch(Exception unavailable){/* Provider expiry. */}}

    /** Read only SOF metadata, never decode untrusted compressed pixels on a
     * servlet thread. The qualified producer emits exactly192x108 MJPEG. */
    static boolean boundedJpeg(byte[] bytes){
        if(bytes==null||bytes.length<4||bytes.length>32768||(bytes[0]&255)!=255||(bytes[1]&255)!=216
                ||(bytes[bytes.length-2]&255)!=255||(bytes[bytes.length-1]&255)!=217)return false;
        for(int i=2;i+3<bytes.length;){
            if((bytes[i++]&255)!=255)return false;
            int marker=bytes[i++]&255;while(marker==255&&i<bytes.length)marker=bytes[i++]&255;
            if(marker==0||marker==218||marker==217)return false;
            if(marker==216||marker==1||marker>=208&&marker<=215)continue;
            if(i+1>=bytes.length)return false;
            int length=(bytes[i]&255)*256+(bytes[i+1]&255);if(length<2||i+length>bytes.length)return false;
            if((marker>=192&&marker<=195)||(marker>=197&&marker<=199)||(marker>=201&&marker<=203)||(marker>=205&&marker<=207)){
                return length>=8&&((bytes[i+3]&255)*256+(bytes[i+4]&255))==108
                        &&((bytes[i+5]&255)*256+(bytes[i+6]&255))==192;
            }
            i+=length;
        }
        return false;
    }
    private static Reply loopback(String method,String path)throws Exception{
        int port=Integer.getInteger("sagetv.webplayer.previewApiPort",31910);
        if(port<1||port>65535)throw new java.io.IOException("preview_unavailable");
        HttpURLConnection connection=(HttpURLConnection)new URL("http://127.0.0.1:"+port+path).openConnection(Proxy.NO_PROXY);
        long deadline=System.nanoTime()+8000000000L;
        connection.setInstanceFollowRedirects(false);connection.setConnectTimeout(500);connection.setReadTimeout(4000);connection.setRequestMethod(method);
        try{
            int status=connection.getResponseCode();InputStream input=status>=400?connection.getErrorStream():connection.getInputStream();
            ByteArrayOutputStream bytes=new ByteArrayOutputStream();
            if(input!=null)try(InputStream owned=input){byte[] buffer=new byte[2048];int count;
                while(true){long remaining=(deadline-System.nanoTime())/1000000L;if(remaining<=0)throw new java.io.IOException("preview_timeout");
                    connection.setReadTimeout((int)Math.max(1,Math.min(4000,remaining)));count=owned.read(buffer);if(count<0)break;
                    if(bytes.size()+count>32768)throw new java.io.IOException("preview_too_large");bytes.write(buffer,0,count);}
            }
            return new Reply(status,bytes.toByteArray(),connection.getContentType(),connection.getHeaderField("X-Vibe-Preview-Position-Ms"));
        }finally{connection.disconnect();}
    }
}
