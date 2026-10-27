"""Fresh-build replay of all reusable modules, the large example and all controls.

This is a SELECTED replay, not a second compilation of the entire 202-instance
suite. The complete suite is handled by verify_lean.py and its retained ledger.
The JSON result is written only to the caller-supplied external output path.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,platform,re,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
MODULES=['RepresentationCore','FiniteCertificates','InvariantCertificates','ConcreteExamples','GeneratedProfile',
 'MatrixCore','MatrixCertificates','MatrixSmith','MatrixRowWitnesses','CardinalityCore','GeneratedLarge','LargeCardinality']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 lean=str(Path(a.lean).resolve());version=subprocess.run([lean,'--version'],capture_output=True,text=True,check=True).stdout.strip()
 if '4.34.0-rc2' not in version:raise ValueError('wrong pinned toolchain')
 out=Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 logdir=out.parent/(out.stem+'_logs');logdir.mkdir(parents=True,exist_ok=True)
 files=[ROOT/'formalization'/(m+'.lean') for m in MODULES]+sorted((ROOT/'controls').glob('*.lean'))+[Path(__file__)]
 before={str(f.relative_to(ROOT)):sha(f) for f in files};tasks=[];tick=time.monotonic();started=datetime.now(timezone.utc).isoformat()
 with tempfile.TemporaryDirectory(prefix='krc03-extracted-lean-') as tmp:
  env=os.environ.copy();env['LEAN_PATH']=tmp
  def run(label,args,accept=True):
   t=time.monotonic();p=subprocess.run([lean,*args],cwd=ROOT/'formalization',env=env,capture_output=True,text=True,timeout=45)
   log=logdir/(label+'.log');log.write_text(p.stdout+p.stderr)
   ok=(p.returncode==0)==accept;tasks.append({'name':label,'expected':'accept' if accept else 'reject','exit_code':p.returncode,'passed':ok,'seconds':time.monotonic()-t,'log_sha256':sha(log)})
   if not ok:raise RuntimeError(label+': '+(p.stdout+p.stderr)[-1500:])
   return p.stdout+p.stderr
  names=[]
  for m in MODULES:
   run('build_'+m,['-DwarningAsError=true','-o',str(Path(tmp)/(m+'.olean')),m+'.lean'])
   ns=''
   for line in (ROOT/'formalization'/(m+'.lean')).read_text().splitlines():
    q=re.match(r'^namespace\s+(\S+)',line)
    if q:ns=q.group(1)
    q=re.match(r'^(?:noncomputable\s+)?(?:def|abbrev|theorem|structure|instance)\s+([A-Za-z_][A-Za-z0-9_.]*)',line)
    if q:names.append(ns+'.'+q.group(1))
  audit=Path(tmp)/'Audit.lean';audit.write_text('\n'.join('import '+m for m in MODULES)+'\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
  text=run('axioms',[str(audit)]);used=set()
  for q in re.finditer(r'depends on axioms:?\s*\[([^\]]*)\]',text):used.update(z.strip() for z in q.group(1).split(',') if z.strip())
  if used-{'Classical.choice','Quot.sound','propext'} or any(n not in text for n in names):raise RuntimeError('axiom audit invalid')
  for c in sorted((ROOT/'controls').glob('*.lean')):run('control_'+c.stem,['-DwarningAsError=true',str(c)],c.stem=='Positive')
 after={str(f.relative_to(ROOT)):sha(f) for f in files}
 if before!=after:raise RuntimeError('inputs changed')
 result={'status':'PASS','scope':'selected fresh replay: all reusable modules, old finite example, new large symbolic example, compact cardinality proof, complete control set; not all 202 generated instances',
  'modules':len(MODULES),'declarations':len(names),'tasks':tasks,'axioms':sorted(used),'toolchain':version,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
  'runtime_seconds':time.monotonic()-tick,'inputs_unchanged':True,'input_hashes':before,'script_sha256':sha(Path(__file__))}
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('tasks','input_hashes')},indent=2))
if __name__=='__main__':main()
