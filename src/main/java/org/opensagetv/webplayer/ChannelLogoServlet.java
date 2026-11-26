package org.opensagetv.webplayer;

import java.io.IOException;
import javax.servlet.http.*;

/** Serve an existing SageTV channel logo through public APIs, not a file/URL proxy. */
public final class ChannelLogoServlet extends HttpServlet {
    interface Api { Object call(String name,Object... args)throws Exception; }
    static byte[] logo(Api api,int id)throws Exception {
        if(id<=0)throw new IllegalArgumentException("Invalid stationId");
        Object channel=api.call("GetChannelForStationID",Integer.valueOf(id));
        if(channel==null)return null;
        Object image=api.call("GetChannelLogo",channel);
        if(image==null)return null;
        Object value=api.call("GetMetaImageBytes",image);
        if(!(value instanceof byte[]))return null;
        byte[] data=(byte[])value;
        return data.length<=1048576&&contentType(data)!=null?data:null;
    }
    static String contentType(byte[] b) {
        if(b==null)return null;
        if(b.length>=8&&(b[0]&255)==137&&b[1]==80&&b[2]==78&&b[3]==71&&b[4]==13&&b[5]==10&&b[6]==26&&b[7]==10)return "image/png";
        if(b.length>=3&&(b[0]&255)==255&&(b[1]&255)==216&&(b[2]&255)==255)return "image/jpeg";
        if(b.length>=6&&b[0]==71&&b[1]==73&&b[2]==70&&b[3]==56&&(b[4]==55||b[4]==57)&&b[5]==97)return "image/gif";
        return null;
    }
    @Override protected void doGet(HttpServletRequest req,HttpServletResponse resp)throws IOException {
        try {
            final Class<?> sage=Class.forName("sage.SageTV");
            byte[] data=logo(new Api(){public Object call(String name,Object... args)throws Exception {
                return sage.getMethod("api",String.class,Object[].class).invoke(null,name,args);
            }},HttpUtil.requiredInt(req.getParameter("stationId"),"stationId"));
            if(data==null){resp.sendError(404);return;}
            resp.setContentType(contentType(data));resp.setContentLength(data.length);
            resp.setHeader("X-Content-Type-Options","nosniff");resp.setHeader("Cache-Control","private, max-age=300");
            resp.getOutputStream().write(data);
        }catch(IllegalArgumentException e){HttpUtil.jsonError(resp,400,"Invalid channel logo request");}
        catch(Exception e){HttpUtil.jsonError(resp,404,"Channel logo unavailable");}
    }
}
