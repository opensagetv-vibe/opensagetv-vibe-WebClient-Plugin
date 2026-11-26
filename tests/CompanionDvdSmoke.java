package org.opensagetv.webplayer;

/** Production optional client with fake provider responses, not DVD pixels. */
public final class CompanionDvdSmoke {
    public static void main(String[] args)throws Exception{
        final String nonce="0123456789abcdef0123456789abcdef";
        final String offer="{\"protocol\":1,\"profiles\":[\"web-mpegps-v1\"],\"challenge\":\""+nonce+"\"}";
        final String controls="{\"protocol\":1,\"challenge\":\""+nonce+"\"}";
        int[] posts={0};
        CompanionDvdClient missing=new CompanionDvdClient((method,path)->new CompanionDvdClient.Reply(404,"{}"));
        missing.negotiate("da92a86446be");check(!missing.action("resume")&&missing.json().contains("unavailable"),"Missing provider stays optional");
        CompanionDvdClient old=new CompanionDvdClient((method,path)->{if("POST".equals(method))posts[0]++;return new CompanionDvdClient.Reply(200,controls);});
        old.negotiate("da92a86446be");check(posts[0]==0&&old.json().contains("unsupported-profile"),"Old Android-only contract never receives a false browser acknowledgement");
        CompanionDvdClient[] holder=new CompanionDvdClient[1];boolean[] retire={false};
        holder[0]=new CompanionDvdClient((method,path)->{
            if(path.startsWith("/vibe/dvd/client"))return new CompanionDvdClient.Reply(200,"POST".equals(method)?"{\"accepted\":true}":offer);
            if("GET".equals(method))return new CompanionDvdClient.Reply(200,controls);
            if(retire[0])holder[0].reset();return new CompanionDvdClient.Reply(200,"{\"accepted\":true}");
        });
        holder[0].negotiate("da92a86446be");check(holder[0].json().contains("\"controls\":true")&&!holder[0].json().contains(nonce),"Negotiated current load exposes no challenge in diagnostics");
        check(holder[0].action("save_resume"),"Explicit existing operation works");
        try{holder[0].action("arbitrary");throw new AssertionError("Unknown operation accepted");}catch(IllegalArgumentException expected){System.out.println("PASS unknown operation refused");}
        retire[0]=true;check(!holder[0].action("resume"),"Late HTTP response cannot confirm a retired load");
        check(!holder[0].action("resume"),"Reset cannot reuse the old challenge");
        final int[] requests={0};final boolean[] slow={false};
        com.sun.net.httpserver.HttpServer server=com.sun.net.httpserver.HttpServer.create(new java.net.InetSocketAddress("127.0.0.1",0),0);
        server.createContext("/vibe/dvd/controls",e->{
            requests[0]++;try{Thread.sleep(slow[0]?1250:250);}catch(InterruptedException interrupted){Thread.currentThread().interrupt();}
            byte[] bytes="{\"accepted\":true}".getBytes(java.nio.charset.StandardCharsets.UTF_8);
            try{e.sendResponseHeaders(200,bytes.length);e.getResponseBody().write(bytes);}finally{e.close();}
        });server.start();
        try{
            CompanionDvdClient actual=new CompanionDvdClient((method,path)->{
                if(path.startsWith("/vibe/dvd/client"))return new CompanionDvdClient.Reply(200,"POST".equals(method)?"{\"accepted\":true}":offer);
                if("GET".equals(method))return new CompanionDvdClient.Reply(200,controls);
                return CompanionDvdClient.loopback(method,path,server.getAddress().getPort());
            });
            actual.negotiate("da92a86446be");
            long started=System.nanoTime();check(actual.action("beginning"),"Real delayed HTTP action receipt survives old100ms timeout");
            check((System.nanoTime()-started)/1000000L>=200&&requests[0]==1,"One explicit action waits for its bounded provider receipt; no replay");
            slow[0]=true;check(!actual.action("save_resume")&&actual.json().contains("\"actionOutcome\":\"unknown\""),"Timed-out mutating action is unknown, not falsely rejected");
            Thread.sleep(350);check(requests[0]==2,"Unknown mutation is never automatically repeated");
        }finally{server.stop(0);}
        System.out.println("Optional DVD companion: 11 PASS");
    }
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println("PASS "+why);}
}
