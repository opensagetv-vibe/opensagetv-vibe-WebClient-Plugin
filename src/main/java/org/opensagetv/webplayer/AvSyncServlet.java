package org.opensagetv.webplayer;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import javax.servlet.http.*;

/** Authenticated by the existing Jetty application boundary, fixed media only. */
public final class AvSyncServlet extends HttpServlet {
    public void destroy(){AvSyncManager.close();super.destroy();}
    protected void doPost(HttpServletRequest request,HttpServletResponse response)throws IOException{
        try{
            String action=request.getParameter("action");String json;
            if("start".equals(action))json=AvSyncManager.create(StreamOptions.fromRequest(request::getParameter)).json();
            else if("stop".equals(action)){AvSyncManager.stop(request.getParameter("id"));json="{\"ok\":true}";}
            else throw new IllegalArgumentException("Unknown A/V test action");
            response.setContentType("application/json");response.setCharacterEncoding("UTF-8");response.setHeader("Cache-Control","no-store");response.getWriter().write(json);
        }catch(IllegalArgumentException error){HttpUtil.jsonError(response,400,error.getMessage());}
        catch(IOException error){HttpUtil.jsonError(response,503,error.getMessage());}
    }
    protected void doGet(HttpServletRequest request,HttpServletResponse response)throws IOException{
        File file;try{file=AvSyncManager.media(request.getPathInfo());}catch(IOException error){response.sendError(404);return;}
        response.setContentType(file.getName().endsWith(".m3u8")?"application/vnd.apple.mpegurl":"video/mp2t");response.setHeader("Cache-Control","no-store");response.setHeader("X-Content-Type-Options","nosniff");
        response.setContentLengthLong(file.length());Files.copy(file.toPath(),response.getOutputStream());
    }
}
