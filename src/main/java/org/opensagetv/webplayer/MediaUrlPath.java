package org.opensagetv.webplayer;

import java.io.File;
import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

/** Safe MiniClient media-URL decoding. Literal '+' is a filename character, never a space. */
final class MediaUrlPath {
    private MediaUrlPath() {}

    static File decode(String url) throws Exception {
        String value=url==null?"":url.trim();
        int hash=value.indexOf('#'); if(hash>=0)value=value.substring(0,hash);
        if(value.startsWith("stv://")){
            // Stock Windows sends a filesystem path, not a fully escaped URI:
            // stv://host/V:\tv\recording.ts. Escape only the wire backslashes
            // for URI parsing, then restore them once. Authorization remains
            // the caller's existing MediaFile/import-root resolver.
            URI u=new URI(value.replace("\\","%5C"));
            String raw=u.getRawPath();if(raw==null)raw="";
            String path=percentDecode(raw);
            if(path.length()>3&&path.charAt(0)=='/'&&Character.isLetter(path.charAt(1))
                &&path.charAt(2)==':'&&(path.charAt(3)=='/'||path.charAt(3)=='\\'))path=path.substring(1);
            return new File(path);
        }
        if(value.startsWith("file://")){
            try{return new File(new URI(value));}
            catch(Exception ignored){return new File(percentDecode(value.substring(7)));}
        }
        return new File(percentDecode(value));
    }

    static String percentDecode(String value) throws Exception {
        if(value==null||value.indexOf('%')<0)return value==null?"":value;
        // URLDecoder implements application/x-www-form-urlencoded where '+' means space.
        // Protect literal plus signs before percent-decoding filesystem paths.
        return URLDecoder.decode(value.replace("+","%2B"), StandardCharsets.UTF_8.name());
    }
}
