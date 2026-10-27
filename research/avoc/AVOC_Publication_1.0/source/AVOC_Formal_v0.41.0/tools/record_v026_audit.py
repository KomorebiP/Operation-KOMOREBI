#!/usr/bin/env python3
"""Record a fresh evidence-collector run; does not time all prior proof/test runs."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/v0.26.0'
def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def inputs()->dict[str,str]:
    files=list((ROOT/'AVOC').glob('*.lean'))
    files += [ROOT/'checks/test_semantic_synthesis.py',ROOT/'checks/semantic/protocol.json',
              ROOT/'tools/run_semantic_synthesis.py',ROOT/'tools/summarize_v026.py',
              ROOT/'tools/record_semantic_cli.py',Path(__file__)]
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}
def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path)
    args=parser.parse_args()
    cmd=[sys.executable,str(ROOT/'tools/summarize_v026.py')]
    if args.baseline:cmd += ['--baseline',str(args.baseline.resolve())]
    before=inputs();start=datetime.now(timezone.utc).isoformat();t=time.monotonic()
    result=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=90)
    duration=time.monotonic()-t;after=inputs()
    (OUT/'collector_stdout.json').write_text(result.stdout)
    (OUT/'collector_stderr.txt').write_text(result.stderr)
    if result.returncode or before!=after:
        print(result.stderr,file=sys.stderr)
        raise RuntimeError('collector failed or inputs changed')
    provenance={'command':cmd,'started_at':start,'runtime_seconds':duration,
                'exit_status':result.returncode,'source_pins_before':before,'source_pins_after':after,
                'timing_scope':'evidence collection only; individual proof and experiment times are in their original records'}
    (OUT/'collector_execution.json').write_text(json.dumps(provenance,indent=2)+'\n')
    outputs=['results/v0.26.0/verification_summary.json','results/v0.26.0/semantic_tests/summary.json',
             'results/v0.26.0/cli/summary.json','results/v0.26.0/collector_execution.json',
             'results/v0.26.0/collector_stdout.json','results/v0.26.0/collector_stderr.txt']
    manifest={
      'schema_version':1,
      'claim_id':'AVOC-SEMANTIC-REUSE-v0.26.0',
      'repository':{'commit':'source release v0.26.0; v0.25 baseline SHA-256 543afa90b23ec54910abe46348fd82abb3b98582092b7e2e19e8713a2d005707','dirty':True},
      'command':cmd,
      'environment':{'software':['Python '+platform.python_version(),'Lean 4.34.0-rc2 (6a10ac8c22beadecabdbb0919c2b50214762f91d)',
                               'mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06'],
                     'hardware':platform.platform()+'; '+platform.machine()+'; container-reported logical CPUs '+str(os.cpu_count())},
      'mathematics':{
         'assertion_tested':'Formal semantic-library same-depth coverage/optimum preservation, prepaid structural budgets and promotion; independent exact finite executions compare feedback and frozen generation.',
         'coefficient_domain':'Boolean truth functions, exact Nat counts and budgets, Int accounting; elapsed seconds are measured floats, not theorem quantities.',
         'conventions':'Three ordered Boolean inputs, all eight valuations. Stable minimum-node representatives. Tariff emitted +10 node_mass+9 probes. Frozen and feedback share exact checker, constructors and index rules.',
         'inputs':['inherited BooleanProgram and BoundedSynthesis', 'new modules in source_counts.json',
                   'checks/semantic/protocol.json','all 256 truth functions in fixed DNF'],
         'bounds':{'matched_depths':[0,1,2],'feedback_extension_depth':3,'frozen_depth3_executed':False,
                   'query_cases':1792,'budget_cases':32,'equivalence_cases':512,'campaign_cases':27,
                   'invalid_wire_cases':12,'cli_cases':12,'timing_repetitions_per_arm':3,
                   'local_targets':144,'theorem_reports':1393,'negative_tests':67},
         'non_claims':['No autonomous self-modification or LLM calibration.','No universal physical-cost-optimal search.',
                       'No globally minimum unrestricted program for every truth function.','No fresh full-source mathlib rebuild.',
                       'No new durable semantic-cache/filesystem refinement or replay of older physical crash suites.']},
      'randomness':{'used':False,'generator':'none; fixed exhaustive input order','seed':None},
      'run':{'started_at':start,'runtime_seconds':duration,'exit_status':result.returncode},
      'outputs':[{'path':name,'sha256':sha(ROOT/name)} for name in outputs],
      'checks':['Current source/import/output/log hashes for every local target.','Exact theorem-name set and approved axiom union.',
                'All negative files reject without import errors/timeouts.','Independent bitset oracle and actual Lean outputs.',
                'Immutable inherited sources checked against baseline bytes.','Before/after collector source pin equality.'],
      'result':'PASS. Uniform results are established by Lean; the bounded independent execution range agrees. This manifest times collection, not the whole research run.',
      'residual_risks':['Trusted compiler/kernel/cache/runtime and host.','Incomplete structural cost model.',
                        'Read-only in-memory wrapper and unproved external IO correspondence.',
                        'Small one-host timing sample.','Legacy v1 metadata is supplemented by detailed per-run source/output hashes.']
    }
    (OUT/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'passed':True,'collector_seconds':duration,'outputs':len(outputs)},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
