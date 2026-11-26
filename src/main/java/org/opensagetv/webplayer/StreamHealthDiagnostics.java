package org.opensagetv.webplayer;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.atomic.AtomicLong;

/** WEB-121 passive flight recorder. No playback commands, source reads or lifecycle locks. */
final class StreamHealthDiagnostics {
    static final int MAX_SESSIONS=16, MAX_SAMPLES=90, MAX_FILE_BYTES=1024*1024;
    private static final LinkedHashMap<String,ArrayDeque<String>> HISTORY=new LinkedHashMap<String,ArrayDeque<String>>();
    private static final ArrayBlockingQueue<String> WRITES=new ArrayBlockingQueue<String>(128);
    private static final AtomicLong DROPPED=new AtomicLong();
    private static volatile String storageState="not-written";

    static boolean enabled(){return Boolean.parseBoolean(System.getProperty("sagetv.webplayer.streamDiagnostics.enabled","true"));}

    static String transportFailure(Throwable error){
        if(error instanceof java.net.SocketTimeoutException)return "timeout";
        if(error instanceof java.io.EOFException)return "eof";
        String message=error==null?"":String.valueOf(error.getMessage()).toLowerCase(Locale.ROOT);
        if(message.contains("broken pipe"))return "broken-pipe";
        if(message.contains("connection reset"))return "connection-reset";
        return "io-error";
    }

    static String classify(boolean stopped,boolean alive,boolean ready,boolean ended,boolean failed,
                           long age,long inputAge,long outputAge,String inputStage,
                           long feedbackAge,boolean paused,boolean browserEnded,long bufferAheadMs){
        if(stopped)return "stopped";
        if(!alive&&failed)return "producer-failed";
        if(!alive&&ended)return "producer-complete"; // not proof the browser presented EOF
        if(age<15000&&!ready)return "starting";
        if(!alive)return "producer-not-running";
        if(outputAge>=10000){
            if("waiting-source".equals(inputStage))return "waiting-source-growth";
            if("dvd-read-ahead-paused".equals(inputStage))return "dvd-read-ahead-paused";
            if("write".equals(inputStage)&&inputAge>=10000)return "encoder-input-backpressure";
            if(inputAge<5000)return "encoder-output-stalled";
            return ready?"no-output-progress":"no-first-segment";
        }
        if(feedbackAge<10000&&!paused&&!browserEnded&&bufferAheadMs>=0&&bufferAheadMs<250)
            return "browser-buffer-empty";
        if(feedbackAge>=10000)return "browser-feedback-missing";
        return paused?"paused":"progressing";
    }

    static String snapshot(HlsSessionManager.Session s,long now){
        long origin=s.launchedAt>0?s.launchedAt:s.createdAt;
        long inputAge=age(now,s.healthInputAt,origin),outputAge=age(now,s.lastSegmentAt,origin);
        long feedbackAge=age(now,s.healthBrowserAt,origin);
        Process p=s.process; boolean alive=p!=null&&p.isAlive();
        String state=classify(s.stopRequested,alive,s.playlistReady,s.endList,
            s.error.length()>0||s.exitCode!=Integer.MIN_VALUE&&s.exitCode!=0,
            Math.max(0,now-origin),inputAge,outputAge,s.healthInputStage,feedbackAge,
            s.healthIntentPaused,s.healthEnded,s.healthBufferAheadMs);
        return "{\"atMs\":"+now+",\"session\":\""+HttpUtil.json(s.id)+"\",\"mediaId\":"+s.mediaId+
            ",\"sourceSegment\":"+s.firstSegment+",\"nativeSegment\":"+s.nativeSegment+
            ",\"state\":\""+state+"\",\"observationalOnly\":true,\"processAlive\":"+alive+
            ",\"producerPreparing\":"+(s.producerPreparing&&!s.playlistReady)+
            ",\"recording\":"+s.activeRecording+",\"inputStage\":\""+HttpUtil.json(s.healthInputStage)+
            "\",\"inputBytes\":"+s.bytesInput+",\"sourceLength\":"+s.healthSourceLength+
            ",\"sourcePosition\":"+s.healthSourcePosition+",\"inputAgeMs\":"+inputAge+
            ",\"segments\":"+s.segments+",\"outputBytes\":"+s.bytesProduced+",\"outputAgeMs\":"+outputAge+
            ",\"encoderTimeMs\":"+s.healthEncoderTimeMs+",\"encoderProgressAgeMs\":"+age(now,s.healthEncoderAt,origin)+
            ",\"freeOutputBytes\":"+s.healthFreeBytes+
            ",\"endList\":"+s.endList+",\"exitCode\":"+(s.exitCode==Integer.MIN_VALUE?"null":s.exitCode)+
            ",\"fallbackStage\":"+s.fallbackStage+",\"encoder\":\""+HttpUtil.json(s.encoder)+
            "\",\"producerAttempt\":"+s.healthAttempt+",\"browserRecoveryAttempts\":"+s.healthRecoveryAttempts+
            ",\"browserLoaderRepaired\":"+s.healthBrowserRepair+
            ",\"browserRevision\":\""+HttpUtil.json(s.healthBrowserRevision)+"\",\"nativeTransportError\":\""+s.healthNativeError+
            "\",\"nativeTransportErrorAtMs\":"+s.healthNativeErrorAt+
            ",\"inputError\":\""+s.healthInputError+"\",\"inputErrorAtMs\":"+s.healthInputErrorAt+
            ",\"seekRequestedMs\":"+s.seekRequestedMs+",\"seekAnchorMs\":"+s.seekAnchorMs+
            ",\"seekResidualMs\":"+s.seekResidualMs+",\"browserSeen\":"+(s.healthBrowserAt>0)+
            ",\"browserFeedbackAgeMs\":"+feedbackAge+",\"browserTimeMs\":"+s.healthBrowserTimeMs+
            ",\"bufferAheadMs\":"+s.healthBufferAheadMs+",\"readyState\":"+s.healthReadyState+
            ",\"networkState\":"+s.healthNetworkState+",\"paused\":"+s.healthPaused+
            ",\"intentPaused\":"+s.healthIntentPaused+
            ",\"seeking\":"+s.healthSeeking+",\"browserEnded\":"+s.healthEnded+
            ",\"requests\":"+s.healthRequests+",\"requestFailures\":"+s.healthRequestFailures+
            ",\"requestActive\":"+s.healthRequestsActive.get()+",\"lastHttpStatus\":"+s.healthLastHttpStatus+
            ",\"lastRequestMs\":"+s.healthLastRequestMs+",\"deliveredBytes\":"+s.deliveredBytes+
            ",\"feederThread\":\""+thread(s.feederThread)+"\",\"monitorThread\":\""+thread(s.monitorThread)+
            "\",\"errorPresent\":"+(s.error.length()>0)+"}";
    }
    private static long age(long now,long at,long fallback){return Math.max(0,now-(at>0?at:fallback));}
    private static String thread(Thread t){return t==null?"absent":t.getState().name();}

    static void sample(HlsSessionManager.Session s,boolean force){
        if(!enabled()||s==null)return;
        long now=System.currentTimeMillis();
        if(!force&&now-s.healthSampleAt<2000)return;
        s.healthSampleAt=now;
        String row=snapshot(s,now);
        synchronized(HISTORY){
            ArrayDeque<String> rows=HISTORY.get(s.id);
            if(rows==null){rows=new ArrayDeque<String>();HISTORY.put(s.id,rows);}
            while(HISTORY.size()>MAX_SESSIONS)HISTORY.remove(HISTORY.keySet().iterator().next());
            if(rows.size()==MAX_SAMPLES)rows.removeFirst();rows.addLast(row);
        }
        if(!WRITES.offer(row))DROPPED.incrementAndGet(); // logging must never block playback
    }

    static String json(String id){
        StringBuilder b=new StringBuilder("{\"schemaVersion\":1,\"enabled\":"+enabled()+
            ",\"storageState\":\""+storageState+"\",\"droppedJournalSamples\":"+DROPPED.get()+
            ",\"classificationIsEvidenceNotProof\":true,\"sessions\":[");
        synchronized(HISTORY){boolean first=true;int skip=Math.max(0,HISTORY.size()-8),i=0;
            for(Map.Entry<String,ArrayDeque<String>> e:HISTORY.entrySet()){
                if(id!=null&&!id.isEmpty()&&!id.equals(e.getKey()))continue;
                if((id==null||id.isEmpty())&&i++<skip)continue;
                if(!first)b.append(',');first=false;b.append("{\"session\":\"").append(HttpUtil.json(e.getKey())).append("\",\"samples\":[");
                boolean f=true;for(String row:e.getValue()){if(!f)b.append(',');f=false;b.append(row);}b.append("]}");
            }
        }
        return b.append("]}").toString();
    }

    static Path directory(){return Paths.get(System.getProperty("sagetv.webplayer.streamDiagnostics.dir",
        "plugins/SageTVWebPlayer/diagnostics")).toAbsolutePath().normalize();}

    static void poll(HlsSessionManager.Session s){
        // Bounded local progress read, outside producer/HTTP/lifecycle locks.
        try(java.io.RandomAccessFile f=new java.io.RandomAccessFile(new java.io.File(s.directory,"progress.log"),"r")){
            long length=f.length();f.seek(Math.max(0,length-8192));byte[] b=new byte[(int)Math.min(8192,length)];f.readFully(b);
            long time=Math.round(HlsSessionManager.parseProgressSeconds(new String(b,StandardCharsets.UTF_8))*1000);
            if(time>s.healthEncoderTimeMs){s.healthEncoderTimeMs=time;s.healthEncoderAt=System.currentTimeMillis();}
        }catch(IOException ignored){}
        s.healthFreeBytes=s.directory.getUsableSpace();
        sample(s,false);
    }

    static byte[] journal()throws IOException{
        java.io.ByteArrayOutputStream out=new java.io.ByteArrayOutputStream();
        for(String name:new String[]{"stream-health.previous.jsonl","stream-health.jsonl"}){
            Path file=directory().resolve(name);
            if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))continue;
            try(java.io.InputStream in=Files.newInputStream(file)){byte[] b=new byte[8192];int n,left=MAX_FILE_BYTES;
                while(left>0&&(n=in.read(b,0,Math.min(b.length,left)))>0){out.write(b,0,n);left-=n;}}
        }
        return out.toByteArray();
    }

    /** Called by the independent diagnostic worker, never a producer/HTTP thread. */
    static synchronized void flush(){
        String row;int count=0;
        while(count++<128&&(row=WRITES.poll())!=null){
            try{append(directory(),row);storageState="written";}
            catch(IOException|RuntimeException failure){storageState="write-failed";DROPPED.incrementAndGet();}
        }
    }
    static void append(Path dir,String row)throws IOException{
        // Administrator-controlled local path; refuse symlinks along the whole route.
        Path part=dir.getRoot();for(Path name:dir){part=part.resolve(name);if(Files.isSymbolicLink(part))throw new IOException("Diagnostic symlink refused");}
        Files.createDirectories(dir);
        Path active=dir.resolve("stream-health.jsonl"),previous=dir.resolve("stream-health.previous.jsonl");
        for(Path p:new Path[]{active,previous})if(Files.exists(p,LinkOption.NOFOLLOW_LINKS)&&!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS))throw new IOException("Diagnostic target is not a regular file");
        byte[] bytes=(row+"\n").getBytes(StandardCharsets.UTF_8);
        if(bytes.length>16384)throw new IOException("Diagnostic row limit");
        if(Files.exists(active)&&Files.size(active)+bytes.length>MAX_FILE_BYTES)
            Files.move(active,previous,StandardCopyOption.REPLACE_EXISTING);
        Files.write(active,bytes,StandardOpenOption.CREATE,StandardOpenOption.APPEND);
    }
    private StreamHealthDiagnostics(){}
}
