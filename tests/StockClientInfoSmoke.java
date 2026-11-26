package org.opensagetv.webplayer;
import java.util.*;
public final class StockClientInfoSmoke {
    static final class Api implements StockClientPlayback.Api {
        String stv="SageMC_169.xml",symbol="PRQST-1202023",name="Program Info";boolean modal=false,tv=false,exists=true,duplicate=false,throwLaunch=false,known=true;int launches;Map<String,Object> context=new HashMap<String,Object>();
        public Object call(String n,Object... a){
            if(n.equals("GetUIContextNames"))return new String[]{"aabbccddeeff"};
            if(n.equals("GetMediaFileForID")||n.equals("GetAiringForID"))return exists?"selected":null;
            if(n.equals("IsTVFile"))return tv;
            throw new AssertionError("Unexpected global "+n);
        }
        public Object ui(String id,String n,Object... a){
            if(!id.equals("aabbccddeeff"))throw new AssertionError("Foreign context");
            if(n.equals("IsOptionsMenuOpen"))return modal;
            if(n.equals("GetCurrentSTVFile"))return stv;
            if(n.equals("GetWidgetsByType"))return known?(duplicate?new Object[]{"menu","duplicate"}:new Object[]{"menu"}):new Object[0];
            if(n.equals("GetWidgetName"))return name;
            if(n.equals("GetWidgetSymbol"))return symbol;
            if(n.equals("AddStaticContext")){context.put((String)a[0],a[1]);return null;}
            if(n.equals("LaunchMenuWidget")){launches++;if(throwLaunch)throw new IllegalStateException("Unknown launch");return null;}
            if(n.equals("GetCurrentMenuWidget"))return "menu";
            throw new AssertionError("Info must not Watch/Record/close dialogs/run expressions: "+n);
        }
    }
    static void refuse(Api a,String id,boolean local,int media,int airing)throws Exception {
        int before=a.launches;try{StockClientPlayback.info(a,id,local,media,airing);throw new AssertionError("Not refused");}catch(IllegalStateException|IllegalArgumentException expected){}
        if(a.launches!=before)throw new AssertionError("Unexpected launch");
    }
    public static void main(String[] args)throws Exception {
        Api a=new Api();StockClientPlayback.info(a,"AABBCCDDEEFF",true,3,0);
        if(a.launches!=1||!a.context.get("Airing").equals("selected"))throw new AssertionError();
        refuse(a,"aabbccddeeff",false,3,0);refuse(a,"000000000000",true,3,0);refuse(a,"aabbccddeeff",true,3,5);
        a.modal=true;refuse(a,"aabbccddeeff",true,3,0);a.modal=false;a.exists=false;refuse(a,"aabbccddeeff",true,3,0);a.exists=true;
        a.stv="Other.xml";refuse(a,"aabbccddeeff",true,3,0);a.stv="SageMC_169.xml";a.duplicate=true;refuse(a,"aabbccddeeff",true,3,0);a.duplicate=false;a.known=false;refuse(a,"aabbccddeeff",true,3,0);a.known=true;
        a.stv="/SageTV7/SageTV7.xml";a.context.clear();a.name="Detailed Info - Video File";a.symbol="BASE-57922";StockClientPlayback.info(a,"aabbccddeeff",true,3,0);
        if(!a.context.containsKey("MediaFile"))throw new AssertionError();
        a.tv=true;a.name="Detailed Info - Recording";a.symbol="BASE-57832";StockClientPlayback.info(a,"aabbccddeeff",true,3,0);
        a.context.clear();a.name="Detailed Info - Airing";a.symbol="BASE-57768";StockClientPlayback.info(a,"aabbccddeeff",true,0,5);if(!a.context.containsKey("Airing"))throw new AssertionError();
        int before=a.launches;a.throwLaunch=true;try{StockClientPlayback.info(a,"aabbccddeeff",true,0,5);throw new AssertionError();}catch(IllegalStateException expected){}if(a.launches!=before+1)throw new AssertionError("Replayed launch");
        System.out.println("PASS Info SageMC/stock video/recording/airing; exact-context/modal/content/menu/ambiguity/no Watch/no retry guards");
    }
}
