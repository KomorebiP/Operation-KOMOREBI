#!/usr/bin/env python3
"""Read-only local pinned-runtime inventory; this never downloads or builds Lean."""
from __future__ import annotations
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
def main():
 project=HERE.parents[1]
 roots=['/workspace','/opt','/root','/usr/local','/usr/bin','/tmp']
 argv=['find',*roots,'-type','f','(','-name','lean','-o','-name','lake','-o','-name','elan',')','-print']
 r=subprocess.run(argv,capture_output=True,text=True,timeout=60)
 found=r.stdout.splitlines()
 original_kit=Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2')
 pins=json.loads((project/'source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/formal_release/RUNTIME_DEPENDENCY_PINS.json').read_text())
 report={'started_utc':datetime.now(timezone.utc).isoformat(),'scope':'Available local executable inventory, no network requests or dependency installation; not a compiler replay.',
  'python_version':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),
  'path_executables':{x:shutil.which(x) for x in ('lean','lake','elan')},'targeted_search_roots':roots,
  'search_argv':argv,'search_exit_code':r.returncode,'found_runtime_executables':found,'search_stderr':r.stderr,
  'documented_inherited_kit':str(original_kit),'documented_kit_present':original_kit.is_dir(),
  'required_lean_version':'4.34.0-rc2','required_lean_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d',
  'required_lean_binary_sha256':'e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550',
  'required_dependency_records':pins,'fresh_lean_replay':False,
  'status':'LOCAL_PINNED_RUNTIME_NOT_FOUND' if not found and not original_kit.is_dir() else 'CANDIDATE_RUNTIME_REQUIRES_PIN_VALIDATION',
  'limits':['The search establishes absence in the listed accessible roots and PATH, not a universal filesystem or account inventory.',
  'Compiled project .olean objects in the source package do not supply the compiler or pinned Mathlib cache.',
  'No fresh build, new axiom report, negative control, or final consumer compilation was run.',
  'No multi-gigabyte kit download was attempted; source instructions explicitly require a separately installed pinned kit.'],
  'prospective_memory_safety':{'threads':1,'MALLOC_ARENA_MAX':'2','address_space_limit_bytes':4294967296,
   'linux_wsl_ulimit_v_kib':4194304,'note':'Caller must enforce the memory limit; inherited verify.py does not set RLIMIT_AS itself.'}}
 out=project/'verification/lean';out.mkdir(parents=True,exist_ok=True)
 (out/'ENVIRONMENT_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'runtime_search.stdout.txt').write_text(r.stdout)
 (out/'runtime_search.stderr.txt').write_text(r.stderr)
 print(json.dumps({k:report[k] for k in ('status','fresh_lean_replay','found_runtime_executables','documented_kit_present')},indent=2))
 return 0
if __name__=='__main__':sys.exit(main())
