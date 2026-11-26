#!/usr/bin/env python3
"""Explicit metadata refresh via the existing bounded MCP availability action.
Does not install/enable any plugin, restart or modify the installed registry.
"""
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
result=C.request(C.configuration(),'/v1/control',{'action':'companion.available','refresh':'true'},mcp=True)
print(json.dumps({'metadataRefreshRequested':True,'ok':result.get('ok'),
                  'installationPerformed':False}))
