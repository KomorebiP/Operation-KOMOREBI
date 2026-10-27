"""Portable bounded replay of the bundled H12 checks; run from an extracted final package."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess,sys
packet=Path(__file__).resolve().parent;release=packet.parents[1]
sys.path.insert(0,str(packet/'dependencies'))
ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['exact','numerical40','numerical70','independent','visual','continuation','provenance'],required=True);a=ap.parse_args()
group=a.group
contracts={'independent':'independent_centered','visual':'visual','continuation':'continuation','provenance':'provenance_complete'}
c=json.loads((packet/'contracts'/f'{contracts.get(group,group)}.json').read_text())
rel=lambda p:str(p.relative_to(release))
if group in ['exact','numerical40','numerical70']:
 script=packet/'checks/run_copied_check.py';inputs=[script,packet/'v014_copy/checks'/('exact_checks.py' if group=='exact' else 'numerical_checks.py')]
 if group!='exact':inputs += [packet/'v014_copy/prior/gamma_evaluator.py',packet/'v014_copy/prior/v012_numerical_checks.py']
 command=[sys.executable,rel(script),'--mode',group]
elif group=='independent':
 script=packet/'checks/independent_checks.py';inputs=[script,packet/'v014_copy/checks/exact_checks.py',packet/'v014_copy/prior/gamma_evaluator.py'];command=[sys.executable,rel(script)]
elif group=='visual':
 script=packet/'checks/verify_visual_values.py';inputs=[script,release/'visual/finite_control.json',release/'visual/generate_figures.py'];command=[sys.executable,rel(script),'--control','visual/finite_control.json']
elif group=='continuation':
 script=packet/'checks/continuation_diagnostics.py';inputs=[script,packet/'v014_copy/prior/gamma_evaluator.py'];command=[sys.executable,rel(script)]
else:
 # Recreate only archived ZIP aliases named by the historical intake record.
 # Sources stay unchanged; existing aliases must match their pinned bytes.
 intake=json.loads((release/'provenance/ARCHIVE_INTAKE.json').read_text())
 for row in intake['source_chain']:
  dest=(release/row['archive']).resolve();assert dest.is_relative_to(release.resolve())
  if not dest.is_file():
   candidates=list((release/'sources').rglob(Path(row['archive']).name));assert len(candidates)==1
   assert hashlib.sha256(candidates[0].read_bytes()).hexdigest()==row['sha256']
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(candidates[0],dest)
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==row['sha256']
 script=packet/'checks/provenance_audit.py';inputs=[script,packet/'runner/validate_manifest.py']+[p for p in sorted((release/'sources').rglob('*.json')) if p.name.lower()=='manifest.json' or p.name.endswith('_manifest.json') or p.name.endswith('_receipt.json')]+[release/'provenance/ARCHIVE_INTAKE.json'];command=[sys.executable,rel(script),'--release','.']
paths=[rel(p) for p in inputs];c['execution_artifacts']=paths;c['mathematics']['inputs']=paths
c['software']=[{'name':'Python','version':sys.version.split()[0]}]
for name in ['sympy','mpmath']:
 try:m=__import__(name);c['software'].append({'name':name,'version':m.__version__})
 except ImportError:
  if group!='provenance':raise
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');base=packet/'replay_results';base.mkdir(exist_ok=True)
contract=base/f'{group}-{stamp}.contract.json';contract.write_text(json.dumps(c,indent=2)+'\n');out=base/f'{group}-{stamp}';result=out/'result.json'
argv=[sys.executable,str(packet/'runner/run_experiment.py'),'--root',str(release),'--contract',str(contract)]
for path in paths:argv+=['--input',path]
short=group in ['visual','continuation']
argv+=['--output',rel(out),'--result',rel(result),'--timeout','60' if short else '120','--max-output-bytes','1048576','--max-memory-bytes','1073741824','--max-cpu-seconds','45' if short else '90','--max-cores','1','--max-threads','1','--']+command+['--result',rel(result)]
raise SystemExit(subprocess.call(argv,cwd=release))
