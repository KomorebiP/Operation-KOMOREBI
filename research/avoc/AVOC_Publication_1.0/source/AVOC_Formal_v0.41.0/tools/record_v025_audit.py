#!/usr/bin/env python3
"""Record a fresh evidence-collector run, not the duration of all previous checks."""
from pathlib import Path
import argparse,datetime,hashlib,json,platform,sqlite3,subprocess,sys,time
R=Path(__file__).resolve().parents[1];rd=R/'results/v0.25.0'
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=sorted(list((R/'AVOC').glob('*.lean'))+[R/'tools/SynthesisMain.lean',
 R/'tools/synthesize_upgrade.py',R/'checks/test_synthesis.py',R/'tools/summarize_v025.py'])
before={str(p.relative_to(R)):sha(p) for p in sources}
start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
cmd=[sys.executable,str(R/'tools/summarize_v025.py'),'--baseline',str(a.baseline.resolve())]
out=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=100)
log=rd/'final_collector.log';log.write_text(out.stdout+out.stderr)
after={str(p.relative_to(R)):sha(p) for p in sources}
if out.returncode or before!=after:raise RuntimeError(out.stdout+out.stderr+'\nsource check: '+str(before==after))
s=json.loads((rd/'summary.json').read_text())
outputs=[rd/'summary.json',rd/'axiom_audit_summary.json',rd/'differential_summary.json',
 rd/'live_summary.json',rd/'differential_provenance.json',rd/'live_provenance.json',
 rd/'final_cli_search.json',rd/'final_cli_invoke.json',log]
m={'schema_version':1,'claim_id':'AVOC-v0.25-bounded-generated-program-synthesis',
 'repository':{'commit':None,'dirty':True,'baseline_archive_sha256':sha(a.baseline)},
 'command':cmd,
 'environment':{'software':['Python '+platform.python_version(),'SQLite '+sqlite3.sqlite_version,
 'Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d',
 'mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06'],
 'hardware':platform.platform()+'; '+platform.machine()},
 'mathematics':{
 'assertion_tested':'Current proof-source and imported-output records, complete theorem axiom census, substantive negatives and independent exact synthesis/store evidence support the stated bounded proposer and protected promotion contracts.',
 'coefficient_domain':'Three Boolean inputs; exact Nat/Int costs and finite grammar; inherited rational retry semantics.',
 'conventions':'Equivalence is exhaustive on all eight inputs. Eager AST visits differ from complete physical costs. Candidate generation/evaluation is charged; a smaller component can still have negative total net. Collector time is NOT full build/test time.',
 'inputs':[{'path':str(a.baseline.resolve()),'sha256':sha(a.baseline)},'117 byte-identical inherited modules',
 '74 new declarations','retained exact oracle requests and actual Lean outputs'],
 'bounds':{'local_targets':s['local_targets'],'theorem_axiom_reports':s['total_theorems'],
 'negative_files':s['negative_tests'],'grammar_depth_max':2,'runtime_prefix_max':21845,
 'campaign_cases':747,'checker_comparisons':255,'full_input_checks':5976,'invalid_wire_cases':10,'live_cases':16},
 'non_claims':['No arbitrary-source deployment, new Boolean-identity discovery or autonomous recursive improvement.',
 'No universal Python/SQLite/filesystem refinement, rollback protection or power-loss certification.',
 'Controlled exception tests are not SIGKILL process-crash tests.',
 'Protected integer tariffs and declared call counts are not calibrated full physical costs.',
 'No independent kernel or full external mathlib source rebuild.']},
 'randomness':{'used':False,'generator':'Deterministic collector and exhaustive stated test families; no random sampling.','seed':None},
 'run':{'started_at':start,'runtime_seconds':time.monotonic()-t,'exit_status':out.returncode},
 'outputs':[{'path':str(x.relative_to(R)),'sha256':sha(x)} for x in outputs],
 'checks':[{'name':'all recorded input source hashes unchanged during collection','passed':before==after},s],
 'result':'PASS: source claims and bounded implementation evidence verified under the documented contracts.',
 'residual_risks':['Protected authority and host remain trusted.','Complete physical costs and model usefulness are not inferred.',
 'Old release test directories are historical; earlier live suites were not rerun in this block.']}
(rd/'computation_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
(rd/'collector_source_hashes.json').write_text(json.dumps({'before':before,'after':after},indent=2)+'\n')
print(json.dumps(s,indent=2))
