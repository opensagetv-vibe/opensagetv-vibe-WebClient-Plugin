package org.opensagetv.webplayer;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.Proxy;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Optional existing navigator, not a second navigator/transcoder or required
 * service. Only a fixed loopback endpoint and closed production operations.
 * Opaque per-load challenges never leave this Java owner or enter reports. */
final class CompanionDvdClient {
    interface Exchange { Reply call(String method,String path)throws Exception; }
    static final class Reply { final int status;final String body;Reply(int status,String body){this.status=status;this.body=body;} }
    private static final Pattern CHALLENGE=Pattern.compile("\\{\\s*\"protocol\"\\s*:\\s*1\\s*,\\s*\"profiles\"\\s*:\\s*\\[\\s*\"web-mpegps-v1\"\\s*\\]\\s*,\\s*\"challenge\"\\s*:\\s*\"([0-9a-f]{32})\"\\s*\\}");
    private final Exchange exchange;
    private String client="",challenge="",state="off",actionOutcome="none";
    private boolean controls;
    private long generation;
    CompanionDvdClient(){this(CompanionDvdClient::loopback);}
    CompanionDvdClient(Exchange exchange){this.exchange=exchange;}
    synchronized void reset(){generation++;client="";challenge="";state="off";controls=false;actionOutcome="none";}
    void negotiate(String identity){
        if(identity==null||!identity.replace(":","").matches("(?i)[0-9a-f]{12}"))return;
        final String selected=identity.replace(":","").toLowerCase(java.util.Locale.ROOT);final long epoch;
        synchronized(this){reset();epoch=generation;state="unavailable";}
        try{
            Reply offer=exchange.call("GET","/vibe/dvd/client?client="+selected);
            if(offer.status!=200)return;
            Matcher match=CHALLENGE.matcher(offer.body.trim());
            if(!match.matches()){synchronized(this){if(generation==epoch)state="unsupported-profile";}return;}
            String nonce=match.group(1);
            Reply accepted=exchange.call("POST","/vibe/dvd/client?client="+selected+"&challenge="+nonce+"&revision=4&profile=web-mpegps-v1");
            if(!accepted(accepted))return;
            Reply actions=exchange.call("GET","/vibe/dvd/controls?client="+selected);
            boolean available=actions.status==200&&actions.body.matches("\\{\\s*\"protocol\"\\s*:\\s*1\\s*,\\s*\"challenge\"\\s*:\\s*\""+nonce+"\"\\s*\\}");
            synchronized(this){if(generation!=epoch)return;client=selected;challenge=nonce;controls=available;state="ready-native-ps";}
        }catch(Exception unavailable){/* Missing/off/slow service leaves stock DVD intact. */}
    }
    boolean action(String operation){
        if(!("beginning".equals(operation)||"resume".equals(operation)||"save_resume".equals(operation)||"clear_resume".equals(operation)))throw new IllegalArgumentException("Unknown DVD operation");
        final String selected,nonce;final long epoch;
        synchronized(this){if(!controls||challenge.isEmpty())return false;selected=client;nonce=challenge;epoch=generation;actionOutcome="pending";}
        try{
            Reply reply=exchange.call("POST","/vibe/dvd/controls?client="+selected+"&challenge="+nonce+"&operation="+operation);
            synchronized(this){
                if(generation!=epoch||!controls||!nonce.equals(challenge))return false;
                if(!accepted(reply)){actionOutcome="rejected";if(reply.status==404||reply.status==410){controls=false;state="actions-unavailable";}return false;}actionOutcome="accepted";return true;
            }
        }catch(Exception unavailable){synchronized(this){if(generation==epoch&&nonce.equals(challenge))actionOutcome="unknown";}return false;}
    }
    synchronized String json(){return "{\"schemaVersion\":1,\"loadGeneration\":"+generation+",\"state\":\""+state+"\",\"controls\":"+controls+",\"actionOutcome\":\""+actionOutcome+"\",\"profile\":\""+(challenge.isEmpty()?"":"web-mpegps-v1")+"\"}";}
    private static boolean accepted(Reply reply){return reply.status==200&&reply.body.matches("\\{\\s*\"accepted\"\\s*:\\s*true\\s*\\}");}
    private static Reply loopback(String method,String path)throws Exception{
        return loopback(method,path,8273);
    }
    /** Port injection is package-local for isolated real-HTTP regression tests. */
    static Reply loopback(String method,String path,int port)throws Exception{
        if(port<1||port>65535)throw new IllegalArgumentException("Invalid loopback port");
        boolean action="POST".equals(method)&&path.startsWith("/vibe/dvd/controls?");
        HttpURLConnection connection=(HttpURLConnection)new URL("http://127.0.0.1:"+port+path).openConnection(Proxy.NO_PROXY);
        // Negotiation stays short on the media reader. Explicit user actions
        // run on their own HTTP worker and can wait for the bounded provider
        // control lock; a timeout is UNKNOWN, never an automatic POST replay.
        final long deadline=System.nanoTime()+(action?1500000000L:250000000L);
        connection.setConnectTimeout(100);connection.setReadTimeout(action?1000:100);connection.setInstanceFollowRedirects(false);connection.setRequestMethod(method);
        try{
            int status=connection.getResponseCode();InputStream input=status>=400?connection.getErrorStream():connection.getInputStream();
            if(input==null)return new Reply(status,"");
            try{ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[512];int count;
                while(true){if(System.nanoTime()>deadline)throw new java.io.IOException("Companion reply deadline");count=input.read(buffer);if(count==-1)break;
                    if(bytes.size()+count>4096)throw new java.io.IOException("Oversized companion reply");bytes.write(buffer,0,count);}
                return new Reply(status,new String(bytes.toByteArray(),StandardCharsets.UTF_8));
            }finally{input.close();}
        }finally{connection.disconnect();}
    }
}
