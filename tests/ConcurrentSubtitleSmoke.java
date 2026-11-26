package org.opensagetv.webplayer;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.concurrent.*;

/** Actual concurrent generated decoders/epochs, not two-client field playback. */
public final class ConcurrentSubtitleSmoke {
    public static void main(String[] args) throws Exception {
        final byte[] text = Files.readAllBytes(Paths.get("tests/parity/fixtures/teletext-188.ts"));
        final byte[] bitmap = Files.readAllBytes(Paths.get("tests/parity/fixtures/dvb-8bpp.ts"));
        final PlaybackSessionContext a = new PlaybackSessionContext(), b = new PlaybackSessionContext();
        final CyclicBarrier together = new CyclicBarrier(2);
        ExecutorService pool = Executors.newFixedThreadPool(2);
        try {
            Future<Integer> first = pool.submit(() -> run(a, b, together, text, true));
            Future<Integer> second = pool.submit(() -> run(b, a, together, bitmap, false));
            if (first.get(20, TimeUnit.SECONDS) != 100 || second.get(20, TimeUnit.SECONDS) != 100)
                throw new AssertionError("Concurrent run incomplete");
            System.out.println("PASS concurrent Teletext/DVB:2 threads x100 synchronized source/seek/stop epochs, independent tokens/cues");
        } finally {
            pool.shutdownNow();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) throw new AssertionError("Test workers not retired");
        }
    }

    private static int run(PlaybackSessionContext own, PlaybackSessionContext other,
                           CyclicBarrier together, byte[] bytes, boolean text) throws Exception {
        for (int i = 0; i < 100; i++) {
            PlaybackSessionContext.Token token = own.beginSource();
            together.await(5, TimeUnit.SECONDS);
            if (text) {
                TeletextSubtitleSession decoder = new TeletextSubtitleSession(own, token, 0);
                decoder.configure(true, 888, "eng");
                decoder.observe("generated-text", 0, bytes, 0, bytes.length);
            } else {
                DvbSubtitleSession decoder = new DvbSubtitleSession(own, token, 0);
                decoder.configure(true, -1, -1, "eng");
                decoder.observe("generated-bitmap", 0, bytes, 0, bytes.length);
            }
            together.await(5, TimeUnit.SECONDS);
            List<SubtitleCue> cues = own.cues().drainDue(token, 1000, 50);
            if (cues.isEmpty() || !own.isCurrent(token) || other.isCurrent(token))
                throw new AssertionError("Lost/crossed concurrent client ownership");
            for (SubtitleCue cue : cues)
                if (cue.token != token || cue.owner != (text ? SubtitleCue.Owner.LOCAL_BROADCAST : SubtitleCue.Owner.LOCAL_DVB))
                    throw new AssertionError("Wrong client/decoder cue");
            own.beginSeek();
            if (own.isCurrent(token) || own.cues().size() != 0) throw new AssertionError("Old epoch retained after seek");
            own.invalidateSource();
            together.await(5, TimeUnit.SECONDS);
        }
        return 100;
    }
}
