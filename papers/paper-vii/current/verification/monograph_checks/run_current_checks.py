#!/usr/bin/env python3
"""Record the scoped October 9 finite replays using the current bounded runner.

Runs preserve source and downloads. Guide checks are recorded by their owner.
Invoke from any directory; outputs must be new below this project.
"""
from __future__ import annotations
import argparse, importlib.metadata, json, platform, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only',choices=('original','corrected','constructed','all'),default='all')
    a=ap.parse_args()
    here=Path(__file__).resolve().parent
    root=here.parents[1]
    rel=lambda p:str(p.relative_to(root))
    inputs=sorted(rel(p) for tree in (root/'source',root/'downloads') for p in tree.rglob('*') if p.is_file())
    support=[here/'run_current_checks.py',here/'tools/run_experiment.py',here/'tools/validate_manifest.py']
    original=root/'verification/scripts'
    software=[{'name':'Python','version':platform.python_version()}]
    software += [{'name':n,'version':importlib.metadata.version(n)} for n in ('numpy','scipy','matplotlib','PyMuPDF','sympy','mpmath','pytest')]
    common={'software':software,'mathematics':{'coefficient_domain':'IEEE binary64 real/complex arrays, exact rational Fraction witnesses, integer representative sets, SHA-256 bytes and finite strings/sets.',
        'conventions':'Unchanged original tensor/vectorization, Choi and norm/tolerance conventions. Only the two explicit odd-N lower endpoints change in the separately identified corrected verifier.',
        'inputs':['725 complete-source files','59 strengthened-source files','two exact inherited ZIP originals'],
        'non_claims':['No fresh Lean compilation or Lean deliberate-rejection controls.','Finite assertions do not prove universal theorem statements, continuum limits, or the five physical quantum-spacetime targets.','Numerical residuals remain conditional on implemented binary64 tolerances and stated finite inputs.','Repeated direct functions, pytest and experiment cases overlap; their counts are not added as independent mathematical results.']}}
    suites={
        'original':{'claim_id':'PAPER_VII_MONOGRAPH_ORIGINAL_BOUNDED_REPLAY_20261009',
            'assertion':'Unchanged original22 direct test functions and22 collected pytest cases;16 verifier software methods;1048 original experiment leaf fields;18049 raw strengthened assertions in15groups;269 independent Fraction assertions; archives and inherited formal report consistency.',
            'bounds':{'source_files':784,'pytest_cases':22,'direct_test_functions':22,'verifier_methods':16,'verifier_positive_methods':9,'verifier_malformed_or_tamper_controls':7,'experiment_leaf_fields':1048,'experiment_numeric_fields':1045,'raw_strengthened_checks':18049,'raw_strengthened_groups':15,'exact_fraction_assertions':269,'formal_modules_static_only':25,'formal_targets_inherited_only':323,
                'finite_ranges':'seed d1..5,m1..6; cyclic N2..9; dynamics n2..8; Feshbach splits(1,1),(2,1),(2,2),(3,2); torus d1..3,N4..32; heat N16,32,64,128; finite towers up to12levels. Full range/tolerance table retained in verification/COMPUTATION_AUDIT.md.'},
            'files':[here/'replay_current.py',original/'exact_rational_witnesses.py'],
            'argv':[sys.executable,rel(here/'replay_current.py'),'--source','source','--downloads','downloads'],
            'randomness':{'used':True,'generator':'NumPy default_rng PCG64, unchanged original code','seed':{'original_experiments':20260727,'original_tests':[4,2],'strengthened':20260814}}},
        'corrected':{'claim_id':'PAPER_VII_MONOGRAPH_CORRECTED_ODD_N_REPLAY_20261009',
            'assertion':'Exactly two lower endpoints -N//2 become -(N//2). All87 count/uniqueness/bound assertions pass forN4..32 and the corrected finite suite passes17699checks in15groups.',
            'bounds':{'N_min':4,'N_max':32,'representative_assertions':87,'strengthened_groups':15,'expected_corrected_checks':17699,'comparison_raw_checks':18049},
            'files':[original/'replay_corrected.py',root/'verification/corrected_strengthened/verify_paper_vii.py'],
            'argv':[sys.executable,rel(original/'replay_corrected.py'),'--source','source','--corrected','verification/corrected_strengthened/verify_paper_vii.py'],
            'randomness':{'used':True,'generator':'NumPy default_rng PCG64, unchanged random code','seed':20260814}},
        'constructed':{'claim_id':'PAPER_VII_MONOGRAPH_SIX_CONSTRUCTED_BINDINGS_20261009',
            'assertion':'The six inherited constructed-object audit targets are bound to source/inventory/runner/log/cumulative report by12 fresh static consistency assertions; zero added theorem declarations.',
            'bounds':{'objects':6,'binding_assertions':12,'active_formal_modules':25,'theorem_count_addition':0},
            'files':[original/'check_constructed_bindings.py'],
            'argv':[sys.executable,rel(original/'check_constructed_bindings.py'),'--source','source'],
            'randomness':{'used':False,'generator':'','seed':None}}
    }
    (here/'contracts').mkdir(exist_ok=True)
    for name,s in suites.items():
        if a.only not in ('all',name):continue
        out=here/('run_'+name+'_20261009')
        execution=sorted(set(inputs+[rel(p) for p in support+s['files']]))
        contract={**common,'claim_id':s['claim_id'],'randomness':s['randomness'],'execution_artifacts':execution}
        contract['mathematics']={**common['mathematics'],'assertion_tested':s['assertion'],'bounds':s['bounds']}
        cp=here/'contracts'/(name+'_20261009.json');cp.write_text(json.dumps(contract,indent=2)+'\n')
        child=s['argv']+['--out',rel(out/'results.json' if name=='constructed' else out)]
        argv=[sys.executable,str(here/'tools/run_experiment.py'),'--root',str(root),'--contract',str(cp),'--output',rel(out),'--result',rel(out/'results.json'),
            '--timeout','600','--max-output-bytes','10485760','--max-memory-bytes','2147483648','--max-cpu-seconds','480','--max-cores','1','--max-threads','1']
        for p in execution:argv.extend(['--input',p])
        argv += ['--']+child
        rc=subprocess.call(argv,cwd=root)
        if rc:return rc
        rc=subprocess.call([sys.executable,str(here/'tools/validate_manifest.py'),str(out/'manifest.json'),'--root',str(root)],cwd=root)
        if rc:return rc
    return 0

if __name__=='__main__':raise SystemExit(main())
