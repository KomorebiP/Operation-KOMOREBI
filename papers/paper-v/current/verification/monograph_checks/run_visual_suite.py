#!/usr/bin/env python3
"""Bounded-provenance replay of the two unchanged visual exact-example suites."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve()
with tempfile.TemporaryDirectory(prefix='paper-v-visual-provenance-') as temp:
    work=Path(temp)
    for rel in ['source/models.py','checks/verify_examples.py','checks/verify_extension_examples.py']:
        target=work/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'editable/visual_guide'/rel,target)
    counts=[]
    for script,name,n,k in [('verify_examples.py','EXACT_CHECKS.json',181,7),('verify_extension_examples.py','EXTENSION_EXACT_CHECKS.json',38,4)]:
        argv=[sys.executable,'-B',str(work/'checks'/script)]
        print('COMMAND',json.dumps(argv),flush=True)
        p=subprocess.run(argv,cwd=work,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
        (out/(script+'_command.log')).write_text(p.stdout)
        print(p.stdout,flush=True)
        if p.returncode:raise RuntimeError(f'{script} exited{p.returncode}')
        d=json.loads((work/'checks'/name).read_text())
        if d['status']!='PASS' or d['checks_passed']!=n or len(d['invalid_controls_rejected'])!=k:
            raise RuntimeError(f'{script} finite result contract failed')
        shutil.copy2(work/'checks'/name,out/name)
        counts.append({'script':script,'checks_passed':n,'false_controls_rejected':k})
    result={'status':'PASS','suites':counts,'arithmetic':'Exact integers,rationals,SymPy symbolic algebra and algebraic sqrt(2)','randomness_used':False,
            'lean_process_ran':False,'purpose':'Replay addresses missing bounded execution provenance in the earlier custom record. Same finite range; execution counts are not additional independent mathematical results.',
            'non_claim':'No universal recovery bound or new formal theorem follows from finite examples.'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
