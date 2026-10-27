"""Assemble final evidence only after the completed cold audit; check attributed lemmas too."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=Path);ap.add_argument('--build',required=True,type=Path);a=ap.parse_args()
    result=json.loads((ROOT/'results/LEAN_AUDIT.json').read_text());assert result['status']=='PASS'
    state=json.loads((ROOT/'evidence/LEAN_EXECUTION.json').read_text());assert all(t['passed'] for t in state['tasks'])
    lean=a.runtime/'toolchain/bin/lean';env=os.environ.copy();env['TERM']='xterm'
    env['LEAN_PATH']=':'.join([str(a.build.resolve())]+[str(p/'.lake/build/lib/lean') for p in (a.runtime/'workspace/.lake/packages').iterdir() if p.is_dir()])
    extra=json.loads((ROOT/'evidence/ADDITIONAL_DECLARATIONS.json').read_text())
    proof=ROOT/'evidence/AdditionalAxiomAudit.lean';proof.write_text('module\npublic import MatrixLinearBridge\n'+'\n'.join('#print axioms '+x['name'] for x in extra)+'\n')
    tasks=[]
    for label,source in [('additional_axioms',proof),('fresh_minimum_export',ROOT/'examples/FreshMinimum.lean')]:
        cmd=[str(lean),'-DwarningAsError=true',str(source)];before=sha(source)
        proc=subprocess.run(cmd,cwd=ROOT/'formalization',env=env,capture_output=True,text=True,timeout=120)
        text=proc.stdout+proc.stderr;log=ROOT/'evidence'/(label+'_FINAL.log');log.write_text(text)
        if proc.returncode or before!=sha(source):raise RuntimeError(text)
        if label=='additional_axioms':
            assert all(x['name'] in text for x in extra)
            assert 'sorryAx' not in text and 'Lean.ofReduceBool' not in text
        tasks.append({'name':label,'argv':cmd,'exit_status':proc.returncode,'passed':True,'source':str(source.relative_to(ROOT)),'sha256':before,'log':str(log.relative_to(ROOT))})
    supplemental={'status':'PASS','tasks':tasks,'additional_named_declarations':len(extra),'reason':'Three attributed declarations share a line with @[simp] and require a supplemental inventory pass.'}
    (ROOT/'evidence/SUPPLEMENTAL_AUDIT.json').write_text(json.dumps(supplemental,indent=2)+'\n')
    merged=json.loads((ROOT/'evidence/DECLARATIONS.json').read_text())+extra
    (ROOT/'evidence/COMPLETE_DECLARATION_INVENTORY.json').write_text(json.dumps(merged,indent=2)+'\n')
    # Preserve the main runner's records unchanged; report its supplemental pass separately.
    outputs=['results/LEAN_AUDIT.json','evidence/LEAN_EXECUTION.json','evidence/SUPPLEMENTAL_AUDIT.json','evidence/COMPLETE_DECLARATION_INVENTORY.json']
    outputs += [t['log'] for t in state['tasks']]+[t['log'] for t in tasks]
    inputs=dict(state['inputs']);inputs.update({str(proof.relative_to(ROOT)):sha(proof),'examples/FreshMinimum.lean':sha(ROOT/'examples/FreshMinimum.lean'),'evidence/ADDITIONAL_DECLARATIONS.json':sha(ROOT/'evidence/ADDITIONAL_DECLARATIONS.json'),'evidence/ENVIRONMENT.json':sha(ROOT/'evidence/ENVIRONMENT.json'),'tools/finalize_evidence.py':sha(Path(__file__))})
    assert all(sha(ROOT/p)==h for p,h in inputs.items())
    manifest={'schema_version':2,'claim_id':'KRC-0.4-GENERIC-LINEAR-ENCODING-MINIMUM',
      'repository':{'commit':'standalone archive, no git commit','dirty':True},
      'command':state['invocations'][0],
      'environment':{'software':[{'name':'Lean','version':result['toolchain']},{'name':'Mathlib','version':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'}],'platform':platform.platform()},
      'mathematics':{'assertion_tested':'Kernel checking of the generic torsion-safe minimum theorem, all 202 concrete prime-power applications, compatibility bridge, and nonlinear-encoding boundary.',
       'coefficient_domain':'Z/p^r, p prime, r positive; concrete Fin residue representatives with proved arithmetic compatibility',
       'conventions':'All source states and all finite words. Linear initial encoding is required; competing target operations may be nonlinear.',
       'inputs':list(inputs),'bounds':{'local_modules':result['modules'],'generated_minimum_instances':202,'main_named_declarations':result['declarations'],'supplemental_declarations':len(extra)},
       'non_claims':['Python/exporter correctness is not formally verified.','Upstream cached Mathlib dependencies are not cold-rebuilt.','No single-seed, nonlinear-encoding or arbitrary-program lower bound.','No new benchmark advantage or historical novelty.']},
      'randomness':{'used':False,'seed':None,'generator':'none'},
      'run':{'started_at':state['started'],'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':state['seconds'],'exit_status':0,'status':'completed','wall_cap_seconds':None,
       'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'missing_results':[],'invalid_results':[]},
      'input_artifacts':[{'path':p,'sha256':h,'sha256_after':sha(ROOT/p)} for p,h in inputs.items()],
      'execution_artifacts':list(inputs),'declared_results':outputs[:4],
      'outputs':[{'path':p,'sha256':sha(ROOT/p),'kind':'result' if p in outputs[:4] else 'log'} for p in outputs],
      'checks':[{'name':t['name'],'status':'PASS'} for t in state['tasks']+tasks],
      'result':'PASS: actual completed proof checks and declared controls.',
      'residual_risks':['Proof interpretation is self-review.','External source encoding must still match the intended human problem.','No formal executable extraction of the discoverer.']}
    (ROOT/'LEAN_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    py=json.loads((ROOT/'results/PYTHON_AUDIT.json').read_text());counts=dict(result['counts']);counts['theorem']+=len(extra)
    summary={'status':'PASS','modules':result['modules'],'main_tasks':len(state['tasks']),'supplemental_tasks':len(tasks),'named_declarations':len(merged),'counts':counts,'generated_minimum_instances':202,'cardinality_gap_cases':21,'axioms':result['axioms'],'python_counts':py['counts']}
    (ROOT/'results/FINAL_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
