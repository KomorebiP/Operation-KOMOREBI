from pathlib import Path
import subprocess,json,hashlib,time,importlib.util
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
WS=ROOT.parents[1]
freeze=json.loads((OUT.parent/'SOURCE_FREEZE.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'schema':'komorebi.p67-independent-checks.v1','passed':False,'modules':freeze,'stages':[]}
for n,r in freeze.items():assert sha(ROOT/f'KomorebiLSM/{n}.lean')==r['source_sha256']
def run(label,args,log,control=False):
 t=time.monotonic();cmd=[str(WS/'runtime/gated-bin/lean'),'-j1','-DwarningAsError=true']+list(map(str,args))
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,cwd=WS)
 (OUT/log).write_text(r.stdout)
 ok=(r.returncode==1 and r.stdout.count('error:')==1 and 'error: unsolved goals' in r.stdout and '⊢ False' in r.stdout) if control else r.returncode==0
 report['stages'].append({'label':label,'command':cmd,'returncode':r.returncode,'passed':ok,'seconds':round(time.monotonic()-t,4),'log':log,'log_sha256':sha(OUT/log)})
 (OUT/'CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
 print(label,ok,flush=True)
 assert ok,r.stdout
 return r.stdout
for n in freeze:run('isolated compile '+n,['-o',OUT/f'{n}.olean',ROOT/f'KomorebiLSM/{n}.lean'],n+'_compile.log')
s=run('all40 named axioms',[OUT.parent/'AxiomAudit.lean'],'axioms.log')
spec=importlib.util.spec_from_file_location('verify',ROOT/'scripts/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
records=json.loads((OUT.parent/'DECLARATIONS.json').read_text());a=v.parse_axioms(s,{r['name'] for r in records});assert len(a)==40
(OUT/'AXIOMS.json').write_text(json.dumps(a,indent=2)+'\n')
for n in ['CoveredActionMissingCoverage','CoveredActionOmitInflation']:
 run('semantic False '+n,[ROOT/f'negative_controls/{n}.lean'],n+'.log',True)
for n,r in freeze.items():assert sha(ROOT/f'KomorebiLSM/{n}.lean')==r['source_sha256']
report['passed']=True;report['axiom_records']=len(a)
(OUT/'CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print('P67_RAW_CHECKS_PASS',flush=True)
