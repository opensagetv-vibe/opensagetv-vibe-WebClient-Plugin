#!/usr/bin/env python3
"""WEB-121 bounded, read-only existing-phone/source observation. No playback input."""
import argparse,json,runpy,time,uuid
from pathlib import Path
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seconds',type=int,default=150)
    p.add_argument('--producer',required=True)
    p.add_argument('--media-id',type=int,required=True)
    a=p.parse_args()
    if not 140<=a.seconds<=180 or len(a.producer)!=32 or not all(x in '0123456789abcdef' for x in a.producer):
        p.error('Require exact producer and bounded140..180-second observation')
    c=runpy.run_path(str(ROOT/'scripts/commission-mobile.py'));cfg=c['configuration']()
    out=ROOT/'artifacts/active/WEB-121';out.mkdir(parents=True,exist_ok=True)
    path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:8]+'-isolated-live.json')
    report={'passed':False,'scope':'Existing physical iPhone feedback and real tuner status; not HDMI visual proof',
        'producer':a.producer,'mediaId':a.media_id,'seconds':a.seconds,'samples':[]}
    began=time.monotonic()
    try:
        while True:
            history=c['request'](cfg,'/SageTVWebPlayer/api/support?action=streamHealth')
            owners=[o for o in history.get('sessions',[]) if o['session']==a.producer]
            if len(owners)!=1 or not owners[0]['samples']:raise RuntimeError('Exact producer history absent')
            s=owners[0]['samples'][-1]
            with urlopen('http://192.168.10.48/status.json',timeout=8) as response:tuners=json.load(response)
            row={'elapsed':round(time.monotonic()-began,2),'health':s,'tuners':tuners};report['samples'].append(row)
            if time.time()*1000-s['atMs']>10000:raise RuntimeError('Producer observation is stale')
            if s['mediaId']!=a.media_id or s['browserRevision']!='web121.4':raise RuntimeError('Source/revision changed')
            if not s['processAlive'] or not s['recording'] or s['browserEnded'] or s['intentPaused']:
                raise RuntimeError('Playback/source state changed; preserve it, never replay input')
            if s['browserFeedbackAgeMs']>5000:raise RuntimeError('No fresh phone feedback')
            by_name={t['Resource']:t for t in tuners}
            if by_name.get('tuner0',{}).get('VctNumber')!='2.1' or by_name.get('tuner3',{}).get('VctNumber')!='5.1':
                raise RuntimeError('Expected independent channels changed')
            if s['nativeTransportError']!='none' or s['inputError']!='none':raise RuntimeError('Transport/input error observed')
            if len(report['samples'])>1:
                old=report['samples'][-2]['health']
                if s['inputBytes']<=old['inputBytes'] or s['browserTimeMs']<=old['browserTimeMs']:
                    raise RuntimeError('Source or presented clock did not advance during observation')
            print(json.dumps({'elapsed':row['elapsed'],'sourceBytes':s['inputBytes'],'browserMs':s['browserTimeMs'],
                'bufferMs':s['bufferAheadMs'],'recoveries':s['browserRecoveryAttempts']}),flush=True)
            if time.monotonic()-began>=a.seconds:break
            time.sleep(min(15,a.seconds-(time.monotonic()-began)))
        first=report['samples'][0]['health'];last=report['samples'][-1]['health']
        if last['browserRecoveryAttempts']!=first['browserRecoveryAttempts']:raise RuntimeError('Recovery count increased')
        if last['browserTimeMs']-first['browserTimeMs']<(a.seconds-15)*1000:raise RuntimeError('Phone clock advanced too little')
        report['passed']=True
    except Exception as error:
        report['error']=str(error)[:400]
        raise
    finally:
        report['elapsed']=round(time.monotonic()-began,2)
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'passed':report['passed'],'report':str(path.relative_to(ROOT))}),flush=True)

if __name__=='__main__':main()
