"""Cold-check every local library file and audit explicit declarations.

Requires the preserved Lean 4.34.0-rc2 and pinned Mathlib dependency installation.
Does not compile all of Mathlib or claim verification of the Python evaluator.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=['RepresentationCore','FiniteCertificates','ObservationSyntax','LogicalHorizon',
 'SemanticBoundaries','StreamBoundary','FiniteDefinability','ConcreteLogical']
NEW=['RelationalSyntax','RelationalBackForth','StandardTranslation','StandardContracts','QuantifierWitness']
MODULES=PARENT+NEW
CONTROLS={'Positive':0,'PositiveStandard':0,'FalseStateIdentity':1,'FalseExistential':1,
 'Placeholder':1,'FalseBinder':1,'FalseRelationalWitness':1,'FalseQuantifierRank':1}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def declarations():
 result=[]
 for m in MODULES:
  namespace=''
  for line,s in enumerate((ROOT/'formalization'/f'{m}.lean').read_text().splitlines(),1):
   ns=re.match(r'^namespace\s+(\S+)',s)
   if ns:namespace=ns.group(1)
   d=re.match(r'^(?:@\[[^\]]+\]\s*)?(?:noncomputable\s+)?(def|theorem|abbrev|structure|inductive|instance)\s+([\w.]+)',s)
   if d:result.append({'module':m,'line':line,'kind':d.group(1),'name':namespace+'.'+d.group(2)})
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);a=ap.parse_args();rt=Path(a.runtime).resolve()
 lean=rt/'toolchain/bin/lean';mr=rt/'workspace/.lake/packages/mathlib'
 if not lean.is_file():raise SystemExit('Missing Lean binary: '+str(lean))
 commit=subprocess.check_output(['git','-C',str(mr),'rev-parse','HEAD'],text=True).strip()
 if commit!='aeb72f1e9981b6d35b426b16dca7759be3e7ba06':raise SystemExit('Mathlib pin mismatch')
 decs=declarations();(ROOT/'results/DECLARATIONS.json').write_text(json.dumps(decs,indent=2)+'\n')
 audit=ROOT/'tests/AxiomAudit.lean'
 audit.write_text('module\n'+''.join('public import '+m+'\n' for m in MODULES)+'\n'+''.join('#print axioms '+d['name']+'\n' for d in decs))
 inputs=sorted((ROOT/'formalization').glob('*.lean'))+sorted((ROOT/'tests').glob('*.lean'))+[Path(__file__).resolve()]
 before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
 lineage=json.loads((ROOT/'source_records/PARENT_LINEAGE.json').read_text())
 for name,h in lineage['inherited_sources'].items():
  if sha(ROOT/'formalization'/name)!=h:raise RuntimeError('Changed predecessor '+name)
 shutil.rmtree(ROOT/'build',ignore_errors=True);(ROOT/'build').mkdir()
 env=os.environ.copy();env['LEAN_PATH']=':'.join(map(str,[ROOT/'build',*(rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')]))
 logdir=ROOT/'evidence/lean_cold';logdir.mkdir(exist_ok=True)
 tasks=[];started=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
 def task(name,argv,expected=0):
  start=time.monotonic();timed=False
  try:
   p=subprocess.run(argv,cwd=ROOT/'formalization',env=env,capture_output=True,text=True,timeout=100)
   code=p.returncode;out=p.stdout+p.stderr
  except subprocess.TimeoutExpired as exc:
   code=-1;timed=True;out=str(exc.stdout)+'\nTIMEOUT'
  f=logdir/(name+'.log');f.write_text(out)
  good=(not timed) and ((code==0) if expected==0 else (code!=0))
  rec={'name':name,'argv':list(map(str,argv)),'exit_status':code,'expected':expected,'timed_out':timed,
   'passed':good,'runtime_seconds':time.monotonic()-start,'log':str(f.relative_to(ROOT)),'sha256':sha(f)}
  tasks.append(rec);print(json.dumps(rec),flush=True)
  (ROOT/'evidence/lean_progress.json').write_text(json.dumps({'status':'RUNNING' if good else 'FAILED','tasks':tasks},indent=2)+'\n')
  if not good:raise RuntimeError(name+': '+out)
  return out
 version=task('version',[str(lean),'--version']).strip()
 if '4.34.0-rc2' not in version:raise RuntimeError('Lean version mismatch')
 for m in MODULES:task('build_'+m,[str(lean),'-j1','-DwarningAsError=true','-o',str(ROOT/'build'/f'{m}.olean'),m+'.lean'])
 out=task('axioms',[str(lean),'-j1','-DwarningAsError=true',str(audit)])
 used=set()
 for block in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',out):used.update(s.strip() for s in block.split(',') if s.strip())
 if used-{'propext','Classical.choice','Quot.sound'}:raise RuntimeError('Unexpected axioms '+str(used))
 if any(d['name'] not in out for d in decs):raise RuntimeError('Missing axiom-audited declaration')
 for name,expected in CONTROLS.items():task('control_'+name,[str(lean),'-j1','-DwarningAsError=true',str(ROOT/'tests'/f'{name}.lean')],expected)
 after={str(p.relative_to(ROOT)):sha(p) for p in inputs}
 if before!=after:raise RuntimeError('Accepted inputs changed')
 result={'status':'PASS','started_at':started,'runtime_seconds':time.monotonic()-tick,'lean':version,'mathlib':commit,
  'lean_sha256':sha(lean),'modules':MODULES,'tasks':tasks,'named_declarations':len(decs),
  'counts':dict(Counter(d['kind'] for d in decs)),'new_counts':dict(Counter(d['kind'] for d in decs if d['module'] in NEW)),
  'axioms':sorted(used),'input_hashes_before':before,'input_hashes_after':after,
  'non_claims':['No cold rebuild of Mathlib','Python not formally verified','No unrestricted first-order elementarity',
   'Translation specifies a one-sorted relationalization, not a native many-sorted backend','Proof interpretation is self-review']}
 (ROOT/'results/LEAN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
 (ROOT/'evidence/lean_progress.json').write_text(json.dumps({'status':'COMPLETED','tasks':tasks},indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','named_declarations','counts','new_counts','axioms','runtime_seconds']},indent=2))
if __name__=='__main__':main()
