package org.opensagetv.webplayer;

/** Functional client contract checks; synthetic peers are not physical DVD evidence. */
public final class P15StockContractsSmoke {
    public static void main(String[] args) throws Exception {
        MiniClientSession session=new MiniClientSession("p15","127.0.0.1:9","02:00:00:00:15:15",640,360);
        java.lang.reflect.Method property=MiniClientSession.class.getDeclaredMethod("property",String.class);
        property.setAccessible(true); // Test-only access, never a runtime Core hook.
        for(String name:new String[]{"DVD_DISC_TRANSPORTS","DVD_DISC_POLICY","DVD_DISC_SKIP_MENUS",
                "DVD_DISC_SKIP_PREVIEWS","DVD_DISC_NATIVE_FALLBACK","MEDIA_STATE_URL","UNKNOWN_EXTENSION"})
            check("".equals(property.invoke(session,name)),"Unsupported GET stays empty: "+name);
        for(String name:new String[]{"DVD_DISC_POLICY","DVD_DISC_FUTURE","MEDIA_STATE_URL","VIDEO_PLAYBACK_RATE"})
            check(MiniClientCapabilityPolicy.unsupportedExtensionSet(name),"Unsupported SET rejected: "+name);
        check(!MiniClientCapabilityPolicy.unsupportedExtensionSet("MENU_HINT")
                &&!MiniClientCapabilityPolicy.unsupportedExtensionSet("SUBTITLES_CALLBACKS"),"Stock property behavior preserved");
        String capabilities=MiniClientCapabilityPolicy.json();
        check(!DiagnosticJson.sanitize(capabilities,4096).contains("unavailable"),"Capability diagnostics is bounded valid JSON");
        check(capabilities.contains("\"transformedMainFeature\":false")&&capabilities.contains("\"privateMediaStateUrl\":false"),
                "No private Core representation/metadata claims");
        check(capabilities.contains("\"companionDvdNegotiation\":\"optional-per-load\"")
                &&!capabilities.contains("\"controls\":true"),"Supported optional profile is not a negotiated-load claim");
        check(!StreamOptions.defaults().companionDvd,"Extension opt-in stays off by default");
        check(session.media().playbackStateJson().contains("\"displayedPositionMs\":null"),"No invented idle presentation clock");
        System.out.println("P15 stock contracts: 17 PASS");
    }
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println("PASS "+why);}
}
