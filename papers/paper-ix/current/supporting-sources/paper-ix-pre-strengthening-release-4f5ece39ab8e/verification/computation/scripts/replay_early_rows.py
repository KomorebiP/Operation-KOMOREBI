#!/usr/bin/env python3
"""Run the unchanged archived exact Python exploration and compare its output."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,required=True)
parser.add_argument('--recorded-log',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
run=subprocess.run([sys.executable,str(args.source)],capture_output=True,text=True,check=True,timeout=30)
expected='0 78 []\n1 78 []\n2 78 []\n3 78 []\nodd zero-row difference: -2 valuation: 0\n'
if run.stdout!=expected or run.stdout.encode()!=args.recorded_log.read_bytes() or run.stderr:
    raise AssertionError('Unchanged archived exploration did not reproduce exactly')
args.output.write_text(json.dumps({'status':'PASS_IN_STATED_FINITE_RANGE','actual_child_argv':[sys.executable,str(args.source)],'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'stdout':run.stdout,'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'recorded_log_sha256':hashlib.sha256(args.recorded_log.read_bytes()).hexdigest(),'exact_period_congruence_cases':312,'mathematical_negative_controls':1,'bounds':{'j':[0,1,2,3],'r':[1,2,3,4,5,6],'n':list(range(13)),'coefficient_rows_computed':64},'non_claims':['No new Lean acceptance','No universal proof','No least-period conclusion from these samples'],'interpretation':'Unchanged historical exact recurrence and its stated finite assertion reproduced; stdout matches the preserved historical log byte for byte.'},indent=2)+'\n')
print('PASS: 312 exact cases and one odd-prime boundary; historical stdout byte-identical')
