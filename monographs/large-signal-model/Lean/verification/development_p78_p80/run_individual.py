from pathlib import Path
import importlib.util,json,hashlib,subprocess,os,re
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lsm_inventory',root/'scripts/build_inventory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
lean='/workspace/scratch/ea498747acd5/runtime/gated-bin/lean'
modules=['DataSelectedGeometry','ConvexRepairBracketing','CertifiedRepairUpper']
records=[];audit={};sources={}
def run(phase,args,expected=0,marker=None,env=None):
 p=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=1800,env=env)
 (out/(phase+'.stdout')).write_text(p.stdout);(out/(phase+'.stderr')).write_text(p.stderr)
 passed=(p.returncode==expected if expected is not None else p.returncode!=0)
 if marker:passed=passed and marker in p.stdout+p.stderr
 records.append({'phase':phase,'command':args,'returncode':p.returncode,'passed':passed})
 print(phase,'PASS' if passed else 'FAIL',flush=True)
 if not passed:raise AssertionError(p.stdout+p.stderr)
 return p
for module in modules:
 src=root/'KomorebiLSM'/f'{module}.lean';ds=m.scan_file(src)
 sources[module]={'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'declarations':len(ds),'theorems':sum(d['kind']=='theorem' for d in ds)}
 af=out/(module+'_AxiomAudit.lean');af.write_text('import KomorebiLSM.'+module+'\n\n'+''.join('#print axioms '+d['name']+'\n' for d in ds))
 run(module+'_compile',[lean,'-j1','-DwarningAsError=true','-o',str(root/'.build/lib/lean/KomorebiLSM'/f'{module}.olean'),str(src)])
 p=run(module+'_axioms',[lean,'-j1','-DwarningAsError=true',str(af)])
 parsed={a:sorted(x.strip() for x in (b or '').split(',') if x.strip()) for a,b in re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",p.stdout,re.S)}
 assert set(parsed)=={d['name'] for d in ds},(module,set(parsed),{d['name'] for d in ds})
 assert all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in parsed.values())
 audit[module]=parsed
 env=os.environ.copy();env['KOMOREBI_REPLAY_MODULE']='KomorebiLSM.'+module
 run(module+'_kernel_replay',[lean,'-j1','-DwarningAsError=true',str(root/'scripts/ReplayModule.lean')],marker='KERNEL_REPLAY_PASS KomorebiLSM.'+module,env=env)
controls={}
for name in ['GeometryWholeStateIsNotMaxNorm','GeometryVerifierMustCoverWholeSet','RepairSeparatorMustBePositive']:
 control=root/'negative_controls'/f'{name}.lean'
 p=run(name,[lean,'-j1','-DwarningAsError=true',str(control)],expected=None,marker='False')
 assert not any(s in p.stdout+p.stderr for s in ['Unknown identifier','unknown module','does not exist','Invalid field','elaboration function','has been deprecated'])
 controls[name]=hashlib.sha256(control.read_bytes()).hexdigest()
report={'passed':all(r['passed'] for r in records),'sources':sources,'axioms':audit,'controls':controls,'records':records}
(out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'sources':sources,'controls':report['controls']}),flush=True)
