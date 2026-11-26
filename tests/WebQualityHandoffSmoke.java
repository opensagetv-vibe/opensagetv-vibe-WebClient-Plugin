package org.opensagetv.webplayer;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

/** Real production bridge/owner state with blocked fake encoders. These are
 * lifecycle regressions, NOT browser rendering or physical/GPU evidence. */
public final class WebQualityHandoffSmoke {
    private static int checks;
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);checks++;System.out.println("PASS "+message);}
    static void until(java.util.function.BooleanSupplier ready,String message)throws Exception{
        long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(4);
        while(!ready.getAsBoolean()&&System.nanoTime()<end)Thread.sleep(5);
        check(ready.getAsBoolean(),message);
    }
    static Object field(Object target,String name)throws Exception{java.lang.reflect.Field f=target.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(target);}
    static void field(Object target,String name,Object value)throws Exception{java.lang.reflect.Field f=target.getClass().getDeclaredField(name);f.setAccessible(true);f.set(target,value);}
    static final class Factory implements MiniClientMediaBridge.QualityFactory {
        final CountDownLatch registered=new CountDownLatch(1),ready=new CountDownLatch(1);
        final List<String> stopped=Collections.synchronizedList(new ArrayList<String>());
        volatile boolean fail;
        volatile HlsSessionManager.Session candidate;
        public HlsSessionManager.Session start(int id,int segment,long ms,StreamOptions options,PlaybackSessionContext context,Consumer<HlsSessionManager.Session> observer)throws Exception{
            candidate=new HlsSessionManager.Session("candidate-"+UUID.randomUUID(),id,segment,0,ms/1000.0,90000,false,
                new File("build/quality-no-files"),options,context,context.token());
            candidate.streamPlan=new StreamPlan(options,new MediaProbe.Info());candidate.running=true;candidate.playlistReady=true;candidate.hlsSeconds=90;
            observer.accept(candidate);registered.countDown();
            if(!ready.await(5,TimeUnit.SECONDS))throw new IOException("Fixture readiness timeout");
            if(fail)throw new IOException("Deliberate preparation failure");
            return candidate;
        }
        public void stop(HlsSessionManager.Session session){session.stopRequested=true;session.running=false;stopped.add(session.id);}
    }
    static final class Case implements AutoCloseable {
        final MiniClientSession owner=new MiniClientSession("quality-test","127.0.0.1","02:00:00:00:00:52",640,360,false,false);
        final Factory factory=new Factory();
        final MiniClientMediaBridge bridge=new MiniClientMediaBridge(owner,new MiniClientMediaBridge.NativeSeekFactory(){
            public HlsSessionManager.Session start(int id,int segment,long ms,StreamOptions options,PlaybackSessionContext context,PlaybackSessionContext.Token token){
                return new HlsSessionManager.Session("native-seek",id,segment,0,ms/1000.0,90000,false,new File("build/quality-no-native"),options,context,token);
            }
            public void stop(HlsSessionManager.Session session){session.stopRequested=true;session.running=false;}
        },factory);
        final ExecutorService executor=Executors.newSingleThreadExecutor();
        final StreamOptions options;
        final HlsSessionManager.Session original;
        Case()throws Exception{
            Map<String,String> values=new HashMap<String,String>();values.put("player","hls");values.put("videoMode","transcode");values.put("videoKbps","1000");values.put("captions","608");
            options=StreamOptions.fromMap(values);
            PlaybackSessionContext context=(PlaybackSessionContext)field(bridge,"playbackContext");context.beginSource();context.selectCaption("608");
            original=new HlsSessionManager.Session("original",1,0,0,0,90000,false,new File("build/quality-no-original"),options,context,context.token());
            original.streamPlan=new StreamPlan(options,new MediaProbe.Info());original.running=true;original.playlistReady=true;
            field(bridge,"hls",original);field(bridge,"mediaId",1);field(bridge,"durationMs",90000L);
            field(bridge,"browserTimeMs",4000L);field(bridge,"lastProvenBrowserTimeMs",4000L);
            field(bridge,"configured",options);field(bridge,"activeOptions",options);
        }
        Future<Boolean> prepare(){return executor.submit(()->bridge.prepareQuality("original",4000,700,480));}
        public void close()throws Exception{
            factory.ready.countDown();bridge.close();owner.close();executor.shutdownNow();
            // Exact admission-slot readback, not a sleep that hides leaks.
            Object probe=new Object();until(()->{if(!HlsSessionManager.claimQualitySlot(probe))return false;HlsSessionManager.releaseQualitySlot(probe);return true;},"Quality admission slot released after cleanup");
        }
    }
    public static void main(String[] args)throws Exception{
        try(Case c=new Case()){
            Future<Boolean> prepared=c.prepare();check(c.factory.registered.await(1,TimeUnit.SECONDS),"Candidate registered before readiness");
            check(c.original.running&&c.factory.stopped.isEmpty(),"Warming does not stop original");
            check(MiniClientSession.readInt(c.bridge.handle(17,new byte[0]),0)==4000,"Native clock remains responsive during preparation");
            check(c.factory.candidate.playbackContext!=c.original.playbackContext&&
                c.factory.candidate.playbackContext.cues()!=c.original.playbackContext.cues(),"Warming caption queues isolated");
            check(c.factory.candidate.playbackToken.json().equals(c.original.playbackToken.json()),"Quality preserves logical source/seek identity");
            c.bridge.reportBrowserState("original",6250,1920,1080,1,false,false);
            c.factory.ready.countDown();check(prepared.get(2,TimeUnit.SECONDS),"Ready candidate published");
            check(c.factory.stopped.isEmpty(),"Readiness alone does not retire original");
            List<String> events=c.owner.pollEvents(500,10);
            check(events.stream().anyMatch(e->e.contains("\"type\":\"videoStart\"")&&e.contains("\"resumeSeconds\":2.250")),"Replacement joins latest old position rather than replaying warmup");
            check(c.options.videoKbps==1000&&c.factory.candidate.options.videoKbps==700,"Saved quality unchanged");
            c.bridge.reportPresented("original",7000);c.bridge.reportPresented(c.factory.candidate.id,4000);
            check(c.factory.stopped.isEmpty(),"Wrong producer/pre-join frame cannot commit");
            c.bridge.reportPresented(c.factory.candidate.id,6251);
            until(()->c.factory.stopped.contains("original"),"Exact presented replacement retires original");
            check(!c.factory.candidate.stopRequested&&c.bridge.playbackStateJson().contains("\"qualityHandoff\":\"presented\""),"Replacement survives commit");
            check(!c.bridge.abortQuality(c.factory.candidate.id),"Late abort cannot kill committed replacement");
        }
        try(Case c=new Case()){
            c.factory.ready.countDown();check(c.prepare().get(2,TimeUnit.SECONDS),"Abort candidate ready");
            check(!c.bridge.abortQuality("foreign"),"Foreign abort refused");
            check(c.bridge.abortQuality(c.factory.candidate.id),"Exact abort accepted");
            until(()->c.factory.stopped.contains(c.factory.candidate.id),"Abort retires only replacement");
            check(field(c.bridge,"hls")==c.original&&!c.original.stopRequested,"Abort restores original owner");
            check(c.owner.pollEvents(500,10).stream().anyMatch(e->e.contains("\"hlsSession\":\"original\"")&&e.contains("\"resumeSeconds\":4.000")),"Rollback resumes original at source position, not zero");
        }
        try(Case c=new Case()){
            c.factory.ready.countDown();c.prepare().get(2,TimeUnit.SECONDS);
            Object pending=field(c.bridge,"qualityHandoff");Method expire=c.bridge.getClass().getDeclaredMethod("expireQuality",pending.getClass());expire.setAccessible(true);expire.invoke(c.bridge,pending);
            until(()->c.factory.candidate.stopRequested,"Expiry cancels candidate");
            check(field(c.bridge,"hls")==c.original&&!c.original.stopRequested,"Expiry preserves original");
        }
        try(Case c=new Case()){
            Future<Boolean> preparing=c.prepare();check(c.factory.registered.await(1,TimeUnit.SECONDS),"STOP case is preparing");
            c.bridge.handle(19,new byte[0]);c.factory.ready.countDown();
            try{preparing.get(2,TimeUnit.SECONDS);throw new AssertionError("Late preparation resurrected STOP");}catch(ExecutionException expected){}
            until(()->c.factory.candidate.stopRequested,"STOP cancels registered candidate");
            check(c.owner.pollEvents(500,10).stream().noneMatch(e->e.contains("\"type\":\"videoStart\"")),"No late source resurrection");
        }
        try(Case c=new Case()){
            c.factory.fail=true;c.factory.ready.countDown();
            try{c.prepare().get(2,TimeUnit.SECONDS);throw new AssertionError("Failed producer published");}catch(ExecutionException expected){}
            until(()->c.factory.candidate.stopRequested,"Failed producer cleaned");
            check(field(c.bridge,"hls")==c.original&&!c.original.stopRequested,"Startup failure retains original");
        }
        try(Case c=new Case()){
            Future<Boolean> preparing=c.prepare();check(c.factory.registered.await(1,TimeUnit.SECONDS),"Decoder INIT case preparing");
            c.bridge.handle(0,new byte[4]);c.factory.ready.countDown();
            try{preparing.get(2,TimeUnit.SECONDS);throw new AssertionError("INIT accepted old candidate");}catch(ExecutionException expected){}
            until(()->c.factory.candidate.stopRequested,"Decoder INIT cancels previous handoff");
        }
        try(Case c=new Case()){
            Future<Boolean> preparing=c.prepare();check(c.factory.registered.await(1,TimeUnit.SECONDS),"User seek case preparing");
            PlaybackSessionContext context=(PlaybackSessionContext)field(c.bridge,"playbackContext");
            check(c.bridge.timelineSeek(context.token().sourceGeneration,"user_seek",12000),"User seek accepted without waiting for quality preparation");
            c.factory.ready.countDown();
            try{preparing.get(2,TimeUnit.SECONDS);throw new AssertionError("Superseded quality published");}catch(ExecutionException expected){}
            until(()->c.factory.candidate.stopRequested,"User seek retires quality candidate");
            until(()->c.bridge.streamingJson().contains("\"completed\":1"),"User seek commits independently");
            check(c.owner.pollEvents(500,10).stream().noneMatch(e->e.contains("\"hlsSession\":\""+c.factory.candidate.id+"\"")),"No obsolete quality event after seek");
        }
        try(Case c=new Case();Case other=new Case()){
            Future<Boolean> preparing=c.prepare();check(c.factory.registered.await(1,TimeUnit.SECONDS),"Admission case preparing");
            try{other.bridge.prepareQuality("original",4000,700,480);throw new AssertionError("Second concurrent handoff admitted");}catch(IllegalArgumentException expected){}
            check(other.factory.candidate==null&&other.original.running,"Admission refusal creates no extra producer");
            c.bridge.handle(20,new byte[0]);c.factory.ready.countDown();check(preparing.get(2,TimeUnit.SECONDS),"Pause during preparation preserved");
            check(c.owner.pollEvents(500,10).stream().anyMatch(e->e.contains("\"type\":\"videoStart\"")&&e.contains("\"paused\":true")),"Latest Pause retained on switch");
            c.bridge.abortQuality(c.factory.candidate.id);
        }
        try(Case c=new Case()){
            field(c.bridge,"activeOptions",c.options.reducedQuality(500,480));
            c.factory.ready.countDown();check(c.bridge.prepareQuality("original",4000,700,1080),"Recovery handoff accepts bitrate below saved ceiling");
            check(c.factory.candidate.options.videoKbps==700&&"source".equals(c.options.resolution),"Recovery leaves configured defaults unchanged");
            c.bridge.reportPresented(c.factory.candidate.id,4001);
            until(()->c.factory.stopped.contains("original"),"Recovery also retires original only on exact frame ACK");
            check(c.bridge.playbackStateJson().contains("\"qualityRecoveryRevision\":1"),"Recovery capability explicitly negotiated");
        }
        System.out.println("Web quality handoff: "+checks+" PASS");
    }
}
