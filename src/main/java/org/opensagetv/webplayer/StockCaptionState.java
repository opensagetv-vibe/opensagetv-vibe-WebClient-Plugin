package org.opensagetv.webplayer;

import java.lang.reflect.Method;

/** Read only the exact local MiniClient's public STV selection. Stock Core
 * does not necessarily send VIDEO_CC_STATE. No private renderer/reflection,
 * fallback-to-another-UI, external server query or normal MCP dependency. */
final class StockCaptionState {
    interface Api { Object contexts() throws Exception; Object state(String context) throws Exception; }
    private static Object exactState(Api api,String clientId,boolean local)throws Exception {
        // MiniClientSession stores its canonical identity WITH colons. Public
        // UI context names can use either spelling; validate the same compact
        // bytes on both sides instead of rejecting every real session.
        String compactId=clientId==null?"":clientId.replace(":","");
        if(!local||!compactId.matches("[0-9a-fA-F]{12}"))return null;
            Object contexts=api.contexts();if(!(contexts instanceof Object[])||((Object[])contexts).length>256)return null;
            String exact=null;
            for(Object candidate:(Object[])contexts) {
                if(!(candidate instanceof String))continue;
                String name=(String)candidate;
                if(!name.replace(":","").equalsIgnoreCase(compactId))continue;
                if(exact!=null)return null;exact=name;
            }
            if(exact==null)return null;
            return api.state(exact);
    }
    static Integer read(Api api,String clientId,boolean local) {
        try {
            Object value=exactState(api,clientId,local);
            if(value instanceof Number){double d=((Number)value).doubleValue();int n=((Number)value).intValue();return d==n&&n>=0&&n<=4?Integer.valueOf(n):null;}
            if(value instanceof String){String s=((String)value).trim();if("Off".equalsIgnoreCase(s)||"Captions Off".equalsIgnoreCase(s))return Integer.valueOf(0);if(s.matches("(?i)CC[1-4]"))return Integer.valueOf(s.substring(2));}
        }catch(Exception unavailable){return null;}catch(LinkageError unavailable){return null;}
        return null;
    }
    static Boolean dvdMenu(Api api,String clientId,boolean local) {
        try {Object value=exactState(api,clientId,local);return value instanceof Boolean?(Boolean)value:null;}
        catch(Exception unavailable){return null;}catch(LinkageError unavailable){return null;}
    }
    static Boolean dvdMenu(final String clientId,boolean local) {
        return dvdMenu(new Api(){
            public Object contexts()throws Exception {
                return Class.forName("sage.SageTV").getMethod("api",String.class,Object[].class).invoke(null,"GetUIContextNames",new Object[0]);
            }
            public Object state(String context)throws Exception {
                return Class.forName("sage.SageTV").getMethod("apiUI",String.class,String.class,Object[].class).invoke(null,context,"IsShowingDVDMenu",new Object[0]);
            }
        },clientId,local);
    }
    static Integer read(final String clientId,boolean local) {
        return read(new Api(){
            public Object contexts()throws Exception {
                Method method=Class.forName("sage.SageTV").getMethod("api",String.class,Object[].class);
                return method.invoke(null,"GetUIContextNames",new Object[0]);
            }
            public Object state(String context)throws Exception {
                Method method=Class.forName("sage.SageTV").getMethod("apiUI",String.class,String.class,Object[].class);
                return method.invoke(null,context,"GetMediaPlayerClosedCaptionState",new Object[0]);
            }
        },clientId,local);
    }
    static boolean localServer(String host){
        if("localhost".equalsIgnoreCase(host)||"127.0.0.1".equals(host)||"::1".equals(host))return true;
        try{return java.net.NetworkInterface.getByInetAddress(java.net.InetAddress.getByName(host))!=null;}
        catch(Exception unavailable){return false;}
    }
    private StockCaptionState(){}
}
