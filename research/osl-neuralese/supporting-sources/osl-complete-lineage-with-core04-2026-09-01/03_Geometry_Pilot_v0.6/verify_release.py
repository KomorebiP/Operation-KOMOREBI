#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

EXCLUDED={'SHA256SUMS.txt','SHA256SUMS.txt.sha256'}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def canonical_digest(obj):
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def main():
 root=Path(__file__).resolve().parent
 manifest=root/'SHA256SUMS.txt'
 companion=root/'SHA256SUMS.txt.sha256'
 lines=[x for x in manifest.read_text().splitlines() if x.strip()]
 expected={}
 for line in lines:
  d,rel=line.split('  ',1); expected[rel]=d
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() not in EXCLUDED and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and p.suffix not in {'.pyc','.pyo'}}
 checks={
  'companion_matches':companion.read_text().split()[0]==sha(manifest),
  'file_set_exact':actual==set(expected),
 }
 for rel,d in expected.items():
  p=root/rel;checks[f'sha::{rel}']=p.is_file() and sha(p)==d
 freeze=json.loads((root/'PREOUTCOME_FREEZE.json').read_text());unsigned=dict(freeze);fd=unsigned.pop('digest')
 checks['freeze_digest']=canonical_digest(unsigned)==fd
 analysis=json.loads((root/'results/PILOT_ANALYSIS.json').read_text());unsigned=dict(analysis);ad=unsigned.pop('digest')
 checks['frozen_analysis_digest']=canonical_digest(unsigned)==ad
 final=json.loads((root/'results/FINAL_ADJUDICATION.json').read_text());unsigned=dict(final);jd=unsigned.pop('digest')
 checks['final_adjudication_digest']=canonical_digest(unsigned)==jd
 checks['deterministic_recheck']=json.loads((root/'results/DETERMINISTIC_RECHECK.json').read_text())['exact_metric_replay']
 checks['checkpoint_count']=len(list((root/'checkpoints').glob('*.pt')))==9
 result={
  'schema':'osl.emergence.release-verification.v1',
  'entry_count':len(expected),
  'manifest_sha256':sha(manifest),
  'all_checks_pass':all(checks.values()),
  'failed_checks':sorted(k for k,v in checks.items() if not v),
 }
 print(json.dumps(result,indent=2,sort_keys=True))
 return 0 if result['all_checks_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
