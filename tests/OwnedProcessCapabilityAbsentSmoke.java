package org.opensagetv.webplayer;
import java.util.concurrent.TimeUnit;
/** Run on a provider-absent classpath: never attempt an unsafe legacy kill. */
public final class OwnedProcessCapabilityAbsentSmoke {
    public static void main(String[] args)throws Exception{
        if(OwnedProcessControlBridge.available())throw new AssertionError("provider unexpectedly present");
        Process process=new ProcessBuilder("/bin/sh","-c","exec sleep 10").start();
        try{
            if(OwnedProcessControlBridge.stop(process,100))throw new AssertionError("missing capability claimed stop");
            if(!process.isAlive())throw new AssertionError("missing capability mutated process");
            System.out.println("PASS absent provider declines boundedly without legacy process mutation");
        }finally{process.destroy();process.waitFor(2,TimeUnit.SECONDS);}
    }
}
