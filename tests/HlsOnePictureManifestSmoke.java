package org.opensagetv.webplayer;
import java.nio.charset.StandardCharsets;

/** Serving-only target bound repair; never modifies a segment or EXTINF. */
public final class HlsOnePictureManifestSmoke {
    public static void main(String[] args) {
        String tiny="#EXTM3U\n#EXT-X-VERSION:6\n#EXT-X-TARGETDURATION:0\n#EXTINF:0.041711,\nseg_00000.ts\n#EXT-X-ENDLIST\n";
        byte[] fixed=HlsFileServlet.browserPlaylist(tiny.getBytes(StandardCharsets.UTF_8));
        String text=new String(fixed,StandardCharsets.UTF_8);
        if(!text.equals(tiny.replace("TARGETDURATION:0","TARGETDURATION:1")))throw new AssertionError("One-picture manifest target not repaired");
        if(Math.abs(HlsSessionManager.parsePlaylistSeconds(text)-.041711)>.000001)throw new AssertionError("Media duration fabricated");
        byte[] ordinary=tiny.replace("TARGETDURATION:0","TARGETDURATION:2").getBytes(StandardCharsets.UTF_8);
        if(HlsFileServlet.browserPlaylist(ordinary)!=ordinary)throw new AssertionError("Ordinary playlist changed");
        String crlf=tiny.replace("\n","\r\n");
        if(!new String(HlsFileServlet.browserPlaylist(crlf.getBytes(StandardCharsets.UTF_8)),StandardCharsets.UTF_8).equals(crlf.replace("TARGETDURATION:0","TARGETDURATION:1")))throw new AssertionError("CRLF changed");
        System.out.println("PASS four one-picture target/duration/ordinary/CRLF guards");
    }
}
