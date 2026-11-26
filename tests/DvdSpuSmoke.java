package org.opensagetv.webplayer;
import java.util.*;
import java.util.concurrent.*;
/** P09 pure-core SPU vector, palette/highlight, stream-disable and generation smoke. */
public final class DvdSpuSmoke{
 static int pass; public static void main(String[]a)throws Exception{core();session();selection();history();concurrency();geometry();System.out.println("DvdSpuSmoke PASS "+pass+"/6");}
 static void geometry()throws Exception{
  // INIT0/1 chooses monitor aspect, not the authored television standard.
  for(int aspect:new int[]{0,1})for(int height:new int[]{480,576})for(int split=1;split<7;split++){
   DvdNativeSession dvd=new DvdNativeSession();dvd.init(aspect);dvd.setNewCell(new byte[]{0,0,0,4,0,0,0,0});
   byte[] header=new byte[]{0,0,1,(byte)0xb3,0x2d,(byte)(height>>>8),(byte)height};
   dvd.push(push(Arrays.copyOfRange(header,0,split)));dvd.push(push(Arrays.copyOfRange(header,split,header.length)));
   truth(dvd.subtitleCanvasHeight()==height,"split sequence raster, aspect="+aspect+", height="+height+", split="+split);
   dvd.flush();truth(dvd.subtitleCanvasHeight()==height,"cell FLUSH preserves authored grid");
   dvd.setNewCell(new byte[]{0,0,0,4,0,0,0,0});dvd.spu().select(0);
   dvd.push(push(pes(0x20,packet())));dvd.spu().presentAt(1000L);
   boolean image=false;for(SubtitleCue c:dvd.spu().queue().drainDue(dvd.spu().token(),Long.MAX_VALUE,256))if(c.payload.length>0){image=true;truth(c.canvasHeight==height&&c.canvasWidth==720,"emitted SPU uses authored standard");}
   truth(image,"actual composed SPU geometry witness");
   dvd.init(aspect);truth(dvd.subtitleCanvasHeight()==480,"new source never reuses previous PAL geometry");dvd.close();
  }
  DvdPsInspector p=new DvdPsInspector();DvdPtsClock c=new DvdPtsClock();
  p.observe(new byte[]{0,0,1,(byte)0xb3,0x2d,2,0x40},0,7,c);
  p.observe(new byte[]{0,0,1,(byte)0xb3,0,0,0},0,7,c);
  truth(p.subtitleCanvasHeight()==576,"invalid sequence size does not corrupt known standard");
  pass++;
 }
 static void history()throws Exception{
  DvdNativeSession dvd=new DvdNativeSession();dvd.init(0);dvd.setNewCell(new byte[]{0,0,0,4,0,0,0,0});dvd.spu().select(0x80);
  dvd.push(push(pes(0x20,packet(),90_000L)));dvd.push(push(pes(0x20,packet(),21L*90_000L)));
  dvd.clock().setServerStc45k(1500L*45L);dvd.spu().select(0x40);
  List<SubtitleCue> shown=dvd.spu().queue().drainDue(dvd.spu().token(),1500L,256);
  truth(shown.size()==1&&shown.get(0).payload.length>0,"late enable selects current history, never future read-ahead");
  dvd.spu().presentAt(1500L);truth(dvd.spu().queue().size()==0,"same presented frame is not repeated");
  dvd.spu().presentAt(21_000L);int pending=dvd.spu().queue().size();dvd.spu().select(0x40);
  truth(pending>0&&dvd.spu().queue().size()==pending,"repeated NAV selection cannot erase pending subtitle");
  for(int i=0;i<300;i++)dvd.push(push(pes(0x20,packet(),(22L+i)*90_000L)));
  truth(dvd.spu().json().contains("\"historyFrames\":256"),"history count bounded");
  long generation=dvd.generation();dvd.flush();truth(dvd.spu().json().contains("\"historyFrames\":0"),"flush retires history");
  int pendingAfterFlush=dvd.spu().queue().size();truth(!dvd.spu().presentAt(generation,1500L)&&dvd.spu().queue().size()==pendingAfterFlush,"retired HLS reader cannot recompose or clear replacement");dvd.close();pass++;
 }
 static void selection()throws Exception{
  for(int selected:new int[]{0,0x20,0x40,0x41,62,8192,0x80,0xc0,-1,256}){
   DvdNativeSession dvd=new DvdNativeSession();dvd.init(0);dvd.setNewCell(new byte[]{0,0,0,4,0,0,0,0});
   dvd.spu().select(selected);dvd.spu().queue().clearAll();
   int physical=selected==0x41?0x21:0x20;dvd.push(push(pes(physical,packet())));dvd.spu().presentAt(1000L);
   boolean image=false;for(SubtitleCue cue:dvd.spu().queue().drainDue(dvd.spu().token(),Long.MAX_VALUE,256))if(cue.payload.length>0)image=true;
   truth(image==(selected==0||selected==0x20||selected==0x40||selected==0x41),"stock slot/HD flag selection "+selected);
   dvd.spu().select(0x80);for(SubtitleCue cue:dvd.spu().queue().drainDue(dvd.spu().token(),Long.MAX_VALUE,256))truth(cue.payload.length==0,"Off never recomposes previous bitmap");
   dvd.close();
  }
  pass++;
 }
 static void core()throws Exception{DvdSpuCore.Diagnostics d=new DvdSpuCore.Diagnostics();DvdSpuCore.Assembler as=new DvdSpuCore.Assembler(d);DvdSpuCore.Decoder de=new DvdSpuCore.Decoder(d);byte[] p=packet();List<DvdSpuCore.Packet> q=as.feed(new DvdSpuCore.Packet(0x20,90000,Arrays.copyOfRange(p,0,7)));truth(q.isEmpty(),"fragment waits");q=as.feed(new DvdSpuCore.Packet(0x20,-1,Arrays.copyOfRange(p,7,p.length)));truth(q.size()==1,"reassembled");List<DvdSpuCore.Frame> f=de.decode(q.get(0));truth(f.size()==1&&f.get(0).w==1&&f.get(0).h==1,"decoded 1x1");int[] clut=new int[16];clut[3]=0x00EB8080;DvdSpuCore.Argb normal=DvdSpuCore.compose(f.get(0),clut,true,DvdSpuCore.Highlight.hidden());truth(normal.rgba.length==4&&(normal.rgba[3]&255)>0,"rgba alpha");DvdSpuCore.Highlight hi=new DvdSpuCore.Highlight(true,10,10,10,10,0xF000F000);DvdSpuCore.Argb h=DvdSpuCore.compose(f.get(0),clut,true,hi);truth(h.rgba.length==4,"highlight compose");pass++;}
 static void session()throws Exception{DvdNativeSession dvd=new DvdNativeSession();dvd.init(0);byte[] nc=new byte[8];writeInt(nc,0,4);writeInt(nc,4,0);dvd.setNewCell(nc);dvd.spu().select(62);dvd.spu().queue().clearAll();byte[] ps=pes(0x20,packet());dvd.push(push(ps));dvd.spu().queue().clearAll();byte[] ctl=new byte[24];writeInt(ctl,0,20);writeInt(ctl,4,10);writeInt(ctl,8,10);writeInt(ctl,12,10);writeInt(ctl,16,10);writeInt(ctl,20,0xF000F000);dvd.setSpuControl(ctl);truth(dvd.spu().queue().size()>0,"menu highlight visible while subtitles off");long g=dvd.generation();dvd.flush();truth(dvd.generation()!=g,"flush generation");dvd.close();pass++;}
 static void concurrency()throws Exception{DvdNativeSession dvd=new DvdNativeSession();dvd.init(0);dvd.setNewCell(new byte[]{0,0,0,4,0,0,0,0});byte[] p=pes(0x20,packet());ExecutorService e=Executors.newFixedThreadPool(2);try{Future<?> writer=e.submit(()->{try{for(int i=0;i<200;i++)dvd.push(push(p));}catch(Exception x){throw new RuntimeException(x);}});Future<?> reader=e.submit(()->{for(int i=0;i<200;i++)dvd.spu().json();});writer.get(5,TimeUnit.SECONDS);reader.get(5,TimeUnit.SECONDS);}finally{e.shutdownNow();dvd.close();}pass++;}
 static byte[] packet(){byte[] a=new byte[29];a[0]=0;a[1]=29;a[2]=0;a[3]=5;a[4]=0x70;int p=5;a[p++]=0;a[p++]=0;a[p++]=0;a[p++]=5;a[p++]=1;a[p++]=3;a[p++]=0x32;a[p++]=0x10;a[p++]=4;a[p++]=(byte)0xff;a[p++]=(byte)0xff;a[p++]=5;a[p++]=0;a[p++]=(byte)0xa0;a[p++]=10;a[p++]=0;a[p++]=(byte)0xa0;a[p++]=10;a[p++]=6;a[p++]=0;a[p++]=4;a[p++]=0;a[p++]=4;a[p++]=(byte)0xff;return a;}
 static byte[] pes(int sub,byte[] spu){return pes(sub,spu,90000L);}
 static byte[] pes(int sub,byte[] spu,long pts){int n=9+5+1+spu.length,plen=n-6;byte[] p=new byte[n];p[0]=0;p[1]=0;p[2]=1;p[3]=(byte)0xbd;p[4]=(byte)(plen>>>8);p[5]=(byte)plen;p[6]=(byte)0x80;p[7]=(byte)0x80;p[8]=5;p[9]=(byte)(0x20|(((pts>>30)&7)<<1)|1);p[10]=(byte)(pts>>22);p[11]=(byte)((((pts>>15)&127)<<1)|1);p[12]=(byte)(pts>>7);p[13]=(byte)(((pts&127)<<1)|1);p[14]=(byte)sub;System.arraycopy(spu,0,p,15,spu.length);return p;}
 static byte[] push(byte[] p){byte[] b=new byte[p.length+8];writeInt(b,0,p.length);writeInt(b,4,0);System.arraycopy(p,0,b,8,p.length);return b;} static void writeInt(byte[]b,int o,int v){b[o]=(byte)(v>>>24);b[o+1]=(byte)(v>>>16);b[o+2]=(byte)(v>>>8);b[o+3]=(byte)v;}static void truth(boolean x,String m){if(!x)throw new AssertionError(m);}
}
