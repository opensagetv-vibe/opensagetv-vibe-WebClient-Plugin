package org.opensagetv.webplayer;

/** Public-API ownership/submission tests, not physical playback evidence. */
public final class StockDvdReconfigureSmoke {
    static final class Api implements StockClientPlayback.Api {
        int seeks,prepared,reads; boolean local=true,loaded=true,modal=false,dvd=true,menu=false,playing=true,unknown=false,changed=false;
        Object position=23456L,duration=60000L,rate=1.0f,title=1;Object[] contexts={"AA:BB:CC:DD:EE:FF"};
        public Object call(String method,Object... args){
            if(method.equals("GetUIContextNames"))return contexts;
            if(method.equals("GetMediaFileID"))return args[0];
            throw new AssertionError(method);
        }
        public Object ui(String context,String method,Object... args){
            if(!context.equals(contexts[0]))throw new AssertionError("Foreign UI");
            if(method.equals("IsMediaPlayerFullyLoaded"))return loaded;
            if(method.equals("IsOptionsMenuOpen"))return modal;
            if(method.equals("IsCurrentMediaFileDVD"))return dvd;
            if(method.equals("IsShowingDVDMenu"))return menu;
            if(method.equals("GetCurrentMediaFile"))return changed&&++reads>1?8:7;
            if(method.equals("GetDVDCurrentTitle"))return title;
            if(method.equals("GetRawMediaTime"))return position;
            if(method.equals("GetMediaDuration"))return duration;
            if(method.equals("GetPlaybackRate"))return rate;
            if(method.equals("IsPlaying"))return playing;
            if(method.equals("Seek")){
                if(!args[0].equals(23456L)||prepared!=1)throw new AssertionError("Wrong clock or unprepared profile");
                seeks++;if(unknown)throw new IllegalStateException("Unknown receipt");return null;
            }
            throw new AssertionError("Unexpected control "+method);
        }
        boolean prepare(){prepared++;return true;}
    }
    static void refused(Api a)throws Exception {
        if(StockClientPlayback.reconfigureDvd(a,"aabbccddeeff",true,a::prepare)||a.prepared!=0||a.seeks!=0)
            throw new AssertionError("Unsafe configuration/control");
    }
    public static void main(String[] args)throws Exception {
        for(boolean playing:new boolean[]{true,false}){
            Api a=new Api();a.playing=playing;
            if(!StockClientPlayback.reconfigureDvd(a,"aabbccddeeff",true,a::prepare)||a.seeks!=1)
                throw new AssertionError("Missing one native seek");
        }
        Api a=new Api();a.loaded=false;refused(a);a=new Api();a.modal=true;refused(a);
        a=new Api();a.dvd=false;refused(a);a=new Api();a.menu=true;refused(a);
        a=new Api();a.position=-1L;refused(a);a=new Api();a.position=null;refused(a);
        a=new Api();a.position=Double.NaN;refused(a);a=new Api();a.position=1.5;refused(a);
        a=new Api();a.duration=100L;refused(a);a=new Api();a.rate=16.0f;refused(a);
        a=new Api();a.rate=Float.NaN;refused(a);a=new Api();a.title=0;refused(a);
        a=new Api();a.changed=true;refused(a);a=new Api();
        if(StockClientPlayback.reconfigureDvd(a,"aabbccddeeff",true,()->false)||a.seeks!=0)
            throw new AssertionError("Retired producer submitted");
        a=new Api();a.unknown=true;
        try{StockClientPlayback.reconfigureDvd(a,"aabbccddeeff",true,a::prepare);throw new AssertionError("Unknown swallowed");}
        catch(IllegalStateException expected){}
        if(a.seeks!=1)throw new AssertionError("Unknown Seek replayed");
        a=new Api();try{StockClientPlayback.reconfigureDvd(a,"aabbccddeeff",false,a::prepare);throw new AssertionError();}
        catch(IllegalArgumentException expected){}
        if(a.seeks!=0||a.prepared!=0)throw new AssertionError("Remote client changed");
        System.out.println("PASS DVD public title clock / paused intent / source-modal-rate guards / one-shot unknown receipt");
    }
}
