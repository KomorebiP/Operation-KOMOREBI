#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(__file__).resolve().parent
hashes=json.loads((root/'SOURCE_HASHES.json').read_text())
for relative,expected in hashes.items():
    with (root/relative).open('rb') as stream:
        actual=hashlib.file_digest(stream,'sha256').hexdigest()
    if actual!=expected: raise SystemExit('Hash mismatch: '+relative)
evidence=json.loads((root/'stationary_separation/CURRENT_EVIDENCE.json').read_text())
for run in evidence['current_runs']:
    result=subprocess.run([sys.executable,str(root/'audit_helpers/validate_manifest.py'),
       str(root/run['manifest']),'--root',str(root/run['execution_root'])],
       capture_output=True,text=True)
    if result.returncode: raise SystemExit(result.stdout+result.stderr)
print(str(len(hashes))+' files and '+str(len(evidence['current_runs']))+' current manifests verified.')
