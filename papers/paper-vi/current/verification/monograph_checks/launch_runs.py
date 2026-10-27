#!/usr/bin/env python3
"""Create contracts and execute bounded current Paper VI replays.

Run from any directory. Existing run evidence is never overwritten. Supply a
fresh --run-prefix for an intentional replay. Manifests do not prove the paper.
"""
from __future__ import annotations
import argparse
import ast
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
BASE='verification/monograph_checks'
SUITES=['source_integrity','static_pytest_verifier','original_sympy_exact',
        'independent_exact_rational','numerical_companion','annals_numerical',
        'strengthened_baseline','strengthened_expanded','monograph_figure_models']

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def source_bounds(paths):
    """Retain exact source loop and tolerance expressions, not inferred ranges."""
    records=[]
    for p in paths:
        text=p.read_text();node=ast.parse(text)
        for n in ast.walk(node):
            if isinstance(n,(ast.For,ast.comprehension)):
                records.append({'path':p.relative_to(ROOT).as_posix(),'line':getattr(n,'lineno',None),
                                'iterator_expression':ast.get_source_segment(text,n.iter) or ast.unparse(n.iter)})
            elif isinstance(n,ast.Call):
                func=ast.unparse(n.func)
                if func.endswith(('isclose','allclose','scalar_close','array_close','record','linspace','quad','quad_vec','solve_ivp')):
                    records.append({'path':p.relative_to(ROOT).as_posix(),'line':n.lineno,
                                    'comparison_or_sampling_expression':ast.get_source_segment(text,n) or ast.unparse(n)})
    return records

def contract(suite):
    # run_suite also verifies unchanged original trees after every invocation.
    originals=sorted(p.relative_to(ROOT).as_posix() for folder in ['source','downloads'] for p in (ROOT/folder).rglob('*') if p.is_file())
    inputs=originals+[BASE+'/run_suite.py',BASE+'/exact_rational_checks.py']
    files=[]
    coeff='Mixed original numerical/scanning arithmetic; exact scope below'
    assertion='The current recovered original source/archive bytes match their recorded identities.'
    bounds={'archive_branches':3,'snapshot_files_expected':534,'source_files_expected':739,'no_Lean_process':True}
    random={'used':False,'generator':'','seed':None}
    if suite=='static_pytest_verifier':
        files=[ROOT/'source/complete/original_snapshot/verification/verify.py',ROOT/'source/complete/original_snapshot/verification/test_verifier.py',*(ROOT/'source/complete/original_snapshot/companion/tests').glob('*.py')]
        assertion='The unchanged original --static-only dispatch passes its source contract, 54 finite pytest cases and six fail-closed unittest control methods.'
        coeff='NumPy IEEE floating real/complex regression checks with source tolerances; static lexical checks and exact integrity hashes'
        bounds.update(pytest_cases=54,verifier_methods=6,verifier_positive_controls=1,verifier_corruption_controls=5,
                      source_contract_theorem_targets=341,proof_modules=47,scoped_result_rows=33)
        random={'used':True,'generator':'NumPy default_rng PCG64 in unchanged tests','seed':[1,2]}
    elif suite=='original_sympy_exact':
        files=[ROOT/'source/complete/visual_appendix/checks/verify_examples.py',ROOT/'source/complete/visual_appendix/source/models.py']
        assertion='The original exact example suite reproduces 204 assertions and rejects its 11 deliberately false controls.'
        coeff='SymPy exact rational/algebraic matrices and symbolic identities/integrals under declared real/positive assumptions'
        bounds.update(assertions=204,false_controls=11,simplex_denominator=4,simplex_priors=35,
                      green_interior_sizes=[1,3,7,15],lumping_horizons=[0,6],defect_horizons=[0,8],feynman_kac_horizon=3,feynman_kac_paths=8)
    elif suite=='independent_exact_rational':
        files=[ROOT/BASE/'exact_rational_checks.py']
        assertion='The independently coded finite Fraction witnesses reproduce 182 assertions and reject four false controls.'
        coeff='Python fractions.Fraction exact rational arithmetic'
        bounds.update(assertions=182,false_controls=4,simplex_denominator=4,simplex_priors=35,
                      green_interior_sizes=[1,3,7,15],lumping_horizons=[0,6],defect_horizons=[0,8],feynman_kac_horizon=3,feynman_kac_paths=8,
                      jordan_resolvent_parameters=['1/2','1','3','7'],rectangular_powers=[0,6])
    elif suite=='numerical_companion':
        files=[ROOT/'source/complete/original_snapshot/companion/run_all.py',*(ROOT/'source/complete/original_snapshot/companion/projector_transfer_semigroups').glob('*.py')]
        assertion='The original documented run_all.py regenerates 19 figure pairs and all 79 numeric output fields agree with the saved record within rtol1e-7/atol5e-10.'
        coeff='Original NumPy/SciPy IEEE floating real/complex arithmetic with unchanged quadrature/sampling; figures are illustrations'
        bounds.update(numeric_fields=79,figure_pairs=19,comparison_relative_tolerance=1e-7,comparison_absolute_tolerance=5e-10)
        random={'used':True,'generator':'NumPy default_rng PCG64 in unchanged original experiments','seed':20260727}
    elif suite in ['annals_numerical','strengthened_baseline','strengthened_expanded']:
        branch='annals' if suite=='annals_numerical' else 'strengthened';script='verify_paper_vi_strengthened.py' if suite=='strengthened_expanded' else 'verify_paper_vi.py'
        files=[ROOT/'source'/branch/'verification'/script]
        counts={'annals_numerical':(475471,16),'strengthened_baseline':(149349,14),'strengthened_expanded':(154608,15)}[suite]
        assertion='The unchanged '+branch+' checker passes its own mixed finite numerical/source-hygiene assertions under its own tolerances.'
        coeff='Mixed finite NumPy/SciPy floating comparisons, finite Boolean/integer checks and original source/reference integrity checks'
        bounds.update(checks_reported=counts[0],groups=counts[1],tolerance_policy='Exactly the per-comparison source thresholds retained below; no global uniform numerical certification')
        random={'used':True,'generator':'NumPy default_rng PCG64 in unchanged '+branch+' checker','seed':20260813 if suite=='annals_numerical' else 260813}
    elif suite=='monograph_figure_models':
        files=[ROOT/'editable/traditional/generate_monograph_figures.py'];inputs.extend(p.relative_to(ROOT).as_posix() for p in files)
        assertion='The three new explanatory models pass their 51 counted rational matrix, likelihood and nilpotent polynomial assertions.'
        coeff='fractions.Fraction exact rational arithmetic. Floating exp(-t) coordinates are illustrative only and are not a checked exact claim.'
        bounds.update(assertions=51,markov_matrix_shape=[3,3],rational_priors=2,likelihood_vectors=2,jordan_matrix_shape=[2,2],
                      jordan_t_parameters=['0','1/4','1/2','1','2','3'],jordan_u_parameters=['0','1/3','1','2'])
    bounds['source_expressions']=source_bounds(files)
    soft=[{'name':'Python','version':platform.python_version()}]
    for name in ['numpy','scipy','sympy','mpmath','matplotlib','pytest']:
        soft.append({'name':name,'version':importlib.metadata.version(name)})
    return {'claim_id':'PAPER_VI_MONOGRAPH_'+suite.upper(),
            'mathematics':{'assertion_tested':assertion,'coefficient_domain':coeff,
                          'conventions':'Original column probability transitions, departure-state Feynman-Kac weighting, weighted expectation adjoints and explicit resolvent hypotheses; unchanged suite conventions.',
                          'inputs':['Unchanged archived original branches and source code listed in execution_artifacts'],
                          'bounds':bounds,'non_claims':['No Lean compilation or kernel/namespace axiom replay.','Finite checks and symbolic library output do not independently prove universal analytic theorems or close the three open conjectures.','Overlapping suites and mixed assertion counts are not summed into independent mathematical coverage.','Original source-hygiene checks are not checks of current monograph typography or all source-to-Lean correspondence.']},
            'execution_artifacts':sorted(set(inputs)),'software':soft,'randomness':random}

def results(suite,out):
    files=['result.json']
    if suite!='source_integrity': files.append('command.log')
    extra={'static_pytest_verifier':['static_status.json','companion_tests.log','verifier_controls.log'],
           'original_sympy_exact':['EXACT_CHECKS.json'],'independent_exact_rational':['EXACT_RATIONAL_RESULTS.json'],
           'numerical_companion':['NUMERICAL_COMPARISON.json','FIGURE_HASHES.json','results/numerical_results.json','tables/numerical_summary.csv'],
           'annals_numerical':['verification_results.json','verification_summary.txt'],
           'monograph_figure_models':['EXACT_FIGURE_MODELS.json']}
    files+=extra.get(suite,[])
    if suite=='numerical_companion':
        src=ROOT/'source/complete/original_snapshot/companion/figures'
        files += ['figures/'+p.name for p in sorted(src.iterdir()) if p.suffix in ['.pdf','.png']]
    return [out+'/'+name for name in files]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--suite',choices=SUITES,action='append');ap.add_argument('--run-prefix',default='')
    args=ap.parse_args();selected=args.suite or SUITES
    for suite in selected:
        name=args.run_prefix+suite;out=BASE+'/runs/'+name
        if (ROOT/out).exists(): raise SystemExit('Evidence already exists: '+out+'; choose a fresh --run-prefix')
        data=contract(suite);cpath=ROOT/BASE/'contracts'/(name+'.json');write(cpath,data)
        argv=[sys.executable,'-B',str(ROOT/BASE/'tools/run_experiment.py'),'--root',str(ROOT),'--contract',str(cpath),'--output',out,
              '--timeout','300','--max-output-bytes','4194304','--max-memory-bytes','8589934592','--max-cpu-seconds','240','--max-cores','1','--max-threads','1']
        for p in data['execution_artifacts']: argv.extend(['--input',p])
        for p in results(suite,out): argv.extend(['--result',p])
        argv.extend(['--',sys.executable,'-B',BASE+'/run_suite.py','--suite',suite,'--out',out])
        status=subprocess.call(argv,cwd=ROOT)
        validator=[sys.executable,'-B',str(ROOT/BASE/'tools/validate_manifest.py'),str(ROOT/out/'manifest.json'),'--root',str(ROOT)]
        v=subprocess.run(validator,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (ROOT/out/'MANIFEST_VALIDATION.txt').write_text(v.stdout,encoding='utf-8')
        print(json.dumps({'suite':suite,'execution_exit':status,'manifest_validation_exit':v.returncode,'output':out}),flush=True)
        if status or v.returncode: raise SystemExit(status or v.returncode)

if __name__=='__main__': main()
