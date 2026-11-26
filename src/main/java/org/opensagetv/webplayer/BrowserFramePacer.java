package org.opensagetv.webplayer;

import java.util.concurrent.TimeUnit;

/** One native FLIPBUFFER at a time, acknowledged by the actual browser renderer.
 * The stock protocol is unchanged. Waiting never holds the native event-write
 * lock or media-reader lock, and a lost/background browser cannot wait forever.
 */
final class BrowserFramePacer {
    private final boolean enabled;
    private final long timeoutMs;
    private boolean closed;
    private long pending,acknowledged,waits,timeouts;
    BrowserFramePacer(boolean enabled){this(enabled,1500L);}
    BrowserFramePacer(boolean enabled,long timeoutMs){this.enabled=enabled;this.timeoutMs=Math.max(1L,Math.min(1500L,timeoutMs));}
    synchronized boolean prepare(long sequence){
        if(!enabled||closed||sequence<=0||pending!=0L)return false;
        pending=sequence;return true;
    }
    synchronized boolean acknowledge(long sequence){
        if(!enabled||closed||sequence<=0)return false;
        if(sequence==acknowledged)return true;
        if(sequence!=pending)return false;
        acknowledged=sequence;pending=0L;notifyAll();return true;
    }
    synchronized void await(long sequence){
        if(pending!=sequence||closed)return;
        waits++;long deadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(timeoutMs);
        while(!closed&&pending==sequence){
            long remaining=deadline-System.nanoTime();
            if(remaining<=0){pending=0L;timeouts++;break;}
            try{TimeUnit.NANOSECONDS.timedWait(this,remaining);}
            catch(InterruptedException e){Thread.currentThread().interrupt();pending=0L;break;}
        }
    }
    synchronized void close(){closed=true;pending=0L;notifyAll();}
    synchronized String json(){return "{\"enabled\":"+enabled+",\"pending\":"+pending+",\"acknowledged\":"+acknowledged+",\"waits\":"+waits+",\"timeouts\":"+timeouts+"}";}
}
