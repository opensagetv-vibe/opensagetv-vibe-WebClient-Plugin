package org.opensagetv.webplayer;
import java.lang.reflect.Proxy;
import java.util.*;
import javax.servlet.http.*;

/** WEB-121 cache policy only; not proof a physical page loaded a revision. */
public final class ShellCachePolicySmoke {
    public static void main(String[] args)throws Exception{
        int count=0;
        for(String path:Arrays.asList("/","/miniclient.html","/client.html","/index.html","/sw.js","/manifest.webmanifest","/js/miniclient.js","/js/miniclient-playback.js","/js/miniclient-app.js","/js/atsc-captions.js","/css/miniclient.css","/hls/owner/seg_00001.ts","/api/hls","/vendor/hls.js","/icons/icon-192.png")){
            Map<String,String> headers=new HashMap<String,String>();boolean[] called={false};
            HttpServletRequest req=(HttpServletRequest)Proxy.newProxyInstance(ShellCachePolicySmoke.class.getClassLoader(),new Class<?>[]{HttpServletRequest.class},(o,m,a)->m.getName().equals("getServletPath")?path:null);
            HttpServletResponse res=(HttpServletResponse)Proxy.newProxyInstance(ShellCachePolicySmoke.class.getClassLoader(),new Class<?>[]{HttpServletResponse.class},(o,m,a)->{if(m.getName().equals("setHeader"))headers.put((String)a[0],(String)a[1]);return null;});
            new SecurityHeadersFilter().doFilter(req,res,(r,s)->called[0]=true);
            boolean shell=!path.startsWith("/hls/")&&!path.startsWith("/api/")&&!path.startsWith("/vendor/")&&!path.startsWith("/icons/");
            if(shell?!"private, no-cache, must-revalidate".equals(headers.get("Cache-Control")):headers.containsKey("Cache-Control"))throw new AssertionError("Wrong shell cache policy: "+path);
            if(!called[0]||!"nosniff".equals(headers.get("X-Content-Type-Options")))throw new AssertionError("Existing chain/header changed");
            count++;
        }
        System.out.println("Shell cache policy: "+count+" PASS");
    }
}
