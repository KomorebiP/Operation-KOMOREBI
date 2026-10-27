#!/usr/bin/env python3
"""Time and hash a fresh evidence-collection run. This is not the duration of
all underlying proof and process tests; their records are retained separately.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,platform,sqlite3,subprocess,sys,time
R=Path(__file__).resolve().parents[1];rd=R/'results/v0.24.0'
a=argparse.ArgumentParser();a.add_argument('--baseline',type=Path,required=True);ns=a.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(list((R/'AVOC').glob('*.lean'))+[R/'tools/durable_upgrade_campaign.py',R/'checks/test_durable_upgrade.py'])
before={str(p.relative_to(R)):sha(p) for p in files}
start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
cmd=[sys.executable,str(R/'tools/summarize_v024.py'),'--baseline',str(ns.baseline)]
p=subprocess.run(cmd,capture_output=True,text=True)
log=rd/'final_collector.log';log.write_text(p.stdout+p.stderr)
after={str(p.relative_to(R)):sha(p) for p in files}
assert p.returncode==0,p.stdout+p.stderr
assert before==after,'source changed during evidence collection'
summary=json.loads((rd/'summary.json').read_text())
outputs=[rd/'summary.json',rd/'axiom_audit_summary.json',rd/'tests/differential.json',rd/'tests/oracle_requests.json',rd/'tests/oracle_stdout.json',log]
manifest={'schema_version':1,'claim_id':'AVOC-v0.24-durable-prepaid-promotion',
 'repository':{'commit':None,'dirty':True,'baseline_archive_sha256':sha(ns.baseline)},
 'command':cmd,'environment':{'software':['Python '+platform.python_version(),'SQLite '+sqlite3.sqlite_version,
  'Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06'],
  'hardware':platform.platform()+'; '+platform.machine()},
 'mathematics':{'assertion_tested':'Current local proof records and complete bounded oracle/process evidence support the prepaid journal, source-fixed catalogue dispatch, replay and nominal accounting claims.',
 'coefficient_domain':'Nat and Int for generic accounting; inherited exact rational retry model',
 'conventions':'One protected pending evaluation. BEGIN reserves tariff; FINISH settles original gate; ABANDON retains reservation. Replay may recheck pure proofs. Collector time is not whole campaign time.',
 'inputs':[{'path':str(ns.baseline),'sha256':sha(ns.baseline)},'113 unchanged baseline non-audit modules','52 new declarations','retained exact oracle requests and outputs'],
 'bounds':{'local_targets':summary['local_targets'],'theorem_axiom_reports':summary['total_theorems'],'negative_files':summary['negative_tests'],
           'oracle_cases':summary['differential_cases'],'live_scenarios':summary['live_cases'],'process_exit_scenarios':summary['process_exit_scenarios'],'oracle_seed':240024},
 'non_claims':['No arbitrary-source deployment or autonomous improvement','No universal Python/SQLite/filesystem refinement','Process crashes are not power-loss certification','Tariffs are not full physical costs','No independent kernel or full mathlib source rebuild']},
 'randomness':{'used':False,'generator':'Evidence collector is deterministic; underlying retained oracle generation uses Python Random seed 240024.','seed':None},
 'run':{'started_at':start,'runtime_seconds':time.monotonic()-t,'exit_status':p.returncode},
 'outputs':[{'path':str(x.relative_to(R)),'sha256':sha(x)} for x in outputs],
 'checks':[{'name':'source bytes unchanged during collection','passed':before==after},summary],
 'result':'PASS: compiled statements and bounded implementations checked within the stated scope.',
 'residual_risks':['Fixed protected authority and correct utility bounds are premises.','Runtime, cache, SQL, host and physical snapshot origin are trusted.','Historical test suites not rerun for this block.']}
(rd/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(rd/'collector_source_hashes.json').write_text(json.dumps({'before':before,'after':after},indent=2)+'\n')
print(json.dumps(summary,indent=2))
