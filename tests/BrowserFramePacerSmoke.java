package org.opensagetv.webplayer;
import java.util.concurrent.*;
public final class BrowserFramePacerSmoke {
    static int count;
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);count++;System.out.println("PASS "+why);}
    public static void main(String[] args)throws Exception{
        BrowserFramePacer legacy=new BrowserFramePacer(false,100);
        check(!legacy.prepare(1)&&!legacy.acknowledge(1),"legacy clients do not opt into frame waits");
        BrowserFramePacer p=new BrowserFramePacer(true,1000);
        check(p.prepare(7)&&!p.prepare(8),"one outstanding native frame");
        CountDownLatch returned=new CountDownLatch(1);
        Thread t=new Thread(()->{p.await(7);returned.countDown();});t.start();
        check(!returned.await(30,TimeUnit.MILLISECONDS),"native frame reply waits for actual browser rendering");
        check(!p.acknowledge(6)&&!p.acknowledge(8),"stale and future acknowledgements cannot release current frame");
        check(p.acknowledge(7)&&returned.await(500,TimeUnit.MILLISECONDS),"matching browser frame releases native GFX reader");
        check(p.acknowledge(7),"duplicate matching acknowledgement is idempotent");
        check(p.prepare(9),"next frame can start after acknowledgement");
        Thread closeWait=new Thread(()->p.await(9));closeWait.start();p.close();closeWait.join(500);
        check(!closeWait.isAlive()&&!p.prepare(10)&&!p.acknowledge(9),"close releases wait and rejects late browser callbacks");
        BrowserFramePacer lost=new BrowserFramePacer(true,50);lost.prepare(1);
        long begin=System.nanoTime();lost.await(1);long ms=TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-begin);
        check(ms>=35&&ms<1000&&lost.json().contains("\"timeouts\":1"),"lost browser acknowledgement has a bounded timeout");
        check(lost.prepare(2)&&!lost.acknowledge(1)&&lost.acknowledge(2),"timeout cannot let an old acknowledgement release a new frame");
        System.out.println("Browser frame pacing: "+count+" PASS");
    }
}
