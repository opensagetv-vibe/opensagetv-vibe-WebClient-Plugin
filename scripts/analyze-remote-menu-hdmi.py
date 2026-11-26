#!/usr/bin/env python3
"""Review the fixed SageMC main-menu green highlight in an owned HDMI capture.

No arbitrary screenshot classifier, source edit or calibrated latency claim.
Capture startup is not a synchronized input clock. Review representative frames.
"""
import argparse,json,subprocess,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);a=p.parse_args()
path=a.report.resolve();base=(ROOT/'artifacts/active/WEB-037').resolve()
if not path.is_relative_to(base):p.error('Require owning WEB037 report')
report=json.loads(path.read_text(encoding='utf-8'));video=Path(report['video']).resolve()
if video.parent!=base or not report.get('deliveryAndCaptureCompleted'):p.error('Require completed owned HDMI capture')
ffmpeg=tomllib.loads((BRIDGE/'config/toolbox.local.toml').read_text(encoding='utf-8'))['capture']['ffmpeg']
result=subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-i',str(video),'-an','-vf','scale=320:180',
                       '-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,timeout=25,check=True)
data=result.stdout;size=320*180*3
if len(data)%size:raise RuntimeError('Incomplete decoded frame')
states=[]
for frame in range(len(data)//size):
    b=data[frame*size:(frame+1)*size];scores=[]
    for center in (49,61,73,85,99,112):
        score=0
        for y in range(center-4,center+5):
            for x in range(90,205):
                r,g,blue=b[(y*320+x)*3:(y*320+x)*3+3]
                if r>60 and g>r*1.04 and g>blue*1.4:score+=1
        scores.append(score)
    state=scores.index(max(scores)) if max(scores)>200 else None
    states.append(state)
# Two consecutive frames reject transition/fade noise. Native capture is30fps.
transitions=[];previous=None
for index,state in enumerate(states[:-1]):
    if state is not None and state==states[index+1] and state!=previous:
        transitions.append({'captureTimeSeconds':round(index/30,3),'row':state})
        previous=state
observed=[r['row'] for r in transitions];expected=[0,1,2,3,2,1,0]
output={'physicalHDMI':True,'downscaledAnalysisOnly':True,'frames':len(states),
        'expectedRows':expected,'observedRows':observed,'transitions':transitions,
        'allSixSelectionsVisible':observed==expected,'calibratedInputToPhoton':False,
        'timingBoundary':'Capture startup and key submissions are not synchronized; no exact WAN latency inferred'}
destination=path.with_name(path.stem+'-analysis.json')
destination.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps(output))
raise SystemExit(0 if output['allSixSelectionsVisible'] else 1)
