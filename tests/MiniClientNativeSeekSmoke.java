package org.opensagetv.webplayer;

import java.io.*;
import java.lang.reflect.Field;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.BooleanSupplier;

/** WEB-049: real bridge and native wire, deliberately blocked fake producer.
 * No stock Core mutation, actual encoder, browser pixels or physical claim. */
public final class MiniClientNativeSeekSmoke {
    static int checks;
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);checks++;System.out.println("PASS "+why);}
    static void until(BooleanSupplier ready,String why)throws Exception{
        long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(4);
        while(!ready.getAsBoolean()&&System.nanoTime()<end)Thread.sleep(5);
        check(ready.getAsBoolean(),why);
    }
    static void field(Object o,String name,Object value)throws Exception{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);f.set(o,value);}
    static Object field(Object o,String name)throws Exception{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
    static byte[] seek(long ms)throws Exception{ByteArrayOutputStream b=new ByteArrayOutputStream();new DataOutputStream(b).writeLong(ms);return b.toByteArray();}
    static int clock(MiniClientMediaBridge bridge){return MiniClientSession.readInt(bridge.handle(17,new byte[0]),0);}
    static HlsSessionManager.Session fake(String id,long ms,PlaybackSessionContext c,PlaybackSessionContext.Token t){
        return new HlsSessionManager.Session(id,1,0,0,ms/1000.0,90000,false,new File("build/native-seek-no-files/"+id),StreamOptions.defaults(),c,t);
    }
    static final class Factory implements MiniClientMediaBridge.NativeSeekFactory {
        final CountDownLatch started=new CountDownLatch(1),release=new CountDownLatch(1),cleanupStarted=new CountDownLatch(1),cleanupRelease=new CountDownLatch(1);
        final List<Long> starts=Collections.synchronizedList(new ArrayList<Long>());
        final List<String> stopped=Collections.synchronizedList(new ArrayList<String>());
        volatile boolean fail,holdCleanup;
        public HlsSessionManager.Session start(int id,int seg,long ms,StreamOptions opts,PlaybackSessionContext c,PlaybackSessionContext.Token token)throws Exception{
            starts.add(ms);started.countDown();if(!release.await(5,TimeUnit.SECONDS))throw new IOException("Fixture wait exceeded");
            if(fail)throw new IOException("Deliberate producer preparation failure");
            return fake("seek-"+starts.size()+"-"+ms,ms,c,token);
        }
        public void stop(HlsSessionManager.Session s){
            stopped.add(s.id);
            if(holdCleanup&&s.id.equals("original")){cleanupStarted.countDown();try{cleanupRelease.await(5,TimeUnit.SECONDS);}catch(InterruptedException e){Thread.currentThread().interrupt();}}
        }
        void releaseAll(){release.countDown();cleanupRelease.countDown();}
    }
    static MiniClientSession owner(Factory f){return new MiniClientSession("seek-test","127.0.0.1","02:00:00:00:00:49",640,360,false,false,f);}
    static MiniClientMediaBridge seed(MiniClientSession owner)throws Exception{
        MiniClientMediaBridge b=owner.media();PlaybackSessionContext c=(PlaybackSessionContext)field(b,"playbackContext");
        PlaybackSessionContext.Token token=c.beginSource();field(b,"mediaId",1);field(b,"durationMs",90000L);
        field(b,"browserTimeMs",4000L);field(b,"lastProvenBrowserTimeMs",4000L);field(b,"hls",fake("original",0,c,token));return b;
    }
    static void initOwnership()throws Exception{
        Factory factory=new Factory();MiniClientSession session=owner(factory);MiniClientMediaBridge bridge=seed(session);
        try {
            check(field(bridge,"hls")!=null,"recording producer exists before decoder INIT");
            bridge.handle(0,new byte[4]);
            check(field(bridge,"hls")==null,"fresh decoder INIT retires the preceding ordinary recording owner");
            PlaybackSessionContext context=(PlaybackSessionContext)field(bridge,"playbackContext");
            check(!context.sourceActive(),"INIT invalidates old ordinary source/caption epoch");
            check(!bridge.reportBrowserState("original",42000,640,360,1f,false,false),"late old recording feedback cannot enter fresh DVD INIT");
            check(session.pollEvents(500,10).stream().anyMatch(e->e.contains("\"type\":\"videoStop\"")),"INIT retires browser video before DVD starts");
        } finally {factory.releaseAll();session.close();}
    }
    public static void main(String[] args)throws Exception{
        initOwnership();
        recovery();
        Factory f=new Factory();MiniClientSession s=owner(f);MiniClientMediaBridge b=seed(s);
        final MiniClientMediaBridge firstBridge=b;
        try{
            long began=System.nanoTime();b.handle(29,seek(23000));
            check(TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-began)<300,"native SEEK acceptance does not wait for producer preparation");
            check(f.started.await(1,TimeUnit.SECONDS),"producer is deliberately blocked off the media reader");
            check(clock(b)==23000,"following native clock query immediately returns accepted target");
            check(!b.reportBrowserState("original",5000,640,360,1f,false,false)&&clock(b)==23000,"old browser reports cannot rewind pending clock or pause intent");
            b.handle(20,new byte[0]);f.release.countDown();until(()->firstBridge.streamingJson().contains("\"completed\":1"),"prepared producer commits once");
            check(s.pollEvents(500,10).stream().anyMatch(e->e.contains("\"type\":\"videoStart\"")&&e.contains("\"paused\":true")),"new seek generation preserves Pause issued during preparation");
        }finally{f.releaseAll();s.close();}

        f=new Factory();s=owner(f);b=seed(s);final Factory latestFactory=f;final MiniClientMediaBridge latestBridge=b;
        try{
            b.handle(29,seek(15000));check(f.started.await(1,TimeUnit.SECONDS),"first rapid seek is in flight");
            b.handle(29,seek(35000));b.handle(29,seek(10000));check(clock(b)==10000,"rapid forward/backward reports newest target immediately");
            f.release.countDown();until(()->latestBridge.streamingJson().contains("\"completed\":1"),"latest coalesced seek commits");
            check(f.starts.equals(Arrays.asList(15000L,10000L)),"one in-flight plus latest request, no obsolete middle encoder");
            check(f.stopped.contains("seek-1-15000")&&f.stopped.contains("original"),"obsolete result and previous producer both retire");
        }finally{f.releaseAll();s.close();}

        f=new Factory();s=owner(f);b=seed(s);final Factory stoppedFactory=f;
        try{
            b.handle(29,seek(20000));check(f.started.await(1,TimeUnit.SECONDS),"stop test has blocked seek");
            b.handle(19,new byte[0]);f.release.countDown();until(()->stoppedFactory.stopped.contains("seek-1-20000"),"STOP retires a late prepared producer");
            check(s.pollEvents(500,10).stream().noneMatch(e->e.contains("\"type\":\"videoStart\"")),"STOP cannot resurrect playback with a late seek callback");
        }finally{f.releaseAll();s.close();}

        f=new Factory();s=owner(f);b=seed(s);final Factory sourceFactory=f;
        try{
            b.handle(29,seek(25000));check(f.started.await(1,TimeUnit.SECONDS),"source retirement test has blocked seek");
            b.handle(0,new byte[4]);PlaybackSessionContext c=(PlaybackSessionContext)field(b,"playbackContext");c.beginSource();field(b,"mediaId",2);
            f.release.countDown();until(()->sourceFactory.stopped.contains("seek-1-25000"),"new source epoch rejects old prepared seek");
            check(s.pollEvents(500,10).stream().noneMatch(e->e.contains("\"type\":\"videoStart\"")),"retired source never publishes new video");
        }finally{f.releaseAll();s.close();}

        f=new Factory();f.fail=true;f.release.countDown();s=owner(f);b=seed(s);final MiniClientMediaBridge failedBridge=b;
        try{
            b.handle(29,seek(30000));until(()->failedBridge.streamingJson().contains("\"failures\":1"),"producer failure exits pending state visibly");
            List<String> events=s.pollEvents(500,10);
            check(events.stream().anyMatch(e->e.contains("Seek preparation:"))&&events.stream().anyMatch(e->e.contains("\"type\":\"videoStop\"")),"failed seek stops invalid generation and reports failure instead of infinite spinner");
            check(clock(b)==4000,"failed accepted seek does not leave a false playback clock at requested target");
        }finally{f.releaseAll();s.close();}

        f=new Factory();f.holdCleanup=true;f.release.countDown();s=owner(f);b=seed(s);
        try{
            b.handle(29,seek(Long.MAX_VALUE));check(f.cleanupStarted.await(2,TimeUnit.SECONDS),"old producer cleanup is deliberately blocked");
            long began=System.nanoTime();check(clock(b)==89750,"accepted target retains duration clamp");b.handle(20,new byte[0]);
            check(TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-began)<300,"clock and Pause stay responsive during old converter shutdown");
        }finally{f.releaseAll();s.close();}
        wire(false);wire(true);System.out.println("Native seek: "+checks+" PASS");
    }
    static void recovery()throws Exception{
        Factory f=new Factory();MiniClientSession s=owner(f);MiniClientMediaBridge b=seed(s);
        final MiniClientMediaBridge recovering=b;
        try{
            check(!b.recoverFromBrowserPosition("old",23000)&&!b.recoverFromBrowserPosition("",23000)&&!b.recoverFromBrowserPosition(null,23000),"recovery rejects stale and unscoped requests");
            long began=System.nanoTime();
            check(b.recoverFromBrowserPosition("original",23000),"HTTP recovery accepted for exact source");
            check(TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-began)<300,"HTTP recovery does not hold native clock behind producer preparation");
            check(f.started.await(1,TimeUnit.SECONDS),"recovery producer deliberately blocked outside media monitor");
            check(clock(b)==23000,"native clock remains responsive during slow browser recovery");
            check(!b.recoverFromBrowserPosition("original",25000),"duplicate recovery cannot queue another producer while pending");
            b.handle(20,new byte[0]);f.release.countDown();
            until(()->recovering.streamingJson().contains("\"completed\":1"),"asynchronous recovery commits once");
            check(s.pollEvents(500,10).stream().anyMatch(e->e.contains("\"type\":\"videoStart\"")&&e.contains("\"recovery\":true")&&e.contains("\"paused\":true")),"recovery event preserves retry budget and latest Pause");
        }finally{f.releaseAll();s.close();}
        f=new Factory();s=owner(f);b=seed(s);final Factory stopped=f;
        try{
            b.recoverFromBrowserPosition("original",18000);check(f.started.await(1,TimeUnit.SECONDS),"recovery Stop test blocks preparation");
            b.handle(19,new byte[0]);f.release.countDown();until(()->stopped.stopped.contains("seek-1-18000"),"Stop retires late HTTP recovery result");
            check(s.pollEvents(500,10).stream().noneMatch(e->e.contains("\"type\":\"videoStart\"")),"HTTP recovery cannot resurrect stopped playback");
        }finally{f.releaseAll();s.close();}
    }
    static void wire(boolean recovery)throws Exception{
        Factory f=new Factory();ServerSocket listener=new ServerSocket(0,10,InetAddress.getByName("127.0.0.1"));
        MiniClientSession s=new MiniClientSession("wire-seek","127.0.0.1:"+listener.getLocalPort(),"02:00:00:00:00:48",640,360,false,false,f);
        seed(s);ExecutorService executor=Executors.newSingleThreadExecutor();
        Future<?> peer=executor.submit(()->{
            try(Socket media=MiniClientProtocolSmoke.acceptHandshake(listener,1);Socket gfx=MiniClientProtocolSmoke.acceptHandshake(listener,0)){
                gfx.getOutputStream().write(new byte[]{16,0,0,4,1,0,0,4});gfx.getOutputStream().flush();MiniClientProtocolSmoke.replyPayload(gfx.getInputStream(),16);
                gfx.getOutputStream().write(new byte[]{16,0,0,4,31,0,0,0,16,0,0,4,30,0,0,0});gfx.getOutputStream().flush();
                MiniClientProtocolSmoke.replyPayload(gfx.getInputStream(),16);MiniClientProtocolSmoke.replyPayload(gfx.getInputStream(),192);MiniClientProtocolSmoke.replyPayload(gfx.getInputStream(),193);
                DataOutputStream out=new DataOutputStream(media.getOutputStream());
                if(recovery)check(s.recoverMedia("original",42000),"HTTP recovery accepted while native sockets are active");
                else{out.writeInt((29<<24)|8);out.writeLong(42000);}
                out.writeInt(17<<24);out.flush();
                media.setSoTimeout(1000);
                check(new DataInputStream(media.getInputStream()).readInt()==42000,"real native "+(recovery?"HTTP recovery":"SEEK")+"→GETMEDIATIME wire responds while producer is blocked");
                MiniClientProtocolSmoke.replyPayload(gfx.getInputStream(),201);
                check(true,"accepted native seek sends existing event201 to wake stock VideoFrame");
                check(f.started.await(1,TimeUnit.SECONDS)&&f.release.getCount()==1,"wire proof does not secretly finish encoder preparation first");
            }catch(Exception e){throw new RuntimeException(e);}
        });
        try{s.start();peer.get(5,TimeUnit.SECONDS);}finally{s.close();f.releaseAll();listener.close();executor.shutdownNow();}
    }
}
