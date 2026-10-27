from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(1<<20):h.update(b)
    return h.hexdigest()

def main():
    manifest=json.loads((ROOT/'package_manifest.json').read_text())
    failures=[]
    for rel,meta in manifest['files'].items():
        p=ROOT/rel
        if not p.is_file():failures.append(f"missing:{rel}");continue
        if p.stat().st_size!=meta['size_bytes']:failures.append(f"size:{rel}")
        if sha(p)!=meta['sha256']:failures.append(f"sha:{rel}")
    if failures:raise SystemExit('BLOCK23_PACKAGE_INVALID '+','.join(failures[:20]))
    result=json.loads((ROOT/'results'/'block23_final.json').read_text())
    if not result['summary']['all_correct'] or result['summary']['certificate_accuracy']!=1.0:
        raise SystemExit('BLOCK23_CANONICAL_RESULT_INVALID')
    status=json.loads((ROOT/'external_status'/'preflight.json').read_text())
    if status['real_checkpoint_executed']:
        raise SystemExit('BLOCK23_FALSE_EXTERNAL_EXECUTION_FLAG')
    print('SRIC_BLOCK23_PACKAGE_VALID')
    print(f"manifest_files={len(manifest['files'])}")
    print(f"result_receipt={result['result_receipt']}")
    print(f"external_status={status['status']}")
if __name__=='__main__':main()
