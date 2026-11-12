"""Replay the capacitor-shunt shape in the same pinned environment. Author: Komorebi P."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess
import replay_formal as core

ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ('lean','mathlib','git','output'):parser.add_argument('--'+n,type=Path,required=True)
    args=parser.parse_args()
    lean,mathlib,git,out=[getattr(args,n).resolve() for n in ('lean','mathlib','git','output')]
    out.mkdir(parents=True,exist_ok=False);build=out/'build';build.mkdir()
    def capture(argv,cwd=None):return subprocess.check_output(list(map(str,argv)),cwd=cwd,stderr=subprocess.STDOUT)
    version=capture([lean,'--version']).decode().strip()
    if sha(lean)!=core.LEAN_SHA or 'version 4.34.0-rc2' not in version:raise RuntimeError('Compiler mismatch')
    lock=json.loads(core.LOCK.read_bytes())
    if sha(mathlib/'lake-manifest.json')!=lock['mathlib_manifest_sha256']:raise RuntimeError('Manifest mismatch')
    dependencies={}
    for name,path,want in [('mathlib',mathlib,lock['mathlib_revision'])]+[
      (p['name'],mathlib/'.lake/packages'/p['name'],p['rev']) for p in lock['packages']]:
        commit=capture([git,'-C',path,'rev-parse','HEAD']).decode().strip()
        dirty=capture([git,'-C',path,'status','--porcelain','--untracked-files=no']).decode().strip()
        if commit!=want or dirty:raise RuntimeError('Dependency differs: '+name)
        dependencies[name]={'revision':commit,'tracked_status':dirty}
    earlier={}
    for name in ('phase2-formal-001','phase2-shunt-formal-001'):
        p=ROOT.parent/'verification'/name/'receipt.json';r=json.loads(p.read_bytes())
        if r['status']!='PASS':raise RuntimeError('Prior receipt failed')
        for source,h in r['input_sha256_before'].items():
            path=core.LOCK if source=='dependency-lock.json' else ROOT/source
            if sha(path)!=h:raise RuntimeError('Prior proof source changed: '+source)
        earlier[name]=sha(p)
    names=('CapShuntMargin.lean','replay_cap_shunt_formal.py','replay_formal.py')
    before={n:sha(ROOT/n) for n in names};before['dependency-lock.json']=sha(core.LOCK)
    text=(ROOT/names[0]).read_text(encoding='utf-8')
    if re.search(r'\b(?:sorry|admit)\b|^\s*(?:axiom|unsafe)\s',text,re.M):raise RuntimeError('Placeholder')
    shutil.copyfile(ROOT/names[0],build/names[0])
    (build/'WrongCapShunt.lean').write_text('import CapShuntMargin\nexample : SmithCapShuntMargin.stencil (fun s => 1/(s+1)) < 0 := by\n  norm_num [SmithCapShuntMargin.stencil]\n',encoding='utf-8')
    (build/'PositiveCapShunt.lean').write_text('import CapShuntMargin\nexample : 0 ≤ SmithCapShuntMargin.stencil (fun s => (3:ℝ)+4*s+∑ _j : Fin 1, (3:ℝ)/(s+2)) := by\n  exact SmithCapShuntMargin.shape 3 4 (fun _ => 3) (fun _ => 2) (by intro j; norm_num) (by intro j; norm_num)\n',encoding='utf-8')
    libraries=[mathlib/'.lake/build/lib/lean']+[
      mathlib/'.lake/packages'/p['name']/'.lake/build/lib/lean' for p in lock['packages']]
    objects={}
    for module in re.findall(r'^import (Mathlib\.[A-Za-z0-9_.]+)$',text,re.M):
        relative=Path(*module.split('.')).with_suffix('.olean')
        matches=[p/relative for p in libraries if (p/relative).is_file()]
        if len(matches)!=1:raise RuntimeError('Cached import not uniquely identified')
        objects[module]=sha(matches[0])
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[build,*libraries]));steps=[]
    for name,argv,expected in [('compile-cap-shunt',['-o','CapShuntMargin.olean','CapShuntMargin.lean'],True),
      ('wrong-cap-shunt',['WrongCapShunt.lean'],False),('positive-cap-shunt',['PositiveCapShunt.lean'],True)]:
        result=subprocess.run([str(lean),'-j1','-DwarningAsError=true',*argv],cwd=build,env=env,capture_output=True,timeout=180)
        row={'name':name,'arguments':argv,'expected_success':expected,'exit_code':result.returncode}
        for stream,raw in [('stdout',result.stdout),('stderr',result.stderr)]:
            p=out/(name+'.'+stream+'.txt');p.write_bytes(raw);row[stream+'_sha256']=sha(p)
        steps.append(row)
        if (result.returncode==0)!=expected:raise RuntimeError('Unexpected Lean result: '+name)
        print('PASS '+name,flush=True)
    axioms=(out/'compile-cap-shunt.stdout.txt').read_text(encoding='utf-8')
    if axioms.count('depends on axioms:')!=4:raise RuntimeError('Expected four explicit axiom audits')
    for row in re.findall(r'axioms:\s*\[([^]]*)\]',axioms):
        if set(re.findall(r'[A-Za-z_][A-Za-z_0-9.]*',row))-core.ALLOWED:raise RuntimeError('Unexpected axiom')
    after={n:sha(ROOT/n) for n in names};after['dependency-lock.json']=sha(core.LOCK)
    if before!=after or sha(lean)!=core.LEAN_SHA:raise RuntimeError('Inputs changed during replay')
    receipt={'status':'PASS','schema':'komorebi-smith-cap-shunt-formal-v1','lean':{'version':version,'sha256':core.LEAN_SHA},
      'dependencies':dependencies,'direct_mathlib_objects':objects,'earlier_receipt_sha256':earlier,
      'input_sha256_before':before,'input_sha256_after':after,'steps':steps,'new_theorem_axiom_audits':4,
      'total_selected_with_earlier':25,'new_negative_controls':1,'new_positive_fixtures':1,
      'scope':'Selected sixth-difference kernel and positive-sum shape; not full formal physical characterization, Cayley interval bridge or universal mixed margin.',
      'review_provenance':'Author-produced actual kernel replay; no independent human review'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','total_selected_theorems':25}))

if __name__=='__main__':main()
