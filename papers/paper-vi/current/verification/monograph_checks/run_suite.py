#!/usr/bin/env python3
"""Replay documented Paper VI finite suites in disposable copies.

The unchanged recovered source trees are execution inputs, never work areas.
This wrapper records finite computation scope and does not execute Lean.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'source'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(p): return {x.relative_to(p).as_posix(): digest(x) for x in sorted(p.rglob('*')) if x.is_file()}
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
def clone(src, dst):
    # Caches are excluded only from disposable copies, never removed from originals.
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache', '.lake'))
def invoke(argv, cwd, log, timeout=240):
    print('COMMAND', json.dumps(argv), 'CWD', str(cwd), flush=True)
    p = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=timeout)
    log.write_text(p.stdout, encoding='utf-8')
    print(p.stdout, flush=True)
    if p.returncode: raise RuntimeError(f'command exited {p.returncode}: {argv}')
    return p.stdout
def flatten(x, p=''):
    if isinstance(x, dict): return {kk:vv for k,v in x.items() for kk,vv in flatten(v, p+'/'+str(k)).items()}
    if isinstance(x, list): return {kk:vv for k,v in enumerate(x) for kk,vv in flatten(v, p+'/'+str(k)).items()}
    return {p:x}

def reconcile(out):
    mapping = {'complete':'Paper_VI_Complete_v0.5.0_With_Visual_Appendix.zip',
               'strengthened':'PSC_Paper_VI_Strengthened_Annals_Edition_Package.zip',
               'annals':'PSC_Paper_VI_Annals_Human_Edition_Package.zip'}
    archives = []
    for branch, name in mapping.items():
        archive = ROOT/'downloads'/name
        with zipfile.ZipFile(archive) as z:
            bad = z.testzip()
            if bad is not None: raise RuntimeError('ZIP CRC failure: '+bad)
            files = [n for n in z.namelist() if not n.endswith('/')]
            prefix = files[0].split('/')[0]+'/'
            if not all(n.startswith(prefix) for n in files): raise RuntimeError('Multiple ZIP roots')
            expected = {n[len(prefix):]: hashlib.sha256(z.read(n)).hexdigest() for n in files}
            if len(expected) != len(files): raise RuntimeError('Duplicate archive file')
        actual = tree(SOURCE/branch)
        if expected != actual: raise RuntimeError('Archive extraction mismatch: '+branch)
        archives.append({'branch':branch, 'archive':'downloads/'+name,
                         'sha256':digest(archive), 'bytes':archive.stat().st_size,
                         'files':len(expected), 'crc':'PASS', 'exact_file_set_and_byte_match':True})
    snapshot = SOURCE/'complete/original_snapshot'
    pins = json.loads((SOURCE/'complete/verification/ORIGINAL_SNAPSHOT_HASHES.json').read_text())
    if pins != tree(snapshot): raise RuntimeError('534-file snapshot pin mismatch')
    nested = []
    for path, key, prefix in [('complete/FILE_MANIFEST.json','files','complete'),
                             ('complete/original_snapshot/RELEASE_MANIFEST.json','sha256','complete/original_snapshot')]:
        data = json.loads((SOURCE/path).read_text())[key]
        failures = [rel for rel,h in data.items() if not (SOURCE/prefix/rel).is_file() or digest(SOURCE/prefix/rel)!=h]
        if failures: raise RuntimeError('Nested manifest mismatch '+path+': '+repr(failures))
        nested.append({'path':'source/'+path,'hashes_checked':len(data),'status':'PASS'})
    return {'status':'PASS','source_files':len(tree(SOURCE)), 'original_snapshot_files':len(pins),
            'archives':archives, 'nested_manifests':nested, 'source_sha256':tree(SOURCE),
            'downloads_sha256':tree(ROOT/'downloads'), 'missing_current_source_files':[],
            'scope':'Current recovered source/archive identities are intact. Historical global manifest differences are an editorial provenance issue outside these original trees.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--suite',required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    if sys.flags.optimize: raise RuntimeError('Original assertions require unoptimized Python')
    report={'suite':args.suite,'status':'STARTED','started_utc':datetime.now(timezone.utc).isoformat(),
            'lean_process_ran':False,'universal_proof_claimed':False,'python_optimization_level':sys.flags.optimize}
    before=tree(SOURCE); downloads_before=tree(ROOT/'downloads')
    with tempfile.TemporaryDirectory(prefix='paper-vi-current-replay-') as temp:
        tmp=Path(temp)
        if args.suite=='source_integrity':
            report.update(reconcile(out))
        elif args.suite=='static_pytest_verifier':
            work=tmp/'snapshot';clone(SOURCE/'complete/original_snapshot',work)
            text=invoke([sys.executable,'-B','verification/verify.py','--static-only'],work,out/'command.log')
            for name in ['static_status.json','companion_tests.log','verifier_controls.log']:
                shutil.copy2(work/'verification'/name,out/name)
            data=json.loads((out/'static_status.json').read_text())
            if data['status']!='STATIC_AND_COMPANION_ONLY' or data['lean_kernel_checked'] or data['gates']['companion']['passed']!=54:
                raise RuntimeError('Unexpected static-only gate result')
            controls=(out/'verifier_controls.log').read_text()
            if not re.search(r'Ran 6 tests\b',controls) or 'OK' not in controls: raise RuntimeError('Unittest control summary missing')
            pytest=(out/'companion_tests.log').read_text()
            if re.search(r'\b(?:failed|error|skipped)\b',pytest,re.I): raise RuntimeError('Pytest did not produce all-success report')
            report.update(source_contract=data['gates']['source'],pytest_cases=54,pytest_failures=0,pytest_errors=0,pytest_skipped=0,
                          verifier_test_methods=6,verifier_corruption_controls=5,verifier_positive_controls=1,
                          scope='Unchanged original --static-only dispatch executes source integrity/scanning, 54 NumPy regression cases and six verifier unittest methods. No Lean compiler or axiom replay.')
        elif args.suite=='original_sympy_exact':
            work=tmp/'visual_appendix';clone(SOURCE/'complete/visual_appendix',work)
            invoke([sys.executable,'-B','checks/verify_examples.py','--output',str(out/'EXACT_CHECKS.json')],work,out/'command.log')
            data=json.loads((out/'EXACT_CHECKS.json').read_text())
            if data['status']!='PASS' or data['checks_passed']!=204 or len(data['invalid_controls_rejected'])!=11:
                raise RuntimeError('Unexpected original exact-check scope')
            report.update(checks_passed=204,false_controls_rejected=11,finite_families=data['finite_families'],computed_values=data['computed_values'],
                          original_input_hashes=data['sources'],arithmetic='SymPy exact rational/algebraic matrices and symbolic identities/integrals with declared positive/real assumptions',
                          scope='The original 204 assertions include symbolic identities and finite matrices, not 204 independent theorems or unrestricted analytic existence claims.')
        elif args.suite=='independent_exact_rational':
            text=invoke([sys.executable,'-B',str(Path(__file__).with_name('exact_rational_checks.py'))],tmp,out/'command.log')
            data=json.loads(text);write(out/'EXACT_RATIONAL_RESULTS.json',data)
            if data['status']!='PASS' or data['checks_passed']!=182 or data['false_controls_rejected']!=4:
                raise RuntimeError('Unexpected rational witness count')
            report.update(checks_passed=182,false_controls_rejected=4,bounded_families=data['bounded_families'],arithmetic=data['arithmetic'],
                          overlap='These independently coded rational witnesses overlap the original SymPy examples. They are not added as independent mathematical coverage.')
        elif args.suite=='numerical_companion':
            work=tmp/'companion';clone(SOURCE/'complete/original_snapshot/companion',work)
            text=invoke([sys.executable,'-B','run_all.py'],work,out/'command.log')
            if 'Generated 19 figure pairs.' not in text: raise RuntimeError('Figure generation count mismatch')
            inherited=flatten(json.loads((SOURCE/'complete/original_snapshot/companion/results/numerical_results.json').read_text()))
            fresh=flatten(json.loads((work/'results/numerical_results.json').read_text()))
            if set(inherited)!=set(fresh): raise RuntimeError('Numerical key-set mismatch')
            rows=[];non_numeric=[]
            for key,v in inherited.items():
                w=fresh[key]
                if isinstance(v,(float,int)) and not isinstance(v,bool):
                    okay=math.isfinite(v) and math.isfinite(w) and math.isclose(v,w,rel_tol=1e-7,abs_tol=5e-10)
                    rows.append({'path':key,'inherited':v,'fresh':w,'same_value':v==w,'within_tolerance':okay})
                    if not okay: raise RuntimeError('Numerical difference: '+key)
                else:
                    if type(v)!=type(w) or v!=w: raise RuntimeError('Non-numeric leaf differs: '+key)
                    non_numeric.append(key)
            if len(rows)!=79: raise RuntimeError('Numeric field count mismatch')
            for folder in ['results','tables','figures']: shutil.copytree(work/folder,out/folder)
            figs=sorted(p for p in (out/'figures').iterdir() if p.suffix in ['.png','.pdf'])
            if len(figs)!=38: raise RuntimeError('Expected exactly 19 regenerated figure pairs')
            figrows=[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size} for p in figs]
            write(out/'FIGURE_HASHES.json',figrows);write(out/'NUMERICAL_COMPARISON.json',{'status':'PASS','rows':rows,'relative_tolerance':1e-7,'absolute_tolerance':5e-10,'non_numeric_paths':non_numeric})
            report.update(numeric_output_fields=79,identical_numeric_values=sum(r['same_value'] for r in rows),non_numeric_leaves=len(non_numeric),
                          figure_pairs=19,relative_tolerance=1e-7,absolute_tolerance=5e-10,
                          arithmetic='Original NumPy/SciPy IEEE floating real/complex arithmetic and numerical integration',
                          scope='Numerical output comparison and regeneration, without claiming bit-identical PDFs or exact algebraic certificates.')
        elif args.suite in ['annals_numerical','strengthened_baseline','strengthened_expanded']:
            branch='annals' if args.suite=='annals_numerical' else 'strengthened'
            script='verify_paper_vi_strengthened.py' if args.suite=='strengthened_expanded' else 'verify_paper_vi.py'
            work=tmp/branch;clone(SOURCE/branch,work)
            text=invoke([sys.executable,'-B','verification/'+script],work,out/'command.log')
            match=re.search(r'(\d+)/(\d+) checks passed in (\d+) groups',text)
            expected={'annals_numerical':(475471,16),'strengthened_baseline':(149349,14),'strengthened_expanded':(154608,15)}[args.suite]
            if not match or int(match[1])!=int(match[2]) or (int(match[1]),int(match[3]))!=expected:
                raise RuntimeError('Unexpected suite count: '+str(match.groups() if match else None))
            # Only the Annals checker writes fresh structured outputs. The two
            # strengthened checkers print their fresh results to command.log.
            if branch=='annals':
                for name in ['verification_results.json','verification_summary.txt']:
                    shutil.copy2(work/'verification'/name,out/name)
            report.update(checks_reported=expected[0],groups=expected[1],branch=branch,script='verification/'+script,
                          arithmetic='Mixed finite NumPy/SciPy floating comparisons, integer/Boolean checks and historical source/package hygiene checks',
                          overlap='Suites overlap each other and original regression examples. Tallies use different conventions and are not summed into independent result counts.',
                          scope='Historical source/reference hygiene checks apply to immutable original sources. Current monograph prose/layout is checked separately.')
        elif args.suite=='monograph_figure_models':
            path=tmp/'generate_monograph_figures.py'
            shutil.copy2(ROOT/'editable/traditional/generate_monograph_figures.py',path)
            code="import importlib.util,json,sys; spec=importlib.util.spec_from_file_location('paper_vi_figure_models',sys.argv[1]);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);print(json.dumps(mod.exact_models(),indent=2,default=str))"
            text=invoke([sys.executable,'-B','-c',code,str(path)],tmp,out/'command.log')
            data=json.loads(text);write(out/'EXACT_FIGURE_MODELS.json',data)
            if data.get('exact_assertions')!=51:
                raise RuntimeError('Unexpected exact figure model count: '+str(data.keys()))
            report.update(checks_passed=51,arithmetic='Exact fractions.Fraction rational arithmetic in the declared matrix/likelihood/Jordan examples',
                          scope='New pedagogic finite examples underlying three Python figures. Floating exponentials are illustrative plotting coordinates, not proof evidence.')
        else: raise ValueError(args.suite)
    if before!=tree(SOURCE) or downloads_before!=tree(ROOT/'downloads'): raise RuntimeError('Original source or downloads changed during replay')
    report.update(status='PASS',finished_utc=datetime.now(timezone.utc).isoformat(),source_files_verified_unchanged=len(before),downloads_files_verified_unchanged=len(downloads_before))
    write(out/'result.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['source_sha256','downloads_sha256']},indent=2))

if __name__=='__main__': main()
