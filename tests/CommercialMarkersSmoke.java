package org.opensagetv.webplayer;

import java.nio.file.Files;
import java.nio.file.Path;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;
import java.util.List;

/** Existing source-side EDL parser with bounded hostile/large-input tests. */
public final class CommercialMarkersSmoke {
    public static void main(String[] args)throws Exception{
        Path dir=Files.createTempDirectory("vibe-edl-"),file=dir.resolve("fixture.edl");
        Method read=CommercialsServlet.class.getDeclaredMethod("readEdl",java.io.File.class);read.setAccessible(true);
        try{
            Files.write(file,"# marker fixture\n10 20 0\n30 40 3\nNaN 50 0\n-1 5 0\n30 20 0\n".getBytes("UTF-8"));
            if(((List<?>)read.invoke(null,file.toFile())).size()!=2)throw new AssertionError("EDL validation changed");
            byte[] oversizedLine=new byte[4097];java.util.Arrays.fill(oversizedLine,(byte)'1');Files.write(file,oversizedLine);reject(read,file);
            Files.write(file,new byte[1024*1024+1]);reject(read,file);
            StringBuilder many=new StringBuilder();for(int i=0;i<5000;i++)many.append("10 20 0\n");Files.write(file,many.toString().getBytes("UTF-8"));
            if(((List<?>)read.invoke(null,file.toFile())).size()!=4096)throw new AssertionError("Marker count unbounded");
            System.out.println("Commercial marker validation/line/byte/count bounds: 4 PASS");
        }finally{Files.deleteIfExists(file);Files.deleteIfExists(dir);}
    }
    private static void reject(Method read,Path file)throws Exception{
        try{read.invoke(null,file.toFile());throw new AssertionError("Oversized EDL accepted");}
        catch(InvocationTargetException expected){if(!(expected.getCause() instanceof java.io.IOException))throw expected;}
    }
}
