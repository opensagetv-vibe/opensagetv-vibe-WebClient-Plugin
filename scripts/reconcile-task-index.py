#!/usr/bin/env python3
"""Audit the historical WP mirror against canonical TASKS, never create PASS.

Default/read-only prints proposed status corrections. --write is explicit.
Checkboxes, acceptance text, evidence and source files are never changed.
"""
import argparse,copy,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def reconcile(source,index):
    found={};matches=list(re.finditer(r'^- \[([ x*\-])\] (?:\*\*)?(WP\d{2}-\d{3})\b',source,re.M));removed=set();flagged=set()
    for i,m in enumerate(matches):
        key=m[2]
        if key in found:raise ValueError('Duplicate canonical ID '+key)
        block=source[m.end():matches[i+1].start() if i+1<len(matches) else len(source)]
        status=re.search(r'\*\*(?:Status|Current\d{4}-\d{2}-\d{2})[^\n]*?:\*\*\s*([A-Z][A-Z0-9_]*)',block)
        found[key]=(m[1]=='x',status[1] if status else None)
        if m[1]=='-':
            if not status or status[1]!='REMOVED_USER_REQUEST':
                raise ValueError('Removed canonical ID needs explicit user-request status '+key)
            removed.add(key)
        if m[1]=='*':
            if not status or status[1]!='POSSIBLY_FIXED_NOT_REPEATABLE':
                raise ValueError('Starred canonical ID needs explicit non-repeatable status '+key)
            flagged.add(key)
    result=copy.deepcopy(index);changes=[];indexed=[]
    for phase in result['phases']:
        checked=[]
        for task in phase['tasks']:
            key=task['id'];indexed.append(key)
            if key not in found:raise ValueError('Missing canonical ID '+key)
            done,declared=found[key];checked.append(done or key in removed);old=task['status'];new=old
            if key in removed:new='REMOVED_USER_REQUEST'
            elif key in flagged:new='POSSIBLY_FIXED_NOT_REPEATABLE'
            elif declared=='UNAVAILABLE_STOCK_CONTRACT':new=declared
            elif old=='AWAITING_SEPARATE_APPROVAL' and not (done and declared=='COMPLETE_STOCK_ALTERNATIVE'):pass
            elif done:
                if declared=='COMPLETE_STOCK_ALTERNATIVE':new=declared
                elif not (old=='DONE' or old.startswith('COMPLETE')):new='COMPLETE_LOCAL'
            elif declared in ('PASS_LOCAL','PASS_LOCAL_AT_P07_BOUNDARY','IMPLEMENTED_AWAITING_FIELD','COMPLETE_LOCAL',
                              'PARTIAL_AVAILABLE_FIELD','QUALIFIED_AVAILABLE_LINUX_SCOPE',
                              'BLOCKED_BASELINE_ARTIFACT','AWAITING_PUBLICATION_APPROVAL','UNAVAILABLE_STOCK_CONTRACT'):
                new='PASS_LOCAL' if declared=='COMPLETE_LOCAL' else declared
            if new!=old:task['status']=new;changes.append(dict(id=key,before=old,after=new))
        if phase.get('scope')=='optional':continue
        old=phase.get('status');new=old
        remaining=[t for t in phase['tasks'] if not found[t['id']][0] and t['id'] not in removed]
        if remaining and all(t['id'] in flagged for t in remaining):
            new='QUALIFIED_SCOPE_WITH_FLAGGED_OBSERVATIONS'
        elif remaining and all(t['status']=='AWAITING_PUBLICATION_APPROVAL' for t in remaining):
            new='AWAITING_PUBLICATION_APPROVAL'
        elif all(checked) and any(task['id'] in removed for task in phase['tasks']):
            new='CLOSED_WITH_USER_WAIVERS'
        elif all(checked):
            if old and ('NOT_STARTED' in old or 'PENDING' in old or old.startswith(('IN_PROGRESS','IMPLEMENTED')) or old=='QUALIFIED_SCOPE_WITH_FLAGGED_OBSERVATIONS'):
                new='COMPLETE_CANONICAL_SCOPE'
        elif remaining and old and (old.startswith(('COMPLETE','CLOSED')) or old=='QUALIFIED_SCOPE_WITH_FLAGGED_OBSERVATIONS'):
            new='IMPLEMENTED_LOCAL_AWAITING_FIELD'
        elif old=='NOT_STARTED' and any(t['status']!='PLANNED' for t in phase['tasks']):new='IMPLEMENTED_LOCAL_AWAITING_FIELD'
        if old!=new:phase['status']=new;changes.append(dict(id=phase['id'],before=old,after=new))
    if len(indexed)!=len(set(indexed)):raise ValueError('Duplicate mirror ID')
    extra=set(found)-set(indexed)
    if extra:raise ValueError('Canonical IDs missing from mirror: '+','.join(sorted(extra)))
    if 'progress' in result:
        progress={'completed':sum(done for done,_ in found.values()),'total':len(found)}
        if removed:progress['removed']=len(removed)
        if flagged:progress['flagged']=len(flagged)
        if result['progress']!=progress:
            changes.append(dict(id='progress',before=result['progress'],after=progress))
            result['progress']=progress
    if 'next_task' in result:
        pending=[task['id'] for phase in result['phases'] if phase.get('scope')!='optional'
                 for task in phase['tasks'] if not found[task['id']][0] and task['id'] not in removed and task['id'] not in flagged]
        next_task=pending[0] if pending else None
        if result['next_task']!=next_task:
            changes.append(dict(id='next_task',before=result['next_task'],after=next_task))
            result['next_task']=next_task
    return result,changes
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    path=ROOT/'docs/parity/TASK_INDEX.json';source=(ROOT/'TASKS.md').read_text(encoding='utf-8')
    current=json.loads(path.read_text(encoding='utf-8'));result,changes=reconcile(source,current)
    if a.write:path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(canonical='TASKS.md',readOnly=not a.write,changes=changes,changedAcceptanceOrCheckboxes=False),indent=2))
    raise SystemExit(1 if changes and not a.write else 0)
if __name__=='__main__':main()
