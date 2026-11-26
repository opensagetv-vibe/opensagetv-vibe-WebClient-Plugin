#!/usr/bin/env python3
"""Guarded exact test-container restart; stock bytes are verified, not changed.
Standing user authority covers232 only. No recording/client interruption."""
import argparse,hashlib,importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
if cfg['unraid_container_name']!='sagetv-vibe-server-u26-gpu-j11':raise SystemExit('Exact stock232 test container only')
parser=argparse.ArgumentParser()
parser.add_argument('--mcp-self-update-bootstrap',action='store_true',help='Standing232 exception ONLY for the exact locally-built pending MCP self-update; pre-restart activity remains UNKNOWN')
args=parser.parse_args()
try:before=C.activity(cfg)
except Exception:
 if not args.mcp_self_update_bootstrap:raise
 before=None
if before is not None and not before.get('safeToRestart'):raise SystemExit('Recording/client activity blocks restart')
with C.ssh(cfg) as ssh:
 name=shlex.quote(cfg['unraid_container_name'])
 if before is None:
  owner=ROOT.parent/'opensagetv-vibe-core-MCP-Plugin'
  if not owner.is_dir():owner=ROOT.parent/'core-mcp-plugin'
  expected=hashlib.sha256((owner/'dist/OpenSageTVVibeCoreMCPPlugin.jar').read_bytes()).hexdigest()
  pending=C.remote(ssh,'docker exec '+name+" find /opt/sagetv/server/JARs -maxdepth 1 -type f -name 'OpenSageTVVibeCoreMCPPlugin.jar*' -exec sha256sum {} +")
  if not any(line.split()[0]==expected for line in pending.splitlines()):raise SystemExit('Exact pending MCP self-update not verified; bootstrap refused')
 verify='docker exec -w /opt/sagetv/server '+name+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256'
 protectedBefore=C.remote(ssh,verify).count(': OK')
 if before is not None and not C.activity(cfg).get('safeToRestart'):raise SystemExit('Activity changed before restart')
 C.remote(ssh,'docker restart --time 20 '+name)
 deadline=time.monotonic()+120
 while True:
  try:
   after=C.activity(cfg)
   if not after.get('ok'):raise RuntimeError('Not ready')
   break
  except Exception:
   if time.monotonic()>deadline:raise
   time.sleep(2)
 protectedAfter=C.remote(ssh,verify).count(': OK')
 if protectedAfter!=protectedBefore:raise RuntimeError('Protected inventory changed')
 print(json.dumps({'recordingCountBefore':before['recordingCount'] if before else 'UNKNOWN','clientsBefore':before['connectedClientCount'] if before else 'UNKNOWN',
  'uiBefore':before['uiContextCount'] if before else 'UNKNOWN','restartAuthority':'standing-user-stock232' if before else 'standing232-missing-MCP-self-update-bootstrap','protectedBefore':protectedBefore,
  'protectedAfter':protectedAfter,'after':after},indent=2))
