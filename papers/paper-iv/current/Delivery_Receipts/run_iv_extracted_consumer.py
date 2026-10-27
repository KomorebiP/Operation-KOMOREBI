from pathlib import Path
import json,subprocess,os,hashlib,time,signal,sys
sys.dont_write_bytecode=True
R=Path('/mnt/data/paper_iv_fresh_extraction/Paper_IV_Verification_Closeout_v1.1.0')
D=Path('/mnt/data/iv_extraction_consumer');D.mkdir(exist_ok=False)
rt=Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2')
paths=[str(R/'verification/lean_primary/objects')]+[str(rt/'workspace/.lake/packages'/p['name']/'.lake/build/lib/lean') for p in json.loads((R/'formalization/lean/lake-manifest.json').read_text())['packages']]
s=D/'ExtractedConsumer.lean';s.write_bytes(Path('/mnt/data/iv_extraction_consumer_attempt_A/ExtractedConsumer.lean').read_bytes())
cmd=[str(rt/'toolchain/bin/lean'),'-j1','-M3072','-DwarningAsError=true',str(s)]
start=time.monotonic();timed=False
with (D/'consumer.log').open('wb') as log:
 p=subprocess.Popen(cmd,cwd=R/'formalization/lean',stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,LEAN_PATH=os.pathsep.join(paths),MALLOC_ARENA_MAX='2'),start_new_session=True)
 try:code=p.wait(timeout=300)
 except subprocess.TimeoutExpired:timed=True;os.killpg(p.pid,signal.SIGKILL);code=p.wait()
text=(D/'consumer.log').read_text()
sys.path.insert(0,str(R/'scripts'))
from replay_lean import check_axiom_reports
try:
 axioms=check_axiom_reports(text,{'Komorebi.PaperIV.cyclicProjector_idempotent','Komorebi.PaperIV.cyclicAlgebra_pointwise_exponential'})
 status='PASS' if code==0 and not timed and text.count('PAPER_IV_EXTRACTED_IMPORT_PASS')==1 else 'FAILED'
except Exception as e:
 axioms={'error':str(e)};status='FAILED'
result={'status':status,'argv':cmd,'returncode':code,'timed_out':timed,'timeout_seconds':300,'seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256((D/'consumer.log').read_bytes()).hexdigest(),'axioms':axioms,'scope':'Fresh import, real projector application and two axiom queries against hash-verified packaged objects. Not a second 118-module source compilation.','prior_attempt':'Initial same-source consumer was killed at a 30-second budget; that attempt remains failed.'}
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
