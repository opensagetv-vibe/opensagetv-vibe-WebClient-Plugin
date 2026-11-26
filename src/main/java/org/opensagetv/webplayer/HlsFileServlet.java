package org.opensagetv.webplayer;

import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;

/** Snapshot-serving endpoint for FFmpeg HLS playlist/segments. */
public class HlsFileServlet extends HttpServlet {
    @Override protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String path = request.getPathInfo();
        if (path == null) { response.sendError(404); return; }
        String[] parts = path.replaceFirst("^/+", "").split("/");
        if (parts.length != 2) { response.sendError(404); return; }
        String sessionId = parts[0];
        String filename = parts[1];
        long started=System.nanoTime(),delivered=0;
        int httpStatus=500;
        HlsSessionManager.Session delivery=HlsSessionManager.beginDelivery(sessionId);
        try {
            // The initial manifest request is allowed to wait for FFmpeg startup. Segment requests
            // wait briefly for temp_file atomic rename to become visible.
            File file = HlsSessionManager.waitForFile(sessionId, filename,
                    "stream.m3u8".equals(filename) ? 16000L : 5000L);
            if (!file.isFile() || file.length() <= 0) {
                HlsSessionManager.Session s = HlsSessionManager.get(sessionId);
                if (s != null && s.error != null && s.error.length() > 0) {httpStatus=502;response.sendError(502, s.error);}
                else {httpStatus=404;response.sendError(404);}
                return;
            }
            byte[] data = Files.readAllBytes(file.toPath());
            if(filename.endsWith(".m3u8"))data=browserPlaylist(data);
            response.setContentType(filename.endsWith(".m3u8") ? "application/vnd.apple.mpegurl" : "video/mp2t");
            response.setHeader("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0");
            response.setHeader("Pragma", "no-cache");
            response.setHeader("Expires", "0");
            response.setHeader("Accept-Ranges", "none");
            response.setHeader("X-Content-Type-Options", "nosniff");
            response.setContentLength(data.length);
            ServletOutputStream out = response.getOutputStream();
            out.write(data);
            out.flush();
            httpStatus=200;delivered=data.length;
            HlsSessionManager.browserMediaRead(sessionId);
        } catch (IOException e) {
            httpStatus=404;
            response.sendError(404, e.getMessage());
        } finally {
            HlsSessionManager.endDelivery(delivery,started,httpStatus,delivered);
        }
    }

    /** A one-frame DVD cell can make FFmpeg round its target duration to zero.
     * Native Safari rejects that manifest before requesting its valid segment.
     * Raise only the target bound; do not fabricate media duration/frames/EOS.
     */
    static byte[] browserPlaylist(byte[] data) {
        String text=new String(data,StandardCharsets.UTF_8);
        String normalized=text.replaceAll("(?m)^#EXT-X-TARGETDURATION:0([\\t ]*\\r?)$","#EXT-X-TARGETDURATION:1$1");
        return normalized.equals(text)?data:normalized.getBytes(StandardCharsets.UTF_8);
    }
}
