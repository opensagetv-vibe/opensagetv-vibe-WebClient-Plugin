package org.opensagetv.webplayer;

import java.io.File;
import java.lang.reflect.Field;

/** WEB-098: existing four-byte stock Pull EOS contract, no retune/API shortcut. */
public final class MiniClientEndOfStreamSmoke {
    static int checks;
    static void check(boolean value,String why){if(!value)throw new AssertionError(why);checks++;}
    static void set(Object target,String name,Object value)throws Exception{
        Field field=target.getClass().getDeclaredField(name);field.setAccessible(true);field.set(target,value);
    }
    static int clock(MiniClientMediaBridge b){byte[] reply=b.handle(17,new byte[0]);check(reply.length==4,"Pull reply remains exactly four bytes");return MiniClientSession.readInt(reply,0);}
    static void wire()throws Exception{
        try(java.net.ServerSocket listener=new java.net.ServerSocket(0,2,java.net.InetAddress.getByName("127.0.0.1"))){
            MiniClientSession owner=new MiniClientSession("eos-wire","127.0.0.1:"+listener.getLocalPort(),"020000000099",640,360,false);
            java.util.concurrent.ExecutorService worker=java.util.concurrent.Executors.newSingleThreadExecutor();
            java.util.concurrent.Future<?> result=worker.submit(()->{try{
                try(java.net.Socket media=MiniClientProtocolSmoke.acceptHandshake(listener,1);java.net.Socket gfx=MiniClientProtocolSmoke.acceptHandshake(listener,0)){
                    MiniClientMediaBridge b=owner.media();PlaybackSessionContext c=new PlaybackSessionContext();c.beginSource();
                    HlsSessionManager.Session h=new HlsSessionManager.Session("wire",1,0,0,0,1000,false,new File("build/eos-wire-no-files"),StreamOptions.defaults().hlsFallback(),c,c.token());
                    h.endList=true;h.exitCode=0;set(b,"hls",h);set(b,"mediaId",1);
                    b.reportBrowserState(h.id,1000,640,360,1,true,true);
                    media.getOutputStream().write(new byte[]{17,0,0,0,26,0,0,0});media.getOutputStream().flush();
                    java.io.DataInputStream in=new java.io.DataInputStream(media.getInputStream());
                    check(in.readInt()==-1,"real media socket reports existing signed EOS word");
                    check(in.readInt()==65535,"following volume reply stays aligned without fifth byte");
                }
            }catch(Exception e){throw new RuntimeException(e);}});
            try{owner.start();result.get(10,java.util.concurrent.TimeUnit.SECONDS);}finally{owner.close();worker.shutdownNow();}
        }
    }
    public static void main(String[] args)throws Exception{
        MiniClientSession owner=new MiniClientSession("eos-test","127.0.0.1","020000000098",640,360,false);
        MiniClientMediaBridge b=owner.media();PlaybackSessionContext c=new PlaybackSessionContext();c.beginSource();
        HlsSessionManager.Session h=new HlsSessionManager.Session("current",1,0,0,0,90000,false,new File("build/eos-no-files"),StreamOptions.defaults().hlsFallback(),c,c.token());
        set(b,"playbackContext",c);set(b,"mediaId",1);set(b,"hls",h);
        try{
            b.reportBrowserState(h.id,89000,640,360,1,false,false);
            check(clock(b)==89000,"ordinary clock unchanged before browser end");
            h.endList=true;h.exitCode=0;h.running=false;
            check(clock(b)==89000,"encoder EOF alone is not presentation EOF");
            check(!b.reportBrowserState("retired",90000,640,360,1,true,true),"stale producer end rejected");
            check(clock(b)==89000,"stale EOF does not finish current stream");
            b.reportBrowserState("",89000,640,360,1,true,true);
            check(clock(b)==89000,"legacy untagged report cannot assert EOF");
            b.reportBrowserState(h.id,90000,640,360,1,true,true);
            check(clock(b)==-1,"actual completed presentation signals stock Pull EOS");
            check(clock(b)==-1,"EOS remains available for following stock poll");
            for(String reason:new String[]{"running","recording","open","failed","stopping","dvd"}){
                h.running="running".equals(reason);h.activeRecording="recording".equals(reason);
                h.endList=!"open".equals(reason);h.exitCode="failed".equals(reason)?1:0;
                h.stopRequested="stopping".equals(reason);
                h.dvdSource="dvd".equals(reason)?new DvdNativeSession():null;
                check(clock(b)==90000,"no ordinary EOS for "+reason);
            }
            h.running=false;h.activeRecording=false;h.endList=true;h.exitCode=0;h.stopRequested=false;h.dvdSource=null;
            b.reportBrowserState(h.id,90000,640,360,1,false,false);
            check(clock(b)==90000,"fresh non-ended report clears ended state");
            b.reportBrowserState(h.id,90000,640,360,1,true,true);
            b.handle(22,new byte[0]);
            check(clock(b)==90000,"FLUSH invalidates prior presentation end");
            b.reportBrowserState(h.id,90000,640,360,1,true,true);
            b.handle(19,new byte[0]);
            check(clock(b)>=0,"explicit STOP is not presentation EOF");
        }finally{owner.close();}
        wire();System.out.println("Stock Pull end-of-stream: "+checks+" PASS");
    }
}
