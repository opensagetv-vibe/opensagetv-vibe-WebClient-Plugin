package org.opensagetv.webplayer;
import java.util.*;
public final class LegacyCaptionBridgeSmoke {
  static void set(Object o,String name,Object value)throws Exception{java.lang.reflect.Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);f.set(o,value);}
  static void seekEpoch()throws Exception{
    java.nio.file.Path dir=java.nio.file.Files.createTempDirectory("vibe-legacy-caption-epoch-");
    java.io.File sidecar=dir.resolve("captions.bin").toFile();
    MiniClientSession owner=new MiniClientSession("caption-epoch-test","127.0.0.1","020000000072",640,360,false);
    try{
      try(java.io.DataOutputStream out=new java.io.DataOutputStream(new java.io.FileOutputStream(sidecar))){
        for(long ms:new long[]{1000,8000}){out.writeLong(ms);out.writeByte(3);out.write(new byte[]{4,(byte)0x94,0x25});}
      }
      MiniClientMediaBridge bridge=owner.media();PlaybackSessionContext context=new PlaybackSessionContext();context.beginSource();
      HlsSessionManager.Session s=new HlsSessionManager.Session("caption-epoch",1,0,0,30.0,90000,false,dir.toFile(),StreamOptions.defaults(),context,context.token());
      set(bridge,"hls",s);set(bridge,"subtitleCallbacksEnabled",true);
      bridge.reportBrowserState(s.id,30000,640,360,1f,false,false);
      if(!bridge.captionAuthorityJson().contains("\"forwardedSamples\":0"))throw new AssertionError("absolute30s clock must not emit future1s/8s caption records from the replacement epoch");
      bridge.reportBrowserState(s.id,31000,640,360,1f,false,false);
      if(!bridge.captionAuthorityJson().contains("\"forwardedSamples\":1"))throw new AssertionError("only current1s replacement caption is due");
      bridge.reportBrowserState("retired",60000,640,360,1f,false,false);
      if(!bridge.captionAuthorityJson().contains("\"forwardedSamples\":1"))throw new AssertionError("old producer must not drain replacement captions");
      bridge.reportBrowserState(s.id,38000,640,360,1f,false,false);
      if(!bridge.captionAuthorityJson().contains("\"forwardedSamples\":2"))throw new AssertionError("later8s replacement caption becomes due normally");
    }finally{owner.close();java.nio.file.Files.deleteIfExists(sidecar.toPath());java.nio.file.Files.deleteIfExists(dir);}
  }
  static final class E{long p;int f;byte[] d;E(long p,int f,byte[] d){this.p=p;this.f=f;this.d=d;}}
  public static void main(String[] args)throws Exception{
    List<E> e=new ArrayList<E>();LegacyExtenderCaptionBridge b=new LegacyExtenderCaptionBridge((p,d,x,f)->e.add(new E(p,f,x)));
    if(!b.onCeaSample(2000,new byte[]{4,(byte)0x94,0x25,7,0x45,0x46}))throw new AssertionError();
    b.drainTo(1000);if(!e.isEmpty())throw new AssertionError("read ahead leaked");
    b.drainTo(2000);if(e.size()!=1||e.get(0).p!=90000||e.get(0).d.length!=16)throw new AssertionError("bad legacy packet");
    b.clearPending();b.postFlush();if(e.size()!=2||e.get(1).f!=(LegacyExtenderCaptionBridge.CC_SUBTITLE|LegacyExtenderCaptionBridge.FLUSH_SUBTITLE_QUEUE)||e.get(1).d.length!=128)throw new AssertionError("bad flush");
    e.clear();b.clearPending();
    for(int n=0;n<100;n++)b.onCeaSample(n,new byte[]{4,(byte)0x94,0x25});
    b.drainTo(200);if(e.size()!=1||e.get(0).d.length!=800||b.pendingSamples()!=0)throw new AssertionError("one bounded event, not100callbacks, per drain");
    for(int n=0;n<100;n++){int p=java.nio.ByteBuffer.wrap(e.get(0).d,n*8,4).getInt();if(p!=n*45)throw new AssertionError("embedded PTS changed");}
    e.clear();b.clearPending();
    for(int n=0;n<4096;n++)b.onCeaSample(n,new byte[]{4,(byte)0x94,0x25});
    b.drainTo(5000);if(e.size()!=1||e.get(0).d.length!=16384||b.pendingSamples()!=2048)throw new AssertionError("batch budget/remaining records");
    b.drainTo(5000);if(e.size()!=2||e.get(1).d.length!=16384||b.pendingSamples()!=0)throw new AssertionError("next explicit clock drains remaining records");
    e.clear();b.clearPending();b.onCeaSample(200,new byte[]{5,(byte)0x94,0x25});b.onCeaSample(100,new byte[]{7,0x45,0x46});b.drainTo(300);
    if(e.size()!=1||e.get(0).p!=4500||e.get(0).d[4]!=3||e.get(0).d[12]!=1)throw new AssertionError("PTS/field reordering");
    b.onCeaSample(90000,new byte[]{4,(byte)0x94,0x25});b.clearPending();b.postFlush();int afterFlush=e.size();b.drainTo(100000);
    if(e.size()!=afterFlush)throw new AssertionError("pre-flush read-ahead escaped");
    final java.util.concurrent.CountDownLatch entered=new java.util.concurrent.CountDownLatch(1),release=new java.util.concurrent.CountDownLatch(1);
    List<Long> delivered=Collections.synchronizedList(new ArrayList<Long>());
    LegacyExtenderCaptionBridge ordered=new LegacyExtenderCaptionBridge((p,d,x,f)->{if(p==45){entered.countDown();try{if(!release.await(2,java.util.concurrent.TimeUnit.SECONDS))throw new AssertionError("sink release");}catch(InterruptedException ex){throw new RuntimeException(ex);}}delivered.add(p);});
    ordered.onCeaSample(1,new byte[]{4,0x21,0x22});Thread first=new Thread(()->ordered.drainTo(1));first.start();
    if(!entered.await(2,java.util.concurrent.TimeUnit.SECONDS))throw new AssertionError("first emission absent");
    ordered.onCeaSample(2,new byte[]{4,0x23,0x24});Thread second=new Thread(()->ordered.drainTo(2));second.start();
    try{Thread.sleep(40);if(!delivered.isEmpty())throw new AssertionError("later callback overtook blocked earlier write");}finally{release.countDown();first.join(2000);second.join(2000);}
    if(first.isAlive()||second.isAlive()||!delivered.equals(Arrays.asList(45L,90L)))throw new AssertionError("ordered emissions");
    final int[] unknownCalls={0};LegacyExtenderCaptionBridge uncertain=new LegacyExtenderCaptionBridge((p,d,x,f)->{unknownCalls[0]++;throw new IllegalStateException("unknown delivery");});
    uncertain.onCeaSample(1,new byte[]{4,0x21,0x22});try{uncertain.drainTo(1);throw new AssertionError("sink failure hidden");}catch(IllegalStateException expected){}
    uncertain.drainTo(1);if(unknownCalls[0]!=1||uncertain.pendingSamples()!=0)throw new AssertionError("unknown emission replayed");
    final java.util.concurrent.CountDownLatch writing=new java.util.concurrent.CountDownLatch(1),finish=new java.util.concurrent.CountDownLatch(1);
    List<Integer> flushOrder=Collections.synchronizedList(new ArrayList<Integer>());
    LegacyExtenderCaptionBridge reset=new LegacyExtenderCaptionBridge((p,d,x,f)->{if(p==45){writing.countDown();try{if(!finish.await(2,java.util.concurrent.TimeUnit.SECONDS))throw new AssertionError("flush wait");}catch(InterruptedException ex){throw new RuntimeException(ex);}}flushOrder.add(f);});
    reset.onCeaSample(1,new byte[]{4,0x21,0x22});Thread writer=new Thread(()->reset.drainTo(1));writer.start();if(!writing.await(2,java.util.concurrent.TimeUnit.SECONDS))throw new AssertionError("write absent");
    reset.onCeaSample(200,new byte[]{4,0x23,0x24});Thread flusher=new Thread(()->{reset.clearPending();reset.postFlush();});flusher.start();
    try{Thread.sleep(40);if(!flushOrder.isEmpty())throw new AssertionError("FLUSH overtook earlier write");}finally{finish.countDown();writer.join(2000);flusher.join(2000);}
    if(writer.isAlive()||flusher.isAlive()||reset.pendingSamples()!=0||!flushOrder.equals(Arrays.asList(17,18)))throw new AssertionError("reset ordering");
    seekEpoch();System.out.println("legacy event-225 caption bridge: 16 PASS");
  }
}
