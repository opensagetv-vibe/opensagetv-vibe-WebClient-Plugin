package org.opensagetv.webplayer;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

/** Exact associated palette context, never a browser path or guessed VOB palette. */
final class VobSubPalette {
    private VobSubPalette() {}

    static void configure(List<String> args, File idx) throws IOException {
        File parent=idx.getCanonicalFile().getParentFile();
        requireSibling(idx,parent);
        String text;
        try(RandomAccessFile in=new RandomAccessFile(idx,"r")) {
            long size=in.length();if(size>256*1024)throw new IOException("VobSub IDX exceeds context limit");
            byte[] bytes=new byte[(int)size];in.readFully(bytes);
            if(in.length()!=size)throw new IOException("VobSub IDX changed during context read");
            // Palette directives are ASCII; legacy IDX comments need not be UTF-8.
            text=new String(bytes,StandardCharsets.ISO_8859_1);
        }
        String name=idx.getName();
        if(!name.toLowerCase(Locale.ROOT).endsWith(".idx"))throw new IOException("VobSub IDX context required");
        String base=name.substring(0,name.length()-4);
        requireSibling(new File(idx.getParentFile(),base+".sub"),parent);
        String palette=null;
        for(String line:text.split("\\r?\\n")) {
            String value=line.trim();
            if(!value.toLowerCase(Locale.ROOT).startsWith("palette:"))continue;
            if(palette!=null)throw new IOException("Ambiguous VobSub IDX palette");
            String[] colors=value.substring(8).trim().split("\\s*,\\s*",-1);
            if(colors.length!=16)throw new IOException("Invalid VobSub IDX palette");
            for(String color:colors)if(!color.matches("[0-9a-fA-F]{6}"))throw new IOException("Invalid VobSub IDX palette");
            palette=String.join(",",colors);
        }
        if(palette!=null){Collections.addAll(args,"-palette",palette);return;}
        File ifo=new File(idx.getParentFile(),base+".ifo");
        if(!ifo.isFile())throw new IOException("VobSub palette unavailable: provide IDX palette or associated VTS IFO");
        requireSibling(ifo,parent);
        validateIfo(ifo);
        Collections.addAll(args,"-ifo_palette",ifo.getCanonicalPath());
    }

    private static void requireSibling(File file,File parent)throws IOException {
        if(!file.isFile()||Files.isSymbolicLink(file.toPath())||!parent.equals(file.getCanonicalFile().getParentFile()))
            throw new IOException("VobSub context must be an exact local associated file");
    }

    // Validate the bounded VTS first-PGC palette region consumed by FFmpeg's
    // public ifo_palette option. FFmpeg can otherwise fall back to guessed gray
    // after an invalid IFO, which is not verified authored-color support.
    static void validateIfo(File file)throws IOException {
        try(RandomAccessFile in=new RandomAccessFile(file,"r")) {
            long length=in.length();
            if(length<0xd0||length>8*1024*1024)throw new IOException("Invalid VobSub VTS IFO size");
            byte[] magic=new byte[12];in.readFully(magic);
            if(!Arrays.equals(magic,"DVDVIDEO-VTS".getBytes(StandardCharsets.US_ASCII)))throw new IOException("VobSub VTS IFO required");
            in.seek(0xcc);long table=Integer.toUnsignedLong(in.readInt())*2048L;
            if(table<2048||table>length-16)throw new IOException("Invalid VobSub IFO PGC table");
            in.seek(table);int entries=in.readUnsignedShort();in.skipBytes(2);long last=Integer.toUnsignedLong(in.readInt());
            if(entries<1||last<15||last>=length-table)throw new IOException("Invalid VobSub IFO PGC extent");
            in.seek(table+12);long offset=Integer.toUnsignedLong(in.readInt());
            if(offset<16||offset>last-0xe3||table+offset+0xe4>length)throw new IOException("VobSub IFO palette region unavailable");
            in.seek(table+offset+0xa4);byte[] palette=new byte[64];in.readFully(palette);
        }
    }
}
