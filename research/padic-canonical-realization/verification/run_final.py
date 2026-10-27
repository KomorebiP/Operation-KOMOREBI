#!/usr/bin/env python3
"""Bounded fresh Block34 phases; no promotion from incomplete outputs."""
from pathlib import Path
import os,sys,json,subprocess,hashlib,time,datetime,shutil
ROOT=Path(__file__).resolve().parents[1];RESULTS=ROOT/'results';RESULTS.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
    files=[f for folder in ['lean','verification'] for f in (ROOT/folder).rglob('*')
      if f.is_file() and f.suffix in ['.lean','.py','.json'] and '__pycache__' not in f.parts]
    files += [ROOT/f for f in ['lakefile.lean','lake-manifest.json','lean-toolchain','PREDECESSOR_SOURCE_HASHES.json','PREDECESSOR_ARCHIVE.json','verify_release.py','validate_manifest.py']]
    return {str(f.relative_to(ROOT)):sha(f) for f in sorted(files)}
def main():
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    phases=[('parser_controls',[sys.executable,'verification/evidence_parser.py'],0,None),
      ('clean_build',['lake','build'],0,None),
      ('declared_axioms',['lake','env','lean','-DwarningAsError=true','verification/AllAxioms34.lean'],0,None),
      ('environment_axioms',['lake','env','lean','-DwarningAsError=true','verification/KernelAxiomInventory.lean'],0,None),
      ('examples',['lake','env','lean','-DwarningAsError=true','verification/ResidualChecks.lean'],0,None),
      ('universal',['lake','env','lean','-DwarningAsError=true','verification/ResidualUniversal.lean'],0,None),
      ('predecessor_examples',['lake','env','lean','-DwarningAsError=true','verification/ObservabilityChecks.lean'],0,None),
      ('positive',['lake','env','lean','-DwarningAsError=true','verification/PositiveControl.lean'],0,None),
      ('allword_negative',['lake','env','lean','-DwarningAsError=true','verification/FalseAllWord.lean'],1,'false'),
      ('minimum_negative',['lake','env','lean','-DwarningAsError=true','verification/FalseLinearMinimum.lean'],1,'false'),
      ('output_negative',['lake','env','lean','-DwarningAsError=true','verification/FalseIgnoreOutput.lean'],1,'false'),
      ('false_negative',['lake','env','lean','-DwarningAsError=true','verification/FalseControl.lean'],1,'false'),
      ('placeholder_negative',['lake','env','lean','-DwarningAsError=true','verification/PlaceholderControl.lean'],1,'sorry'),
      ('leanchecker',['lake','env','leanchecker','-v','KomorebiPadic.ResidualMinimalityExamples'],0,None),
      ('integer_audit',[sys.executable,'verification/audit_residual.py'],0,None),
      ('make_manifest',[sys.executable,'verification/make_manifest.py'],0,None),
      ('manifest_validation',[sys.executable,'validate_manifest.py','COMPUTATION_MANIFEST.json','--root','.'],0,None)]
    if (ROOT/'.lake/build').exists():shutil.rmtree(ROOT/'.lake/build')
    receipts=[]
    for tag,argv,expected,diagnostic in phases:
      before=inputs();started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();log=RESULTS/(tag+'.log');status='completed'
      try:
        with log.open('w') as f:q=subprocess.run(argv,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
        code=q.returncode
      except subprocess.TimeoutExpired:code=-1;status='timeout'
      after=inputs();text=log.read_text(errors='replace');ok=code==expected and before==after and (diagnostic is None or diagnostic in text.lower())
      receipt={'tag':tag,'argv':argv,'started_at':started,'seconds':time.monotonic()-t,'status':status,
        'exit_status':code,'expected_exit':expected,'expected_diagnostic':diagnostic,'input_hashes':before,'input_hashes_after':after,
        'unchanged':before==after,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log),'pass':ok,
        'resource_limits':{'subprocess_timeout_seconds':600,'hard_memory_limit':None,'hard_thread_limit':None}}
      (RESULTS/(tag+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');receipts.append(receipt)
      print(tag,'PASS' if ok else 'FAIL','exit',code,'seconds',round(receipt['seconds'],2),flush=True)
      if not ok:
        print(text[-4000:],flush=True)
        (RESULTS/'FINAL_RUN.json').write_text(json.dumps({'status':'FAIL','failed_phase':tag,'completed_phases':len(receipts)},indent=2));return 1
    (RESULTS/'FINAL_RUN.json').write_text(json.dumps({'status':'PASS','phases':[x['tag'] for x in receipts]},indent=2)+'\n');return 0
if __name__=='__main__':raise SystemExit(main())
