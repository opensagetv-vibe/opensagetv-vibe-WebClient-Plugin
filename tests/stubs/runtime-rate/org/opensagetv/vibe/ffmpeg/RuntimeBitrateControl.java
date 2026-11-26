package org.opensagetv.vibe.ffmpeg;
/** Test-only optional provider. Never packaged in the WAR. */
public final class RuntimeBitrateControl {
    public static int protocolVersion(){return 1;}
    public static boolean enabled(){return !Boolean.getBoolean("vibe.test.rateDisabled");}
}
