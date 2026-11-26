package org.opensagetv.webplayer;
public final class StockCaptionStateSmoke {
    static final class Api implements StockCaptionState.Api {
        Object values=new String[]{"AA:BB:CC:DD:EE:FF"};Object cc="CC2";int reads;
        public Object contexts(){return values;}
        public Object state(String context){if(!context.equals("AA:BB:CC:DD:EE:FF"))throw new AssertionError("foreign UI");reads++;return cc;}
    }
    static void check(boolean pass){if(!pass)throw new AssertionError();}
    public static void main(String[] args){
        Api api=new Api();check(StockCaptionState.read(api,"aabbccddeeff",true)==2);
        check(StockCaptionState.read(api,"AA:BB:CC:DD:EE:FF",true)==2);
        api.cc="Captions Off";check(StockCaptionState.read(api,"AA:BB:CC:DD:EE:FF",true)==0);
        api.cc="Off";check(StockCaptionState.read(api,"aabbccddeeff",true)==0);
        api.cc=Double.valueOf(1.5);check(StockCaptionState.read(api,"aabbccddeeff",true)==null);
        api.cc=Double.valueOf(Double.NaN);check(StockCaptionState.read(api,"aabbccddeeff",true)==null);
        api.cc=Boolean.FALSE;check(Boolean.FALSE.equals(StockCaptionState.dvdMenu(api,"aabbccddeeff",true)));
        check(Boolean.FALSE.equals(StockCaptionState.dvdMenu(api,"AA:BB:CC:DD:EE:FF",true)));
        api.cc=Boolean.TRUE;check(Boolean.TRUE.equals(StockCaptionState.dvdMenu(api,"aabbccddeeff",true)));
        api.cc="false";check(StockCaptionState.dvdMenu(api,"aabbccddeeff",true)==null);
        check(StockCaptionState.dvdMenu(api,"aabbccddeeff",false)==null);
        check(StockCaptionState.read(api,"112233445566",true)==null);
        int before=api.reads;check(StockCaptionState.read(api,"aabbccddeeff",false)==null&&api.reads==before);
        api.values=new String[]{"AA:BB:CC:DD:EE:FF","aabbccddeeff"};check(StockCaptionState.read(api,"aabbccddeeff",true)==null);
        check(StockCaptionState.dvdMenu(api,"aabbccddeeff",true)==null);
        api.values=null;check(StockCaptionState.read(api,"aabbccddeeff",true)==null);
        check(StockCaptionState.localServer("127.0.0.1"));
        System.out.println("PASS stock public caption state: exact local UI, ambiguity/off/foreign/unavailable guards");
    }
}
