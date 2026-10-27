#!/usr/bin/env python3
"""Run one pinned finite suite through the skill's bounded v2 evidence runner."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('suite',choices=['exact_and_verifier','current_pytest','historical_pytest','numerical_companion','annals_checker'])
args=ap.parse_args();base='verification/monograph_checks';contract=ROOT/base/'contracts'/f'{args.suite}.json'
data=json.loads(contract.read_text());out=f'{base}/runs/{args.suite}'
cmd=[sys.executable,'-B',str(ROOT/base/'tools/run_experiment.py'),'--root',str(ROOT),'--contract',str(contract),'--output',out,
     '--timeout','300','--max-output-bytes','1048576','--max-memory-bytes','8589934592','--max-cpu-seconds','240','--max-cores','1','--max-threads','1']
for path in data['execution_artifacts']:cmd.extend(['--input',path])
results=['result.json','command.log']
if args.suite=='exact_and_verifier':results.extend(['static_status.json','exact_model_results.json','second_block_results.json','verifier_controls_results.json'])
elif args.suite in ['current_pytest','historical_pytest']:results.append('junit.xml')
elif args.suite=='numerical_companion':results.extend(['results/numerical_results.json','results/run_summary.json','figure_hashes.json'])
for name in results:cmd.extend(['--result',f'{out}/{name}'])
cmd.extend(['--',sys.executable,'-B',f'{base}/run_suite.py','--suite',args.suite,'--out',out])
raise SystemExit(subprocess.call(cmd,cwd=ROOT))
