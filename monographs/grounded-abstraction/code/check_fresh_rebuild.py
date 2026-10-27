"""Rebuild a temporary source copy and compare texts and exact scientific outputs.

This is a same-environment reproducibility check, not independent verification.
The shipped PDF assets are reused; figure regeneration is a separate command.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = 'Grounded_Abstraction_v1.0.0.pdf'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    out = ROOT/'validation'
    source = ROOT/'Grounded_Abstraction_v1.0.0.tex'
    original_source_hash = digest(source)
    steps = []
    with tempfile.TemporaryDirectory(prefix='grounded-abstraction-rebuild-') as temp:
        fresh = Path(temp)/ROOT.name
        shutil.copytree(ROOT, fresh, ignore=shutil.ignore_patterns('build','__pycache__','*.pyc','SHA256SUMS.json'))
        (fresh/PDF).unlink(missing_ok=True)
        for i, (argv, limit) in enumerate([
            (['bash','build.sh'], 30),
            ([sys.executable,'code/audit_manuscript.py'], 20),
            ([sys.executable,'code/run_checks.py'], 45),
            ([sys.executable,'code/pdf_preflight.py'], 20),
            ([sys.executable,'code/verify_release.py','--receipt-only'], 20),
        ],1):
            begin=time.perf_counter()
            cp=subprocess.run(argv,cwd=fresh,text=True,capture_output=True,timeout=limit,check=False)
            log=f'validation/fresh_step_{i}.log'
            (ROOT/log).write_text(cp.stdout+cp.stderr,encoding='utf-8')
            steps.append({'argv':argv,'wall_limit_seconds':limit,'exit_status':cp.returncode,
                          'runtime_seconds':time.perf_counter()-begin,'log':log})
            if cp.returncode:
                raise RuntimeError(f'Fresh command failed; see {log}')
        with fitz.open(ROOT/PDF) as a, fitz.open(fresh/PDF) as b:
            if len(a)!=len(b):
                raise AssertionError('Fresh PDF page count changed')
            page_checks=[{'page':i+1,'text_equal':a[i].get_text()==b[i].get_text()}
                         for i in range(len(a))]
        if not all(p['text_equal'] for p in page_checks):
            raise AssertionError('Fresh PDF text changed')
        science=[]
        for name in ('validation/exact_checks.json','validation/observable_checks.json','validation/quantitative_checks.json',
                     'validation/aggregate_checks.json','validation/preservation.json',
                     'validation/source_audit.json','data/illustrations.json',
                     'data/observable_illustrations.json','data/quantitative_illustrations.json','STATEMENT_INDEX.json'):
            left=json.loads((ROOT/name).read_text());right=json.loads((fresh/name).read_text())
            ignored=[]
            if name in ('validation/exact_checks.json','validation/observable_checks.json','validation/quantitative_checks.json'):
                for obj in (left,right): obj.pop('runtime_seconds',None)
                ignored=['runtime_seconds']
            equal=left==right
            science.append({'path':name,'equal':equal,'excluded_fields':ignored})
            if not equal:raise AssertionError('Scientific result changed: '+name)
        if digest(source)!=original_source_hash:raise AssertionError('Original source changed during fresh rebuild')
        result={'status':'PASS','started_at':started,'runtime_seconds':time.perf_counter()-t0,
                'source_sha256':original_source_hash,'original_pdf_sha256':digest(ROOT/PDF),
                'fresh_pdf_sha256':digest(fresh/PDF),'page_count':len(page_checks),
                'page_text_checks':page_checks,'scientific_checks':science,'commands':steps,
                'limits':['Same environment and supplied figure assets, not independent or cross-platform replication.',
                          'Only explicitly listed timing fields are excluded from scientific equality.',
                          'PDF binary identity is not required. Windows and tagged accessibility were not tested.']}
    (out/'fresh_rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: clean rebuild; {len(page_checks)} pages have identical extracted text; {len(science)} scientific files match.')

if __name__=='__main__':main()
