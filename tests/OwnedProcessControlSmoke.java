package org.opensagetv.webplayer;

import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.CountDownLatch;
import org.opensagetv.vibe.ffmpeg.OwnedProcessControl;

/** Real duplex processes; optional shared implementation, no server/Core. */
public final class OwnedProcessControlSmoke {
    private static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
    private static Process duplex() throws IOException {
        return OwnedProcessControlBridge.start(new ProcessBuilder("/bin/sh", "-c", "dd if=/dev/zero bs=32768 count=4096 2>/dev/null & wait"));
    }
    private static Thread writer(final Process process) {
        Thread thread = new Thread(new Runnable() { public void run() {
            byte[] bytes = new byte[32768];
            try { for (int i=0; i<512; i++) process.getOutputStream().write(bytes); }
            catch (IOException expected) { }
        }}); thread.setDaemon(true); thread.start(); return thread;
    }
    public static void main(String[] args) throws Exception {
        check(OwnedProcessControlBridge.stop(null, 100), "no-process no-op");
        Process unrelated = new ProcessBuilder("/bin/sh", "-c", "exec sleep 30").start();
        Process normal = duplex(); Thread normalWriter=writer(normal);
        Process legacy = duplex(); Thread legacyWriter=writer(legacy);
        final CountDownLatch release = new CountDownLatch(1);
        try {
            Thread.sleep(250);
            check(normalWriter.isAlive() && legacyWriter.isAlive(), "real blocked input writers");
            check(OwnedProcessControlBridge.stop(normal, 2000), "optional shared API releases blocked tree");
            normalWriter.join(1000); check(!normalWriter.isAlive(), "shared API writer retired");
            final AtomicInteger attempts = new AtomicInteger();
            OwnedProcessControlBridge.Terminator old = new OwnedProcessControlBridge.Terminator() {
                public void terminate(Process owned) throws Exception { attempts.incrementAndGet(); release.await(); }
            };
            long start=System.nanoTime();
            check(!OwnedProcessControlBridge.stop(legacy, 100, old), "blocked termination returns incomplete, not success");
            check(!OwnedProcessControlBridge.stop(legacy, 100, old), "same owned stop remains pending");
            check(System.nanoTime()-start < 1000000000L, "HTTP-side wait bounded");
            check(attempts.get()==1 && legacy.isAlive(), "no repeated workers or forgotten live Process");
            check(unrelated.isAlive(), "other playback process untouched");
            OwnedProcessControl.terminate(legacy); check(legacy.waitFor(2,TimeUnit.SECONDS), "explicit test cleanup exits");
            release.countDown();
            legacyWriter.join(1000); check(!legacyWriter.isAlive(), "legacy blocked writer released by shared cleanup");
            Thread.sleep(50);
            check(OwnedProcessControlBridge.stop(legacy, 100), "exited owner is retired");
            System.out.println("PASS optional API, blocked duplex, bounded incomplete-stop refusal, one worker, retained owner, unrelated preservation");
        } finally {
            release.countDown();
            OwnedProcessControl.terminate(normal); OwnedProcessControl.terminate(legacy); OwnedProcessControl.terminate(unrelated);
            normal.waitFor(2,TimeUnit.SECONDS); legacy.waitFor(2,TimeUnit.SECONDS); unrelated.waitFor(2,TimeUnit.SECONDS);
        }
    }
}
