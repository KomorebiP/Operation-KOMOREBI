from pathlib import Path
import subprocess,json,hashlib,time,importlib.util
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];WS=ROOT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/'KomorebiLSM/VilleInequality.lean')=='a5a13a20dd32f80d22120d498cbcb51c7aba47f69733695c8bb77c17c649ffdc'
r={'passed':False,'stages':[]}
def run(label,args,log,control=False):
 cmd=[str(WS/'runtime/gated-bin/lean'),'-j1','-DwarningAsError=true']+list(map(str,args));ret=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,cwd=WS);OUT.joinpath(log).write_text(ret.stdout)
 ok=(ret.returncode==1 and ret.stdout.count('error:')==1 and '⊢ False' in ret.stdout) if control else ret.returncode==0
 r['stages'].append({'label':label,'command':cmd,'returncode':ret.returncode,'passed':ok,'log':log,'log_sha256':sha(OUT/log)});OUT.joinpath('CHECKS.json').write_text(json.dumps(r,indent=2)+'\n');assert ok,ret.stdout;print(label,ok,flush=True);return ret.stdout
run('isolated compile',['-o',OUT/'VilleInequality.olean',ROOT/'KomorebiLSM/VilleInequality.lean'],'compile.log')
a=run('all7 named axioms',[OUT.parent/'AxiomAudit.lean'],'axioms.log')
spec=importlib.util.spec_from_file_location('verify',ROOT/'scripts/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
d=json.loads(OUT.parent.joinpath('DECLARATIONS.json').read_text());parsed=v.parse_axioms(a,{q['name'] for q in d});assert len(parsed)==7
run('initial budget semantic False',[ROOT/'negative_controls/VilleMissingInitialBudget.lean'],'control.log',True)
r['passed']=True;r['axiom_records']=len(parsed);r['source_sha256']=sha(ROOT/'KomorebiLSM/VilleInequality.lean');OUT.joinpath('CHECKS.json').write_text(json.dumps(r,indent=2)+'\n');print('VILLE_RAW_CHECKS_PASS',flush=True)
