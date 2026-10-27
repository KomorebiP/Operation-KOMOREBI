from pathlib import Path
import subprocess,os,json,hashlib,time,re,datetime
root=Path(__file__).resolve().parents[2]
ws=root.parents[1]
out=Path(__file__).resolve().parent
lean=ws/'runtime/gated-bin/lean'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((out/'SOURCE_FREEZE.json').read_text())
assert sha(root/'KomorebiLSM/EuclideanMatrixNorms.lean')==freeze['EuclideanMatrixNorms']['source_sha256']
report={'schema':'komorebi.euclidean-matrix-norms-development.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False,'modules':freeze,'stages':[]}
def save(): (out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
def run(label,args,log,extra=None,control=False):
 env=os.environ.copy();env.update(extra or {})
 started=time.monotonic();r=subprocess.run([str(lean),'-j1','-DwarningAsError=true']+list(map(str,args)),cwd=ws,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (out/log).write_text(r.stdout)
 good=(r.returncode==1 and r.stdout.count('error:')==1 and 'error: unsolved goals' in r.stdout and '⊢ False' in r.stdout) if control else r.returncode==0
 row={'label':label,'returncode':r.returncode,'passed':good,'seconds':round(time.monotonic()-started,6),'log':log,'log_sha256':sha(out/log)}
 report['stages'].append(row);save();print(json.dumps(row),flush=True)
 if not good: raise RuntimeError(r.stdout)
 return r.stdout
save()
run('fresh warnings-as-errors compile',['-o',root/'.build/lib/lean/KomorebiLSM/EuclideanMatrixNorms.olean',root/'KomorebiLSM/EuclideanMatrixNorms.lean'],'compile.log')
s=run('all named axiom audit',[out/'AxiomAudit.lean'],'axiom_audit.log')
names=json.loads((out/'DECLARATIONS.json').read_text())
parsed={}
for m in re.finditer(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",s,re.S):
 parsed[m[1]]=sorted(x.strip() for x in (m[2] or '').split(',') if x.strip())
assert set(parsed)=={x['name'] for x in names}
assert all(set(x)<={'propext','Classical.choice','Quot.sound'} for x in parsed.values())
report['axiom_records']=len(parsed);report['allowed_axioms']=['propext','Classical.choice','Quot.sound'];report['axioms']=parsed;save()
s=run('exact module kernel replay',[root/'scripts/ReplayModule.lean'],'replay.log',{'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.EuclideanMatrixNorms'})
assert 'KERNEL_REPLAY_PASS KomorebiLSM.EuclideanMatrixNorms' in s
p=root/'negative_controls/EuclideanFrobeniusIdentityNorm.lean'
run('semantic Frobenius identity rejection',[p],'control.log',control=True)
report['negative_control']={'path':str(p.relative_to(root)),'source_sha256':sha(p)}
assert sha(root/'KomorebiLSM/EuclideanMatrixNorms.lean')==freeze['EuclideanMatrixNorms']['source_sha256']
report.update(passed=True,complete=True,named_declarations=len(names),named_theorems=sum(x['kind']=='theorem' for x in names),lean_commit='6a10ac8c22beadecabdbb0919c2b50214762f91d',mathlib_commit='aeb72f1e9981b6d35b426b16dca7759be3e7ba06',scope='Literal entry-flattened Frobenius and Euclidean spectral norms; sharp mixed multiplication and congruence perturbation bound. Empty finite D included.')
save();print('EUCLIDEAN_MATRIX_NORMS_CHECKS_PASS',flush=True)
