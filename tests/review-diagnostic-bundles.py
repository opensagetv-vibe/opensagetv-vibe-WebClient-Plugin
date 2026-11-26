#!/usr/bin/env python3
"""Read-only payload-free sensitive-field audit of owned WP14 test bundles."""
import argparse,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--task',choices=('WP14-006','WEB-103'),default='WP14-006')
parser.add_argument('--retired',action='store_true',help='Read the already-owned recoverable archive path; no move/write')
args=parser.parse_args()
count=0;violations=[]
def scan(value):
 global count
 if isinstance(value,dict):
  for key,child in value.items():
   if re.search('authorization|password|cookie|token|secret|crypto',key,re.I):
    count+=1
    if child not in (None,False,'','[redacted]','[omitted]') and not isinstance(child,(bool,int,float)):
     violations.append(key)
   scan(child)
 elif isinstance(value,list):
  for child in value:scan(child)
 elif isinstance(value,str) and value[:1] in ('{','['):
  try:parsed=json.loads(value)
  except (ValueError,RecursionError):return
  if isinstance(parsed,(dict,list)):scan(parsed)
directory=ROOT/'artifacts/active'/args.task
if args.retired:directory=ROOT.parents[1]/'deleteme'/directory.relative_to(ROOT.parents[1])
files=list(directory.glob('*.zip'))
if not files:raise SystemExit('No owned reports to review')
for path in files:
 with zipfile.ZipFile(path) as archive:
  if archive.getinfo('report.json').file_size>12*1024*1024:raise SystemExit('Report exceeds bound')
  scan(json.loads(archive.read('report.json')))
print(json.dumps({'reports':len(files),'sensitiveNamedFieldsReviewed':count,'nonRedactedSensitiveFieldNames':sorted(set(violations))}))
raise SystemExit(1 if violations else 0)
