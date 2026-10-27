#!/usr/bin/env python3
"""Replay current source preservation, corpus arithmetic and model comparisons."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(exist_ok=True,parents=True);c=ROOT/'verification/monograph_checks'
 prior=json.loads((c/'RETRIEVED_INTEGRITY.json').read_text());rows=prior['source_inventory'];assert len(rows)==1062
 for row in rows:
  f=ROOT/row['path'];assert f.stat().st_size==row['bytes'] and sha(f)==row['sha256'],row['path']
 archives=[]
 for row in prior['archives']:
  f=ROOT/row['path'];assert sha(f)==row['sha256'];branch='complete' if f.name.startswith('Paper_VIII_Complete') else 'strengthened'
  with zipfile.ZipFile(f) as z:
   payload=[q for q in z.namelist() if not q.endswith('/')];assert len(payload)==row['payload_files']
   for q in payload:assert z.read(q)==(ROOT/'source'/branch/q).read_bytes(),q
   archives.append({'path':row['path'],'sha256':sha(f),'payload_files':len(payload),'all_members_match':True})
 foundation=ROOT/'source/complete/Paper_VIII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot/formalization/QuantumPacketCore.lean';reference=c/'Paper_VII_QuantumPacketCore_reference.lean';assert foundation.read_bytes()==reference.read_bytes()
 # Compare generator output with the two explicitly documented layout repairs.
 gen=c/'run_vectors_20261009_final_vectors/generated_graphics';ed=ROOT/'editable/visual_guide/graphics';vector=[]
 edits={'complex_core.tex':('at (0,3) {$A^*A=', 'at (0,3.4) {$A^*A='),'quantization.tex':('at (0,2.7) {actual error sum','at (0,3.2) {actual error sum')}
 for f in sorted(gen.glob('*.tex')):
  text=f.read_text();actual=(ed/f.name).read_text();change=edits.get(f.name)
  if change:
   assert text.count(change[0])==1 and actual==text.replace(*change),f.name
  else:assert actual==text,f.name
  vector.append({'name':f.name,'matches_original_except_documented_header_move':True,'generated_sha256':sha(f),'delivered_sha256':sha(ed/f.name),'header_coordinate_change':list(change) if change else None})
 assert len(vector)==30
 jobs=[('corpus','check_corpus_arithmetic.py',['--corpus',str(ROOT/'source/strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package/verification/benchmark_results_sanitized.json')]),('traditional_models','check_traditional_models.py',['--data',str(ROOT/'editable/traditional/monograph_data/exact_examples.json')])]
 results={}
 for name,script,args in jobs:
  q=out/(name+'.json');argv=[sys.executable,str(c/script),*args,'--out',str(q)];r=subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/(name+'.log')).write_text(r.stdout);print(r.stdout);assert r.returncode==0,(name,r.returncode);results[name]={'result':q.name,'sha256':sha(q),'argv':argv,'exit_code':r.returncode}
 report={'status':'PASS','source_inventory_files':1062,'source_hashes_match_retrieved_inventory':True,'archives':archives,'shared_foundation':{'current_sha256':sha(foundation),'previous_VII_reference_sha256':sha(reference),'bytes_identical':True,'origin_record_sha256':sha(c/'FOUNDATION_REFERENCE_ORIGIN.json')},'vector_plates':vector,'vector_original_exact_matches':28,'vector_header_moves_only':2,'subruns':results,'non_claims':['Raw source-byte preservation and finite-code replays do not authenticate compiler proofs or historical timings.','Historical outer manifest discrepancies are recorded from the retrieved baseline in RETRIEVED_INTEGRITY.json; no new mathematical discrepancy is inferred.']}
 (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS current auxiliary evidence')
if __name__=='__main__':main()
