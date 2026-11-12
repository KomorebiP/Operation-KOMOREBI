"""Replay the selected universal graph/shape lemmas. Author: Komorebi P."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
LOCK=REPO/'formal/smith-chart-v0.1.0/dependency-lock.json'
LEAN_SHA='37dfe799f69b990251f3b6bcff8a1c10c1afe2adcdecc5c580cc6726ffb63433'
ALLOWED={'propext','Classical.choice','Quot.sound'}
NEGATIVE_CONSERVATION='''import GraphCore
open SmithGraphCore
example : divergence (fun _ : Fin 1 => (0 : Fin 1))
    (fun _ => (0 : Fin 1)) (fun _ => (1 : ℝ)) 0 = 1 := by
  norm_num [divergence]
'''
NEGATIVE_MARGIN='''import PureTypeMargins
example : (401/5286560 : ℝ) ≤ 0 := by norm_num
'''
POSITIVE='''import PureTypeMargins
open SmithPureTypeMargins
example : stencil (fun s => 7 - ∑ _j : Fin 1, (3 : ℝ)/(s+2)) ≤ 0 := by
  exact rl_shape (fun _ => 3) (fun _ => 2) 7 (by intro j; norm_num) (by intro j; norm_num)
'''


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('lean','mathlib','git','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    lean,mathlib,git,out=[getattr(args,n).resolve() for n in ('lean','mathlib','git','output')]
    out.mkdir(parents=True,exist_ok=False);build=out/'build';build.mkdir()
    def capture(argv,cwd=None):return subprocess.check_output(list(map(str,argv)),cwd=cwd,stderr=subprocess.STDOUT)
    version=capture([lean,'--version']).decode().strip()
    if sha(lean.read_bytes())!=LEAN_SHA or 'version 4.34.0-rc2' not in version:
        raise RuntimeError('Compiler differs from the existing pinned environment')
    lock=json.loads(LOCK.read_bytes())
    if sha((mathlib/'lake-manifest.json').read_bytes())!=lock['mathlib_manifest_sha256']:
        raise RuntimeError('Mathlib manifest differs from the lock')
    dependencies={}
    for name,path,want in [('mathlib',mathlib,lock['mathlib_revision'])]+[
        (p['name'],mathlib/'.lake/packages'/p['name'],p['rev']) for p in lock['packages']]:
        commit=capture([git,'-C',path,'rev-parse','HEAD']).decode().strip()
        dirty=capture([git,'-C',path,'status','--porcelain','--untracked-files=no']).decode().strip()
        if commit!=want or dirty:raise RuntimeError('Dependency revision/cleanliness mismatch: '+name)
        dependencies[name]={'revision':commit,'tracked_status':dirty}
    names=('GraphCore.lean','PureTypeMargins.lean','AxiomAudit.lean','replay_formal.py')
    before={name:sha((ROOT/name).read_bytes()) for name in names}
    before['dependency-lock.json']=sha(LOCK.read_bytes())
    for name in names[:3]:
        text=(ROOT/name).read_text(encoding='utf-8')
        if re.search(r'\b(?:sorry|admit)\b|^\s*(?:axiom|unsafe)\s',text,re.M):
            raise RuntimeError('Placeholder or added axiom in '+name)
        shutil.copyfile(ROOT/name,build/name)
    for name,text in [('WrongConservation.lean',NEGATIVE_CONSERVATION),
                      ('WrongMargin.lean',NEGATIVE_MARGIN),('PositiveFixture.lean',POSITIVE)]:
        (build/name).write_text(text,encoding='utf-8',newline='\n')
    libraries=[mathlib/'.lake/build/lib/lean']+[
        mathlib/'.lake/packages'/p['name']/'.lake/build/lib/lean' for p in lock['packages']]
    objects={}
    for name in names[:2]:
        for module in re.findall(r'^import (Mathlib\.[A-Za-z0-9_.]+)$',(ROOT/name).read_text(encoding='utf-8'),re.M):
            relative=Path(*module.split('.')).with_suffix('.olean')
            matches=[p/relative for p in libraries if (p/relative).is_file()]
            if len(matches)!=1:raise RuntimeError('Cached module not uniquely identified: '+module)
            objects[module]=sha(matches[0].read_bytes())
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[build,*libraries]))
    steps=[]
    for name,argv,expected in [
        ('compile-graph',['-o','GraphCore.olean','GraphCore.lean'],True),
        ('compile-margins',['-o','PureTypeMargins.olean','PureTypeMargins.lean'],True),
        ('axioms',['AxiomAudit.lean'],True),
        ('wrong-conservation',['WrongConservation.lean'],False),
        ('wrong-margin',['WrongMargin.lean'],False),
        ('positive-fixture',['PositiveFixture.lean'],True)]:
        result=subprocess.run([str(lean),'-j1','-DwarningAsError=true',*argv],cwd=build,
            env=env,capture_output=True,timeout=180)
        for stream,raw in [('stdout',result.stdout),('stderr',result.stderr)]:
            (out/(name+'.'+stream+'.txt')).write_bytes(raw)
        steps.append({'name':name,'arguments':argv,'expected_success':expected,
            'exit_code':result.returncode,'stdout_sha256':sha(result.stdout),'stderr_sha256':sha(result.stderr)})
        if (result.returncode==0)!=expected:raise RuntimeError('Unexpected compiler result: '+name)
        print('PASS '+name,flush=True)
    axiom_text=(out/'axioms.stdout.txt').read_text(encoding='utf-8')
    audits=axiom_text.count('depends on axioms:')+axiom_text.count('does not depend on any axioms')
    if audits!=17:raise RuntimeError('Expected seventeen explicit theorem axiom audits')
    for row in re.findall(r'axioms:\s*\[([^]]*)\]',axiom_text):
        if set(re.findall(r'[A-Za-z_][A-Za-z_0-9.]*',row))-ALLOWED:
            raise RuntimeError('Unexpected proof axiom')
    after={name:sha((ROOT/name).read_bytes()) for name in names}
    after['dependency-lock.json']=sha(LOCK.read_bytes())
    if before!=after:raise RuntimeError('Formal source inputs changed during replay')
    receipt={'status':'PASS','schema':'komorebi-smith-selected-formal-v1',
        'lean':{'version':version,'sha256':LEAN_SHA},'dependencies':dependencies,
        'direct_mathlib_objects':objects,'input_sha256_before':before,'input_sha256_after':after,
        'steps':steps,'theorem_axiom_audits':audits,'negative_controls':2,'positive_fixtures':1,
        'scope':'Selected finite-graph, port-power and Stieltjes/shape/error statements only. Not complete formal compactness, external classical network characterization, full Hughes margin or packet-transfer verification.',
        'review_provenance':'author-produced kernel replay; not independent human peer review'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','theorem_axiom_audits':audits,'negative_controls':2}))


if __name__=='__main__':main()
