package org.opensagetv.webplayer;

import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicInteger;

/** Local injected-provider boundaries, not physical browser/image proof. */
public final class SharedSourcePreviewSmoke {
    static final String TOKEN="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    static int checks;
    static void check(boolean value,String label){if(!value)throw new AssertionError(label);checks++;}
    static SharedSourcePreview.Reply json(String text){return new SharedSourcePreview.Reply(200,text.getBytes(StandardCharsets.UTF_8),"application/json",null);}
    static byte[] jpeg(){return new byte[]{-1,-40,-1,-64,0,11,8,0,108,0,-64,1,1,17,0,-1,-39};}
    public static void main(String[] args)throws Exception{
        AtomicInteger reserves=new AtomicInteger(),images=new AtomicInteger(),retired=new AtomicInteger();
        SharedSourcePreview preview=new SharedSourcePreview((method,path)->{
            if(path.equals("/v1/capabilities"))return json("{\"mimDirect\":{\"contractVersion\":1,\"available\":true,\"sourcePreviewLeaseRevision\":1}}");
            check(method.equals("POST"),"All preview mutations use POST");
            check(!path.contains("/v1/direct/start"),"No extra playback producer");
            if(path.startsWith("/v1/previews/reserve?source=%2Fknown%2F")){reserves.incrementAndGet();return json("{\"previewToken\":\""+TOKEN+"\"}");}
            if(path.startsWith("/v1/previews/image?previewToken="+TOKEN)){images.incrementAndGet();return new SharedSourcePreview.Reply(200,jpeg(),"image/jpeg","40000");}
            if(path.startsWith("/v1/previews/teardown?")){retired.incrementAndGet();return json("{}");}
            throw new AssertionError("Unexpected provider operation");
        });
        SharedSourcePreview.Image first=preview.image("source-a","/known/recording.ts",42000,()->true);
        check(first!=null&&first.positionMs==40000,"Actual source bucket, not requested exact frame");
        check(preview.image("source-a","/known/recording.ts",43000,()->true)!=null&&reserves.get()==1&&images.get()==2,"Reuse bounded read-only lease");
        check(preview.image("source-a","/known/recording.ts",0,()->false)==null,"Stale source never requests I/O");
        preview.reset();long until=System.nanoTime()+2000000000L;while(retired.get()==0&&System.nanoTime()<until)Thread.sleep(5);
        check(retired.get()==1,"Retire only owned read-only lease on reset");
        AtomicInteger calls=new AtomicInteger();
        SharedSourcePreview absent=new SharedSourcePreview((method,path)->{calls.incrementAndGet();return json("{\"mimDirect\":{\"available\":true,\"contractVersion\":1}}");});
        check(absent.image("source","/known/file",0,()->true)==null&&calls.get()==1,"Old provider does not reserve/play/seek");
        check(absent.image("source","/known/file",-1,()->true)==null&&calls.get()==1,"Reject invalid position before I/O");
        check(SharedSourcePreview.boundedJpeg(jpeg()),"Qualified JPEG dimensions accepted");
        byte[] wrong=jpeg();wrong[10]=1;check(!SharedSourcePreview.boundedJpeg(wrong),"Unexpected dimensions refused without decoding pixels");
        check(!SharedSourcePreview.boundedJpeg(new byte[32769]),"Byte limit before decode");
        final SharedSourcePreview[] changed={null};AtomicInteger leaked=new AtomicInteger();
        changed[0]=new SharedSourcePreview((method,path)->{
            if(path.equals("/v1/capabilities"))return json("{\"mimDirect\":{\"sourcePreviewLeaseRevision\":1,\"available\":true,\"contractVersion\":1}}");
            if(path.startsWith("/v1/previews/reserve")){changed[0].reset();return json("{\"previewToken\":\""+TOKEN+"\"}");}
            if(path.startsWith("/v1/previews/teardown")){leaked.incrementAndGet();return json("{}");}
            throw new AssertionError("Retired source requested an image");
        });
        check(changed[0].image("old","/known/file",0,()->true)==null&&leaked.get()==1,"Late reservation is retired, never attached to a different source");
        System.out.println(checks+" shared preview checks PASS");
    }
}
