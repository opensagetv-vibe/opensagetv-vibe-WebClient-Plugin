package org.opensagetv.webplayer;
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

/** Real native wire framing against a synthetic stock-protocol peer. */
public final class MiniClientFramePacingSmoke {
    public static void main(String[] args)throws Exception{
        ServerSocket listener=new ServerSocket(0,10,InetAddress.getByName("127.0.0.1"));
        ExecutorService executor=Executors.newSingleThreadExecutor();
        CountDownLatch mediaLive=new CountDownLatch(1);
        Future<?> peer=executor.submit(()->{
            try(Socket media=MiniClientProtocolSmoke.acceptHandshake(listener,1);
                Socket gfx=MiniClientProtocolSmoke.acceptHandshake(listener,0)){
                OutputStream out=gfx.getOutputStream();InputStream in=gfx.getInputStream();
                out.write(new byte[]{16,0,0,4,1,0,0,4});out.flush();MiniClientProtocolSmoke.replyPayload(in,16);
                out.write(new byte[]{16,0,0,4,31,0,0,0,16,0,0,4,30,0,0,0});out.flush();
                // While GFX awaits its real frame, media time must still reply.
                media.getOutputStream().write(new byte[]{17,0,0,0});media.getOutputStream().flush();
                MiniClientProtocolSmoke.readN(media.getInputStream(),4);mediaLive.countDown();
                gfx.setSoTimeout(100);
                try{in.read();throw new AssertionError("FLIP replied before browser ACK");}
                catch(SocketTimeoutException expected){}
                finally{gfx.setSoTimeout(3000);}
                MiniClientProtocolSmoke.replyPayload(in,16);
                MiniClientProtocolSmoke.replyPayload(in,192);
                MiniClientProtocolSmoke.replyPayload(in,193);
            }catch(Exception error){throw new RuntimeException(error);}
        });
        MiniClientSession session=new MiniClientSession("paced","127.0.0.1:"+listener.getLocalPort(),"02:00:00:00:00:29",640,360,false,true);
        try{
            session.start();int sequence=-1;
            long deadline=System.currentTimeMillis()+3000;
            while(sequence<0&&System.currentTimeMillis()<deadline){
                for(String event:session.pollEvents(500,100)){
                    if(event.contains("\"cmd\":30")&&event.contains("\"ackRequired\":true")){
                        java.util.regex.Matcher matcher=java.util.regex.Pattern.compile("\"seq\":([0-9]+)").matcher(event);
                        if(matcher.find())sequence=Integer.parseInt(matcher.group(1));
                    }
                }
            }
            if(sequence<0||!mediaLive.await(500,TimeUnit.MILLISECONDS))throw new AssertionError("paced frame/media reply absent");
            Thread.sleep(150);
            if(!session.acknowledgeFrame(sequence))throw new AssertionError("matching frame ACK rejected");
            peer.get(5,TimeUnit.SECONDS);
            System.out.println("PASS native FLIP waits for browser ACK; independent media reply and first-frame resize/repaint stay live");
        }finally{session.close();listener.close();executor.shutdownNow();}
    }
}
