#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, time
from pathlib import Path

root = Path(__file__).resolve().parents[3]
block05 = root / 'blocks' / 'Block05'
scripts = []
for block in ('Block01','Block02','Block03','Block04'):
    scripts.extend(sorted((root/'blocks'/block).glob('verify_*.py')))
records=[]
overall=True
for script in scripts:
    rel=str(script.relative_to(root))
    start=time.perf_counter()
    try:
        cp=subprocess.run(
            [sys.executable, script.name],
            cwd=script.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=240,
            check=False,
        )
        status='PASS' if cp.returncode==0 else 'FAIL'
        rc=cp.returncode
        output=cp.stdout
    except subprocess.TimeoutExpired as exc:
        status='TIMEOUT'
        rc=None
        output=(exc.stdout or '') + (exc.stderr or '')
    elapsed=time.perf_counter()-start
    overall &= status=='PASS'
    log_name=rel.replace('/','__').replace('.py','.log')
    (block05/'logs'/log_name).write_text(output or '',encoding='utf-8')
    records.append({'script':rel,'status':status,'returncode':rc,'runtime_seconds':elapsed,'log':f'logs/{log_name}'})
    print(f'{status:7s} {elapsed:8.3f}s {rel}')
result={
    'schema_version':1,
    'status':'PASS' if overall else 'FAIL',
    'python':sys.version,
    'scripts':records,
    'count':len(records),
}
(block05/'results'/'predecessor_replay.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
raise SystemExit(0 if overall else 1)
