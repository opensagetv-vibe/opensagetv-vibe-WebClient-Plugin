package org.opensagetv.webplayer;

/** An explicit library Play intent, scoped to this local browser MiniClient.
 * Public SageTV API only; no MCP, private renderer or fallback to another UI. */
final class StockClientPlayback {
    interface Current { boolean current(); }
    interface Api {
        Object call(String method,Object... args)throws Exception;
        Object ui(String context,String method,Object... args)throws Exception;
    }
    static boolean goLive(Api api,String identity,boolean local,int expectedMediaId,Current current)throws Exception {
        if(expectedMediaId<=0)return false;
        String context=context(api,identity,local);
        if(!Boolean.TRUE.equals(api.ui(context,"IsMediaPlayerFullyLoaded"))||
           Boolean.TRUE.equals(api.ui(context,"IsCurrentMediaFileDVD")))return false;
        Object media=api.ui(context,"GetCurrentMediaFile");
        if(media==null||!Integer.valueOf(expectedMediaId).equals(api.call("GetMediaFileID",media))||
           !Boolean.TRUE.equals(api.call("IsTVFile",media))||
           !Boolean.TRUE.equals(api.call("IsFileCurrentlyRecording",media)))return false;
        Object edge=api.ui(context,"GetAvailableSeekingEnd");
        if(!(edge instanceof Number)||((Number)edge).longValue()<=0||!current.current())return false;
        // Public absolute stock clock, not a browser/segment-relative offset.
        // One intent; no Watch/Record/retune or retry of an unknown receipt.
        api.ui(context,"Seek",Long.valueOf(((Number)edge).longValue()));
        api.ui(context,"Play");
        return true;
    }
    static boolean goLive(String identity,boolean local,int mediaId,Current current)throws Exception {
        return goLive(runtime(),identity,local,mediaId,current);
    }
    static void watch(Api api,String identity,boolean local,int mediaId,int airingId)throws Exception {
        String context=context(api,identity,local,mediaId,airingId);
        Object content=api.call(mediaId>0?"GetMediaFileForID":"GetAiringForID",Integer.valueOf(mediaId>0?mediaId:airingId));
        if(content==null)throw new IllegalArgumentException("Content no longer available; refresh the list");
        if(airingId>0){
            Object start=api.call("GetAiringStartTime",content),end=api.call("GetAiringEndTime",content);
            long now=System.currentTimeMillis();
            if(!(start instanceof Number)||!(end instanceof Number)||now<((Number)start).longValue()||now>=((Number)end).longValue())
                throw new IllegalArgumentException("This program is not currently airing");
        }
        Object accepted=api.ui(context,"Watch",content);
        // A public asynchronous receipt acknowledges dispatch, not pictures.
        if(accepted==null||Boolean.FALSE.equals(accepted)||accepted instanceof String)
            throw new IllegalStateException("SageTV did not accept playback"+(accepted instanceof String?": "+accepted:""));
    }
    private static String context(Api api,String identity,boolean local,int mediaId,int airingId)throws Exception {
        if((mediaId>0)==(airingId>0)||mediaId<0||airingId<0)throw new IllegalArgumentException("Choose exactly one media or airing ID");
        return context(api,identity,local);
    }
    private static String context(Api api,String identity,boolean local)throws Exception {
        String compact=identity==null?"":identity.replace(":","");
        if(!local||!compact.matches("[0-9a-fA-F]{12}"))throw new IllegalArgumentException("Content Play requires this server's local MiniClient");
        Object contexts=api.call("GetUIContextNames");
        if(!(contexts instanceof Object[])||((Object[])contexts).length>256)throw new IllegalStateException("MiniClient context unavailable");
        String context=null;
        for(Object candidate:(Object[])contexts)if(candidate instanceof String&&((String)candidate).replace(":","").equalsIgnoreCase(compact)){
            if(context!=null)throw new IllegalStateException("Ambiguous MiniClient context");context=(String)candidate;
        }
        if(context==null)throw new IllegalStateException("MiniClient context unavailable; reconnect first");
        return context;
    }
    static boolean selectDvdMenu(Api api,String identity,boolean local,boolean nativeDvd)throws Exception {
        return selectDvdMenu(api,identity,local,nativeDvd,()->true);
    }
    static boolean selectDvdMenu(Api api,String identity,boolean local,boolean nativeDvd,Current current)throws Exception {
        if(!local||!nativeDvd)return false;
        String context;
        try {
            context=context(api,identity,local);
            if(!Boolean.TRUE.equals(api.ui(context,"IsMediaPlayerFullyLoaded"))||
               !Boolean.FALSE.equals(api.ui(context,"IsOptionsMenuOpen"))||
               !Boolean.TRUE.equals(api.ui(context,"IsCurrentMediaFileDVD"))||
               !Boolean.TRUE.equals(api.ui(context,"IsShowingDVDMenu")))return false;
            String stv=String.valueOf(api.ui(context,"GetCurrentSTVFile")).replace('\\','/');
            String file=stv.substring(stv.lastIndexOf('/')+1).toLowerCase(java.util.Locale.ROOT);
            Object menu=api.ui(context,"GetCurrentMenuWidget");
            String name=String.valueOf(api.ui(context,"GetWidgetName",menu)),symbol=String.valueOf(api.ui(context,"GetWidgetSymbol",menu));
            boolean mc=file.startsWith("sagemc")&&(file.endsWith(".xml")||file.endsWith(".stv"));
            boolean known=(mc&&"PRQST-1202549".equals(symbol)&&(name.equals("MediaPlayer OSD")||name.equals("MC MediaPlayer OSD")))||
                ((file.equals("sagetv7.xml")||file.equals("sagetv7.stv"))&&"BASE-44375".equals(symbol)&&name.equals("MediaPlayer OSD"));
            if(!known)return false;
        }catch(Exception unavailable){return false;}
        // The public API queues this one DVD intent and returns void. Once
        // called, an exception/unknown receipt must NOT fall through/replay a
        // generic Select. No private VM, guessed button or navigation coords.
        if(!current.current())return false;
        api.ui(context,"DirectPlaybackControl",Integer.valueOf(208),Long.valueOf(0),Long.valueOf(0));
        return true;
    }
    /** Reconfigure only via one public native title seek. Never reconstruct
     * DVD input as an ordinary file, guess a browser/title offset, or Play a
     * paused disc. Prepare runs after read-only validation and immediately
     * before the ordered intent; an unknown Seek receipt must not be replayed. */
    static boolean reconfigureDvd(Api api,String identity,boolean local,Current prepare)throws Exception {
        String context=context(api,identity,local);
        if(!Boolean.TRUE.equals(api.ui(context,"IsMediaPlayerFullyLoaded"))||
           !Boolean.FALSE.equals(api.ui(context,"IsOptionsMenuOpen"))||
           !Boolean.TRUE.equals(api.ui(context,"IsCurrentMediaFileDVD"))||
           !Boolean.FALSE.equals(api.ui(context,"IsShowingDVDMenu")))return false;
        Object media=api.ui(context,"GetCurrentMediaFile");
        if(media==null)return false;
        Object id=api.call("GetMediaFileID",media),title=api.ui(context,"GetDVDCurrentTitle"),
            position=api.ui(context,"GetRawMediaTime"),duration=api.ui(context,"GetMediaDuration"),
            rate=api.ui(context,"GetPlaybackRate"),playing=api.ui(context,"IsPlaying");
        if(!(id instanceof Number)||((Number)id).longValue()<=0||
           !(title instanceof Number)||((Number)title).intValue()<1||
           !milliseconds(position)||!milliseconds(duration)||
           ((Number)duration).longValue()<=((Number)position).longValue()||
           !(rate instanceof Number)||((Number)rate).doubleValue()!=1.0||!(playing instanceof Boolean))return false;
        Object fresh=api.ui(context,"GetCurrentMediaFile");
        if(fresh==null||!id.equals(api.call("GetMediaFileID",fresh))||
           !title.equals(api.ui(context,"GetDVDCurrentTitle"))||
           !Boolean.TRUE.equals(api.ui(context,"IsCurrentMediaFileDVD"))||
           !Boolean.FALSE.equals(api.ui(context,"IsShowingDVDMenu"))||
           !Boolean.FALSE.equals(api.ui(context,"IsOptionsMenuOpen"))||!prepare.current())return false;
        // No media/bridge monitor may be held across this public Core call:
        // the stock reader must be free to reply to FLUSH and fresh Push/NAV.
        api.ui(context,"Seek",Long.valueOf(((Number)position).longValue()));
        return true;
    }
    private static boolean milliseconds(Object value){
        if(!(value instanceof Number))return false;
        double d=((Number)value).doubleValue();
        return Double.isFinite(d)&&d>=0&&d==((Number)value).longValue();
    }
    static boolean ready(Api api,String identity,boolean local,int mediaId,int airingId)throws Exception {
        String context=context(api,identity,local,mediaId,airingId);
        if(!Boolean.TRUE.equals(api.ui(context,"IsMediaPlayerFullyLoaded")))return false;
        if(!Boolean.FALSE.equals(api.ui(context,"IsOptionsMenuOpen")))return false;
        Object current=api.ui(context,"GetCurrentMediaFile");
        if(current==null)return false;
        Object id=mediaId>0?api.call("GetMediaFileID",current):api.call("GetAiringID",api.call("GetMediaFileAiring",current));
        return id instanceof Number&&((Number)id).longValue()==(mediaId>0?mediaId:airingId);
    }
    static boolean show(Api api,String identity,boolean local,int mediaId,int airingId,boolean preview)throws Exception {
        if(!preview||!ready(api,identity,local,mediaId,airingId))return false;
        // Exactly one ordinary TV command after fresh exact-source/modal proof.
        // Never close dialogs, reset position or inspect private Core classes.
        api.ui(context(api,identity,local,mediaId,airingId),"SageCommand","TV");return true;
    }
    static String layout(Api api,String identity,boolean local,int mediaId,int airingId,String nativeLayout)throws Exception {
        if(!ready(api,identity,local,mediaId,airingId))return "unknown";
        String context=context(api,identity,local,mediaId,airingId);
        try {
            // Some stock DVD sessions emit neither media SETVIDEORECT nor
            // GFX SETVIDEOPROP. A canvas colour-key cannot tell this server-side
            // intent guard which STV menu owns input. Use public, read-only
            // widget identity, never pixels, private Core or a guessed toggle.
            String stv=String.valueOf(api.ui(context,"GetCurrentSTVFile")).replace('\\','/');
            String file=stv.substring(stv.lastIndexOf('/')+1).toLowerCase(java.util.Locale.ROOT);
            boolean mc=file.startsWith("sagemc")&&(file.endsWith(".xml")||file.endsWith(".stv"));
            boolean stock=file.equals("sagetv7.xml")||file.equals("sagetv7.stv");
            if(mc||stock){
                Object menu=api.ui(context,"GetCurrentMenuWidget");
                String name=String.valueOf(api.ui(context,"GetWidgetName",menu));
                String symbol=String.valueOf(api.ui(context,"GetWidgetSymbol",menu));
                if((mc&&"PRQST-1202549".equals(symbol)&&(name.equals("MediaPlayer OSD")||name.equals("MC MediaPlayer OSD")))||
                   (stock&&"BASE-44375".equals(symbol)&&name.equals("MediaPlayer OSD")))return "fullscreen";
                if((mc&&"PRQST-1205984".equals(symbol)&&name.equals("Main Menu"))||
                   (mc&&"PRQST-1212481".equals(symbol)&&name.equals("Dynamic Menu by nielm"))||
                   (stock&&"BASE-44343".equals(symbol)&&name.equals("Main Menu")))return "preview";
            }
        }catch(Exception unavailable){
            // Optional public STV inspection unavailable: preserve the old
            // protocol-only path, with unknown remaining unknown.
        }
        return "fullscreen".equals(nativeLayout)||"preview".equals(nativeLayout)?nativeLayout:"unknown";
    }
    static String viewEvidence(String identity,boolean local,int mediaId,int airingId)throws Exception {
        Api api=runtime();if(!ready(api,identity,local,mediaId,airingId))return "{}";
        String context=context(api,identity,local,mediaId,airingId);
        try {
            Object menu=api.ui(context,"GetCurrentMenuWidget");
            String name=String.valueOf(api.ui(context,"GetWidgetName",menu));
            String symbol=String.valueOf(api.ui(context,"GetWidgetSymbol",menu));
            // Fixed public menu metadata only; no widget contents, arbitrary
            // expressions, user text, media paths or raw API errors.
            if(!name.matches("[A-Za-z0-9 _-]{1,96}")||!symbol.matches("[A-Za-z0-9_-]{1,96}"))return "{\"available\":false}";
            return "{\"available\":true,\"menuName\":\""+name+"\",\"menuSymbol\":\""+symbol+"\"}";
        }catch(Exception unavailable){return "{\"available\":false}";}
    }
    static void info(Api api,String identity,boolean local,int mediaId,int airingId)throws Exception {
        String context=context(api,identity,local,mediaId,airingId);
        if(!Boolean.FALSE.equals(api.ui(context,"IsOptionsMenuOpen")))throw new IllegalStateException("Close the STV dialog first");
        Object content=api.call(mediaId>0?"GetMediaFileForID":"GetAiringForID",Integer.valueOf(mediaId>0?mediaId:airingId));
        if(content==null)throw new IllegalArgumentException("Content no longer available; refresh the list");
        String stv=String.valueOf(api.ui(context,"GetCurrentSTVFile")).replace('\\','/');
        String file=stv.substring(stv.lastIndexOf('/')+1).toLowerCase(java.util.Locale.ROOT);
        boolean mc=file.startsWith("sagemc")&&(file.endsWith(".xml")||file.endsWith(".stv"));
        boolean stock=file.equals("sagetv7.xml")||file.equals("sagetv7.stv");
        if(!mc&&!stock)throw new IllegalStateException("This STV has no qualified content Info menu; use Controls");
        boolean tv=mediaId>0&&Boolean.TRUE.equals(api.call("IsTVFile",content));
        String name=mc?"Program Info":airingId>0?"Detailed Info - Airing":tv?"Detailed Info - Recording":"Detailed Info - Video File";
        String symbol=mc?"PRQST-1202023":airingId>0?"BASE-57768":tv?"BASE-57832":"BASE-57922";
        Object all=api.ui(context,"GetWidgetsByType","Menu"),menu=null;
        if(!(all instanceof Object[])||((Object[])all).length>4096)throw new IllegalStateException("STV menus unavailable");
        for(Object widget:(Object[])all)if(name.equals(api.ui(context,"GetWidgetName",widget))&&symbol.equals(api.ui(context,"GetWidgetSymbol",widget))){
            if(menu!=null)throw new IllegalStateException("Ambiguous STV information menu");menu=widget;
        }
        if(menu==null)throw new IllegalStateException("STV information menu unavailable");
        // Use the public STV convention; never create/edit a Widget or run an
        // arbitrary expression. Launch once, and do not replay unknown results.
        if(mc){
            api.ui(context,"AddStaticContext","Airing",content);
            api.ui(context,"AddStaticContext","AiringForBackground",content);
            api.ui(context,"AddStaticContext","AiringList",new Object[]{content});
            api.ui(context,"AddStaticContext","AiringIndex",Integer.valueOf(0));
        }else api.ui(context,"AddStaticContext",airingId>0?"Airing":"MediaFile",content);
        api.ui(context,"LaunchMenuWidget",menu);
        Object current=api.ui(context,"GetCurrentMenuWidget");
        if(current==null||!symbol.equals(api.ui(context,"GetWidgetSymbol",current)))throw new IllegalStateException("Info menu was not confirmed; it was not retried");
    }
    private static Api runtime()throws Exception {
        final Class<?> sage=Class.forName("sage.SageTV");
        return new Api(){
            public Object call(String method,Object... args)throws Exception {
                return sage.getMethod("api",String.class,Object[].class).invoke(null,method,args);
            }
            public Object ui(String context,String method,Object... args)throws Exception {
                return sage.getMethod("apiUI",String.class,String.class,Object[].class).invoke(null,context,method,args);
            }
        };
    }
    static void watch(String identity,boolean local,int mediaId,int airingId)throws Exception {
        watch(runtime(),identity,local,mediaId,airingId);
    }
    static void info(String identity,boolean local,int mediaId,int airingId)throws Exception {
        info(runtime(),identity,local,mediaId,airingId);
    }
    static boolean ready(String identity,boolean local,int mediaId,int airingId)throws Exception {
        return ready(runtime(),identity,local,mediaId,airingId);
    }
    static boolean show(String identity,boolean local,int mediaId,int airingId,boolean preview)throws Exception {
        return show(runtime(),identity,local,mediaId,airingId,preview);
    }
    static String layout(String identity,boolean local,int mediaId,int airingId,String nativeLayout)throws Exception {
        return layout(runtime(),identity,local,mediaId,airingId,nativeLayout);
    }
    static boolean selectDvdMenu(String identity,boolean local,boolean nativeDvd,Current current)throws Exception {
        return local&&nativeDvd&&selectDvdMenu(runtime(),identity,local,nativeDvd,current);
    }
    static boolean reconfigureDvd(String identity,boolean local,Current prepare)throws Exception {
        return reconfigureDvd(runtime(),identity,local,prepare);
    }
    private StockClientPlayback(){}
}
