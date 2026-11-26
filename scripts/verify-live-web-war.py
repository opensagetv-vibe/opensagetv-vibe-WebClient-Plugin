#!/usr/bin/env python3
"""Read-only hash comparison of the normal-manager-owned stock232 Web WAR."""
import hashlib,importlib.util,json,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
expected=hashlib.sha256((ROOT/'dist/SageTVWebPlayer.war').read_bytes()).hexdigest()
with C.ssh(cfg) as client:
    command='docker exec '+shlex.quote(cfg['unraid_container_name'])+' sha256sum /opt/sagetv/server/jetty/webapps/SageTVWebPlayer.war'
    actual=C.remote(client,command).split()[0]
matched=actual==expected
print(json.dumps(dict(passed=matched,liveWarSha256=actual,expectedWarSha256=expected,readOnly=True)))
raise SystemExit(0 if matched else 1)
