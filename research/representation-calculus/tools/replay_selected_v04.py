"""Selected fresh cold replay, not a second 202-instance suite audit."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,time
from audit_lean import ROOT, modules_order

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=Path);ap.add_argument('--build',required=True,type=Path);a=ap.parse_args()
    modules,src=modules_order();targets=['LargeLinearMinimum','TorsionEncodingBoundary'];wanted=set()
    def add(m):
        if m in wanted:return
        wanted.add(m)
        for dep in re.findall(r'^(?:public )?import (\S+)',src[m].read_text(),re.M):
            if dep in src:add(dep)
    for m in targets:add(m)
    order=[m for m in modules if m in wanted];a.build.mkdir(parents=True,exist_ok=True)
    if any(a.build.rglob('*.olean')):raise RuntimeError('Selected cold build must be empty')
    inputs=[src[m] for m in order]+[ROOT/'examples/FreshMinimum.lean']+[ROOT/'controls'/(n+'.lean') for n in ['BadPrime','BadNonzeroWeights','BadNonlinearEncoding']]
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    env=os.environ.copy();env['TERM']='xterm';env['LEAN_PATH']=':'.join([str(a.build.resolve())]+[str(p/'.lake/build/lib/lean') for p in (a.runtime/'workspace/.lake/packages').iterdir() if p.is_dir()])
    lean=str(a.runtime/'toolchain/bin/lean');tasks=[];logs=ROOT/'evidence/selected_replay';logs.mkdir(parents=True,exist_ok=True)
    def run(name,source,expected=0,out=None):
        cmd=[lean,'-DwarningAsError=true'];start=time.monotonic()
        if out is not None:out.parent.mkdir(parents=True,exist_ok=True);cmd+=['-o',str(out)]
        cmd+=[str(source)];proc=subprocess.run(cmd,cwd=ROOT/'formalization',env=env,capture_output=True,text=True,timeout=120)
        log=logs/(name+'.log');log.write_text(proc.stdout+proc.stderr)
        passed=(proc.returncode==0) if expected==0 else (proc.returncode!=0)
        tasks.append({'name':name,'command':cmd,'exit_status':proc.returncode,'expected':'accept' if expected==0 else 'reject','passed':passed,'seconds':time.monotonic()-start})
        if not passed:raise RuntimeError(log.read_text())
    for m in order:run('build_'+m,src[m],out=a.build/(m.replace('.','/')+'.olean'))
    run('fresh_export',ROOT/'examples/FreshMinimum.lean')
    for n in ['BadPrime','BadNonzeroWeights','BadNonlinearEncoding']:run(n,ROOT/'controls'/(n+'.lean'),1)
    proof=logs/'Axioms.lean';proof.write_text('module\npublic import MatrixPrimeMinimality\npublic import TorsionEncodingBoundary\npublic import LargeLinearMinimum\n'+
        '\n'.join('#print axioms '+n for n in ['Komorebi.Representation.Matrix.prime_certificate_minimum_iff','Komorebi.Representation.Matrix.fin_certificate_minimum_iff','Komorebi.Representation.TorsionBoundary.two_linear_coordinates_necessary','Komorebi.Representation.TorsionBoundary.one_nonlinear_residue_suffices'])+'\n')
    run('axioms',proof)
    text=(logs/'axioms.log').read_text();assert 'sorryAx' not in text and 'Lean.ofReduceBool' not in text
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    result={'status':'PASS','scope':'Selected core/large/torsion cold rebuild, one freshly exported instance, three rejection controls and endpoint axiom checks; NOT a second full 202-instance suite.','modules':len(order),'tasks':tasks,'inputs_unchanged':True,'input_hashes':hashes}
    (ROOT/'evidence/SELECTED_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','modules':len(order),'tasks':len(tasks)}))
if __name__=='__main__':main()
