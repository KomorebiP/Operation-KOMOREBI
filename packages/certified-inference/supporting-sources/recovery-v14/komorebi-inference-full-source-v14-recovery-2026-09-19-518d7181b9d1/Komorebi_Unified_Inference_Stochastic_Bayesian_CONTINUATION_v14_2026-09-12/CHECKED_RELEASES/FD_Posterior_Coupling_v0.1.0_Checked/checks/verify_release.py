#!/usr/bin/env python3
"""Validate the sealed source/evidence package; optionally compare present runtime outputs.
This checks consistency and integrity, not theorem correctness independently of Lean.
"""
import argparse,hashlib,json,re
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',type=Path);a=ap.parse_args()
 r=Path(__file__).resolve().parents[1];rec=json.loads((r/'FINAL_VERIFICATION_RECEIPT.json').read_text())
 manifest=json.loads((r/'COMPUTATION_MANIFEST.json').read_text())
 for p in manifest['outputs']:assert sha(r/p['path'])==p['sha256'],p['path']
 for key in ['claim_id','command','mathematics','environment','outputs','result','checks']:assert manifest[key],key
 assert manifest['run']['exit_status']==0 and manifest['run']['runtime_seconds']>0
 decl=json.loads((r/'DECLARATIONS.json').read_text());ax=json.loads((r/'AXIOM_AUDIT.json').read_text())
 assert len(decl)==ax['audited_declarations']==len(ax['results'])
 assert {d['name'] for d in decl}==set(ax['results'])
 assert all(set(v)<=set(ax['allowed_axioms']) for v in ax['results'].values())
 assert sha(r/ax['log_path'])==ax['log_sha256']
 for d in rec['successful_final_modules']:
  p=r/'Komorebi'/(d['module']+'.lean');assert sha(p)==d['source_sha256_before']==d['source_sha256_after']==d['staged_source_sha256']
  assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',p.read_text()),p
  rd=r/d['receipt_path'];raw=json.loads(rd.read_text());assert raw['exit_status']==0 and raw['output_sha256']==d['output_sha256']
  assert sha(rd.with_suffix('.log'))==d['log_sha256'];assert sha(rd.with_suffix('.lean'))==sha(p)
  for dep,h in d['dependencies'].items():
   dn=dep.rsplit('.',1)[1];assert sha(r/'Komorebi'/(dn+'.lean'))==h['source_sha256']
  if a.runtime:
   out=a.runtime/'workspace/.lake/build/lib/lean/Komorebi'/(d['module']+'.olean')
   assert sha(out)==d['output_sha256'],out
 if (r/'MANIFEST_SHA256.txt').exists():
  for line in (r/'MANIFEST_SHA256.txt').read_text().splitlines():
   h,n=line.split('  ',1);assert sha(r/n)==h,n
 print('PASS:',rec['active_modules'],'final-source receipts;',len(decl),'axiom records; all sealed hashes match.')
if __name__=='__main__':main()
