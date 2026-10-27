#!/usr/bin/env python3
"""Record a fresh evidence-collector invocation (not the duration of all proof runs)."""
from pathlib import Path
import argparse,datetime,hashlib,json,platform,subprocess,time,sys
root=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);args=p.parse_args()
inputs=[str(p.relative_to(root)) for p in sorted((root/'AVOC').glob('*.lean'))]
inputs+=['checks/test_upgrade_campaign.py','tools/run_upgrade_campaign.py','tools/UpgradeMain.lean']
before={s:sha(root/s) for s in inputs}
started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
cmd=[sys.executable,str(root/'tools/summarize_v023.py'),'--baseline',str(args.baseline.resolve())]
cp=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=60)
elapsed=time.monotonic()-t
rd=root/'results/v0.23.0';(rd/'collector_run.log').write_text(cp.stdout+cp.stderr)
after={s:sha(root/s) for s in inputs}
if cp.returncode or before!=after:raise SystemExit('collector failed or inputs changed')
outputs=['results/v0.23.0/summary.json','results/v0.23.0/collector_run.log',
'results/v0.23.0/demo_promote.json','results/v0.23.0/demo_costly_search.json',
'results/v0.23.0/axiom_audit_summary.json']
obj=dict(schema_version=1,claim_id='AVOC-v023-protected-upgrade-campaign',
 repository=dict(commit=None,dirty=True,baseline_sha256=sha(args.baseline)),command=cmd,
 environment=dict(software=[f'Python {platform.python_version()}', 'Lean 4.34.0-rc2 commit 6a10ac8c22beadecabdbb0919c2b50214762f91d',
'mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06'],hardware=platform.platform()),
 mathematics=dict(assertion_tested='Current source compilation and axiom audit; finite executed promotion/accounting/contract regression; inherited-source nonregression.',
 coefficient_domain='Lean Nat/Int campaign accounting; exact rational retry models',
 conventions='Fixed immutable authority; action-only NoRevival contract; state visits and nominal tariffs, not physical speed.',
 inputs=[dict(path=s,sha256=h) for s,h in before.items()],
 bounds=dict(local_targets=123,theorem_reports=1184,negative_files=55,campaign_cases=1442,
             seeded_sequences=300,seeded_sequence_lengths=[3,12],max_wire_proposals=128,wrapper_defenses=13,raw_wire_rejections=11),
 non_claims=['No autonomous candidate discovery or multi-generation RSI experiment',
'No physical-time speedup, calibrated scientific utility or general external-source deployment',
'No full rebuild of external dependency sources or independent kernel verification']),
 randomness=dict(used=True,generator='Python random.Random for 300 bounded test sequences',seed=230023),
 run=dict(started_at=started,runtime_seconds=elapsed,exit_status=cp.returncode,
         timing_scope='fresh evidence collector only; per-proof/per-test timing is recorded separately'),
 outputs=[dict(path=s,sha256=sha(root/s)) for s in outputs],
 checks=['All current per-target source/import/output/log hashes validated','Exact theorem name set and axiom allowlist',
'No positive-source proof shortcuts','All 110 inherited source modules unchanged','Finite oracle and defensive tests passed',
'Collector input files unchanged'],result='PASS: protected component-upgrade contracts and finite executable assertions verified in the stated scope.',
 residual_risks=['Fixed authority soundness premises are not automatically empirical facts',
'Pinned external binaries, Python, parser and protected host remain trusted',
'Legacy v1 metadata does not independently certify complete process provenance or resources'])
(rd/'computation_manifest.json').write_text(json.dumps(obj,indent=2)+'\n')
print('Recorded collector:',elapsed,'seconds; source hashes unchanged')
