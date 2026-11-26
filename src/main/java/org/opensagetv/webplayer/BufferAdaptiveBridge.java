package org.opensagetv.webplayer;

/** Optional shared MIM policy, not a second adaptation algorithm. No provider
 * dependency is bundled in this WAR; absence leaves ordinary Fixed playback. */
final class BufferAdaptiveBridge {
    private final Object delegate;
    private static Class<?> provider()throws Exception{
        Class<?> p=Class.forName("org.opensagetv.vibe.ffmpeg.BufferAdaptiveController");
        if(((Number)p.getMethod("protocolVersion").invoke(null)).intValue()!=1)throw new IllegalStateException("unsupported_buffer_protocol");
        return p;
    }
    static boolean available(){try{provider();return true;}catch(Exception|LinkageError missing){return false;}}
    BufferAdaptiveBridge(int min,int max,boolean inPlace)throws Exception{delegate=provider().getConstructor(int.class,int.class,boolean.class).newInstance(min,max,inPlace);}
    void epoch()throws Exception{delegate.getClass().getMethod("epoch").invoke(delegate);}
    String report(long id,long reserve,boolean buffering,boolean eligible,boolean healthy,int current)throws Exception{
        int target=((Number)delegate.getClass().getMethod("observe",long.class,long.class,long.class,boolean.class,boolean.class,boolean.class,int.class)
            .invoke(delegate,System.nanoTime()/1000000L,id,reserve,buffering,eligible,healthy,current)).intValue();
        return (String)delegate.getClass().getMethod("json",long.class,int.class).invoke(delegate,id,target);
    }
}
