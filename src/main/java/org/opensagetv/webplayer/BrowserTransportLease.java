package org.opensagetv.webplayer;

/** Browser ownership, not the SageTV/DVD clock. Diagnostic status is not a
 * heartbeat. Actual browser state/event requests and encoded-media reads are.
 * A dropped pagehide beacon must not retain native sockets forever. */
final class BrowserTransportLease {
    static final long DETACHED_NS=java.util.concurrent.TimeUnit.SECONDS.toNanos(30);
    static final long ATTACHED_NS=java.util.concurrent.TimeUnit.SECONDS.toNanos(90);
    private long generation,lastClientNs;
    private boolean attached;
    BrowserTransportLease(long now){lastClientNs=now;}
    synchronized long open(long now){attached=true;lastClientNs=now;return ++generation;}
    synchronized void activity(long now){lastClientNs=now;}
    synchronized void detach(long ticket,long now){if(ticket==generation){attached=false;lastClientNs=now;}}
    synchronized boolean expired(long now,long mediaReadNs){
        long idle=attached?ATTACHED_NS:DETACHED_NS;
        return now-lastClientNs>=idle&&(mediaReadNs==0||now-mediaReadNs>=idle);
    }
}
