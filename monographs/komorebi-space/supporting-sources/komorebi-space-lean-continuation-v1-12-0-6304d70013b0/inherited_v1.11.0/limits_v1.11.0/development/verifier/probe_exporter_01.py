"""Development-only exporter probe using accepted parent objects, not clean replay."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, time
here=Path(__file__).resolve().parent
attempt=here/'exporter_probe_01'
attempt.mkdir()
root=here.parents[2]
base=root/'budget_v1.10.0/integration/runs/clean_budget_01'
runtime=root/'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
exporter=here.parents[1]/'integration/scripts/ExportAudit.lean'
for name in ['wanted_modules.txt','type_modules.txt','type_names.txt']:
    shutil.copyfile(base/'source'/name,attempt/name)
shutil.copyfile(exporter,attempt/'ExportAudit.lean')
(attempt/'new_modules.txt').write_text('KomorebiSpace.BudgetRobustness\n')
pins=json.loads((base/'source/pinned-dependencies.json').read_text())['packages']
env=dict(os.environ)
for k in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME','LD_PRELOAD','LD_LIBRARY_PATH']:env.pop(k,None)
caches=[runtime/'workspace/.lake/packages'/p['name']/'.lake/build/lib/lean' for p in pins]
env['LEAN_PATH']=os.pathsep.join(str(p) for p in [base/'build']+caches if p.is_dir())
env['LD_PRELOAD']=str(runtime/'compat/app_path.so')
env['KS_COMBINED_AUDIT']=str(attempt/'axioms.json')
argv=[str(runtime/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-DautoImplicit=false',str(attempt/'ExportAudit.lean')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rec={'status':'RUNNING','clean_replay':False,'purpose':'Exporter option branching and complete parent axiom scope probe using accepted cached project objects','argv':argv,'cwd':str(attempt),'environment':{k:env[k] for k in ['LEAN_PATH','LD_PRELOAD','KS_COMBINED_AUDIT']},'source_sha256':{p.name:sha(p) for p in attempt.iterdir() if p.is_file()},'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(attempt/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
start=time.monotonic()
with (attempt/'compiler.log').open('x') as log:
    proc=subprocess.run(argv,cwd=attempt,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900)
rec.update(exit_code=proc.returncode,seconds=round(time.monotonic()-start,3),status='PASS' if proc.returncode==0 else 'FAIL',log_sha256=sha(attempt/'compiler.log'))
if proc.returncode==0:
    data=json.loads((attempt/'axioms.json').read_text());rows=data['declarations']
    modes={k:sum(r['type_mode']==k for r in rows) for k in ['full','readable','omitted']}
    rec.update(declarations=len(rows),type_modes=modes,unexpected=data['unexpected'],axiom_report_sha256=sha(attempt/'axioms.json'),axiom_report_bytes=(attempt/'axioms.json').stat().st_size)
rec['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(attempt/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps(rec,indent=2))
