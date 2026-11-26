package org.opensagetv.webplayer;

import java.io.File;

/** Stock Windows sends raw backslashes for newly created recording paths. */
public final class MediaUrlPathSmoke {
    public static void main(String[] args) throws Exception {
        same("V:/tv/NBCNewsDaily-28048-0.ts",
            "stv://192.168.10.185/V:\\tv\\NBCNewsDaily-28048-0.ts");
        same("V:/tv/NBCNewsDaily-28048-0.ts",
            "stv://192.168.10.185/V:/tv/NBCNewsDaily-28048-0.ts");
        same("V:/tv/Show+Name.ts", "stv://server/V:%5Ctv%5CShow%2BName.ts");
        same("/media/Folder+One/VIDEO_TS", "stv://server/media/Folder%2BOne/VIDEO_TS");
        same("/media/a+b.ts", "stv://server/media/a+b.ts");
        same("/media/My Movie.ts", "stv://server/media/My%20Movie.ts");
        boolean rejected=false;
        try { MediaUrlPath.decode("stv://server/media/bad%QQ.ts"); }
        catch(Exception expected) { rejected=true; }
        if(!rejected)throw new AssertionError("Malformed percent escape must still fail");
        System.out.println("MediaUrlPathSmoke PASS7/7");
    }
    private static void same(String expected,String url) throws Exception {
        File file=MediaUrlPath.decode(url);
        String path=file.getPath().replace('\\','/');
        if(!expected.equals(path))throw new AssertionError("Expected "+expected+", got "+path);
    }
}
