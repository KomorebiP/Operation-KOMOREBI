#!/usr/bin/env python3
"""Rebuild the editorial synthesis and readers; check the new examples only."""
from __future__ import annotations
import datetime, hashlib, json, platform, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def hashes():
    paths=[ROOT/'SOURCE_CATALOG.json']
    for folder,patterns in [('code',['*.py']),('editorial',['*.tex']),('figures',['*.pdf','*.svg','*.png']),('sources',['*.pdf'])]:
        for pattern in patterns:paths.extend((ROOT/folder).glob(pattern))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
def main():
    before=hashes();start=datetime.datetime.now(datetime.timezone.utc).isoformat();records=[]
    commands=[([sys.executable,'code/check_connections.py'],ROOT)]
    commands += [(['pdflatex','-interaction=nonstopmode','-halt-on-error','connected_synthesis.tex'],ROOT/'editorial')]*3
    commands += [([sys.executable,'code/assemble.py'],ROOT),([sys.executable,'code/validate_assembly.py'],ROOT)]
    logs=ROOT/'validation'/'rebuild_logs';logs.mkdir(parents=True,exist_ok=True)
    for i,(argv,cwd) in enumerate(commands,1):
        t=time.perf_counter();log=logs/f'{i:02}.log'
        with log.open('w') as f:
            try:proc=subprocess.run(argv,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=60,check=False);rc=proc.returncode
            except subprocess.TimeoutExpired:rc=124
        records.append({'argv':argv,'cwd':str(cwd.relative_to(ROOT)) or '.','timeout_seconds':60,'exit_status':rc,'elapsed_seconds':time.perf_counter()-t,'log':str(log.relative_to(ROOT)),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
        print(i,argv[0],rc,round(records[-1]['elapsed_seconds'],3),flush=True)
        if rc:break
    after=hashes();ok=before==after and len(records)==len(commands) and all(r['exit_status']==0 for r in records)
    rec={'status':'PASS' if ok else 'FAIL','scope':'New connecting examples, editorial LaTeX compilation, source-page assembly and navigation. No original scientific suite or Lean run.','started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'commands':records,'input_hashes_before':before,'input_hashes_after':after,'inputs_unchanged':before==after,'limits':'60-second wall timeout per command. No separately imposed memory or CPU cap. No independent external attestation.'}
    (ROOT/'validation/build_receipt.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
    if not ok:raise SystemExit(1)
if __name__=='__main__':main()
