package org.opensagetv.webplayer;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.*;
import java.util.concurrent.TimeUnit;

/** Generated-source FFmpeg gate, not actual-phone presentation evidence. */
public final class DvdReadAheadRuntimeSmoke {
    static void require(boolean value,String why){if(!value)throw new AssertionError(why);}
    static void put(byte[] b,int p,int v){b[p]=(byte)(v>>>24);b[p+1]=(byte)(v>>>16);b[p+2]=(byte)(v>>>8);b[p+3]=(byte)v;}
    static byte[] push(byte[] data,int offset,int size,int flags){byte[] b=new byte[size+8];put(b,0,size);put(b,4,flags);System.arraycopy(data,offset,b,8,size);return b;}
    static void remove(File f){if(f.isDirectory()){File[] files=f.listFiles();if(files!=null)for(File c:files)remove(c);}f.delete();}
    public static void main(String[] args)throws Exception {
        require(!HlsSessionManager.dvdReadAheadLimitReached(14,0),"reserve can fill to existing12s plus margin");
        require(HlsSessionManager.dvdReadAheadLimitReached(14.1,0),"pause unbounded produced lead");
        require(!HlsSessionManager.dvdReadAheadLimitReached(20,7000),"new presented progress permits refill");
        require(!HlsSessionManager.dvdReadAheadLimitReached(Double.NaN,0),"unknown metrics cannot block first output");
        require(!HlsSessionManager.dvdReadAheadLimitReached(Double.POSITIVE_INFINITY,0),"malformed metrics cannot deadlock");
        String ffmpeg=args.length>0?args[0]:"/usr/bin/ffmpeg";
        System.setProperty("sagetv.webplayer.ffmpeg",ffmpeg);System.setProperty("sagetv.webplayer.videoEncoder","software");
        Path dir=Files.createTempDirectory("vibe-dvd-read-ahead-");DvdNativeSession dvd=new DvdNativeSession();HlsSessionManager.Session hls=null;
        AtomicBoolean stop=new AtomicBoolean();AtomicReference<Throwable> failure=new AtomicReference<Throwable>();Thread writer=null;
        try{
            Path file=dir.resolve("title.vob");
            // Include the normal DVD AC-3 track. A video-only35s/875-picture
            // fixture fits inside FFmpeg6's1024-packet input queue, which can
            // consume it before any output metric exists. That measures the
            // converter's startup queue, not the application's pacing loop.
            Process generated=new ProcessBuilder(ffmpeg,"-hide_banner","-loglevel","error","-y",
                    "-f","lavfi","-i","testsrc2=size=352x288:rate=25:duration=35",
                    "-f","lavfi","-i","sine=frequency=440:sample_rate=48000:duration=35",
                    "-map","0:v","-map","1:a","-c:v","mpeg2video","-b:v","3500k","-g","12",
                    "-c:a","ac3","-b:a","192k","-f","dvd",file.toString()).redirectErrorStream(true).start();
            ByteArrayOutputStream diagnostic=new ByteArrayOutputStream();byte[] buffer=new byte[4096];for(int n;(n=generated.getInputStream().read(buffer))>=0;)diagnostic.write(buffer,0,n);
            require(generated.waitFor(30,TimeUnit.SECONDS)&&generated.exitValue()==0,"generate bounded PS: "+diagnostic.toString("UTF-8"));
            final byte[] data=Files.readAllBytes(file);dvd.init(0);int first=Math.min(32768,data.length);dvd.push(push(data,0,first,0));
            hls=HlsSessionManager.startDvd(dvd);
            final int start=first;
            writer=new Thread(()->{try{
                int at=start;
                while(at<data.length&&!stop.get()){
                    int n=Math.min(32768,data.length-at);
                    // Model stock's previous free-space reply. Do not force a
                    // write into a full native pipe and call timeout a defect.
                    if(dvd.input().freeBytes()<n){Thread.sleep(5);continue;}
                    dvd.push(push(data,at,n,0));at+=n;
                }
                if(!stop.get())dvd.push(push(new byte[0],0,0,0x100));
            }catch(Throwable e){if(!stop.get())failure.set(e);}},"dvd-read-ahead-test-writer");writer.start();
            long end=System.currentTimeMillis()+15000;
            while(System.currentTimeMillis()<end&&!hls.dvdReadAheadPaused){HlsSessionManager.refreshMetrics(hls);Thread.sleep(20);}
            require(failure.get()==null,"native writer error");
            require(hls.dvdReadAheadPaused,"real converter must yield before encoding whole35s title; produced="
                    +hls.hlsSeconds+", consumed="+dvd.input().totalRead()+"/"+data.length
                    +", ready="+hls.playlistReady+", running="+hls.running+", exit="+hls.exitCode
                    +", waits="+hls.dvdReadAheadWaits+", stderr="+hls.stderrTail);
            double held=hls.hlsSeconds;long consumed=dvd.input().totalRead();Thread.sleep(300);HlsSessionManager.refreshMetrics(hls);
            require(hls.hlsSeconds<22&&hls.hlsSeconds>=14,"bounded actual lead, seconds="+hls.hlsSeconds);
            require(dvd.input().totalRead()<=consumed+32768,"feeder stays held without frame progress");
            require(dvd.input().totalRead()<data.length,"whole title not consumed at first chapter");
            HlsSessionManager.updateDvdBrowserProgress(hls,8000);
            end=System.currentTimeMillis()+5000;
            while(System.currentTimeMillis()<end&&dvd.input().totalRead()<=consumed){Thread.sleep(20);}
            require(dvd.input().totalRead()>consumed,"presented advance resumes same consumer without restart");
            stop.set(true);dvd.flush();writer.join(2000);
            hls.feederThread.join(2000);require(!hls.feederThread.isAlive(),"FLUSH cancels paced consumer without waiting for browser progress");
            require(failure.get()==null,"writer remains clean");
            Process consumer=hls.process;HlsSessionManager.stop(hls.id);
            require(consumer==null||!consumer.isAlive(),"Stop terminates the exact owned converter");
            System.out.println("PASS real DVD input pacing: held="+held+"s, refill/FLUSH/Stop, native capacity="+dvd.capacity()+"; no physical-clock claim");
        }finally{
            stop.set(true);if(hls!=null)HlsSessionManager.stop(hls.id);dvd.close();if(writer!=null)writer.join(2000);remove(dir.toFile());
        }
    }
}
