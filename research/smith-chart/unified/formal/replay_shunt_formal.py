"""Replay the shunt-L extension and revalidate its pinned core. Author: Komorebi P."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys
import replay_formal as core

ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ('lean','mathlib','git','output'):parser.add_argument('--'+n,type=Path,required=True)
    args=parser.parse_args()
    lean,mathlib,git,out=[getattr(args,n).resolve() for n in ('lean','mathlib','git','output')]
    out.mkdir(parents=True,exist_ok=False)
    names=('ShuntMargin.lean','replay_shunt_formal.py')
    before={n:sha(ROOT/n) for n in names}
    subprocess.run([sys.executable,'-B',str(ROOT/'replay_formal.py'),'--lean',str(lean),
      '--mathlib',str(mathlib),'--git',str(git),'--output',str(out/'core')],check=True)
    observed=out/'core/receipt.json'
    retained=ROOT.parent/'verification/phase2-formal-001/receipt.json'
    if sha(observed)!=sha(retained):raise RuntimeError('Fresh core replay differs from retained receipt')
    core_record=json.loads(observed.read_bytes())
    build=out/'build';build.mkdir()
    text=(ROOT/'ShuntMargin.lean').read_text(encoding='utf-8')
    if re.search(r'\b(?:sorry|admit)\b|^\s*(?:axiom|unsafe)\s',text,re.M):raise RuntimeError('Placeholder')
    shutil.copyfile(ROOT/'ShuntMargin.lean',build/'ShuntMargin.lean')
    (build/'WrongShunt.lean').write_text('import ShuntMargin\nexample : SmithShuntMargin.stencil (fun s => 1/(s+1)) < 0 := by\n  norm_num [SmithShuntMargin.stencil]\n',encoding='utf-8')
    (build/'PositiveShunt.lean').write_text('import ShuntMargin\nexample : SmithShuntMargin.stencil (fun s => (2:ℝ)/s+3+4*s-∑ _j : Fin 1, (3:ℝ)/(s+2)) ≤ 0 := by\n  exact SmithShuntMargin.shape 2 3 4 (fun _ => 3) (fun _ => 2) (by intro j; norm_num) (by intro j; norm_num)\n',encoding='utf-8')
    lock=json.loads(core.LOCK.read_bytes())
    libraries=[mathlib/'.lake/build/lib/lean']+[
      mathlib/'.lake/packages'/p['name']/'.lake/build/lib/lean' for p in lock['packages']]
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[build,*libraries]))
    steps=[]
    for name,argv,expected in [('compile-shunt',['-o','ShuntMargin.olean','ShuntMargin.lean'],True),
      ('wrong-shunt',['WrongShunt.lean'],False),('positive-shunt',['PositiveShunt.lean'],True)]:
        result=subprocess.run([str(lean),'-j1','-DwarningAsError=true',*argv],cwd=build,env=env,capture_output=True,timeout=180)
        row={'name':name,'arguments':argv,'expected_success':expected,'exit_code':result.returncode}
        for stream,raw in [('stdout',result.stdout),('stderr',result.stderr)]:
            p=out/(name+'.'+stream+'.txt');p.write_bytes(raw);row[stream+'_sha256']=sha(p)
        steps.append(row)
        if (result.returncode==0)!=expected:raise RuntimeError('Unexpected Lean result: '+name)
        print('PASS '+name,flush=True)
    axioms=(out/'compile-shunt.stdout.txt').read_text(encoding='utf-8')
    if axioms.count('depends on axioms:')!=4:raise RuntimeError('Expected four new axiom audits')
    for row in re.findall(r'axioms:\s*\[([^]]*)\]',axioms):
        if set(re.findall(r'[A-Za-z_][A-Za-z_0-9.]*',row))-core.ALLOWED:raise RuntimeError('Unexpected axiom')
    after={n:sha(ROOT/n) for n in names}
    if before!=after or sha(lean)!=core.LEAN_SHA:raise RuntimeError('Inputs changed during replay')
    receipt={'status':'PASS','schema':'komorebi-smith-shunt-formal-v1','lean':core_record['lean'],
      'core_receipt':'../phase2-formal-001/receipt.json','core_receipt_sha256':sha(observed),
      'input_sha256_before':before,'input_sha256_after':after,'steps':steps,
      'new_theorem_axiom_audits':4,'total_selected_with_core':21,'new_negative_controls':1,
      'scope':'Finite shunt-admittance kernel and finite positive-sum shape only. Classical RC physical characterization, Cayley interval translation and full universal mixed proof remain separate.',
      'review_provenance':'Author-produced actual kernel replay; no independent human review'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','total_selected_theorems':21}))

if __name__=='__main__':main()
