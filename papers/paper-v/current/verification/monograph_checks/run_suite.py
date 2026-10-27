#!/usr/bin/env python3
"""Isolated replay of documented Paper V suites, without modifying source snapshots."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'source'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')

def invoke(argv, cwd, log):
    print('COMMAND',json.dumps(argv),'CWD',str(cwd),flush=True)
    result=subprocess.run(argv,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    log.write_text(result.stdout,encoding='utf-8')
    print(result.stdout,flush=True)
    if result.returncode:
        raise RuntimeError(f'command exited {result.returncode}: {argv}')
    return result.stdout

def clone(src,dst):
    shutil.copytree(src,dst,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache','.lake'))

def compare_values(a,b,path='',counts=None):
    if counts is None: counts={'floating_metrics':0,'nonfloating_leaves':0,'all_values_identical':True}
    counts['all_values_identical'] &= a == b
    if isinstance(a,dict):
        if not isinstance(b,dict) or a.keys()!=b.keys(): raise RuntimeError(f'keys differ: {path}')
        for k in a: compare_values(a[k],b[k],path+'/'+k,counts)
    elif isinstance(a,list):
        if not isinstance(b,list) or len(a)!=len(b): raise RuntimeError(f'length differs: {path}')
        for i,(x,y) in enumerate(zip(a,b)): compare_values(x,y,path+'/'+str(i),counts)
    elif isinstance(a,float):
        counts['floating_metrics']+=1
        if not isinstance(b,(int,float)) or not math.isfinite(b) or not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12):
            raise RuntimeError(f'floating metric differs: {path}, {a}, {b}')
    else:
        counts['nonfloating_leaves']+=1
        if type(a)!=type(b) or a!=b: raise RuntimeError(f'discrete leaf differs: {path}')
    return counts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--suite',required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    report={'suite':args.suite,'status':'STARTED','started_utc':datetime.now(timezone.utc).isoformat(),
            'lean_process_ran':False,'universal_proof_claimed':False}
    with tempfile.TemporaryDirectory(prefix='paper-v-current-replay-') as temp:
        tmp=Path(temp)
        if args.suite=='exact_and_verifier':
            work=tmp/'snapshot';clone(SOURCE/'complete/original_snapshot',work)
            invoke([sys.executable,'-B','-O','verification/verify.py','--static-only'],work,out/'command.log')
            for name in ['static_status.json','exact_model_results.json','second_block_results.json','verifier_controls_results.json']:
                shutil.copy2(work/'verification'/name,out/name)
            d=json.loads((out/'static_status.json').read_text())
            if d['status']!='STATIC_AND_EXACT_ONLY' or d['lean_kernel_checked']: raise RuntimeError('static scope status failed')
            exact=[json.loads((out/name).read_text()) for name in ['exact_model_results.json','second_block_results.json']]
            controls=json.loads((out/'verifier_controls_results.json').read_text())
            report.update(source_contract=d['gates']['source'],exact_tests=sum(r['tests_run'] for r in exact),
                          counted_assertions=sum(r['counted_assertions'] for r in exact),verifier_control_tests=controls['tests_run'],
                          arithmetic='Z and fractions.Fraction, including exact Q(sqrt(2)) pairs',
                          negative_controls='16 verifier test methods include one clean positive contract and deliberate corruptions; not16 invalid-case count')
        elif args.suite in ['current_pytest','historical_pytest']:
            src=SOURCE/'complete/original_snapshot/companion' if args.suite=='current_pytest' else SOURCE/'annals/verification/original_release'
            work=tmp/'companion';clone(src,work)
            invoke([sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider','--junitxml='+str(out/'junit.xml'),'tests'],work,out/'command.log')
            suites=ET.parse(out/'junit.xml').getroot();rows=list(suites.iter('testsuite'))
            totals={k:sum(int(row.attrib.get(k,0)) for row in rows) for k in ['tests','failures','errors','skipped']}
            expected=33 if args.suite=='current_pytest' else 27
            if totals!={'tests':expected,'failures':0,'errors':0,'skipped':0}: raise RuntimeError(f'pytest totals differ: {totals}')
            report.update(totals,arithmetic='NumPy IEEE float/complex values with the explicit original tolerances; some Boolean/index identity checks',
                          historical_overlap='27 historical tests overlap the current33 tests; their counts are not combined into distinct theorem or coverage totals')
        elif args.suite=='numerical_companion':
            src=SOURCE/'complete/original_snapshot/companion';work=tmp/'companion';clone(src,work)
            baseline=json.loads((src/'results/numerical_results.json').read_text())
            invoke([sys.executable,'-B','run_all.py'],work,out/'command.log')
            current=json.loads((work/'results/numerical_results.json').read_text())
            cmp=compare_values(baseline,current)
            if cmp['floating_metrics']!=52: raise RuntimeError(f'wrong metric count: {cmp}')
            for folder in ['results','tables','figures']: shutil.copytree(work/folder,out/folder)
            summary=json.loads((out/'results/run_summary.json').read_text())
            if summary['figure_file_count']!=36: raise RuntimeError('wrong regenerated figure count')
            figfiles=[p for p in (out/'figures').iterdir() if p.suffix in ['.pdf','.png']]
            if len(figfiles)!=36: raise RuntimeError('figure pair file set differs')
            write(out/'figure_hashes.json',[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p)} for p in sorted(figfiles)])
            report.update(cmp,comparison_rtol=1e-10,comparison_atol=1e-12,figure_pairs=18,
                          arithmetic='IEEE floating-point; numerical residuals, not exact algebraic certification',
                          historical_exact_certificates_key='Preserved original key is a historical label for floating residuals')
        elif args.suite=='annals_checker':
            work=tmp/'annals';clone(SOURCE/'annals',work)
            stdout=invoke([sys.executable,'-B','verification/verify_paper_v.py'],work,out/'command.log')
            m=re.search(r'Paper V revised verification: (\d+)/(\d+) checks passed in (\d+) groups',stdout)
            if not m or tuple(map(int,m.groups()))!=(11052,11052,13): raise RuntimeError('Annals result count differs')
            report.update(checks=11052,groups=13,arithmetic='Mixed integer/Boolean/source checks and NumPy floating checks with explicit original tolerances',
                          hygiene_scope='Final source-format group tests the immutable historical Annals source, not current monograph prose or layout',
                          dominant_count='10001 half-shift sampled positions; finite quadrature does not certify a universal bound')
        else: raise ValueError(args.suite)
    report['status']='PASS';report['finished_utc']=datetime.now(timezone.utc).isoformat();write(out/'result.json',report)
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
