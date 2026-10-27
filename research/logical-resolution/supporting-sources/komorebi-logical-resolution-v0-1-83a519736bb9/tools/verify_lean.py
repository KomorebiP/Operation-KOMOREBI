"""Cold build, axiom audit, and expected-success/rejection controls.

Usage: python tools/verify_lean.py --lean /absolute/path/to/lean
No runtime is downloaded, no background work is launched, and timeout is failure.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, re, shutil, subprocess, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODULES=['RepresentationCore','FiniteCertificates','ObservationSyntax','LogicalHorizon',
         'SemanticBoundaries','StreamBoundary','FiniteDefinability','ConcreteLogical']

def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def declarations():
    records=[]
    for module in MODULES:
        namespace=''
        text=(ROOT/'formalization'/f'{module}.lean').read_text()
        for lineno,line in enumerate(text.splitlines(),1):
            m=re.match(r'^namespace\s+(\S+)',line)
            if m: namespace=m.group(1)
            m=re.match(r'^(?:noncomputable\s+)?(def|theorem|abbrev|structure|inductive)\s+([\w.]+)',line)
            if m: records.append({'module':module,'line':lineno,'kind':m.group(1),
                                  'name':namespace+'.'+m.group(2)})
    return records

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--lean',required=True);args=ap.parse_args()
    lean=Path(args.lean).resolve()
    if not lean.is_file(): raise SystemExit(f'Lean executable missing: {lean}')
    decls=declarations()
    (ROOT/'tests'/'AxiomAudit.lean').write_text('module\n' + ''.join('public import '+m+'\n' for m in MODULES)
        + '\n' + ''.join('#print axioms '+d['name']+'\n' for d in decls))
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results'/'DECLARATIONS.json').write_text(json.dumps(decls,indent=2)+'\n')
    accepted=[ROOT/'formalization'/f'{m}.lean' for m in MODULES]
    inputs=accepted+sorted((ROOT/'tests').glob('*.lean'))+[Path(__file__).resolve()]
    before={str(p.relative_to(ROOT)):digest(p) for p in inputs}
    shutil.rmtree(ROOT/'build',ignore_errors=True);(ROOT/'build').mkdir()
    env=os.environ.copy();env['LEAN_PATH']=str(ROOT/'build')
    logdir=ROOT/'evidence'/'lean_cold';logdir.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat(); start=time.monotonic();tasks=[]
    def task(name,argv,expected=0):
        tick=time.monotonic();timed=False
        try:
            p=subprocess.run(argv,cwd=ROOT/'formalization',env=env,stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,timeout=60,text=True)
            code=p.returncode;out=p.stdout
        except subprocess.TimeoutExpired as exc:
            timed=True;code=-1;out=str(exc.stdout or '')+'\nTIMEOUT'
        path=logdir/(name+'.log');path.write_text(out)
        passed=(not timed) and (code==0 if expected==0 else code!=0)
        rec={'name':name,'argv':[str(a) for a in argv],'exit_status':code,'expected':expected,
             'timed_out':timed,'passed':passed,'runtime_seconds':time.monotonic()-tick,
             'log':str(path.relative_to(ROOT)),'sha256':digest(path)}
        tasks.append(rec);print(json.dumps(rec),flush=True)
        if not passed: raise RuntimeError(f'Failed task {name}: {out}')
        return out
    version=task('version',[str(lean),'--version']).strip()
    for m in MODULES:
        task('build_'+m,[str(lean),'-j1','-DwarningAsError=true','-o',str(ROOT/'build'/f'{m}.olean'),m+'.lean'])
    audit=task('axioms',[str(lean),'-j1','-DwarningAsError=true',str(ROOT/'tests'/'AxiomAudit.lean')])
    allowed={'propext','Classical.choice','Quot.sound'};used=set()
    for block in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',audit):
        used.update(x.strip() for x in block.split(',') if x.strip())
    if used-allowed: raise RuntimeError('Unexpected axioms: '+str(used-allowed))
    if any(d['name'] not in audit for d in decls): raise RuntimeError('Missing axiom-audited declaration')
    for name in ['Positive','FalseStateIdentity','FalseExistential','Placeholder']:
        task('control_'+name,[str(lean),'-j1','-DwarningAsError=true',str(ROOT/'tests'/(name+'.lean'))],
             expected=0 if name=='Positive' else 'nonzero')
    after={str(p.relative_to(ROOT)):digest(p) for p in inputs}
    if before!=after: raise RuntimeError('Execution inputs changed')
    counts=dict(Counter(d['kind'] for d in decls))
    newcounts=dict(Counter(d['kind'] for d in decls if d['module'] not in MODULES[:2]))
    result={'status':'PASS','started_at':started,'runtime_seconds':time.monotonic()-start,'lean':version,
            'lean_executable_sha256':digest(lean),'modules':MODULES,'counts':counts,'new_counts':newcounts,
            'named_declarations':len(decls),'axioms':sorted(used),'tasks':tasks,
            'input_hashes_before':before,'input_hashes_after':after,
            'limits':{'per_task_wall_seconds':60,'lean_worker_threads':1},
            'non_claims':['No rerun of full v0.4 or p-adic corpus','No Mathlib syntax translation',
                          'Python implementation not Lean-verified','Self-review, not independent referee']}
    (ROOT/'results'/'LEAN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','counts','new_counts','named_declarations','axioms','runtime_seconds']},indent=2))
if __name__=='__main__':main()
