package org.opensagetv.webplayer;

import java.util.UUID;

/**
 * One browser MiniClient media lifetime. Source, seek and FLUSH generations are
 * independent so asynchronous work can reject callbacks from a retired epoch.
 */
final class PlaybackSessionContext {
    static final class Token {
        final String sessionId;
        final long sourceGeneration, seekGeneration, flushGeneration;
        final long captionGeneration;
        Token(String id,long source,long seek,long flush){this(id,source,seek,flush,0);}
        Token(String id,long source,long seek,long flush,long caption){sessionId=id;sourceGeneration=source;seekGeneration=seek;flushGeneration=flush;captionGeneration=caption;}
        String json(){return "{\"sessionId\":\""+HttpUtil.json(sessionId)+"\",\"sourceGeneration\":"+sourceGeneration+
                ",\"seekGeneration\":"+seekGeneration+",\"flushGeneration\":"+flushGeneration+",\"captionGeneration\":"+captionGeneration+"}";}
    }

    private final String sessionId;
    private long sourceGeneration,seekGeneration,flushGeneration;
    private long captionGeneration;
    private boolean sourceActive;
    private int selectedAudio=-1,selectedSubtitle=-1;
    private String selectedCaption="off";
    private final SubtitleCueQueue cues=new SubtitleCueQueue(this,true);
    private final SubtitleCueQueue fileCues=new SubtitleCueQueue(this);

    PlaybackSessionContext(){this(UUID.randomUUID().toString().replace("-",""));}
    private PlaybackSessionContext(String id){sessionId=id;}

    /** A quality replacement is the SAME logical playback position, not a
     * new source or user seek. Keep its source/seek identity and selections,
     * but give the warming producer private cue queues. It must not flush or
     * inject captions into the still-playing original before a handoff. */
    synchronized PlaybackSessionContext forkQuality(){
        PlaybackSessionContext next=new PlaybackSessionContext(sessionId);
        next.sourceGeneration=sourceGeneration;next.seekGeneration=seekGeneration;
        next.flushGeneration=flushGeneration;next.captionGeneration=captionGeneration;
        next.sourceActive=sourceActive;next.selectedAudio=selectedAudio;
        next.selectedSubtitle=selectedSubtitle;next.selectedCaption=selectedCaption;
        return next;
    }

    Token beginSource(){Token t; synchronized(this){sourceGeneration++;seekGeneration=0;flushGeneration=0;sourceActive=true;selectedAudio=-1;selectedSubtitle=-1;selectedCaption="off";t=token();}cues.clearAll();fileCues.clearAll();return t;}
    Token beginSeek(){Token t; synchronized(this){if(sourceActive)seekGeneration++;t=token();}cues.clearAll();fileCues.clearAll();return t;}
    Token beginFlush(){Token t; synchronized(this){if(sourceActive)flushGeneration++;t=token();}cues.clearAll();fileCues.clearAll();return t;}
    Token invalidateSource(){Token t; synchronized(this){if(sourceActive){sourceGeneration++;seekGeneration=0;flushGeneration=0;}sourceActive=false;t=token();}cues.clearAll();fileCues.clearAll();return t;}
    Token beginCaptionSelection(){Token t;synchronized(this){captionGeneration++;t=token();}cues.clearAll();return t;}
    synchronized Token token(){return new Token(sessionId,sourceGeneration,seekGeneration,flushGeneration,captionGeneration);}
    synchronized boolean isCurrent(Token t){return t!=null&&sourceActive&&sessionId.equals(t.sessionId)&&sourceGeneration==t.sourceGeneration&&seekGeneration==t.seekGeneration&&flushGeneration==t.flushGeneration;}
    synchronized boolean sourceActive(){return sourceActive;}
    synchronized boolean isCurrentCaption(Token t){return isCurrent(t)&&t.captionGeneration==captionGeneration;}
    synchronized void selectAudio(int index){selectedAudio=index;}
    synchronized void selectSubtitle(int index){selectedSubtitle=index;}
    synchronized void selectCaption(String caption){selectedCaption=caption==null?"off":caption;}
    synchronized String selectionJson(){return "{\"audioTrack\":"+selectedAudio+",\"subtitleTrack\":"+selectedSubtitle+",\"caption\":\""+HttpUtil.json(selectedCaption)+"\"}";}
    SubtitleCueQueue cues(){return cues;}
    SubtitleCueQueue fileCues(){return fileCues;}
}
