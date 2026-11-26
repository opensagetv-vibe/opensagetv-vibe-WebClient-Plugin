package org.opensagetv.webplayer;
public final class BufferAdaptiveBridgeSmoke {
 public static void main(String[] args)throws Exception{
  if(!BufferAdaptiveBridge.available())throw new AssertionError("new provider not negotiated");
  BufferAdaptiveBridge policy=new BufferAdaptiveBridge(1000,4000,false);
  String result=policy.report(1,500,false,true,true,4000);
  if(!result.contains("\"minimumKbps\":1000")||!result.contains("\"maximumKbps\":4000")||!result.contains("\"targetKbps\":0"))throw new AssertionError(result);
  policy.epoch();
  StreamOptions adjusted=StreamOptions.fromRequest(k->"stream_adaptiveQuality".equals(k)?"true":"stream_adaptiveMinimumKbps".equals(k)?"1000":"stream_videoKbps".equals(k)?"4000":null);
  if(!adjusted.adaptiveQuality||!adjusted.player.equals("hls")||adjusted.videoKbps!=4000||adjusted.adaptiveMinimumKbps!=1000)throw new AssertionError("start range/delivery");
  StreamOptions fixed=StreamOptions.defaults();if(fixed.adaptiveQuality||fixed.videoKbps!=8000)throw new AssertionError("Fixed default changed");
  try{StreamOptions.fromRequest(k->"stream_adaptiveMinimumKbps".equals(k)?"9000":null);throw new AssertionError("invalid range admitted");}catch(IllegalArgumentException expected){}
  System.out.println("PASS Web uses actual shared MIM class; startup range/HLS normalization, Fixed maximum and bad-range refusal");
 }
}
