#!/usr/bin/env python3
"""Rerun all expected-invalid files, excluding setup errors and timeouts."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys,json,re,hashlib
root=Path(__file__).resolve().parents[1];rd=root/'results/v0.28.0'
def one(f):
    log=f'results/v0.28.0/negative_{f.stem}.log'
    rp=(root/log).with_suffix('.json')
    if rp.exists() and (root/log).exists():
        cached=json.loads(rp.read_text())
        if (cached.get('source_sha256')==hashlib.sha256(f.read_bytes()).hexdigest()
            and cached.get('source_unchanged') and cached.get('imports_unchanged')
            and cached.get('log_sha256')==hashlib.sha256((root/log).read_bytes()).hexdigest()
            and not cached.get('timed_out')):
            txt=(root/log).read_text()
            bad=bool(re.search(r'object file .*does not exist|unknown module|failed to locate application|unknown identifier',txt))
            cached['file']=str(f.relative_to(root))
            cached['expected_rejection']=cached['returncode']!=0 and not bad and 'error' in txt
            return cached
    subprocess.run([sys.executable,str(root/'tools/lean_one.py'),str(f.relative_to(root)),
        '--seconds','40','--no-output','--log',log],cwd=root,stdout=subprocess.DEVNULL,check=False)
    r=json.loads((root/log).with_suffix('.json').read_text());txt=(root/log).read_text()
    setup=bool(re.search(r'object file .*does not exist|unknown module|failed to locate application|unknown identifier',txt))
    r['file']=str(f.relative_to(root));r['expected_rejection']=r['returncode']!=0 and not r['timed_out'] and not setup and 'error' in txt
    return r
with ThreadPoolExecutor(max_workers=3) as ex:
    rows=list(ex.map(one,sorted((root/'tests/negative').glob('*.lean'))))
(rd/'negative_summary.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(dict(tested=len(rows),rejected=sum(r['expected_rejection'] for r in rows),failures=[r['file'] for r in rows if not r['expected_rejection']]),indent=2))
sys.exit(0 if all(r['expected_rejection'] for r in rows) else 1)
