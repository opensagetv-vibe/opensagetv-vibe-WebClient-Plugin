package org.opensagetv.webplayer;
public final class ChannelLogoSmoke {
    static final class Api implements ChannelLogoServlet.Api {
        int calls;boolean missing;Object data=new byte[]{(byte)137,80,78,71,13,10,26,10};
        public Object call(String n,Object... args){calls++;if(n.equals("GetChannelForStationID"))return missing?null:"channel";if(n.equals("GetChannelLogo"))return "logo";if(n.equals("GetMetaImageBytes"))return data;throw new AssertionError("Unexpected API");}
    }
    public static void main(String[] args)throws Exception {
        Api a=new Api();if(ChannelLogoServlet.logo(a,1)==null||a.calls!=3)throw new AssertionError();
        try{ChannelLogoServlet.logo(a,-1);throw new AssertionError();}catch(IllegalArgumentException expected){}if(a.calls!=3)throw new AssertionError();
        a.missing=true;if(ChannelLogoServlet.logo(a,2)!=null)throw new AssertionError();a.missing=false;
        for(Object b:new Object[]{null,"not bytes","<svg/>".getBytes("UTF-8"),new byte[1048577]}){a.data=b;if(ChannelLogoServlet.logo(a,2)!=null)throw new AssertionError();}
        if(!"image/jpeg".equals(ChannelLogoServlet.contentType(new byte[]{(byte)255,(byte)216,(byte)255}))||!"image/gif".equals(ChannelLogoServlet.contentType("GIF89a".getBytes("UTF-8"))))throw new AssertionError();
        System.out.println("PASS channel logos public station/image/bytes APIs only: invalid/missing/type/size/HTML-SVG guards, PNG-JPEG-GIF");
    }
}
