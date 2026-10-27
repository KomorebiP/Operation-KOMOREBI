#!/usr/bin/env python3
"""Verify saved source/object correspondence without invoking Lean.

Integrity and provenance only: reading an old axiom report is not a fresh kernel check.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect():
 saved=json.loads((ROOT/'editorial_evidence/UPSTREAM_HASHES.json').read_text())
 failures=[p for p,h in saved.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
 if failures:raise RuntimeError('Preserved files differ: '+repr(failures[:5]))
 base=ROOT/'original_releases/residue_counting';latest=ROOT/'current_continuation'
 manifest=json.loads((base/'manifest.json').read_text());base_rows=manifest['predecessor_sources']+manifest['modules_in_build_order']
 for row in base_rows:
  n=row['module']
  for folder,suffix,key in [('lean','.lean','source_sha256'),('build','.olean','olean_sha256')]:
   if sha(base/folder/'PaperX'/(n+suffix))!=row[key]:raise RuntimeError('Predecessor receipt mismatch: '+n)
  if (latest/'lean/PaperX'/(n+'.lean')).read_bytes()!=(base/'lean/PaperX'/(n+'.lean')).read_bytes():raise RuntimeError('Changed common source: '+n)
 v=json.loads((latest/'verification/CLAIM91_CONTINUATION_VERIFICATION.json').read_text())
 if set(v['source_sha256'])!=set(v['object_sha256']):raise RuntimeError('Receipt source/object sets differ.')
 for n,h in v['source_sha256'].items():
  if sha(latest/'lean/PaperX'/(n+'.lean'))!=h:raise RuntimeError('Latest source mismatch: '+n)
  if sha(latest/'checked_objects/PaperX'/(n+'.olean'))!=v['object_sha256'][n]:raise RuntimeError('Latest object mismatch: '+n)
 for n,code in v['strict_compile_exit_codes'].items():
  p=latest/'verification/final_logs'/(n+'.exit')
  if code!=0 or int(p.read_text().strip())!=0:raise RuntimeError('Nonzero saved final exit: '+n)
 text=(latest/'verification/audit/axiom_report.log').read_text()
 audits=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",text)
 if not audits:raise RuntimeError('No saved named axiom reports.')
 found={a.strip() for _,g in audits for a in g.split(',') if a.strip()}
 if not found<={'propext','Classical.choice','Quot.sound'}:raise RuntimeError('Unexpected saved axiom: '+repr(found))
 names=[p.stem for p in (latest/'lean/PaperX').glob('*.lean')]
 if set(names)!={r['module'] for r in base_rows}|set(v['source_sha256']):raise RuntimeError('Cumulative source set differs.')
 return {'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'Preserved file hashes and saved Lean receipt correspondence only. Lean was not invoked.',
  'unchanged_upstream_files':len(saved),'predecessor_source_object_pairs':len(base_rows),'latest_source_object_pairs':len(v['source_sha256']),
  'unchanged_shared_source_files':len(base_rows),'cumulative_current_sources':len(names),'saved_final_exit_records_verified':len(v['strict_compile_exit_codes']),
  'saved_named_axiom_records_read':len(audits),'saved_axioms':sorted(found),'current_ledger':v['claim_ledger'],
  'compiler_invoked':False,'note':'Old replay_residues.py belongs to the residue-counting layout. The latest source overlay retains that old script but stores only its 16 new objects. No new full-cumulative Lean launcher is asserted here.'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path);a=ap.parse_args();r=inspect()
 if a.output:
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':
 try:main()
 except (RuntimeError,OSError,ValueError) as e:raise SystemExit(str(e)) from e
