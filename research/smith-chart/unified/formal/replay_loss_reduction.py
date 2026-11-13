"""Replay finite resistor elimination and mixed-loss contraction, including KCL and power. Author: Komorebi P."""
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
    names=('StarMesh.lean','LossContraction.lean','LossReductionAudit.lean','replay_loss_reduction.py')
    before={n:sha(ROOT/n) for n in names}
    subprocess.run([sys.executable,'-B',str(ROOT/'replay_formal.py'),'--lean',str(lean),
      '--mathlib',str(mathlib),'--git',str(git),'--output',str(out/'core')],check=True)
    observed=out/'core/receipt.json'
    retained=ROOT.parent/'verification/phase2-formal-001/receipt.json'
    if sha(observed)!=sha(retained):raise RuntimeError('Fresh core replay differs from retained receipt')
    core_record=json.loads(observed.read_bytes())
    build=out/'build';build.mkdir()
    for name in names[:3]:
        text=(ROOT/name).read_text(encoding='utf-8')
        if re.search(r'\b(?:sorry|admit)\b|^\s*(?:axiom|unsafe)\s',text,re.M):raise RuntimeError('Placeholder')
        shutil.copyfile(ROOT/name,build/name)
    (build/'WrongMesh.lean').write_text("import StarMesh\nexample : SmithStarMesh.mesh (fun _ : Fin 2 => (1:ℝ)) 0 1 = 1 := by\n  norm_num [SmithStarMesh.mesh,SmithStarMesh.degree,Fin.sum_univ_two]\n",encoding='utf-8')
    (build/'WrongDisk.lean').write_text("import LossContraction\nexample : Complex.normSq (7/10:ℂ) ≤ (1/4:ℝ) := by\n  norm_num [Complex.normSq]\n",encoding='utf-8')
    (build/'PositiveFixtures.lean').write_text("import StarMesh\nimport LossContraction\nexample : SmithStarMesh.mesh (fun _ : Fin 2 => (1:ℝ)) 0 1 = 1/2 := by\n  norm_num [SmithStarMesh.mesh,SmithStarMesh.degree,Fin.sum_univ_two]\nexample : Complex.normSq (((1+(1:ℝ)*(1-Complex.normSq (0:ℂ)):ℝ):ℂ)*(7/10:ℂ)-0) ≤ (1:ℝ)*(1+1)*(1-Complex.normSq (0:ℂ))^2 := by\n  apply SmithLossContraction.polynomial_disk (0:ℂ) (7/10:ℂ) 1\n  all_goals norm_num [Complex.normSq]\n",encoding='utf-8')
    lock=json.loads(core.LOCK.read_bytes())
    libraries=[mathlib/'.lake/build/lib/lean']+[
      mathlib/'.lake/packages'/p['name']/'.lake/build/lib/lean' for p in lock['packages']]
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[build,out/'core/build',*libraries]))
    objects={}
    for name in names[:2]:
        for module in re.findall(r'^import (Mathlib\.[A-Za-z0-9_.]+)$',(ROOT/name).read_text(encoding='utf-8'),re.M):
            relative=Path(*module.split('.')).with_suffix('.olean')
            matches=[p/relative for p in libraries if (p/relative).is_file()]
            if len(matches)!=1:raise RuntimeError('Cached module not uniquely identified: '+module)
            objects[module]=sha(matches[0])
    steps=[]
    for name,argv,expected in [
      ('compile-star-mesh',['-o','StarMesh.olean','StarMesh.lean'],True),
      ('compile-loss-contraction',['-o','LossContraction.olean','LossContraction.lean'],True),
      ('axioms-loss-reduction',['LossReductionAudit.lean'],True),
      ('wrong-mesh',['WrongMesh.lean'],False),('wrong-disk',['WrongDisk.lean'],False),
      ('positive-fixtures',['PositiveFixtures.lean'],True)]:
        result=subprocess.run([str(lean),'-j1','-DwarningAsError=true',*argv],cwd=build,env=env,capture_output=True,timeout=180)
        row={'name':name,'arguments':argv,'expected_success':expected,'exit_code':result.returncode}
        for stream,raw in [('stdout',result.stdout),('stderr',result.stderr)]:
            p=out/(name+'.'+stream+'.txt');p.write_bytes(raw);row[stream+'_sha256']=sha(p)
        steps.append(row)
        if (result.returncode==0)!=expected:raise RuntimeError('Unexpected Lean result: '+name)
        if not expected and ('unsolved goals' not in result.stdout.decode('utf-8',errors='replace')):
            raise RuntimeError('Negative fixture did not fail for its mathematical goal')
        print('PASS '+name,flush=True)
    axioms=(out/'axioms-loss-reduction.stdout.txt').read_text(encoding='utf-8')
    if axioms.count('depends on axioms:')!=16:raise RuntimeError('Expected sixteen new axiom audits')
    for row in re.findall(r'axioms:\s*\[([^]]*)\]',axioms):
        if set(re.findall(r'[A-Za-z_][A-Za-z_0-9.]*',row))-core.ALLOWED:raise RuntimeError('Unexpected axiom')
    after={n:sha(ROOT/n) for n in names}
    if before!=after or sha(lean)!=core.LEAN_SHA:raise RuntimeError('Inputs changed during replay')
    receipt={'status':'PASS','schema':'komorebi-smith-loss-reduction-formal-v1','lean':core_record['lean'],
      'core_receipt':'../phase2-formal-001/receipt.json','core_receipt_sha256':sha(observed),
      'input_sha256_before':before,'input_sha256_after':after,'steps':steps,
      'direct_mathlib_objects':objects,'new_theorem_axiom_audits':16,'total_selected_with_three_prior_receipts':41,'new_negative_controls':2,'new_positive_fixture_statements':2,
      'scope':'One finite resistor-node elimination, zero-degree case and retained-current preservation; finite mixed-loss contraction from actual KCL and branch laws; exact polynomial disk. Iterated reduction, existence and analytic limits, component-box interpretation, full universal margin and transfer remain separate.',
      'review_provenance':'Author-produced actual kernel replay; no independent human review'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','new_selected_theorems':16,'total_selected_theorems':41}))

if __name__=='__main__':main()
