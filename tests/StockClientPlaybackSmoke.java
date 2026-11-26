package org.opensagetv.webplayer;
public final class StockClientPlaybackSmoke {
    static final class Api implements StockClientPlayback.Api {
        Object[] contexts={"AA:BB:CC:DD:EE:FF","112233445566"};int watches,shows,currentId=5;boolean live=true,exists=true,loaded=true,inspect=true;Object modal=Boolean.FALSE,accepted=Boolean.TRUE;
        String stv="SageMC_169.xml",menuName="Main Menu",menuSymbol="PRQST-1205984";boolean dvd=true,dvdMenu=true,failSelect=false;int selects;
        public Object call(String method,Object... args){
            if("GetUIContextNames".equals(method))return contexts;
            if("GetMediaFileForID".equals(method)||"GetAiringForID".equals(method))return exists?"content":null;
            if("GetAiringStartTime".equals(method))return System.currentTimeMillis()+(live?-60000:60000);
            if("GetAiringEndTime".equals(method))return System.currentTimeMillis()+120000;
            if("GetMediaFileID".equals(method))return currentId;
            if("GetMediaFileAiring".equals(method))return "airing";
            if("GetAiringID".equals(method))return 7;
            throw new AssertionError("unexpected API "+method);
        }
        public Object ui(String context,String method,Object... args){
            if(!context.equals("AA:BB:CC:DD:EE:FF"))throw new AssertionError("foreign context");
            if(method.equals("IsMediaPlayerFullyLoaded"))return loaded;
            if(method.equals("IsOptionsMenuOpen"))return modal;
            if(method.equals("GetCurrentMediaFile"))return "current";
            if(method.equals("IsCurrentMediaFileDVD"))return dvd;
            if(method.equals("IsShowingDVDMenu"))return dvdMenu;
            if(method.equals("DirectPlaybackControl")){
                if(!args[0].equals(208)||!args[1].equals(0L)||!args[2].equals(0L))throw new AssertionError("Unexpected DVD operation");
                selects++;if(failSelect)throw new IllegalStateException("Unknown submission");return null;
            }
            if(method.equals("GetCurrentSTVFile")){if(!inspect)throw new IllegalStateException("Optional API absent");return stv;}
            if(method.equals("GetCurrentMenuWidget"))return "menu";
            if(method.equals("GetWidgetName"))return menuName;
            if(method.equals("GetWidgetSymbol"))return menuSymbol;
            if(method.equals("SageCommand")&&args[0].equals("TV")){shows++;return null;}
            if(!method.equals("Watch")||!args[0].equals("content"))throw new AssertionError("unexpected mutation");
            watches++;return accepted;
        }
    }
    static void refused(Api api,String identity,boolean local,int media,int airing)throws Exception {
        int before=api.watches;try{StockClientPlayback.watch(api,identity,local,media,airing);throw new AssertionError("not refused");}
        catch(IllegalArgumentException|IllegalStateException expected){}if(before!=api.watches)throw new AssertionError("unexpected Watch");
    }
    public static void main(String[] args)throws Exception {
        Api api=new Api();StockClientPlayback.watch(api,"aabbccddeeff",true,5,0);StockClientPlayback.watch(api,"AA:BB:CC:DD:EE:FF",true,0,7);
        api.accepted=new Object();StockClientPlayback.watch(api,"aabbccddeeff",true,5,0);api.accepted=Boolean.TRUE;
        refused(api,"aabbccddeeff",false,5,0);refused(api,"11223344556600",true,5,0);refused(api,"000000000000",true,5,0);
        refused(api,"aabbccddeeff",true,5,7);refused(api,"aabbccddeeff",true,0,0);refused(api,"aabbccddeeff",true,-1,7);
        api.contexts=new Object[]{"AA:BB:CC:DD:EE:FF","aabbccddeeff"};refused(api,"aabbccddeeff",true,5,0);
        api.contexts=new Object[]{"AA:BB:CC:DD:EE:FF"};api.exists=false;refused(api,"aabbccddeeff",true,5,0);api.exists=true;
        api.live=false;refused(api,"aabbccddeeff",true,0,7);api.live=true;api.accepted=Boolean.FALSE;
        try{StockClientPlayback.watch(api,"aabbccddeeff",true,5,0);throw new AssertionError();}catch(IllegalStateException expected){}
        if(api.watches!=4)throw new AssertionError("replayed Watch");
        if(!StockClientPlayback.ready(api,"aabbccddeeff",true,5,0))throw new AssertionError("exact media not ready");
        if(!StockClientPlayback.ready(api,"aabbccddeeff",true,0,7))throw new AssertionError("exact airing not ready");
        if(StockClientPlayback.show(api,"aabbccddeeff",true,5,0,false)||api.shows!=0)throw new AssertionError("fullscreen/unknown layout toggled");
        api.loaded=false;if(StockClientPlayback.show(api,"aabbccddeeff",true,5,0,true))throw new AssertionError("unloaded source toggled");api.loaded=true;
        api.currentId=9;if(StockClientPlayback.show(api,"aabbccddeeff",true,5,0,true))throw new AssertionError("different source toggled");api.currentId=5;
        for(Object state:new Object[]{Boolean.TRUE,null,"false"}){api.modal=state;if(StockClientPlayback.show(api,"aabbccddeeff",true,5,0,true))throw new AssertionError("modal or unknown toggled");}
        api.modal=Boolean.FALSE;if(!StockClientPlayback.show(api,"aabbccddeeff",true,5,0,true)||api.shows!=1||api.watches!=4)throw new AssertionError("TV transition did not remain separate/once");
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("preview"))throw new AssertionError("Stock DVD main menu without rectangles lost preview intent");
        api.menuName="Dynamic Menu by nielm";api.menuSymbol="PRQST-1212481";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("preview"))throw new AssertionError("Actual SageMC dynamic menu missing");
        api.menuSymbol="UNKNOWN-1212481";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("unknown"))throw new AssertionError("Unqualified dynamic widget accepted");
        api.menuName="MediaPlayer OSD";api.menuSymbol="PRQST-1202549";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"preview").equals("fullscreen"))throw new AssertionError("Stale protocol preview toggles an already-fullscreen DVD");
        api.menuName="MC MediaPlayer OSD";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("fullscreen"))throw new AssertionError("Legacy MC OSD name missing");
        api.stv="SageTV7.xml";api.menuName="Main Menu";api.menuSymbol="BASE-44343";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("preview"))throw new AssertionError("Stock main menu missing");
        api.menuName="MediaPlayer OSD";api.menuSymbol="BASE-44375";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("fullscreen"))throw new AssertionError("Stock OSD missing");
        api.modal=Boolean.TRUE;
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"fullscreen").equals("unknown"))throw new AssertionError("Modal bypassed");api.modal=Boolean.FALSE;
        api.currentId=9;
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"fullscreen").equals("unknown"))throw new AssertionError("Different source bypassed");api.currentId=5;
        api.menuSymbol="unknown";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("unknown"))throw new AssertionError("Unknown widget inferred");
        api.menuSymbol="BASE-44375";api.stv="Custom.xml";
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"unknown").equals("unknown"))throw new AssertionError("Unknown STV inferred");
        api.inspect=false;
        if(!StockClientPlayback.layout(api,"aabbccddeeff",true,5,0,"fullscreen").equals("fullscreen"))throw new AssertionError("Protocol-only fallback regressed");
        if(api.shows!=1||api.watches!=4)throw new AssertionError("Read-only layout mutated playback");
        System.out.println("PASS 13 qualified public STV layout cases; no Watch/TV during reads");
        api.inspect=true;api.stv="SageMC_Vibe.xml";api.menuName="MediaPlayer OSD";api.menuSymbol="PRQST-1202549";
        if(!StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true)||api.selects!=1)throw new AssertionError("Qualified DVD Select absent");
        if(StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",false,true)||StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,false))throw new AssertionError("Foreign/non-DVD input intercepted");
        api.modal=true;if(StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true))throw new AssertionError("Dialog input intercepted");api.modal=false;
        api.dvdMenu=false;if(StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true))throw new AssertionError("Feature Select intercepted");api.dvdMenu=true;
        api.dvd=false;if(StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true))throw new AssertionError("Ordinary media intercepted");api.dvd=true;
        api.menuSymbol="PRQST-1212481";api.menuName="Dynamic Menu by nielm";
        if(StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true))throw new AssertionError("Main menu input intercepted");
        api.menuName="MediaPlayer OSD";api.menuSymbol="PRQST-1202549";api.inspect=false;
        if(StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true))throw new AssertionError("Missing API intercepted input");api.inspect=true;
        if(StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true,()->false))throw new AssertionError("Retired owner dispatched control");
        api.failSelect=true;try{StockClientPlayback.selectDvdMenu(api,"aabbccddeeff",true,true);throw new AssertionError("Unknown result suppressed");}catch(IllegalStateException expected){}
        if(api.selects!=2||api.shows!=1||api.watches!=4)throw new AssertionError("DVD Select retried or unrelated mutation");
        System.out.println("PASS 9 qualified DVD Select groups: no modal/feature/main/remote/retired interception or unknown-result replay");
        System.out.println("PASS exact stock Watch: media/live, ambiguity/foreign/nonlocal/future/deleted/bad-ID guards, no Record/replay");
        System.out.println("PASS exact-source preview TV transition; loaded/modal/unknown/different-source/fullscreen guards");
    }
}
