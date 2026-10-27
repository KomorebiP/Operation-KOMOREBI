#!/usr/bin/env python3
"""Record a fresh evidence-collector run; does not time past proof compilations."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,json,platform,subprocess,sys,time
R=Path(__file__).resolve().parents[1];D=R/'results/v0.22.0'
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);a=p.parse_args()
cmd=[sys.executable,str(R/'tools/summarize_v022.py'),'--baseline',str(a.baseline.resolve())]
start=datetime.now(timezone.utc).isoformat();t=time.monotonic()
run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);elapsed=time.monotonic()-t
(D/'collector_final.log').write_text(run.stdout+run.stderr)
if run.returncode:raise SystemExit(run.returncode)
summary=json.loads((D/'verification_summary.json').read_text())
outputs=['verification_summary.json','negative_final.json','advisor_regression.json','full_axiom_audit.log','collector_final.log']
manifest={'schema_version':1,'claim_id':'AVOC-v022-retry-model-and-runtime-evidence',
 'repository':{'commit':None,'dirty':True,'baseline_archive_sha256':summary['baseline_sha256']},
 'command':cmd,'environment':{'software':[f'Python {platform.python_version()}','Lean 4.34.0-rc2','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06'],
 'hardware':platform.platform()},
 'mathematics':{'assertion_tested':'Current-source proof/audit records and exact bounded retry-advisor differential results agree with delivered sources.',
 'coefficient_domain':'Exact rational arithmetic and finite natural resource ledgers',
 'conventions':'True outcome means operational resolution, NOT proof admission; stopped ties; full-L1 and fixed conditional-iid reliability model.',
 'inputs':['results/v0.22.0/build_order.json','results/v0.22.0/declaration_inventory.json','results/v0.22.0/advisor_requests.jsonl'],
 'bounds':{'local_targets':119,'theorems':1132,'negative_tests':50,'runtime_model_cases':5891,'runtime_horizon_limit':32},
 'non_claims':['Collector runtime is not the elapsed proof or regression runtime.','No empirical calibration, live retry authorization, power-failure guarantee, or full external-cache source rebuild.']},
 'randomness':{'used':False,'generator':'none','seed':None},
 'run':{'started_at':start,'runtime_seconds':elapsed,'exit_status':run.returncode},
 'outputs':[{'path':str((D/f).relative_to(R)),'sha256':hashlib.sha256((D/f).read_bytes()).hexdigest()} for f in outputs],
 'checks':['119 current compilations','1132 exact-name axiom reports','50 substantive negative tests','104 unchanged inherited modules','5891 exact runtime cases plus phase/schema rejections'],
 'result':'All current collector assertions passed.',
 'residual_risks':['Pinned external cache, Lean runtime and host trusted.','Python I/O and parser/runtime correspondence are tested, not universally formally refined.','Legacy manifest v1 has weaker provenance requirements than v2.']}
(D/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Recorded fresh collector only:',elapsed,'seconds')
