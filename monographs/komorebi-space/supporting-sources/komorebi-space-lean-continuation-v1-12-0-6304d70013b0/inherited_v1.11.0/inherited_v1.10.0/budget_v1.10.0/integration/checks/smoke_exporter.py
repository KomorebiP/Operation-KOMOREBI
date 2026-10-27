#!/usr/bin/env python3
"""Compatibility smoke only: run exact exporter on one accepted parent module."""
from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path(__file__).resolve().parents[3]
run=root/'budget_v1.10.0/integration/development/exporter_smoke_01'
run.mkdir(parents=True,exist_ok=False)
helper=root/'budget_v1.10.0/integration/scripts/ExportAudit.lean'
(run/'ExportAudit.lean').write_bytes(helper.read_bytes())
(run/'wanted_modules.txt').write_text('KomorebiSpace.BoundedApproximateRealization\n')
(run/'type_modules.txt').write_text('KomorebiSpace.BoundedApproximateRealization\n')
(run/'type_names.txt').write_text('')
base=root/'continuation/integration/runs/wr01_wr02_overlay_01'
old=json.loads((base/'receipt.json').read_text())
env=dict(os.environ);env.update(old['environment']);env['KS_COMBINED_AUDIT']=str(run/'axioms.json')
cmd=[str(Path(old['runtime'])/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-DautoImplicit=false',str(run/'ExportAudit.lean')]
start=time.monotonic()
with (run/'stdout.log').open('w') as out:
 p=subprocess.run(cmd,cwd=run,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=180)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'scope':'One inherited module exporter compatibility smoke; not new or cumulative proof replay',
   'argv':cmd,'cwd':str(run),'exit_code':p.returncode,'seconds':time.monotonic()-start,
   'helper_sha256':h(helper),'copied_helper_sha256':h(run/'ExportAudit.lean'),
   'log_sha256':h(run/'stdout.log'),'environment':{k:env[k] for k in ('LEAN_PATH','LD_PRELOAD','KS_COMBINED_AUDIT')}}
if p.returncode==0:
 a=json.loads((run/'axioms.json').read_text());r['count']=a['count'];r['unexpected']=a['unexpected']
 r['all_types_nonempty_untruncated']=all(x['type'] and '⋯' not in x['type'] for x in a['declarations'])
 r['axiom_report_sha256']=h(run/'axioms.json')
r['status']='PASS' if p.returncode==0 and r['all_types_nonempty_untruncated'] and not r['unexpected'] else 'FAIL'
(run/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
