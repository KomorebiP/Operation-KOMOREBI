#!/usr/bin/env python3
"""Bind a passing fresh compiler/kernel audit to its frozen production sources."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parent
PACKAGE=ROOT.parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while block:=f.read(1024*1024):h.update(block)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);a=p.parse_args()
 attempt=ROOT/a.attempt;v=json.loads((attempt/'verification.json').read_text())
 assert v['status']=='PASS',v.get('failure')
 assert v['production_module_count']==75 and v['negative_controls']==9
 assert v['replay_exact_name_match'] and v['replay_starting_environment_excludes_project_modules']
 assert v['unreviewed_runtime_helpers']==[]
 manifest=ROOT/'FINAL_PRODUCTION_MANIFEST.json';rows=json.loads(manifest.read_text())
 assert len(rows)==75 and sha(manifest)==v['manifest_sha256']
 owned=json.loads((attempt/'owned_declarations.json').read_text())
 replay=json.loads((attempt/'replayed_constants.json').read_text())
 assert len(owned)==v['owned_total'] and len(replay)==v['logical_checked_count']
 for row in rows:
  assert sha(PACKAGE/'formal/current'/row['source'])==row['source_sha256'],row['source']
 prior=[]
 for f in sorted(ROOT.glob('attempt*/verification.json')):
  x=json.loads(f.read_text());prior.append({'attempt':f.parent.name,'status':x['status'],
   'failure':x.get('failure'),'verification_sha256':sha(f)})
 files={str(f.relative_to(PACKAGE)):sha(f) for f in [manifest,attempt/'verification.json',
  attempt/'owned_declarations.json',attempt/'replayed_constants.json',
  attempt/'generated_runtime_helper_inventory.json',attempt/'upstream_duplicate_body_rechecks.json']}
 summary={'schema':'komorebi.paper-ii.closeout-verification/1','status':'PASS',
  'successful_attempt':a.attempt,'production_modules':75,'baseline_modules':62,'new_modules':13,
  'owned_declarations':v['owned_total'],'logical_declarations_replayed':v['logical_checked_count'],
  'runtime_only_helpers':v['owned_runtime_only'],'unreviewed_runtime_helpers':[],
  'negative_controls':9,'axioms':v['axioms'],'elapsed_seconds':v['elapsed_seconds'],
  'max_rss_kib':v['max_rss_kib'],'flags':v['flags'],'frozen_manifest_sha256':sha(manifest),
  'owned_declarations_by_module':dict(sorted(Counter(x['module'] for x in owned).items())),
  'exact_source_owned_name_match':True,'kernel_replay_starts_without_project_modules':True,
  'attempts':prior,'evidence_sha256':files,
  'limits':v['limits'],'manuscript_correspondence':'Separate semantic review and proof-scope map required.'}
 (ROOT/'FINAL_VERIFICATION_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k not in ['owned_declarations_by_module','evidence_sha256','limits']},indent=2))
if __name__=='__main__':main()
