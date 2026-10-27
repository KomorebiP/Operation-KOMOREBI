from pathlib import Path
import subprocess,json,hashlib,importlib.util
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];WS=ROOT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f={'ConditionalRandomMultiplier':'fc8282499cc633205af72c340482a757d3f3474f9de731148cba28923d5af0e6','RegressionExponential':'01336685449cfa9945e29fe202541305f88bcd2ad57c7f19a33c139fef2a1a01'}
for n,h in f.items():assert sha(ROOT/f'KomorebiLSM/{n}.lean')==h
r={'passed':False,'sources':f,'stages':[]}
def run(label,args,log,control=False):
 cmd=[str(WS/'runtime/gated-bin/lean'),'-j1','-DwarningAsError=true']+list(map(str,args));ret=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,cwd=WS);OUT.joinpath(log).write_text(ret.stdout)
 ok=(ret.returncode==1 and ret.stdout.count('error:')==1 and '⊢ False' in ret.stdout) if control else ret.returncode==0
 r['stages'].append({'label':label,'command':cmd,'returncode':ret.returncode,'passed':ok,'log':log,'log_sha256':sha(OUT/log)});OUT.joinpath('CHECKS.json').write_text(json.dumps(r,indent=2)+'\n');assert ok,ret.stdout;print(label,ok,flush=True);return ret.stdout
for n in f:run('isolated compile '+n,['-o',OUT/f'{n}.olean',ROOT/f'KomorebiLSM/{n}.lean'],n+'_compile.log')
a=run('all37 named axioms',[OUT/'AxiomAudit.lean'],'axioms.log')
spec=importlib.util.spec_from_file_location('verify',ROOT/'scripts/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
d=json.loads(OUT.joinpath('DECLARATIONS.json').read_text());parsed=v.parse_axioms(a,{q['name'] for q in d});assert len(parsed)==37
s=run('arbitrary space signatures',[OUT/'Signatures.lean'],'signatures.log');assert 'StandardBorelSpace' not in s and 'condExpKernel' not in s
for n in ['ConditionalRandomUnpredictable','RegressionUnpredictableDesign','RegressionUnnormalizedMixture']:run('semantic False '+n,[ROOT/f'negative_controls/{n}.lean'],n+'.log',True)
for n,h in f.items():assert sha(ROOT/f'KomorebiLSM/{n}.lean')==h
r['passed']=True;r['axiom_records']=len(parsed);OUT.joinpath('CHECKS.json').write_text(json.dumps(r,indent=2)+'\n');print('P81_HELPERS_RAW_CHECKS_PASS',flush=True)
