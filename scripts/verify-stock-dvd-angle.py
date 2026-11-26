#!/usr/bin/env python3
"""Read-only pinned upstream VM angle capability, not playback acceptance.

Disassemble the canonical staged stock JAR without extracting, patching or
loading its classes into the running server. A changed JAR or method shape
must be investigated, not silently treated as the same limitation.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

EXPECTED = 'd76ded981b9bc51e25b9cec821b6abeb771b46c2996dc45e453349b5e703fcb0'


def angle_path(disassembly):
    marker = 'public synchronized boolean playControlEx(int, long, long, sage.dvd.pci_t);'
    if disassembly.count(marker) != 1:
        raise ValueError('Unknown public stock VM method shape')
    body = disassembly.split(marker, 1)[1]
    body = re.split(r'\n[ \t]+(?:public|protected|private) ', body, maxsplit=1)[0]
    table = re.search(r'lookupswitch\s*\{(.*?)\}', body, re.S)
    if not table:
        raise ValueError('Unknown stock VM dispatch table')
    branches = dict(re.findall(r'^\s*(\d+|default):\s*(\d+)\s*$', table.group(1), re.M))
    if '213' not in branches or 'default' not in branches:
        raise ValueError('Angle/default dispatch unavailable')
    instructions = {int(pc): (op, operand.strip()) for pc, op, operand in
                    re.findall(r'^[ \t]*(\d+):[ \t]+([a-z][a-z0-9_]*)[ \t]*([^\r\n]*)', body, re.M)}
    start = int(branches['213'])
    default = int(branches['default'])
    instruction = instructions.get(start)
    tail = [(pc, *instructions[pc]) for pc in sorted(instructions) if pc >= default]
    noop = instruction == ('goto', str(default)) and [i[1:] for i in tail] == [('iconst_0', ''), ('ireturn', '')]
    return dict(angleControl=213, branchOffset=start, defaultOffset=default,
                angleInstruction=instruction, defaultInstructions=tail,
                angleIsNoOpReturningFalse=noop)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, default=Path('/workspace/container/artifacts/stock/server/Sage.jar'))
    args = parser.parse_args()
    jar = args.jar.resolve(strict=True)
    digest = hashlib.sha256(jar.read_bytes()).hexdigest()
    if digest != EXPECTED:
        raise RuntimeError('Pinned stock9.2.17 JAR hash differs; do not infer this capability')
    result = subprocess.run(['javap', '-classpath', str(jar), '-c', 'sage.dvd.VM'],
                            check=True, capture_output=True, text=True, timeout=30)
    path = angle_path(result.stdout)
    print(json.dumps(dict(stockVersion='9.2.17', sageJarSha256=digest,
                          readOnly=True, physicalPlaybackProof=False, **path), indent=2))
    if not path['angleIsNoOpReturningFalse']:
        raise RuntimeError('Expected limitation not established; inspect changed dispatch')


if __name__ == '__main__':
    main()
