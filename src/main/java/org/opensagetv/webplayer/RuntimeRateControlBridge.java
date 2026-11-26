package org.opensagetv.webplayer;

/** Optional shared FFmpeg-plugin protocol; never accepts a PID, shell command,
 * arbitrary path or another session's Process. Old providers fail safely. */
final class RuntimeRateControlBridge {
    private final Object delegate;
    private RuntimeRateControlBridge(Object value){delegate=value;}
    private static Class<?> provider()throws Exception{
        Class<?> p=Class.forName("org.opensagetv.vibe.ffmpeg.RuntimeBitrateControl");
        if(((Number)p.getMethod("protocolVersion").invoke(null)).intValue()!=1)throw new IllegalStateException("unsupported_rate_protocol");return p;
    }
    static boolean enabled(){try{return Boolean.TRUE.equals(provider().getMethod("enabled").invoke(null));}catch(Exception|LinkageError e){return false;}}
    static String test(boolean start)throws Exception{
        Class<?> p=Class.forName("org.opensagetv.vibe.ffmpeg.RuntimeBitrateSelfTest");
        try{return (String)p.getMethod(start?"start":"status").invoke(null);}
        catch(java.lang.reflect.InvocationTargetException e){throw new IllegalStateException("Bitrate test refused: recording/transcode active, unknown activity, or unsupported runtime");}
    }
    static RuntimeRateControlBridge create(Process owned,int initial,int ceiling){
        try{return new RuntimeRateControlBridge(provider().getConstructor(Process.class,int.class,int.class).newInstance(owned,initial,ceiling));}
        catch(Exception|LinkageError e){return null;}
    }
    void observe(String line){try{delegate.getClass().getMethod("observe",String.class).invoke(delegate,line);}catch(Exception|LinkageError ignored){}}
    int currentKbps(){try{return ((Number)delegate.getClass().getMethod("currentKbps").invoke(delegate)).intValue();}catch(Exception|LinkageError missing){return 0;}}
    boolean available(){try{return Boolean.TRUE.equals(delegate.getClass().getMethod("available").invoke(delegate));}catch(Exception|LinkageError missing){return false;}}
    String snapshot(long progress){try{return (String)delegate.getClass().getMethod("snapshot",long.class,long.class).invoke(delegate,progress,System.nanoTime()/1000000L);}catch(Exception|LinkageError e){return "{\"revision\":0,\"available\":false}";}}
    String request(long id,int kbps)throws Exception{
        try{return (String)delegate.getClass().getMethod("request",long.class,int.class,long.class).invoke(delegate,id,kbps,System.nanoTime()/1000000L);}
        catch(java.lang.reflect.InvocationTargetException e){Throwable cause=e.getCause();if(cause instanceof Exception)throw(Exception)cause;throw e;}
    }
}
