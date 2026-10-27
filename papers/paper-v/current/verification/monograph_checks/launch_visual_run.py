#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2];base='verification/monograph_checks';contract=ROOT/base/'contracts/visual_exact.json';data=json.loads(contract.read_text());out=base+'/runs/visual_exact'
cmd=[sys.executable,'-B',str(ROOT/base/'tools/run_experiment.py'),'--root',str(ROOT),'--contract',str(contract),'--output',out,
     '--timeout','300','--max-output-bytes','1048576','--max-memory-bytes','8589934592','--max-cpu-seconds','240','--max-cores','1','--max-threads','1']
for p in data['execution_artifacts']:cmd.extend(['--input',p])
for name in ['result.json','EXACT_CHECKS.json','EXTENSION_EXACT_CHECKS.json','verify_examples.py_command.log','verify_extension_examples.py_command.log']:cmd.extend(['--result',out+'/'+name])
cmd.extend(['--',sys.executable,'-B',base+'/run_visual_suite.py','--out',out]);raise SystemExit(subprocess.call(cmd,cwd=ROOT))
