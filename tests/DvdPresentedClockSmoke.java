package org.opensagetv.webplayer;

/** Actual A/V PTS, not read-ahead metadata or SPU, anchors a new decoder. */
public final class DvdPresentedClockSmoke {
    static void eq(long expected,long value,String why){if(expected!=value)throw new AssertionError(why+": "+value+" != "+expected);}
    public static void main(String[] args){
        DvdPtsClock c=new DvdPtsClock();
        c.setServerStc45k(0);c.updatePlayerClockMillis(0);c.updatePlayerClockMillis(5000);
        c.beginDiscontinuity();c.onNewCell(-24001);
        c.mapPesPts(20*90000L+48002);
        c.updatePlayerClockMillis(1000);
        eq(21000,c.currentMillis(),"chapter seek without fresh SETSTC must use new A/V origin plus presented time");
        c.onNewCell(-24001);c.mapPesPts(40*90000L+48002);
        c.updatePlayerClockMillis(2000);
        eq(22000,c.currentMillis(),"future read-ahead NEWCELL/PES cannot re-anchor current pictures");
        eq(23000,c.subtitlePresentationMillis(3000),"SPU clock uses current decoder origin");
        c.beginDiscontinuity();c.setServerStc45k(60000L*45);c.mapPesPts(60*90000L+48002);
        c.updatePlayerClockMillis(500);c.updatePlayerClockMillis(1500);
        eq(61000,c.currentMillis(),"fresh explicit STC remains authoritative");
        c.resetAll();c.onNewCell(-24001);c.mapPesPts(48000);c.updatePlayerClockMillis(1000);
        eq(1000,c.currentMillis(),"tiny negative first PTS clamps at zero rather than wrapping days");
        System.out.println("PASS new-decoder A/V origin, no-STC seek, read-ahead isolation, SPU projection, explicit STC and zero origin");
    }
}
