package org.opensagetv.webplayer;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

/** Media command adapter modeled on Vibe core MediaCmd, with browser TS/HLS as the player backend. */
final class MiniClientMediaBridge {
    private static final int INIT=0, DEINIT=1, OPENURL=16, GETMEDIATIME=17, SETMUTE=18, STOP=19,
            PAUSE=20, PLAY=21, FLUSH=22, PUSHBUFFER=23, GETVIDEORECT=24, SETVIDEORECT=25,
            GETVOLUME=26, SETVOLUME=27, FRAMESTEP=28, SEEK=29, SETRATE=30,
            DVD_NEWCELL=32, DVD_CLUT=33, DVD_SPUCTRL=34, DVD_STC=35, DVD_STREAM=36, DVD_FORMAT=37;

    private final MiniClientSession owner;
    private final SageApiBridge sage;
    private volatile PlaybackSessionContext playbackContext=new PlaybackSessionContext();
    private final DvdNativeSession dvdSession=new DvdNativeSession();
    private final CompanionDvdClient companionDvd=new CompanionDvdClient();
    private final SharedSourcePreview sourcePreviews=new SharedSourcePreview();
    private volatile HlsSessionManager.Session hls;
    private volatile long dvdBrowserGeneration=-1L;
    private volatile long dvdStartingGeneration=-1L;
    private long dvdStartSerial;
    private String dvdSettingsProducer="";
    private StreamOptions configured = StreamOptions.defaults();
    private StreamOptions activeOptions = configured;
    private boolean transportFallback;
    private BufferAdaptiveBridge adaptiveController;
    private long adaptiveSource=-1,adaptiveSeek=-1;
    private String adaptiveProducer="";
    private volatile int mediaId;
    private volatile int segment;
    private volatile double startSeconds;
    private volatile long durationMs;
    private volatile long browserTimeMs;
    private volatile long lastProvenBrowserTimeMs;
    private volatile long browserClockRegressions;
    private volatile float volume=1.0f;
    private volatile boolean paused;
    private volatile boolean browserEnded;
    private volatile boolean muted;
    private volatile boolean boundsKnown;
    private volatile String openUrl="";
    private volatile int sourceX,sourceY,sourceW,sourceH,destX,destY,destW,destH;
    private final LegacyExtenderCaptionBridge legacyCaptions;
    private volatile long legacyCaptionCursor;
    private volatile boolean subtitleCallbacksEnabled;
    private boolean browserCaptionOwner;
    private volatile int sageTvCcState=-1;
    private volatile boolean sageTvCcStateSeen;
    /** Native SEEK and source-owned browser recovery prepare off the media
     * monitor. Browser Apply retains its synchronous contract. This seam permits a
     * deliberately blocked producer in stock-wire regression tests. */
    interface NativeSeekFactory {
        HlsSessionManager.Session start(int mediaId,int segment,long timeMs,StreamOptions options,PlaybackSessionContext context,PlaybackSessionContext.Token token) throws Exception;
        void stop(HlsSessionManager.Session session);
    }
    private final NativeSeekFactory nativeSeekFactory;
    interface QualityFactory {
        HlsSessionManager.Session start(int mediaId,int segment,long timeMs,StreamOptions options,PlaybackSessionContext context,java.util.function.Consumer<HlsSessionManager.Session> registered)throws Exception;
        void stop(HlsSessionManager.Session session);
    }
    private final QualityFactory qualityFactory;
    private static final class QualityHandoff {
        final HlsSessionManager.Session previous;
        final PlaybackSessionContext previousContext,nextContext;
        final StreamOptions previousOptions,nextOptions;
        final long targetMs,beganNs=System.nanoTime();
        long joinMs;
        volatile HlsSessionManager.Session candidate;
        java.util.concurrent.ScheduledFuture<?> deadline;
        boolean published;
        QualityHandoff(HlsSessionManager.Session previous,PlaybackSessionContext context,StreamOptions options,StreamOptions next,long target){
            this.previous=previous;previousContext=context;nextContext=context.forkQuality();
            previousOptions=options;nextOptions=next;targetMs=target;joinMs=target;
        }
    }
    private QualityHandoff qualityHandoff;
    private int qualityAttempts;
    private long qualityAttemptNs;
    private String qualityResult="idle";
    private double qualityResumeSeconds;
    private static final class NativeSeek {
        final long serial,timeMs;
        final int mediaId,segment;
        final StreamOptions options;
        final PlaybackSessionContext.Token token;
        final boolean recovery;
        NativeSeek(long serial,long timeMs,int mediaId,int segment,StreamOptions options,PlaybackSessionContext.Token token,boolean recovery){
            this.serial=serial;this.timeMs=timeMs;this.mediaId=mediaId;this.segment=segment;this.options=options;this.token=token;this.recovery=recovery;
        }
    }
    private long nativeSeekSerial,nativeSeekBaseTimeMs,nativeSeekCompleted,nativeSeekStale,nativeSeekFailures;
    private long nativeSeekAcceptedAtMs,nativeSeekPrepareMs;
    private NativeSeek nativeSeek;
    private boolean nativeSeekWorker;
    // WEB-051: these are distinct observations, not three names for the
    // optimistic native clock. A browser frame is unknown until acknowledged
    // by that exact producer. Never use telemetry to replace the Core clock.
    private long requestedPositionMs=-1,reportedPositionMs=-1,presentedPositionMs=-1;
    private long requestAcceptedAtMs,presentedAtMs;
    private String seekRequestId="",seekFailure="",presentedProducer="";

    MiniClientMediaBridge(MiniClientSession owner) {
        this(owner,null);
    }
    MiniClientMediaBridge(MiniClientSession owner,NativeSeekFactory factory) {
        this(owner,factory,null);
    }
    MiniClientMediaBridge(MiniClientSession owner,NativeSeekFactory factory,QualityFactory quality) {
        this.owner=owner;
        this.nativeSeekFactory=factory==null?new NativeSeekFactory(){
            public HlsSessionManager.Session start(int id,int seg,long ms,StreamOptions options,PlaybackSessionContext context,PlaybackSessionContext.Token token)throws Exception{
                return HlsSessionManager.startNativeSegment(id,seg,ms/1000.0,options,context,token,null);
            }
            public void stop(HlsSessionManager.Session session){if(session!=null)HlsSessionManager.stop(session.id);}
        }:factory;
        qualityFactory=quality==null?new QualityFactory(){
            public HlsSessionManager.Session start(int id,int seg,long ms,StreamOptions options,PlaybackSessionContext context,java.util.function.Consumer<HlsSessionManager.Session> registered)throws Exception{
                HlsSessionManager.Session session=HlsSessionManager.startNativeSegment(id,seg,ms/1000.0,options,context,context.token(),registered);
                long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(20);
                while(!session.stopRequested&&System.nanoTime()<deadline){
                    HlsSessionManager.refreshMetrics(session);
                    if(session.playlistReady)return session;
                    if(!session.running&&session.error.length()>0)throw new java.io.IOException("Quality producer failed: "+compact(session.error));
                    Thread.sleep(50L);
                }
                throw new java.io.IOException("Quality producer did not become ready");
            }
            public void stop(HlsSessionManager.Session session){if(session!=null)HlsSessionManager.stop(session.id);}
        }:quality;
        SageApiBridge s;
        try { s=SageApiBridge.create(); } catch(Exception e) { s=null; }
        this.sage=s;
        this.legacyCaptions=new LegacyExtenderCaptionBridge((pts,duration,payload,flags)->owner.postSubtitleInfo(pts,duration,payload,flags));
    }

    byte[] handle(int cmd, byte[] data) {
        try {
            switch(cmd) {
                case INIT:
                    cancelQuality(false);
                    companionDvd.reset();
                    cancelNativeSeek();
                    int videoFormat=data!=null&&data.length>=4?MiniClientSession.readInt(data,0):0;
                    // INIT owns a fresh decoder/source, not just a DVD epoch.
                    // Stock Windows can transition directly from ordinary
                    // Pull to native DVD. Retaining that ordinary HLS owner
                    // prevents PUSHBUFFER from scheduling the new converter.
                    closeDvdPlayback(false);
                    closePlayback();mediaId=0;
                    return intBytes(dvdSession.init(videoFormat));
                case DEINIT:
                    companionDvd.reset();
                    closeDvdPlayback(true); dvdSession.close(); closePlayback(); mediaId=0;
                    return intBytes(1);
                case OPENURL:
                    openUrl=readOpenUrl(data);
                    if(openUrl.toLowerCase(Locale.US).startsWith("push:dvd")){
                        cancelQuality(false);
                        if(configured.companionDvd&&StockCaptionState.localServer(owner.server()))companionDvd.negotiate(owner.clientIdentity());
                        owner.enqueue("{\"type\":\"dvdCompanion\",\"value\":"+companionDvd.json()+"}");
                        // Compatibility transport: it is still the same native DVD
                        // session and must not be resolved as a SageTV MediaFile.
                        return intBytes(1);
                    }
                    dvdSession.cancelPendingForOrdinaryOpenUrl();
                    open(openUrl,0.0);
                    return intBytes(1);
                case GETMEDIATIME:
                    return intBytes(nativeMediaTime());
                case SETMUTE:
                    muted=data.length>=4 && MiniClientSession.readInt(data,0)!=0;
                    owner.enqueue("{\"type\":\"media\",\"action\":\"mute\",\"value\":"+muted+"}");
                    return intBytes(1);
                case STOP:
                    paused=true;
                    if(dvdSession.pending()) closeDvdPlayback(true);
                    else { closePlayback(); mediaId=0; }
                    owner.enqueue("{\"type\":\"media\",\"action\":\"stop\"}");
                    return intBytes(1);
                case PAUSE:
                    paused=true; owner.enqueue("{\"type\":\"media\",\"action\":\"pause\"}"); return intBytes(1);
                case PLAY:
                    paused=false; owner.enqueue("{\"type\":\"media\",\"action\":\"play\"}"); return intBytes(1);
                case FLUSH:
                    if(dvdSession.pending()){
                        boolean preserveStill=dvdSession.epochHasVideo();
                        if(preserveStill)owner.enqueue("{\"type\":\"dvd\",\"action\":\"freeze\",\"generation\":"+dvdSession.generation()+",\"stillCandidate\":"+dvdSession.epochStillCandidate()+"}");
                        closeDvdPlayback(false);
                        int rv=dvdSession.flush();
                        owner.enqueue("{\"type\":\"dvd\",\"action\":\"flush\",\"generation\":"+dvdSession.generation()+"}");
                        return intBytes(rv);
                    }
                    synchronized(this){
                        browserEnded=false;
                        cancelNativeSeek();cancelQuality(true);qualityResumeSeconds=0;
                        PlaybackSessionContext.Token flushToken=playbackContext.beginFlush();
                        HlsSessionManager.Session flushSession=hls;if(flushSession!=null){flushSession.playbackToken=flushToken;if(flushSession.teletext!=null)flushSession.teletext.updateToken(flushToken,browserTimeMs);if(flushSession.dvb!=null)flushSession.dvb.updateToken(flushToken,browserTimeMs);}
                        owner.enqueue("{\"type\":\"media\",\"action\":\"flush\"}");return intBytes(1);
                    }
                case PUSHBUFFER:
                    if(dvdSession.pending()) {
                        int rv=dvdSession.push(data);
                        synchronized(this){
                            if(hls!=null&&hls.dvdSource!=null&&hls.dvdGeneration!=dvdSession.generation()){
                                owner.enqueue("{\"type\":\"dvd\",\"action\":\"freeze\",\"generation\":"+hls.dvdGeneration+",\"stillCandidate\":true}");
                                closeDvdPlayback(false);
                            }
                        }
                        if(dvdSession.active()&&dvdSession.epochPushedBytes()>0&&hls==null)scheduleDvdEpoch();
                        return intBytes(rv);
                    }
                    // Ordinary browser mode remains PULL-only. Returning generous free
                    // space preserves the legacy bandwidth-probe fallback.
                    return intBytes(16*1024*1024);
                case GETVIDEORECT:
                    return shorts((short)owner.browserVideoWidth(),(short)owner.browserVideoHeight());
                case SETVIDEORECT:
                    if(data.length>=32){
                        boundsKnown=true;
                        sourceX=MiniClientSession.readInt(data,0);sourceY=MiniClientSession.readInt(data,4);
                        sourceW=MiniClientSession.readInt(data,8);sourceH=MiniClientSession.readInt(data,12);
                        destX=MiniClientSession.readInt(data,16);destY=MiniClientSession.readInt(data,20);
                        destW=MiniClientSession.readInt(data,24);destH=MiniClientSession.readInt(data,28);
                        videoBoundsEvent();
                    }
                    return intBytes(0);
                case GETVOLUME:
                    return intBytes(Math.round(volume*65535f));
                case SETVOLUME:
                    if(data.length>=4) volume=Math.max(0f,Math.min(1f,MiniClientSession.readInt(data,0)/65535f));
                    owner.enqueue("{\"type\":\"media\",\"action\":\"volume\",\"value\":"+String.format(Locale.US,"%.5f",volume)+"}");
                    return intBytes(Math.round(volume*65535f));
                case FRAMESTEP:
                    return intBytes(0);
                case SEEK:
                    if(data.length>=8){
                        long ms=MiniClientSession.readLong(data,0);
                        if(dvdSession.pending()) owner.enqueue("{\"type\":\"mediaDebug\",\"message\":\"Ignored browser-local DVD SEEK; stock DVD VM owns title/chapter navigation\"}");
                        else {seekRequestId="";scheduleNativeSeek(ms);}
                    }
                    return new byte[0];
                case SETRATE:
                    float rate = data.length >= 4 ? Float.intBitsToFloat(MiniClientSession.readInt(data,0)) : 1.0f;
                    // HTML media has no portable reverse playback. Report the
                    // actual supported rate rather than falsely claiming it.
                    if (Float.isNaN(rate) || Float.isInfinite(rate) || rate < 0.5f || rate > 2.0f) rate = 1.0f;
                    owner.enqueue("{\"type\":\"media\",\"action\":\"rate\",\"value\":" + rate + "}");
                    return intBytes(Float.floatToIntBits(rate));
                case DVD_STREAM:
                    if(dvdSession.pending()) {
                        int rv=dvdSession.setStream(data);
                        if(rv==0&&data!=null&&data.length>=8&&MiniClientSession.readInt(data,0)==0&&hls!=null)
                            owner.enqueue("{\"type\":\"mediaDebug\",\"message\":\"DVD audio selector updated; applies to the next decoder generation\"}");
                        return intBytes(rv);
                    }
                    // Ordinary-video DVB bitmap selection uses the same numeric command
                    // but a different typed contract: stream type 1 + physical TS PID.
                    if(data.length>=8&&hls!=null){
                        int streamType=MiniClientSession.readInt(data,0),streamPos=MiniClientSession.readInt(data,4);
                        if(streamType==1){
                            boolean ok=HlsSessionManager.selectDvbSourcePid(hls,streamPos)==0;
                            if(ok){
                                playbackContext.selectCaption(streamPos==8192?"off":"dvb");
                                owner.enqueue("{\"type\":\"captionState\",\"value\":\""+(streamPos==8192?"off":"dvb")+"\",\"sourcePid\":"+streamPos+"}");
                            }
                            return intBytes(ok?0:-1);
                        }
                    }
                    return intBytes(-1);
                case DVD_NEWCELL: return intBytes(dvdSession.setNewCell(data));
                case DVD_CLUT: return intBytes(dvdSession.setClut(data));
                case DVD_SPUCTRL: return intBytes(dvdSession.setSpuControl(data));
                case DVD_STC: return intBytes(dvdSession.setStc(data));
                case DVD_FORMAT: return intBytes(dvdSession.setFormat(data));
                default:
                    owner.enqueue("{\"type\":\"mediaDebug\",\"message\":\"Unhandled media command "+cmd+"\"}");
                    return new byte[0];
            }
        } catch(Exception e) {
            owner.enqueue("{\"type\":\"error\",\"message\":\"Media command "+cmd+": "+HttpUtil.json(compact(e.getMessage()))+"\"}");
            if(cmd==SEEK)return new byte[0];
            if(cmd>=DVD_NEWCELL&&cmd<=DVD_FORMAT)return intBytes(-1);
            return intBytes(0);
        }
    }

    static int applyDvbStreamCommand(DvbSubtitleSession dvb,int streamType,int streamPos) {
        if(dvb==null||streamType!=1)return -1;
        return (streamPos==8192?dvb.selectSourcePid(-1):dvb.selectSourcePid(streamPos))?0:-1;
    }

    boolean nativeDvdSource(){return dvdSession.pending();}
    synchronized String nativeVideoLayout(){
        if(!boundsKnown||destW<=0||destH<=0)return "unknown";
        return destW>=owner.width()*.9&&destH>=owner.height()*.9?"fullscreen":"preview";
    }

    synchronized void open(String url,double seekSeconds) throws Exception {
        closePlayback();
        PlaybackSessionContext.Token playbackToken=playbackContext.beginSource();
        if(sage==null) throw new IllegalStateException("sagex API is unavailable");
        File path=mediaPath(url);
        AuthorizedMediaResolver.Resolution resolved=AuthorizedMediaResolver.resolve(sage,path);
        Object mf=resolved.mediaFile;
        owner.enqueue("{\"type\":\"mediaDebug\",\"message\":\"Authorized media path via "+resolved.mode+"\"}");
        mediaId=sage.getMediaFileId(mf);
        segment=resolved.segment(sage);
        Object airing=sage.getMediaFileAiring(mf);
        durationMs=sage.getSegmentDuration(mf,segment);
        startSeconds=Math.max(0.0,seekSeconds);
        browserTimeMs=(long)(startSeconds*1000.0);lastProvenBrowserTimeMs=browserTimeMs;
        activeOptions=configured;transportFallback=false;
        playbackContext.selectAudio(activeOptions.audioTrack);playbackContext.selectSubtitle(activeOptions.subtitleTrack);playbackContext.selectCaption(activeOptions.captions);
        hls=HlsSessionManager.startNativeSegment(mediaId,segment,startSeconds,activeOptions,playbackContext,playbackToken,null);
        durationMs=hls.durationMs;
        legacyCaptionCursor=0;legacyCaptions.clearPending();
        paused=false;
        startEvent(false,false);
        videoBoundsEvent();
    }

    synchronized void seek(long ms) throws Exception { seek(ms, false); }

    private synchronized void seek(long ms, boolean recovery) throws Exception {
        cancelQuality(false);qualityResumeSeconds=0;
        cancelNativeSeek();
        ms=Math.max(0L, ms);
        if(durationMs>0) ms=Math.min(ms, Math.max(0L, durationMs-250L));
        double sec=Math.max(0.0,ms/1000.0);
        if(mediaId<=0){ browserTimeMs=ms; return; }
        sourcePreviews.reset();
        PlaybackSessionContext.Token playbackToken=playbackContext.beginSeek();
        HlsSessionManager.Session replacement=HlsSessionManager.startNativeSegment(mediaId,segment,sec,activeOptions,playbackContext,playbackToken,null);
        HlsSessionManager.Session old=hls;hls=replacement;
        legacyCaptionCursor=0;legacyCaptions.clearPending();if(subtitleCallbacksEnabled)legacyCaptions.postFlush();
        startSeconds=sec;browserTimeMs=ms;lastProvenBrowserTimeMs=ms;
        requestedPositionMs=ms;requestAcceptedAtMs=System.currentTimeMillis();seekRequestId="";seekFailure="";
        if(old!=null)HlsSessionManager.stop(old.id);
        startEvent(true,recovery);
    }

    /** Stock Pull SEEK has no wire reply. Its following GETMEDIATIME/PLAY must
     * not sit behind ffprobe, hardware selection, process creation or cleanup.
     * Publish the accepted/clamped target clock now, not a guessed canvas
     * cursor. One worker keeps only the latest request, never an unbounded
     * queue of encoders. A new source/STOP/FLUSH cancels late publication. */
    private synchronized void scheduleNativeSeek(long ms){
        scheduleNativeSeek(ms,false);
    }

    private synchronized void scheduleNativeSeek(long ms,boolean recovery){
        cancelQuality(false);qualityResumeSeconds=0;
        ms=Math.max(0L,ms);
        if(durationMs>0)ms=Math.min(ms,Math.max(0L,durationMs-250L));
        if(mediaId<=0){browserTimeMs=ms;return;}
        sourcePreviews.reset();
        if(nativeSeek==null)nativeSeekBaseTimeMs=lastProvenBrowserTimeMs;
        nativeSeek=new NativeSeek(++nativeSeekSerial,ms,mediaId,segment,activeOptions,playbackContext.beginSeek(),recovery);
        nativeSeekAcceptedAtMs=System.currentTimeMillis();
        requestedPositionMs=ms;requestAcceptedAtMs=nativeSeekAcceptedAtMs;seekFailure="";
        browserTimeMs=ms;lastProvenBrowserTimeMs=ms;
        legacyCaptionCursor=0;legacyCaptions.clearPending();if(subtitleCallbacksEnabled)legacyCaptions.postFlush();
        // Stock event201 wakes VideoFrame now instead of waiting for the next
        // browser metadata notification/periodic clock poll. This is an
        // existing extender event, not a private Core protocol extension.
        try{owner.sendMediaPlayerUpdate();}catch(java.io.IOException ignored){}
        publishPlaybackState();
        if(nativeSeekWorker)return;
        nativeSeekWorker=true;
        Thread worker=new Thread(()->runNativeSeeks(),"webplayer-native-seek-"+owner.id());
        worker.setDaemon(true);worker.start();
    }

    private void runNativeSeeks(){
        while(true){
            final NativeSeek request;
            synchronized(this){
                request=nativeSeek;
                if(request==null){nativeSeekWorker=false;return;}
            }
            HlsSessionManager.Session created=null,retired=null;
            long began=System.nanoTime();
            try{
                created=nativeSeekFactory.start(request.mediaId,request.segment,request.timeMs,request.options,playbackContext,request.token);
                if(created==null)throw new IllegalStateException("Seek producer did not return a session");
                synchronized(this){
                    if(nativeSeek==request&&nativeSeekSerial==request.serial&&mediaId==request.mediaId&&playbackContext.isCurrent(request.token)){
                        retired=hls;hls=created;created=null;
                        startSeconds=request.timeMs/1000.0;
                        browserTimeMs=request.timeMs;lastProvenBrowserTimeMs=request.timeMs;
                        nativeSeekPrepareMs=java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-began);
                        nativeSeek=null;nativeSeekCompleted++;
                        startEvent(true,request.recovery);
                    }else nativeSeekStale++;
                }
            }catch(Exception failure){
                synchronized(this){
                    if(nativeSeek==request&&nativeSeekSerial==request.serial){
                        // Do not leave an accepted clock spinning forever or
                        // resume caption pumps from a retired seek generation.
                        // Fail visibly; later source Open can recover normally.
                        nativeSeekFailures++;nativeSeek=null;retired=hls;hls=null;
                        seekFailure="Replacement stream preparation failed";
                        browserTimeMs=nativeSeekBaseTimeMs;lastProvenBrowserTimeMs=browserTimeMs;
                        playbackContext.invalidateSource();mediaId=0;
                        owner.enqueue("{\"type\":\"videoStop\"}");
                        owner.enqueue("{\"type\":\"error\",\"message\":\"Seek preparation: "+HttpUtil.json(compact(failure.getMessage()))+"\"}");
                        publishPlaybackState();
                    }
                }
            }finally{
                // Never join old converter shutdown under the bridge monitor.
                // Native clock, pause and volume remain responsive meanwhile.
                retireNativeSeekSession(created);retireNativeSeekSession(retired);
            }
        }
    }

    private void retireNativeSeekSession(HlsSessionManager.Session session){
        if(session==null)return;
        try{nativeSeekFactory.stop(session);}catch(RuntimeException error){owner.enqueue("{\"type\":\"mediaDebug\",\"message\":\"Seek session cleanup failed\"}");}
    }

    private synchronized void cancelNativeSeek(){nativeSeekSerial++;nativeSeek=null;}

    private void startEvent(boolean seek,boolean recovery) {
        browserEnded=false;
        double resumeSeconds=qualityResumeSeconds;qualityResumeSeconds=0;
        presentedPositionMs=-1;presentedProducer="";presentedAtMs=0;
        publishPlaybackState();
        owner.enqueue("{\"type\":\"videoStart\",\"mediaId\":"+mediaId+
            ",\"hlsSession\":\""+HttpUtil.json(hls.id)+"\",\"playlistUrl\":\""+HttpUtil.json(hls.playlistUrl())+
            "\",\"transport\":\""+hls.transport()+"\",\"streamUrl\":\""+HttpUtil.json(hls.mediaUrl())+
            "\",\"startSeconds\":"+String.format(Locale.US,"%.3f",startSeconds)+
            ",\"durationMs\":"+durationMs+",\"seek\":"+seek+",\"recovery\":"+recovery+",\"paused\":"+paused+
            ",\"resumeSeconds\":"+String.format(Locale.US,"%.3f",resumeSeconds)+
            ",\"qualityHandoff\":"+(qualityHandoff!=null&&qualityHandoff.published&&qualityHandoff.candidate==hls)+
            ",\"previousHlsSession\":\""+(qualityHandoff==null?"":HttpUtil.json(qualityHandoff.previous.id))+"\""+
            ",\"transportFallback\":"+transportFallback+",\"streamSettings\":"+hls.settingsJson()+"}");
    }


    /**
     * Start conversion outside the MiniClient media reader.  Capability probes
     * and process creation are allowed to be slow, but every stock media
     * command still needs its reply before SageTV's 30-second socket timeout.
     */
    private void scheduleDvdEpoch() {
        final long generation;
        final long serial;
        final StreamOptions options;
        synchronized(this){
            if(!dvdSession.pending()||dvdSession.epochPushedBytes()<=0)return;
            generation=dvdSession.generation();
            if(hls!=null&&hls.dvdSource!=null&&hls.dvdGeneration==generation)return;
            if(dvdStartingGeneration==generation)return;
            dvdStartingGeneration=generation;
            serial=++dvdStartSerial;
            // A DVD is a fresh source epoch. Use the current browser profile,
            // but force MPEG-2/PS to browser-compatible H.264/AAC HLS.
            activeOptions=configured.forDvdTranscode();
            options=activeOptions;
        }
        Thread starter=new Thread(new Runnable(){public void run(){
            HlsSessionManager.Session created=null;
            try{
                created=HlsSessionManager.startDvd(dvdSession,options);
                boolean stale;
                synchronized(MiniClientMediaBridge.this){
                    stale=serial!=dvdStartSerial||!dvdSession.pending()||dvdSession.generation()!=generation||hls!=null;
                    if(!stale){hls=created;dvdBrowserGeneration=created.dvdGeneration;dvdStartingGeneration=-1L;}
                }
                if(stale){HlsSessionManager.stop(created.id);return;}
                watchDvdReady(created,serial);
            }catch(Exception e){
                if(created!=null)try{HlsSessionManager.stop(created.id);}catch(Exception ignored){}
                synchronized(MiniClientMediaBridge.this){if(serial==dvdStartSerial)dvdStartingGeneration=-1L;}
                owner.enqueue("{\"type\":\"error\",\"message\":\"DVD decoder startup: "+HttpUtil.json(compact(e.getMessage()))+"\"}");
            }
        }},"webplayer-dvd-start-"+generation);starter.setDaemon(true);starter.start();
    }

    private void watchDvdReady(final HlsSessionManager.Session created,final long serial){
        // A DVD is a fresh source epoch. Use the current browser profile, but
        // notify the browser only after FFmpeg publishes playable output.
        Thread watcher=new Thread(new Runnable(){public void run(){
            try{
                while(hls==created&&!created.stopRequested&&!created.playlistReady&&!created.dvdConverterEnded)Thread.sleep(50L);
                synchronized(MiniClientMediaBridge.this){
                    if(hls!=created||serial!=dvdStartSerial)return;
                    if(created.playlistReady){startDvdEvent(created);videoBoundsEvent();}
                    else if(created.dvdConverterEnded){HlsSessionManager.updateDvdBrowserProgress(created,0L);owner.enqueue("{\"type\":\"mediaDebug\",\"message\":\"DVD generation "+created.dvdGeneration+" contained no playable A/V\"}");}
                }
            }catch(InterruptedException e){Thread.currentThread().interrupt();}
        }},"webplayer-dvd-ready-"+created.id.substring(0,Math.min(8,created.id.length())));watcher.setDaemon(true);watcher.start();
    }

    private void startDvdEvent(HlsSessionManager.Session s){
        owner.enqueue("{\"type\":\"videoStart\",\"dvd\":true,\"dvdGeneration\":"+s.dvdGeneration+
            ",\"hlsSession\":\""+HttpUtil.json(s.id)+"\",\"playlistUrl\":\""+HttpUtil.json(s.playlistUrl())+
            "\",\"transport\":\"hls\",\"streamUrl\":\""+HttpUtil.json(s.mediaUrl())+
            "\",\"startSeconds\":0,\"durationMs\":0,\"seek\":false,\"recovery\":false,\"paused\":"+paused+
            ",\"streamSettings\":"+s.settingsJson()+"}");
    }

    private synchronized void closeDvdPlayback(boolean stopVideo){
        dvdStartSerial++;
        dvdStartingGeneration=-1L;
        HlsSessionManager.Session old=hls;
        if(old!=null&&old.dvdSource!=null){hls=null;try{HlsSessionManager.stop(old.id);}catch(Exception ignored){}}
        dvdBrowserGeneration=-1L;
        if(stopVideo)owner.enqueue("{\"type\":\"videoStop\"}");
    }

    synchronized void configure(StreamOptions options) { configured=options; }
    boolean applyDvdSettings(final StreamOptions options,final String expected)throws Exception {
        // Stock owns the VM and source reconstruction; no MCP production
        // dependency. The callback commits only after public source/modal/
        // title/clock validation. Do not hold this monitor across public Seek.
        return owner.reconfigureDvd(()->{
            synchronized(MiniClientMediaBridge.this){
                if(!ownsBrowserStream(expected)||hls.dvdSource==null||!dvdSession.active()||
                   hls.dvdGeneration!=dvdSession.generation()||qualityHandoff!=null||nativeSeek!=null||
                   expected.equals(dvdSettingsProducer))return false;
                configured=options.forNextRecording();dvdSettingsProducer=expected;return true;
            }
        });
    }
    synchronized String streamingJson() {
        return "{\"qualityHandoffRevision\":1,\"qualityRecoveryRevision\":1,\"qualityHandoff\":\""+qualityResult+"\",\"configured\":"+configured.json()+",\"active\":"+(hls==null?"null":hls.settingsJson())+
            ",\"session\":\""+(hls==null?"":hls.id)+"\",\"browserClockRegressions\":"+browserClockRegressions+
            ",\"lastProvenBrowserTimeMs\":"+lastProvenBrowserTimeMs+",\"nativeSeek\":{\"pending\":"+(nativeSeek!=null)+",\"targetMs\":"+(nativeSeek==null?-1:nativeSeek.timeMs)+
            ",\"ageMs\":"+(nativeSeek==null?0:Math.max(0L,System.currentTimeMillis()-nativeSeekAcceptedAtMs))+",\"prepareMs\":"+nativeSeekPrepareMs+",\"completed\":"+nativeSeekCompleted+",\"stale\":"+nativeSeekStale+",\"failures\":"+nativeSeekFailures+"},\"dvd\":"+dvdSession.json()+"}";
    }
    synchronized boolean applySettings(StreamOptions options,boolean now,String expected,long time) throws Exception {
        if(now&&qualityHandoff!=null){if(!ownsBrowserStream(expected))return false;cancelQuality(false);expected=hls==null?"":hls.id;}
        if(now&&hls!=null) {
            if(!matchesHls(expected))return false;
            if(hls.dvdSource!=null)throw new IllegalArgumentException("DVD transcoding settings can be saved for the next source generation; this stock DVD Push stream cannot be safely re-created by an ordinary-file seek");
            StreamOptions previous=activeOptions;boolean fallbackWas=transportFallback;
            activeOptions=options;transportFallback=false;
            try {seek(time>=0?time:browserTimeMs,false);}catch(Exception e){activeOptions=previous;transportFallback=fallbackWas;throw e;}
            // Explicit user Apply may change the range. A quality handoff does
            // not come through here and must retain its original budget/range.
            adaptiveController=null;
        }
        configured=options.forNextRecording();return true;
    }
    synchronized String runtimeRate(String expected,long id,int kbps)throws Exception{
        if(hls==null||!matchesHls(expected)||nativeSeek!=null||qualityHandoff!=null||hls.runtimeRate==null)
            throw new IllegalStateException("runtime_rate_owner_unavailable");
        hls.runtimeRateJson();
        return hls.runtimeRate.request(id,kbps);
    }
    synchronized String runtimeRateStatus(String expected){
        if(hls==null||!matchesHls(expected))throw new IllegalStateException("runtime_rate_owner_changed");
        return hls.runtimeRateJson();
    }
    synchronized String bufferReport(String expected,long report,long localPosition,long reserve,boolean buffering,boolean eligible)throws Exception{
        if(hls==null||!matchesHls(expected))throw new IllegalStateException("adaptive_owner_changed");
        if(!activeOptions.adaptiveQuality||!BufferAdaptiveBridge.available())return "{\"revision\":0,\"available\":false,\"reason\":\"fixed-or-provider-unavailable\"}";
        PlaybackSessionContext.Token epoch=playbackContext.token();
        if(adaptiveController==null||adaptiveSource!=epoch.sourceGeneration){
            adaptiveController=new BufferAdaptiveBridge(activeOptions.adaptiveMinimumKbps,activeOptions.videoKbps,hls.runtimeRate!=null);
            adaptiveSource=epoch.sourceGeneration;adaptiveSeek=-1;
        }
        if(adaptiveSeek!=epoch.seekGeneration||!adaptiveProducer.equals(hls.id)){
            adaptiveController.epoch();adaptiveSeek=epoch.seekGeneration;adaptiveProducer=hls.id;
        }
        hls.runtimeRateJson();
        boolean state=eligible&&!paused&&nativeSeek==null&&qualityHandoff==null&&(hls.runtimeRate==null||hls.runtimeRate.available())&&!hls.isTs()&&hls.dvdSource==null&&
            !dvdSession.pending()&&hls.streamPlan!=null&&!hls.streamPlan.copyVideo;
        boolean health=hls.error.isEmpty()&&(hls.running||hls.endList&&hls.exitCode==0)&&
            (hls.endList||hls.lastSegmentAt>0&&System.currentTimeMillis()-hls.lastSegmentAt<=10000)&&
            localPosition>=0&&hls.hlsSeconds*1000-localPosition>5000;
        return adaptiveController.report(report,reserve,buffering,state,health,hls.runtimeRate==null?hls.streamPlan.options.videoKbps:hls.runtimeRate.currentKbps());
    }
    synchronized boolean fallback(String expected,long time) throws Exception {
        return fallback(expected,time,false);
    }
    synchronized boolean fallback(String expected,long time,boolean videoDecodeFailure) throws Exception {
        if(qualityHandoff!=null){if(!ownsBrowserStream(expected))return false;cancelQuality(false);expected=hls==null?"":hls.id;}
        if(hls==null||!matchesHls(expected))return false;
        if(!activeOptions.allowFallback)throw new IllegalArgumentException("Automatic fallback is disabled in streaming settings");
        if(transportFallback)throw new IllegalArgumentException("This recording has already used its compatibility fallback");
        StreamOptions previous=activeOptions;
        if(!hls.isTs()&&!activeExplicitVideoCopy())throw new IllegalArgumentException("No additional compatibility fallback is available for this HLS session");
        activeOptions=activeOptions.compatibilityFallback(hls.isTs(),videoDecodeFailure&&activeExplicitVideoCopy());
        transportFallback=true;
        try {seek(time>=0?time:browserTimeMs,true);}catch(Exception e){activeOptions=previous;transportFallback=false;throw e;}
        return true;
    }

    /** Explicitly optional, session-only quality operation. Exact producer
     * custody and observed transcode ownership are mandatory. It never edits
     * configured defaults or recreates DVD/Copy streams. */
    synchronized boolean reduceQuality(String expected,long time,int kbps,int height)throws Exception{
        if(qualityHandoff!=null)return false;
        if(expected==null||expected.length()==0||!ownsBrowserStream(expected)||nativeSeek!=null)return false;
        if(hls.dvdSource!=null||dvdSession.pending()||hls.streamPlan==null||hls.streamPlan.copyVideo)
            throw new IllegalArgumentException("Quality reduction requires an ordinary transcoded stream");
        StreamOptions previous=activeOptions;
        activeOptions=previous.reducedQuality(kbps,height);
        try{HlsSessionManager.quiesceForQuality(hls);seek(time>=0?time:browserTimeMs,false);}
        catch(Exception e){activeOptions=previous;throw e;}
        return true;
    }

    /** Optional browser handoff contract, separate from legacy /quality. Keep
     * the original decoder stream AND caption queues alive during warmup.
     * Native media reader never waits for this HTTP producer preparation. */
    boolean prepareQuality(String expected,long time,int kbps,int height)throws Exception{
        final QualityHandoff handoff;
        synchronized(this){
            if(!ownsBrowserStream(expected)||nativeSeek!=null||qualityHandoff!=null)return false;
            if(paused||hls.isTs()||hls.dvdSource!=null||dvdSession.pending()||hls.streamPlan==null||hls.streamPlan.copyVideo)
                throw new IllegalArgumentException("Quality handoff requires playing HLS Transcode");
            StreamOptions next=activeOptions.handoffQuality(kbps,height,configured);
            long now=System.nanoTime();
            if(qualityAttempts>=2||qualityAttempts>0&&now-qualityAttemptNs<java.util.concurrent.TimeUnit.SECONDS.toNanos(60))
                throw new IllegalArgumentException("Quality change cooldown/budget reached");
            long target=Math.max(0L,time>=0?time:browserTimeMs);
            if(durationMs>0)target=Math.min(target,Math.max(0,durationMs-250L));
            handoff=new QualityHandoff(hls,playbackContext,activeOptions,next,target);
            if(!HlsSessionManager.claimQualitySlot(handoff))throw new IllegalArgumentException("Another quality handoff is pending");
            qualityAttempts++;qualityAttemptNs=now;qualityHandoff=handoff;qualityResult="preparing";
            // Accepted playback changes outrank optional image work. Reset
            // only our read-only lease, outside its HTTP worker; never stop
            // another client's producer or purge work on admission refusal.
            sourcePreviews.reset();
            handoff.deadline=HlsSessionManager.qualityDeadline(()->expireQuality(handoff));
        }
        try{
            HlsSessionManager.Session candidate=qualityFactory.start(handoff.previous.mediaId,handoff.previous.firstSegment,handoff.targetMs,
                handoff.nextOptions,handoff.nextContext,created->{
                    synchronized(MiniClientMediaBridge.this){
                        handoff.candidate=created;
                        if(qualityHandoff!=handoff){created.stopRequested=true;throw new IllegalStateException("Quality handoff cancelled");}
                    }
                });
            // Old playback advances during warmup. Do not attach a manifest
            // still behind it: players may clamp startPosition and replay the
            // scene. Wait boundedly for real reserve at the latest join point,
            // OUTSIDE the native clock/pause monitor; a slow encoder loses the
            // handoff, never the working original stream.
            long readyDeadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(20);
            while(true){
                synchronized(this){
                    if(qualityHandoff!=handoff||hls!=handoff.previous)throw new IllegalStateException("Quality handoff cancelled");
                    long join=Math.max(handoff.targetMs,browserTimeMs);
                    if(durationMs>0)join=Math.min(join,Math.max(0,durationMs-250L));
                    long required=join-handoff.targetMs+(candidate.endList?100L:1000L);
                    if(candidate.hlsSeconds*1000.0>=required)break;
                }
                if(candidate.stopRequested||System.nanoTime()>=readyDeadline)throw new java.io.IOException("Quality replacement could not catch current playback");
                HlsSessionManager.refreshMetrics(candidate);Thread.sleep(50L);
            }
            synchronized(this){
                if(qualityHandoff!=handoff||hls!=handoff.previous||playbackContext!=handoff.previousContext||!playbackContext.isCurrent(handoff.nextContext.token())){
                    candidate.stopRequested=true;throw new IllegalStateException("Quality handoff superseded");
                }
                handoff.candidate=candidate;handoff.published=true;
                hls=candidate;playbackContext=handoff.nextContext;activeOptions=handoff.nextOptions;
                handoff.joinMs=Math.max(handoff.targetMs,browserTimeMs);
                if(durationMs>0)handoff.joinMs=Math.min(handoff.joinMs,Math.max(0,durationMs-250L));
                startSeconds=candidate.startSeconds;browserTimeMs=handoff.joinMs;lastProvenBrowserTimeMs=browserTimeMs;
                qualityResumeSeconds=Math.max(0,browserTimeMs/1000.0-startSeconds);qualityResult="waiting-for-presentation";
                legacyCaptionCursor=0;legacyCaptions.clearPending();if(subtitleCallbacksEnabled)legacyCaptions.postFlush();
                startEvent(true,false);qualityResumeSeconds=0;
                return true;
            }
        }catch(Exception failure){
            synchronized(this){if(qualityHandoff==handoff){qualityResult="preparation-failed";cancelQuality(false);}}
            throw failure;
        }
    }

    private synchronized void expireQuality(QualityHandoff expected){
        if(qualityHandoff!=expected)return;
        qualityResult="timed-out";cancelQuality(true);
    }

    synchronized boolean abortQuality(String expected){
        QualityHandoff handoff=qualityHandoff;
        if(handoff==null||!handoff.published||handoff.candidate==null||!handoff.candidate.id.equals(expected))return false;
        qualityResult="client-aborted";cancelQuality(true);return true;
    }

    /** Caller holds bridge monitor; cleanup NEVER waits on it. Slot remains
     * occupied until the owner has retired the exact losing producer. */
    private synchronized void cancelQuality(boolean restoreBrowser){
        final QualityHandoff handoff=qualityHandoff;if(handoff==null)return;
        if("preparing".equals(qualityResult)||"waiting-for-presentation".equals(qualityResult))qualityResult="superseded";
        qualityHandoff=null;if(handoff.deadline!=null)handoff.deadline.cancel(false);
        HlsSessionManager.Session candidate=handoff.candidate;if(candidate!=null)candidate.stopRequested=true;
        if(handoff.published&&hls==candidate){
            hls=handoff.previous;playbackContext=handoff.previousContext;activeOptions=handoff.previousOptions;
            startSeconds=hls.startSeconds;
            // The old representation contains the original absolute anchor.
            // Resume it at the most recently accepted handoff position, never
            // reload its playlist at zero and replay earlier programming.
            browserTimeMs=handoff.joinMs;lastProvenBrowserTimeMs=browserTimeMs;
            qualityResumeSeconds=Math.max(0,browserTimeMs/1000.0-startSeconds);
            legacyCaptionCursor=0;legacyCaptions.clearPending();if(subtitleCallbacksEnabled)legacyCaptions.postFlush();
            if(restoreBrowser){startEvent(true,true);qualityResumeSeconds=0;}
        }
        retireQuality(handoff,candidate);
    }

    private void retireQuality(final QualityHandoff handoff,final HlsSessionManager.Session loser){
        Thread cleanup=new Thread(()->{
            try{if(loser!=null)qualityFactory.stop(loser);}
            finally{HlsSessionManager.releaseQualitySlot(handoff);}
        },"webplayer-quality-retire-"+owner.id());cleanup.setDaemon(true);cleanup.start();
    }

    private boolean activeExplicitVideoCopy(){
        StreamPlan p=hls==null?null:hls.streamPlan;
        return p!=null&&p.copyVideo&&"copy".equals(p.options.videoMode);
    }

    synchronized boolean goLive(String expected)throws Exception {
        if(expected==null||expected.isEmpty()||!matchesHls(expected)||dvdSession.pending()||hls==null)return false;
        final int expectedMedia=mediaId;
        return StockClientPlayback.goLive(owner.clientIdentity(),StockCaptionState.localServer(owner.server()),expectedMedia,
            ()->mediaId==expectedMedia&&matchesHls(expected));
    }

    synchronized void reportStreamHealth(String expected,long timeMs,long ahead,int ready,int network,boolean paused,boolean ended,boolean seeking,int recoveries){
        if(expected==null||expected.isEmpty()||!matchesHls(expected)||hls==null)return;
        hls.healthBrowserAt=System.currentTimeMillis();hls.healthBrowserTimeMs=Math.max(0,timeMs);
        hls.healthBufferAheadMs=ahead>=0&&ahead<=86400000?ahead:-1;
        hls.healthReadyState=ready>=0&&ready<=4?ready:-1;hls.healthNetworkState=network>=0&&network<=3?network:-1;
        hls.healthPaused=paused;hls.healthEnded=ended;hls.healthSeeking=seeking;
        hls.healthIntentPaused=this.paused;
        hls.healthRecoveryAttempts=Math.max(0,Math.min(100,recoveries));
    }

    synchronized void reportBufferRepair(String expected,boolean repaired){if(hls!=null&&expected!=null&&expected.equals(hls.id))hls.healthBrowserRepair=repaired;}
    synchronized void reportPlaybackRevision(String expected,String revision){
        if(hls!=null&&expected!=null&&expected.equals(hls.id))
            hls.healthBrowserRevision=revision!=null&&revision.matches("web[0-9]{1,4}\\.[0-9]{1,3}")?revision:"unknown";
    }
    // Socket failure evidence must survive UI cleanup and must not wait on the
    // media monitor. Retain only a category, never raw exception URLs/paths.
    void recordNativeTransportFailure(Throwable failure){
        HlsSessionManager.Session current=hls;if(current==null)return;
        current.healthNativeError=StreamHealthDiagnostics.transportFailure(failure);
        current.healthNativeErrorAt=System.currentTimeMillis();
        StreamHealthDiagnostics.sample(current,true);
    }

    synchronized boolean reportBrowserState(String expectedHlsSession,long timeMs,int videoWidth,int videoHeight,float volume,boolean paused,boolean ended){
        // An old video generation must not drag the accepted seek clock back,
        // overwrite a newer Pause/Play, or repopulate old caption queues.
        if(nativeSeek!=null)return false;
        if(dvdSession.pending()){
            if(hls==null&&expectedHlsSession!=null&&expectedHlsSession.length()>0)return false;
            if(hls!=null&&expectedHlsSession!=null&&expectedHlsSession.length()>0&&!matchesHls(expectedHlsSession))return false;
            if(hls!=null&&hls.dvdSource!=null&&hls.dvdGeneration!=dvdSession.generation())return false;
            if(timeMs>=0)dvdSession.updatePlayerClock(timeMs);
            if(hls!=null)HlsSessionManager.updateDvdBrowserProgress(hls,timeMs,ended);
        } else if(!matchesHls(expectedHlsSession)) return false;
        if(hls!=null && hls.durationMs>0) durationMs=hls.durationMs;
        if(timeMs>=0) {
            long candidate=Math.max(0,timeMs);
            reportedPositionMs=candidate;
            if(!dvdSession.pending() && candidate+1500L<lastProvenBrowserTimeMs) {
                browserClockRegressions++;
                candidate=lastProvenBrowserTimeMs;
            } else if(candidate>lastProvenBrowserTimeMs) lastProvenBrowserTimeMs=candidate;
            browserTimeMs=candidate;
            if(hls!=null&&!dvdSession.pending())hls.broadcastTimeMs=candidate;
        }
        if(!Float.isNaN(volume) && !Float.isInfinite(volume) && volume>=0) this.volume=Math.max(0f,Math.min(1f,volume));
        this.paused=paused;
        browserEnded=ended&&hls!=null&&hls.id.equals(expectedHlsSession);
        pumpLegacyCaptions();
        return true;
    }

    /** Stock MiniPlayer's basic Pull clock uses the signed four-byte -1 EOS
     * sentinel. Keep the last real file clock internally: the server owns live
     * programme advance and watched/resume policy. Never invent another Watch,
     * enable detailed (five-byte) replies, or apply ordinary EOS to DVD drains.
     * Encoder EOF alone is read-ahead, not proof the browser presented the tail.
     */
    private synchronized int nativeMediaTime(){
        if(dvdSession.pending())return (int)Math.max(0L,dvdSession.mediaTimeMs());
        HlsSessionManager.Session current=hls;
        if(mediaId>0&&nativeSeek==null&&NativeRecordingSegment.exhaustedSeek(current))return -1;
        if(browserEnded&&mediaId>0&&nativeSeek==null&&current!=null&&current.dvdSource==null
                &&!current.isTs()&&!current.stopRequested&&!current.running&&!current.activeRecording
                &&current.endList&&current.exitCode==0)return -1;
        return (int)Math.max(0L,browserTimeMs);
    }

    synchronized void setSubtitleCallbacksEnabled(boolean enabled){
        subtitleCallbacksEnabled=enabled;legacyCaptionCursor=0;legacyCaptions.clearPending();
        if(enabled)legacyCaptions.postFlush();
    }

    synchronized void setSageTvClosedCaptionState(int state){
        sageTvCcStateSeen=true;sageTvCcState=Math.max(0,state);
        // Stock property values are authoritative only for STV ownership. Local
        // caption modes keep their own renderer and never mirror event-225.
        if(sageTvCcState==0){
            legacyCaptions.clearPending();
            if(!browserCaptionOwner&&(activeOptions==null||!activeOptions.browserCaptionRendering))playbackContext.cues().clearAll();
            if(subtitleCallbacksEnabled)legacyCaptions.postFlush();
        }
    }

    private void pumpLegacyCaptions(){
        HlsSessionManager.Session s=hls;if(!subtitleCallbacksEnabled||s==null||browserCaptionOwner||activeOptions!=null&&activeOptions.browserCaptionRendering)return;
        // If VIDEO_CC_STATE is present, state zero means stock STV captions are
        // off. On older stock servers that omit the property, callbacks are
        // still delivered and the STV's own CC1/CC2 selection remains the
        // authority (the proven extender fallback contract).
        if(sageTvCcStateSeen&&sageTvCcState==0)return;
        File f=new File(s.directory,"captions.bin");
        try{
            boolean preferTeletext=activeOptions!=null&&"stv".equals(activeOptions.captionAuthority)&&hasObservedTeletext(s.sourceInfo);
            if(!preferTeletext){
                // The tap starts at zero for EACH producer; browserTimeMs is
                // file-relative. Gating against the latter after a seek sends
                // a whole target-position's worth of future CC immediately.
                // Keep encoded timestamps/control bytes intact and translate
                // only the drain clock into this exact producer's epoch.
                long captionTimeMs=Math.max(0L,browserTimeMs-Math.round(s.startSeconds*1000.0));
                legacyCaptionCursor=A53CaptionTap.readPackets(f,legacyCaptionCursor,captionTimeMs+10000L,(pts,data)->legacyCaptions.onCeaSample(pts,data));
                legacyCaptions.drainTo(captionTimeMs);
            }
            if(activeOptions!=null&&"stv".equals(activeOptions.captionAuthority)&&hls.playbackToken!=null){
                java.util.List<SubtitleCue> due=playbackContext.cues().drainDue(hls.playbackToken,Math.max(0,browserTimeMs)+80L,128);
                int channel=sageTvCcState==2?1:0;
                for(SubtitleCue cue:due)if(cue.kind==SubtitleCue.Kind.TEXT&&cue.owner==SubtitleCue.Owner.LOCAL_BROADCAST){
                    byte[] payload=TeletextCea608Bridge.encode(cue.clear?"":cue.text,channel,cue.ptsMs);
                    owner.postSubtitleInfo(cue.ptsMs*45L,0,payload,LegacyExtenderCaptionBridge.CC_SUBTITLE|LegacyExtenderCaptionBridge.PTS_VALID);
                    // Older stock servers do not publish VIDEO_CC_STATE. Mirror
                    // the selected Teletext service onto both legacy CEA-608
                    // channels so either stock CC1 or CC2 can render it.
                    if(!sageTvCcStateSeen){
                        byte[] cc2=TeletextCea608Bridge.encode(cue.clear?"":cue.text,1,cue.ptsMs);
                        owner.postSubtitleInfo(cue.ptsMs*45L,0,cc2,LegacyExtenderCaptionBridge.CC_SUBTITLE|LegacyExtenderCaptionBridge.PTS_VALID);
                    }
                }
            }
        }catch(Exception e){owner.enqueue("{\"type\":\"mediaDebug\",\"message\":\"legacy caption bridge: "+HttpUtil.json(compact(e.getMessage()))+"\"}");}
    }

    synchronized String captionAuthorityJson(){return "{\"callbacks\":"+subtitleCallbacksEnabled+",\"ccStateSeen\":"+sageTvCcStateSeen+",\"ccState\":"+sageTvCcState+",\"cursor\":"+legacyCaptionCursor+",\"pending\":"+legacyCaptions.pendingSamples()+",\"forwardedSamples\":"+legacyCaptions.forwardedSamples()+",\"forwardedBytes\":"+legacyCaptions.forwardedBytes()+"}";}
    synchronized String dvdJson(){return dvdSession.json();}
    String companionDvdJson(){return companionDvd.json();}
    boolean companionDvdAction(String operation){return dvdSession.pending()&&companionDvd.action(operation);}
    DvdNativeSession dvdSession(){return dvdSession;}

    private static boolean hasObservedTeletext(MediaProbe.Info info){if(info==null)return false;for(MediaProbe.Track t:info.tracks)if("teletext".equals(t.serviceKind)&&"observed-pmt".equals(t.evidence))return true;return false;}

    private boolean matchesHls(String expected) {
        return expected == null || expected.length() == 0 || (hls != null && expected.equals(hls.id));
    }

    synchronized boolean recoverFromBrowserPosition(String expected, long timeMs) throws Exception {
        // Recovery is a source-owned request, never a legacy unscoped seek.
        // A slow probe/process launch must not hold stock clock/Pause replies
        // or let another HTTP retry start a parallel replacement.
        if (mediaId <= 0 || expected==null || expected.isEmpty() || !matchesHls(expected)
                || dvdSession.pending() || nativeSeek!=null) return false;
        scheduleNativeSeek(timeMs>=0?timeMs:browserTimeMs,true);
        return true;
    }

    synchronized boolean seekFromBrowser(String expected, long timeMs) throws Exception {
        if (mediaId <= 0 || !matchesHls(expected)) return false;
        seek(timeMs, false); return true;
    }
    /** The source epoch is the custody check for rapid local scrubbing. HLS
     * IDs change on each seek; requiring the previous ID would incorrectly
     * discard the user's newer intent within the SAME source epoch. */
    synchronized boolean timelineSeek(long sourceGeneration,String requestId,long timeMs){
        if(requestId==null||!requestId.matches("[a-zA-Z0-9_-]{1,48}")||timeMs<0)
            throw new IllegalArgumentException("Invalid timeline request");
        if(!playbackContext.sourceActive()||sourceGeneration!=playbackContext.token().sourceGeneration||mediaId<=0||dvdSession.pending())return false;
        seekRequestId=requestId;scheduleNativeSeek(timeMs);return true;
    }
    synchronized void reportPresented(String expected,long timeMs){
        if(nativeSeek!=null||timeMs<0||timeMs>Long.MAX_VALUE/2||!ownsBrowserStream(expected))return;
        long maximum=durationMs>0?durationMs+2000L:Long.MAX_VALUE/2;
        if(timeMs>maximum)return;
        presentedPositionMs=timeMs;presentedProducer=expected;presentedAtMs=System.currentTimeMillis();
        QualityHandoff handoff=qualityHandoff;
        if(handoff!=null&&handoff.published&&handoff.candidate==hls&&timeMs>=handoff.joinMs){
            qualityHandoff=null;if(handoff.deadline!=null)handoff.deadline.cancel(false);
            qualityResult="presented";retireQuality(handoff,handoff.previous);
        }
    }
    /** Cheap versioned snapshot: no ffprobe, API jobs, process waits or
     * filesystem access. Missing bounds/frames remain null, never guessed. */
    synchronized String playbackStateJson(){
        HlsSessionManager.Session current=hls;
        boolean active=playbackContext.sourceActive()&&current!=null;
        boolean dvd=dvdSession.pending()||(current!=null&&current.dvdSource!=null);
        long end=current!=null&&current.durationMs>0?current.durationMs:durationMs;
        boolean canSeek=active&&!dvd&&end>0;
        boolean displayed=current!=null&&current.id.equals(presentedProducer)&&presentedPositionMs>=0;
        String phase=seekFailure.length()>0?"failed":nativeSeek!=null?"preparing":!active?"idle":displayed?(paused?"paused":"playing"):current.playlistReady?"waiting-for-browser":"waiting-for-segments";
        return "{\"schemaVersion\":1,\"bufferAdaptationRevision\":"+(BufferAdaptiveBridge.available()?1:0)+",\"runtimeBitrateControl\":"+(current==null?"null":current.runtimeRateJson())+",\"qualityHandoffRevision\":1,\"qualityRecoveryRevision\":1,\"qualityHandoff\":\""+qualityResult+"\",\"source\":"+playbackContext.token().json()+",\"mediaId\":"+(active?mediaId:0)+
            ",\"producer\":\""+(current==null?"":HttpUtil.json(current.id))+"\",\"phase\":\""+phase+"\",\"dvd\":"+dvd+
            ",\"paused\":"+paused+",\"seekable\":"+canSeek+",\"seekStartMs\":"+(canSeek?"0":"null")+
            ",\"seekEndMs\":"+(canSeek?Long.toString(end):"null")+",\"rangeSource\":\""+(canSeek?"media-duration":"unavailable")+"\""+
            ",\"liveEdgeMs\":"+(canSeek&&current.activeRecording?Long.toString(end):"null")+
            ",\"requestedPositionMs\":"+(requestedPositionMs<0?"null":Long.toString(requestedPositionMs))+
            ",\"acceptedPositionMs\":"+(active&&requestedPositionMs>=0?Long.toString(requestedPositionMs):"null")+
            ",\"reportedPositionMs\":"+(reportedPositionMs<0?"null":Long.toString(reportedPositionMs))+
            ",\"displayedPositionMs\":"+(displayed?Long.toString(presentedPositionMs):"null")+
            ",\"requestId\":\""+HttpUtil.json(seekRequestId)+"\",\"pending\":"+(nativeSeek!=null)+
            ",\"error\":"+(seekFailure.length()==0?"null":"\""+HttpUtil.json(seekFailure)+"\"")+
            ",\"timing\":{\"acceptedAtMs\":"+(requestAcceptedAtMs==0?"null":Long.toString(requestAcceptedAtMs))+
            ",\"prepareMs\":"+(requestAcceptedAtMs>0&&nativeSeek==null?Long.toString(nativeSeekPrepareMs):"null")+",\"presentedAtMs\":"+(displayed?Long.toString(presentedAtMs):"null")+
            ",\"stockUiProcessedAtMs\":null},\"producerReady\":"+(current!=null&&current.playlistReady)+"}";
    }
    private void publishPlaybackState(){owner.enqueue("{\"type\":\"playbackState\",\"value\":"+playbackStateJson()+"}");}
    /** Optional image work never holds the native media/clock monitor. Only
     * this exact local completed single-segment library source is eligible;
     * multi-segment offsets/DVD/live media keep existing viewed-frame previews.
     * The shared provider rechecks library/writer/file identity independently. */
    SharedSourcePreview.Image sourcePreview(long sourceGeneration,long positionMs){
        final int selectedId,selectedSegment;
        synchronized(this){
            if(!previewCurrent(sourceGeneration)||sage==null||!StockCaptionState.localServer(owner.server()))return null;
            selectedId=mediaId;selectedSegment=segment;
        }
        try{
            Object mf=sage.getMediaFile(selectedId);
            if(mf==null||selectedSegment!=0||sage.getNumberOfSegments(mf)!=1||sage.isFileCurrentlyRecording(mf))return null;
            File file=sage.getFileForSegment(mf,0);if(file==null)return null;
            String path=file.getAbsolutePath();
            return sourcePreviews.image(sourceGeneration+":"+selectedId+":"+path,path,positionMs,()->{
                synchronized(MiniClientMediaBridge.this){return previewCurrent(sourceGeneration)&&mediaId==selectedId&&segment==selectedSegment;}
            });
        }catch(Exception unavailable){return null;}
    }
    private boolean previewCurrent(long sourceGeneration){
        return playbackContext.sourceActive()&&playbackContext.token().sourceGeneration==sourceGeneration
                &&mediaId>0&&hls!=null&&!hls.activeRecording&&hls.dvdSource==null&&!dvdSession.pending()&&nativeSeek==null&&qualityHandoff==null;
    }
    synchronized boolean ownsBrowserStream(String expected){return hls!=null&&expected!=null&&expected.length()>0&&matchesHls(expected);}
    synchronized boolean selectBrowserCaptions(String expected,String kind,int pid,int page,String language){
        if(!ownsBrowserStream(expected)||hls.dvdSource!=null)return false;
        boolean selected=HlsSessionManager.selectBroadcast(hls,kind,pid,page,language);
        if(selected&&!browserCaptionOwner){browserCaptionOwner=true;legacyCaptions.clearPending();if(subtitleCallbacksEnabled)legacyCaptions.postFlush();}
        return selected;
    }

    long lastBrowserMediaReadNs(){HlsSessionManager.Session current=hls;return current==null?0:current.lastBrowserMediaReadNs;}
    synchronized void close(){ closeDvdPlayback(true); dvdSession.close(); closePlayback(); }
    private synchronized void closePlayback(){
        browserEnded=false;
        sourcePreviews.reset();
        cancelQuality(false);qualityAttempts=0;qualityAttemptNs=0;qualityResult="idle";qualityResumeSeconds=0;
        companionDvd.reset();
        cancelNativeSeek();
        requestedPositionMs=-1;reportedPositionMs=-1;presentedPositionMs=-1;
        requestAcceptedAtMs=0;presentedAtMs=0;seekRequestId="";seekFailure="";presentedProducer="";
        legacyCaptionCursor=0;legacyCaptions.clearPending();
        playbackContext.invalidateSource();
        HlsSessionManager.Session old=hls;hls=null;
        if(old!=null) try{HlsSessionManager.stop(old.id);}catch(Exception ignored){}
        owner.enqueue("{\"type\":\"videoStop\"}");
    }

    private void videoBoundsEvent(){
        owner.enqueue("{\"type\":\"videoBounds\",\"src\":["+sourceX+","+sourceY+","+sourceW+","+sourceH+"]"+
                ",\"dst\":["+(boundsKnown?destX:0)+","+(boundsKnown?destY:0)+","+(boundsKnown?destW:owner.width())+","+(boundsKnown?destH:owner.height())+"]}");
    }

    private static String readOpenUrl(byte[] data)throws Exception{
        if(data==null||data.length<4)return "";
        int n=MiniClientSession.readInt(data,0); if(n<=1)return "";
        n=Math.min(n-1,data.length-4);
        return new String(data,4,n,StandardCharsets.ISO_8859_1).trim();
    }

    static File mediaPath(String url)throws Exception{return MediaUrlPath.decode(url);}

    private static byte[] intBytes(int v){return new byte[]{(byte)(v>>>24),(byte)(v>>>16),(byte)(v>>>8),(byte)v};}
    private static byte[] shorts(short a,short b){return new byte[]{(byte)(a>>>8),(byte)a,(byte)(b>>>8),(byte)b};}
    private static String compact(String s){return s==null?"unknown error":s.replace('\r',' ').replace('\n',' ').trim();}
}
