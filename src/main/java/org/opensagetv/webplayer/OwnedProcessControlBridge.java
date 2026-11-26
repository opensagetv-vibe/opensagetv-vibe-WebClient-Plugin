package org.opensagetv.webplayer;

import java.lang.reflect.Method;
import java.io.IOException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

/** Optional FFmpeg-plugin lifecycle API; never exposes PIDs or accepts commands.
 * A caller retains its exact Process until this method confirms it has exited.
 * An older/missing provider declines without calling Process.destroy: killing
 * a wrapper first can orphan its still-blocked child. No unsafe legacy kill.
 */
final class OwnedProcessControlBridge {
    interface Terminator { void terminate(Process owned) throws Exception; }
    private static final ConcurrentHashMap<Process, Thread> ATTEMPTS = new ConcurrentHashMap<Process, Thread>();
    private static final Terminator OPTIONAL = new Terminator() {
        public void terminate(Process owned) throws Exception {
            terminateMethod().invoke(null, owned);
        }
    };
    private OwnedProcessControlBridge() { }
    private static Method terminateMethod() throws Exception {
        Class<?> provider = Class.forName("org.opensagetv.vibe.ffmpeg.OwnedProcessControl");
        if (((Number)provider.getMethod("protocolVersion").invoke(null)).intValue() != 1 ||
                !Boolean.TRUE.equals(provider.getMethod("available").invoke(null)))
            throw new IOException("Shared owned-process protocol1 unavailable");
        return provider.getMethod("terminate", Process.class);
    }
    static boolean available() {
        try { terminateMethod(); return true; }
        catch (Exception | LinkageError unavailable) { return false; }
    }
    static Process start(ProcessBuilder builder) throws IOException {
        // Optional additive API. Existing Java9 providers retain their public
        // ProcessHandle stop; Java8 Windows registers the exact native job root.
        try {
            Class<?> provider=Class.forName("org.opensagetv.vibe.ffmpeg.OwnedProcessControl");
            return (Process)provider.getMethod("start",ProcessBuilder.class).invoke(null,builder);
        } catch (ClassNotFoundException | NoSuchMethodException olderProvider) {
            return builder.start();
        } catch (java.lang.reflect.InvocationTargetException failed) {
            Throwable cause=failed.getCause();
            if(cause instanceof IOException)throw (IOException)cause;
            throw new IOException("Owned encoder start failed",cause);
        } catch (ReflectiveOperationException | LinkageError unavailable) {
            throw new IOException("Owned encoder start unavailable",unavailable);
        }
    }
    static boolean stop(Process owned, long timeoutMs) {
        return stop(owned, timeoutMs, OPTIONAL);
    }
    static boolean stop(final Process owned, long timeoutMs, final Terminator terminator) {
        if (owned == null) return true;
        Thread attempt = ATTEMPTS.get(owned);
        if (!owned.isAlive() && (attempt == null || !attempt.isAlive())) { ATTEMPTS.remove(owned); return true; }
        if (timeoutMs < 1 || timeoutMs > 4000) throw new IllegalArgumentException("Bounded stop timeout required");
        Thread candidate = new Thread(new Runnable() { public void run() {
            try { terminator.terminate(owned); }
            catch (Exception | LinkageError unavailable) { /* owner retains live Process and reports incomplete stop */ }
            finally {
                try { if (owned.waitFor(4, TimeUnit.SECONDS)) ATTEMPTS.remove(owned, Thread.currentThread()); }
                catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); }
            }
        }}, "webplayer-owned-process-stop");
        candidate.setDaemon(true);
        Thread previous = ATTEMPTS.putIfAbsent(owned, candidate);
        if (previous == null) candidate.start();
        Thread worker = previous == null ? candidate : previous;
        try { worker.join(timeoutMs); }
        catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); }
        if (!worker.isAlive() && !owned.isAlive()) { ATTEMPTS.remove(owned); return true; }
        return false;
    }
}
