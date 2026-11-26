package org.opensagetv.webplayer;

/** WEB-051 real production bridge state with deliberately blocked fake media
 * preparation; no Core mutation or fake physical/browser qualification. */
public final class PlaybackStateSmoke {
    public static void main(String[] args)throws Exception{
        MiniClientNativeSeekSmoke.Factory factory=new MiniClientNativeSeekSmoke.Factory();
        MiniClientSession owner=MiniClientNativeSeekSmoke.owner(factory);
        MiniClientMediaBridge bridge=MiniClientNativeSeekSmoke.seed(owner);
        try{
            PlaybackSessionContext context=(PlaybackSessionContext)MiniClientNativeSeekSmoke.field(bridge,"playbackContext");
            long source=context.token().sourceGeneration;
            MiniClientNativeSeekSmoke.check(bridge.playbackStateJson().contains("\"displayedPositionMs\":null"),"No presented frame is fabricated from native clock");
            MiniClientNativeSeekSmoke.check(!bridge.timelineSeek(source+1,"wrong_source",30000),"Wrong source epoch cannot seek");
            MiniClientNativeSeekSmoke.check(bridge.timelineSeek(source,"requested",30000),"Current source request is accepted asynchronously");
            String state=bridge.playbackStateJson();
            MiniClientNativeSeekSmoke.check(state.contains("\"requestedPositionMs\":30000")&&state.contains("\"pending\":true")&&state.contains("\"requestId\":\"requested\""),"Requested and pending stages are explicit");
            bridge.reportPresented("original",4000);
            MiniClientNativeSeekSmoke.check(bridge.playbackStateJson().contains("\"displayedPositionMs\":null"),"Old producer cannot confirm new seek while preparation is pending");
            factory.releaseAll();MiniClientNativeSeekSmoke.until(()->bridge.streamingJson().contains("\"completed\":1"),"Asynchronous replacement commits");
            String id=((HlsSessionManager.Session)MiniClientNativeSeekSmoke.field(bridge,"hls")).id;
            bridge.reportPresented("original",30000);
            MiniClientNativeSeekSmoke.check(bridge.playbackStateJson().contains("\"displayedPositionMs\":null"),"Retired producer cannot confirm display");
            bridge.reportPresented(id,30250);
            MiniClientNativeSeekSmoke.check(bridge.playbackStateJson().contains("\"displayedPositionMs\":30250"),"Matching renderer observation is distinct from accepted target");
            bridge.handle(19,new byte[0]);
            MiniClientNativeSeekSmoke.check(!bridge.timelineSeek(source,"after_stop",10000)&&bridge.playbackStateJson().contains("\"seekable\":false"),"STOP retires timeline custody and capability");
            System.out.println("Playback state PASS");
        }finally{factory.releaseAll();owner.close();}
    }
}
