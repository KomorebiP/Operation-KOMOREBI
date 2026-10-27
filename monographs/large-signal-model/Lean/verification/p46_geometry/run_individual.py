from pathlib import Path
import importlib.util,json,hashlib,subprocess,os,re
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lsm_inventory',root/'scripts/build_inventory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
src=root/'KomorebiLSM/RotationConeGeometry.lean';ds=m.scan_file(src)
(out/'AxiomAudit.lean').write_text('import KomorebiLSM.RotationConeGeometry\n\n'+''.join('#print axioms '+d['name']+'\n' for d in ds))
records=[]
def run(phase,args,expected=0,marker=None):
 p=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=180)
 (out/(phase+'.stdout')).write_text(p.stdout);(out/(phase+'.stderr')).write_text(p.stderr)
 passed=(p.returncode==expected if expected is not None else p.returncode!=0)
 if marker:passed=passed and marker in p.stdout+p.stderr
 records.append({'phase':phase,'command':args,'returncode':p.returncode,'passed':passed})
 return passed,p
lean=os.environ['KOMOREBI_LEAN_KIT']+'/toolchain/bin/lean'
ok,p=run('compile',[lean,'-j1','-DwarningAsError=true','-o',str(root/'.build/lib/lean/KomorebiLSM/RotationConeGeometry.olean'),str(src)])
if not ok:raise SystemExit(p.stdout+p.stderr)
ok,p=run('axioms',[lean,'-j1','-DwarningAsError=true',str(out/'AxiomAudit.lean')]);assert ok,p.stdout+p.stderr
parsed={a:sorted(x.strip() for x in (b or '').split(',') if x.strip()) for a,b in re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",p.stdout,re.S)}
assert set(parsed)=={d['name'] for d in ds}
assert all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in parsed.values())
os.environ['KOMOREBI_REPLAY_MODULE']='KomorebiLSM.RotationConeGeometry'
ok,p=run('kernel_replay',[lean,'-j1','-DwarningAsError=true',str(root/'scripts/ReplayModule.lean')],marker='KERNEL_REPLAY_PASS KomorebiLSM.RotationConeGeometry');assert ok,p.stdout+p.stderr
control=root/'negative_controls/RotationConeWithoutNonnegativeMass.lean'
ok,p=run('negative_control',[lean,'-j1','-DwarningAsError=true',str(control)],expected=None,marker='False');assert ok,p.stdout+p.stderr
assert not any(s in p.stdout+p.stderr for s in ['Unknown identifier','unknown module','does not exist','Invalid field'])
report={'passed':all(r['passed'] for r in records),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source':str(src),'declarations':len(ds),'theorems':sum(d['kind']=='theorem' for d in ds),'axioms':parsed,'control_sha256':hashlib.sha256(control.read_bytes()).hexdigest(),'records':records}
(out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['records','axioms']}))
