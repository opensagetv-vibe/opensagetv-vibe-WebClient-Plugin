#!/usr/bin/env python3
"""Add a scoped current checklist resolution without rewriting pinned evidence.

Default is read-only. --write updates only current_resolution fields. A checked
target is not a universal field PASS; optional, superseded and platform-only
entries retain their original classification and reason.
"""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def reconcile(source, ledger):
    tasks = {}; removed = set(); flagged = set()
    for match in re.finditer(r'^- \[([ x*\-])\] (?:\*\*)?(WP\d{2}-\d{3})\b', source, re.M):
        if match[2] in tasks:
            raise ValueError('Duplicate canonical ID ' + match[2])
        tasks[match[2]] = match[1] == 'x'
        if match[1] == '-': removed.add(match[2])
        if match[1] == '*': flagged.add(match[2])
    result = copy.deepcopy(ledger)
    seen = set()
    for entry in result['entries']:
        key = entry['id']
        if key in seen:
            raise ValueError('Duplicate upstream ID ' + key)
        seen.add(key)
        targets = entry['target_task_ids']
        if not targets or any(t not in tasks for t in targets):
            raise ValueError('Missing canonical target for ' + key)
        complete = [t for t in targets if tasks[t]]
        waived = [t for t in targets if t in removed]
        observations = [t for t in targets if t in flagged]
        pending = [t for t in targets if not tasks[t] and t not in removed and t not in flagged]
        category = entry['category']
        if category in ('not_applicable', 'superseded', 'optional_core'):
            state = {'not_applicable': 'NOT_APPLICABLE_RETAIN_REASON',
                     'superseded': 'SUPERSEDED_RETAIN_REASON',
                     'optional_core': 'OPTIONAL_NOT_AUTHORIZED'}[category]
        elif not pending and observations:
            state = 'TARGET_TASKS_WITH_FLAGGED_OBSERVATIONS'
        elif not pending and waived:
            state = 'TARGET_TASKS_CLOSED_WITH_USER_WAIVERS'
        elif not pending:
            state = 'TARGET_TASKS_COMPLETE_SCOPED'
        elif complete or waived or observations:
            state = 'TARGET_TASKS_PARTIAL'
        else:
            state = 'TARGET_TASKS_OPEN'
        entry['current_resolution'] = {
            'state': state, 'completed_targets': complete, 'open_targets': pending,
            'evidence': ['TASKS.md#checklist-change-ledger', 'docs/parity/TASK_INDEX.json'],
            'boundary': 'Canonical target-task scope only; inspect its dated evidence. '
                        'No inferred physical, all-device, all-service or WAN PASS.'}
        if waived:
            entry['current_resolution']['removed_targets'] = waived
            entry['current_resolution']['boundary'] += ' Removed by user request, not PASS.'
        if observations:
            entry['current_resolution']['flagged_targets'] = observations
            entry['current_resolution']['boundary'] += ' Starred: possibly fixed, not repeatable on current build; not a proven correction or active retest queue.'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'docs/parity/UPSTREAM_FIX_LEDGER.json'
    current = json.loads(path.read_text(encoding='utf-8'))
    result = reconcile((ROOT / 'TASKS.md').read_text(encoding='utf-8'), current)
    changes = [e['id'] for e, old in zip(result['entries'], current['entries']) if e != old]
    if args.write:
        result['current_resolution_date'] = datetime.now(timezone.utc).date().isoformat()
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    counts = {}
    for entry in result['entries']:
        state = entry['current_resolution']['state']
        counts[state] = counts.get(state, 0) + 1
    print(json.dumps({'readOnly': not args.write, 'entries': len(result['entries']),
                      'changedIds': changes, 'resolutionCounts': counts,
                      'changedPinnedStatusOrReason': False}, indent=2))
    return 1 if changes and not args.write else 0


if __name__ == '__main__':
    raise SystemExit(main())
