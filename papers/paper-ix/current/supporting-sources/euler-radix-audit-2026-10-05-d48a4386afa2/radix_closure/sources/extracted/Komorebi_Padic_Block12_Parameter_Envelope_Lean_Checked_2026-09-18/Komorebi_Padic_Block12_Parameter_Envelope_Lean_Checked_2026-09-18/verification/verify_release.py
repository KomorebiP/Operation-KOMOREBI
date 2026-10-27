#!/usr/bin/env python3
"""Read-only focused-release integrity verifier for Block 12."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess
from pathlib import Path

def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--json-out',type=Path);args=ap.parse_args();root=args.root.resolve()
 checks=[];failures=[]
 def check(name,ok,**detail):
  rec={'name':name,'passed':bool(ok),**detail};checks.append(rec)
  if not ok:failures.append(rec)
 required=['START_HERE.md','CONTINUE_HERE.md','PROOF_BOUNDARY.md','LEAN_STATUS.md','BLOCK12_THEOREM_INDEX.md','THEOREM_NOTE.md','COMPUTATION_CONTRACT.md','COMPUTATION_MANIFEST.json','COMPUTATION_MANIFEST.sha256','RUN_METADATA.json','FOCUSED_ARCHIVE_INFO.json','FOCUSED_MANIFEST.txt','CHECKSUMS.sha256','results/BUILD_VERIFICATION_BLOCK12.json','results/static_source_audit_block12.json','results/axiom_audit_block12.json','results/kernel_controls_block12.json','results/lean_parameter_envelope_vectors.json','results/parameter_envelope_audit.json','lean/KomorebiPadic/RepresentativeBudgetParameterEnvelope.lean','predecessor/PREDECESSOR_COMPLETE_VERIFICATION.json','predecessor/PREDECESSOR_BLOCK11_VERIFICATION.json']
 for rel in required:check('required:'+rel,(root/rel).is_file())
 def load(rel):return json.loads((root/rel).read_text())
 try:
  source=load('results/static_source_audit_block12.json');axioms=load('results/axiom_audit_block12.json');controls=load('results/kernel_controls_block12.json');vectors=load('results/lean_parameter_envelope_vectors.json');finite=load('results/parameter_envelope_audit.json');build=load('results/BUILD_VERIFICATION_BLOCK12.json');predc=load('predecessor/PREDECESSOR_COMPLETE_VERIFICATION.json');predf=load('predecessor/PREDECESSOR_BLOCK11_VERIFICATION.json');manifest=load('COMPUTATION_MANIFEST.json')
 except Exception as exc:
  check('load_results',False,error=repr(exc));source=axioms=controls=vectors=finite=build=predc=predf=manifest={}
 check('source_audit',source.get('status')=='PASS')
 check('production_files',source.get('lean_file_count')==19,observed=source.get('lean_file_count'))
 check('theorem_count',source.get('block12_theorem_count')==179,observed=source.get('block12_theorem_count'))
 check('predecessor_theorems',source.get('predecessor_theorem_count')==165,observed=source.get('predecessor_theorem_count'))
 check('new_theorems',len(source.get('added_theorems',[]))==14,observed=len(source.get('added_theorems',[])))
 check('predecessor_statement_preservation',not source.get('changed_predecessor_theorem_statements') and not source.get('missing_predecessor_theorems'))
 check('no_placeholders_or_local_axioms',not source.get('placeholder_or_axiom_violations'))
 check('axiom_audit',axioms.get('status')=='PASS' and axioms.get('theorem_count')==179 and not axioms.get('unexpected_axioms'))
 check('negative_controls',controls.get('status')=='PASS')
 check('new_vectors',vectors.get('status')=='PASS' and vectors.get('file_count')==10 and vectors.get('example_count')==1080)
 check('finite_audit',finite.get('status')=='PASS' and finite.get('failure_count')==0 and finite.get('total_recorded_checks_and_cases')==15794336)
 check('build_receipt',build.get('status')=='PASS')
 check('clean_build_jobs',build.get('clean_build',{}).get('jobs')==1162,observed=build.get('clean_build',{}).get('jobs'))
 check('compiled_receipt',build.get('lean',{}).get('compiled_olean_ilean_artifacts')==38,observed=build.get('lean',{}).get('compiled_olean_ilean_artifacts'))
 check('cumulative_vectors',build.get('lean',{}).get('cumulative_native_decide_examples')==8158,observed=build.get('lean',{}).get('cumulative_native_decide_examples'))
 check('cumulative_finite',build.get('computation',{}).get('cumulative_recorded_exact_checks_and_cases')==139968119,observed=build.get('computation',{}).get('cumulative_recorded_exact_checks_and_cases'))
 check('predecessor_complete',predc.get('status')=='PASS')
 check('predecessor_focused',predf.get('status')=='PASS')
 bad=[]
 for rel,expected in manifest.get('sha256',{}).items():
  path=root/rel
  if not path.is_file():bad.append({'path':rel,'reason':'missing'});continue
  observed=sha256(path)
  if observed!=expected:bad.append({'path':rel,'reason':'hash','expected':expected,'observed':observed})
 check('computation_manifest_hashes',not bad,finding_count=len(bad),findings=bad[:20])
 detached=root/'COMPUTATION_MANIFEST.sha256'
 if detached.is_file():
  proc=subprocess.run(['sha256sum','-c',detached.name],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  check('computation_manifest_detached_hash',proc.returncode==0,output=proc.stdout[-1000:])
 compiled=list((root/'compiled_rc2').rglob('*.olean'))+list((root/'compiled_rc2').rglob('*.ilean'))
 check('compiled_artifacts',len(compiled)==38,observed=len(compiled))
 vfiles=sorted((root/'verification').glob('LeanParameter*Vector_[0-9][0-9].lean'))
 vcount=sum(len(re.findall(r'^example\b',p.read_text(),re.MULTILINE)) for p in vfiles)
 check('vector_files',len(vfiles)==10,observed=len(vfiles));check('vector_examples',vcount==1080,observed=vcount)
 forbidden=[]
 for path in sorted((root/'lean').rglob('*.lean')):
  text=path.read_text()
  for token,pat in {'sorry':r'\bsorry\b','admit':r'\badmit\b','axiom':r'^\s*axiom\s+'}.items():
   if re.search(pat,text,re.MULTILINE):forbidden.append({'path':str(path.relative_to(root)),'token':token})
 check('no_forbidden_production_tokens',not forbidden,findings=forbidden)
 check('no_embedded_lake',not (root/'.lake').exists())
 manifest_file=root/'FOCUSED_MANIFEST.txt'
 if manifest_file.is_file():
  entries=[x for x in manifest_file.read_text().splitlines() if x.strip()]
  missing=[x for x in entries if not (root/x).exists()]
  check('focused_manifest_entries_exist',not missing,entry_count=len(entries),missing=missing[:20])
 ledger=root/'CHECKSUMS.sha256'
 if ledger.is_file():
  proc=subprocess.run(['sha256sum','-c',ledger.name],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  check('checksum_ledger',proc.returncode==0,tail=proc.stdout[-4000:])
 report={'schema':'komorebi-padic-block12-release-integrity-v1','status':'PASS' if not failures else 'FAIL','root':str(root),'check_count':len(checks),'failure_count':len(failures),'failures':failures,'checks':checks}
 text=json.dumps(report,indent=2,sort_keys=True)+'\n'
 if args.json_out:args.json_out.parent.mkdir(parents=True,exist_ok=True);args.json_out.write_text(text)
 print(text,end='');return 0 if not failures else 1
if __name__=='__main__':raise SystemExit(main())
