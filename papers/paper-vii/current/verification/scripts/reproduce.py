#!/usr/bin/env python3
"""Portable bounded Paper VII replay. Run from the evidence project root.

Example: python verification/scripts/reproduce.py --source source
  --downloads downloads --out verification/my_fresh_run
"""
from __future__ import annotations
import argparse, importlib.util, json, platform, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--downloads',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--root',type=Path,default=Path.cwd())
    args=ap.parse_args();root=args.root.resolve()
    script=Path(__file__).resolve();base=script.parents[1]
    def rel(p): return str(p.resolve().relative_to(root))
    source=(root/args.source).resolve();downloads=(root/args.downloads).resolve();out=(root/args.out).resolve()
    inputs=sorted(rel(p) for tree in (source,downloads,base/'scripts',base/'tools') for p in tree.rglob('*') if p.is_file() and p.suffix!='.pyc')
    software=[{'name':'Python','version':platform.python_version()}]
    for name in ('numpy','scipy','matplotlib','fitz'):
        if importlib.util.find_spec(name):
            m=__import__(name);software.append({'name':name,'version':str(getattr(m,'__version__',getattr(m,'VersionBind','installed')))})
        else: software.append({'name':name,'version':'unavailable'})
    contract={'claim_id':'PAPER_VII_FRESH_BOUNDED_REPLAY_20261006',
        'mathematics':{'assertion_tested':'Original software/numerical assertions and strengthened finite suite replay, source-byte integrity, static consistency of inherited Lean evidence, and independent exact small witnesses.',
            'coefficient_domain':'IEEE binary64 complex numerical matrices; exact Q in independent witness script; SHA-256 and ZIP CRC for file integrity.',
            'conventions':'Computational basis tensor order; column vectorization in strengthened suite; norm and tolerance as unchanged original scripts state. Exact witnesses use Fraction and row-list matrices.',
            'inputs':['725 complete-source files','59 strengthened-source files','two preserved ZIP archives','unchanged original functions, verifier software and finite experiments'],
            'bounds':{'source_files':784,'original_zero_argument_test_functions':22,'verifier_unittest_cases':16,'active_Lean_modules_static_only':25,'inherited_theorem_audits_static_only':323,
                'strengthened_groups':15,'strengthened_dimensions':'seed d1..5,m1..6; cyclic N2..9; dynamics n2..8; Feshbach splits (1,1),(2,1),(2,2),(3,2); torus d1..3,N4..32 and heat N16,32,64,128; bounded towers≤12 levels; full bound table in COMPUTATION_AUDIT.md',
                'exact_witnesses':'explicit finite rational cases stated in exact_rational_witnesses.json'},
            'non_claims':['No new Lean kernel compilation, Mathlib rebuild or negative-control execution.',
                'Direct test function invocation does not run pytest collection or plugins.',
                'No original SymPy visual example gate replay without SymPy.',
                'Finite floating calculations do not prove universally quantified theorems, continuum conjectures or physical quantum-gravity targets.',
                'Stored original numerical fields are compared with an explicit comparison tolerance distinct from the original tests own thresholds.']},
        'execution_artifacts':inputs,'software':software,
        'randomness':{'used':True,'generator':'NumPy default_rng PCG64 as original code',
            'seed':{'original_experiments':20260727,'original_tests':[4,2],'strengthened':20260814}}}
    contracts=base/'contracts';contracts.mkdir(exist_ok=True)
    path=contracts/(out.name+'.json');path.write_text(json.dumps(contract,indent=2)+'\n')
    argv=[sys.executable,str(base/'tools/run_experiment.py'),'--root',str(root),'--contract',str(path),
        '--output',rel(out),'--result',rel(out/'results.json'),'--timeout','600','--max-output-bytes','10485760',
        '--max-memory-bytes','2147483648','--max-cpu-seconds','480','--max-cores','1','--max-threads','1']
    for p in inputs:argv.extend(['--input',p])
    argv+=['--',sys.executable,rel(script.with_name('replay_gates.py')),'--source',rel(source),'--downloads',rel(downloads),'--out',rel(out)]
    rc=subprocess.call(argv,cwd=root)
    if rc:return rc
    return subprocess.call([sys.executable,str(base/'tools/validate_manifest.py'),str(out/'manifest.json'),'--root',str(root)],cwd=root)

if __name__=='__main__':raise SystemExit(main())
