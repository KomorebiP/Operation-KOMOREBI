#!/usr/bin/env python3
"""Check stored corpus arithmetic without authenticating historical timings."""
from __future__ import annotations
import argparse,collections,hashlib,json,math
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=json.loads(a.corpus.read_text());rows=d['results'];assert len(rows)==154
 checked=[];unavailable=[];flops=[];fail=[]
 for i,row in enumerate(rows):
  t=row.get('median_ms');v=row.get('gflops_logical');work=row.get('logical_flops')
  if all(isinstance(x,(int,float)) for x in [t,v,work]) and t>0:
   expected=work/(t*1e6);ok=math.isclose(v,expected,rel_tol=1e-12,abs_tol=1e-12)
   flops.append({'row':i,'method':row['method'],'actual':v,'expected':expected,'pass':ok})
   if not ok:fail.append({'kind':'gflops','row':i})
  for baseline in ['cpu_dense','gpu_dense']:
   field='speedup_vs_'+baseline;value=row.get(field)
   if value is None:continue
   # Candidate methods and identities are taken from actual recorded fields.
   candidates=[(j,x) for j,x in enumerate(rows) if x.get('case_id')==row.get('case_id') and x.get('suite')==row.get('suite') and str(x.get('method','')).startswith(baseline) and x.get(field)==1.0]
   if len(candidates)!=1:
    unavailable.append({'row':i,'field':field,'stored_value':value,'candidate_baseline_rows':[j for j,_ in candidates],'reason':'No unique same-case recorded dense baseline with stored unit ratio; no replacement baseline invented.'});continue
   j,ref=candidates[0]
   expected=ref['median_ms']/t;ok=math.isclose(value,expected,rel_tol=1e-12,abs_tol=1e-12)
   checked.append({'row':i,'baseline_row':j,'field':field,'actual':value,'expected':expected,'pass':ok,'same_recorded_output_contract':row.get('output_contract')==ref.get('output_contract'),'output_contract':row.get('output_contract'),'baseline_output_contract':ref.get('output_contract'),'timing_scope':row.get('timing_scope'),'baseline_timing_scope':ref.get('timing_scope'),'scope':'Arithmetic only. A matching label does not authenticate same-device outputs, correctness reference, precision contract or timing execution.'})
   if not ok:fail.append({'kind':'ratio','row':i,'field':field})
 result={'status':'PASS' if not fail else 'ARITHMETIC_INCONSISTENCY','corpus_sha256':sha(a.corpus),'rows':154,'recorded_status_counts':dict(collections.Counter(x.get('status') for x in rows)),'ratio_fields_checked':len(checked),'ratio_fields_with_no_unique_recorded_baseline':len(unavailable),'gflops_fields_checked':len(flops),'tolerance':{'relative':1e-12,'absolute':1e-12},'failures':fail,'ratio_checks':checked,'unavailable_ratio_checks':unavailable,'gflops_checks':flops,'non_claims':['No new CPU or GPU timing.','The 154 historical rows label themselves measured; this audit does not authenticate measurements.','No actual same-device output or correctness-reference provenance recovered.','No equality of host/device timing scopes inferred.','Different output contracts and precisions can make an arithmetically correct ratio unsuitable as a speedup claim.']}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['ratio_checks','unavailable_ratio_checks','gflops_checks']},indent=2))
 if fail:raise SystemExit(1)
if __name__=='__main__':main()
