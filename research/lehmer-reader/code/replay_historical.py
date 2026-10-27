#!/usr/bin/env python3
"""Replay named, reviewed historical Lehmer programs without changing originals.

Every input is pinned by the separate bounded-run manifest. This wrapper runs
only an explicit allowlist. It does not execute commands from old manifests.
Programs with fixed output locations run in a private copy below their run dir.
"""
from pathlib import Path
import argparse
import json
import os
import runpy
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
HIST = ROOT / 'historical'
FINAL = HIST / 'Lehmer_Final_Push_2026-09-26' / 'lehmer_final_push'
TRANS = HIST / 'Lehmer_Primitive_Content_Transport_2026-09-26' / 'lehmer_transport'
TREE = HIST / 'Lehmer_Packet_Tree_Sharp_Boundary_2026-09-26' / 'lehmer_attempt'
RESIDUAL = HIST / 'Lehmer_residual_audit_2026-09-26' / 'lehmer_residual_audit'
SYMMETRY = HIST / 'Lehmer_null_packet_resolution_2026-09-26' / 'lehmer_residual_audit'

SUITES = {
    'arithmetic': (FINAL/'arithmetic/check_arithmetic.py', FINAL/'arithmetic', False),
    'valuations': (FINAL/'checks/valuation_barriers.py', FINAL, False),
    'interpolation': (FINAL/'null_span/check_interpolation.py', FINAL/'null_span', False),
    'packet_tree': (TREE/'checks/verify_packet_tree.py', TREE, False),
    'transport': (TRANS/'checks/verify_transport.py', TRANS, False),
    'content121': (TRANS/'checks/content121.py', TRANS, False),
    'differential': (RESIDUAL/'check_differential_projector.py', RESIDUAL, True),
    'trace_inverse': (RESIDUAL/'check_trace_inverse.py', RESIDUAL, True),
    'residual_identity': (RESIDUAL/'explore.py', RESIDUAL, True),
    'dyadic': (RESIDUAL/'dyadic_check.py', RESIDUAL, True),
    'cross_validation': (RESIDUAL/'validate_results.py', RESIDUAL, True),
    'five_core': (SYMMETRY/'continuation_5core/check_five_core.py', SYMMETRY, True),
    'null_kernels': (SYMMETRY/'continuation_symmetry/verify_all.py', SYMMETRY, True),
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suite', choices=SUITES)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    script, working, copy_first = SUITES[args.suite]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if copy_first:
        sandbox = output/'sandbox'
        sandbox.mkdir()
        # The closure is reviewed and named, rather than every archive member.
        names = {'differential':['check_differential_projector.py','explore.py'],
                 'trace_inverse':['check_trace_inverse.py','explore.py'],
                 'residual_identity':['explore.py'],
                 'dyadic':['dyadic_check.py'],
                 'cross_validation':['validate_results.py','results_initial.json',
                                     'dyadic_results.json','eta_ntt_results.txt'],
                 'five_core':['explore.py','continuation_5core/check_five_core.py',
                              'continuation_5core/explore_shell.py'],
                 'null_kernels':['explore.py','continuation_5core/explore_shell.py',
                     'continuation_symmetry/verify_all.py','continuation_symmetry/kernel_lp.py',
                     'continuation_symmetry/KERNELS_EXTENDED.json','continuation_symmetry/KERNELS.json',
                     'continuation_symmetry/POSITIVITY_RESULTS.json','continuation_symmetry/EXTENDED_RESULTS.json',
                     'continuation_symmetry/DUAL_31.json','continuation_symmetry/FACTORIZATIONS.json',
                     'continuation_symmetry/RESEARCH_NOTE.md','continuation_symmetry/SOURCES.md']}[args.suite]
        relative_script = script.relative_to(working)
        for name in names:
            (sandbox/name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(working/name, sandbox/name)
        script = sandbox/relative_script
        working = sandbox
    os.chdir(working)
    sys.path.insert(0, str(script.parent))
    target = output if args.suite == 'transport' else output/'results.json'
    sys.argv = [str(script), str(target)]
    runpy.run_path(str(script), run_name='__main__')
    fixed = {'differential':'differential_results.json',
             'trace_inverse':'trace_inverse_results.json',
             'residual_identity':'results_initial.json',
             'dyadic':'dyadic_results.json',
             'cross_validation':'cross_validation.json',
             'five_core':'continuation_5core/RESULTS.json',
             'null_kernels':'continuation_symmetry/VERIFICATION.json'}
    if args.suite in fixed:
        shutil.copyfile(working/fixed[args.suite], output/'results.json')

if __name__ == '__main__':
    main()
