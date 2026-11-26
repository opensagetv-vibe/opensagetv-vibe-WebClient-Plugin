package org.opensagetv.webplayer;
public final class BrowserTransportLeaseSmoke {
    static long s(long n){return java.util.concurrent.TimeUnit.SECONDS.toNanos(n);}
    static void check(boolean v,String name){if(!v)throw new AssertionError(name);System.out.println("PASS "+name);}
    public static void main(String[] args){
        BrowserTransportLease l=new BrowserTransportLease(s(1));
        check(!l.expired(s(30),0)&&l.expired(s(31),0),"unclaimed response expires without browser, no status heartbeat");
        long first=l.open(s(40));
        check(!l.expired(s(129),0)&&l.expired(s(130),0),"half-open stream has bounded90s idle");
        l.activity(s(125));check(!l.expired(s(130),0),"real state or long-poll keeps owner alive");
        long second=l.open(s(140));l.detach(first,s(141));
        check(!l.expired(s(180),0),"old stream cannot detach a replacement");
        l.detach(second,s(181));check(!l.expired(s(210),0)&&l.expired(s(211),0),"dropped stream receives30s reconnect grace");
        check(!l.expired(s(211),s(200))&&l.expired(s(230),s(200)),"actual media reads preserve background native playback until idle");
        l.open(s(240));check(!l.expired(s(241),0),"new stream cancels detached expiry");
        l.activity(s(300));check(!l.expired(s(389),0)&&l.expired(s(390),0),"activity does not create unbounded permanent ownership");
        BrowserTransportLease wrap=new BrowserTransportLease(Long.MAX_VALUE-s(5));
        check(!wrap.expired(Long.MIN_VALUE+s(5),0)&&wrap.expired(Long.MIN_VALUE+s(30),0),"monotonic signed wrap uses elapsed subtraction");
        MiniClientSession owner=new MiniClientSession("receipt","127.0.0.1:9","020000009292",640,360);
        check(!owner.media().reportBrowserState("__browser_transport_only__",-1,0,0,0,true,true),"idle delivery receipt cannot accept an absent/mismatched producer clock");
    }
}
