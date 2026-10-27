#!/usr/bin/env python3
"""Compile and replay the reviewed integer CRT/NTT coefficient check.

Compare19 selected coefficients modulo2^19 with independently freshly produced
exact coefficients. No modular zero is a claim of an integer zero. The CRT
bound in the C++ source certifies its reconstruction at the implemented size.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT/'historical/Lehmer_residual_audit_2026-09-26/lehmer_residual_audit/verify_eta_ntt.cpp'
CORE = ROOT/'historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/checks/packet_core.py'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--dyadic',type=Path,default=Path('evidence/computation/replays/dyadic/results.json'))
    args = parser.parse_args()
    out = args.output.resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    dyadic_path = args.dyadic if args.dyadic.is_absolute() else ROOT/args.dyadic
    dyadic = json.loads(dyadic_path.read_text())
    exact = {r['p']:r['tau'] for r in dyadic['rows']}
    spec = importlib.util.spec_from_file_location('reviewed_packet_core',CORE)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    small = core.tau_triangular(2411)
    exact.update({p:small[p] for p in [2,3,5,7,11,13,2411]})
    with tempfile.TemporaryDirectory(prefix='ntt-build-',dir=out.parent) as build:
        executable = Path(build)/'verify_eta_ntt'
        compiler_argv = ['g++','-std=c++17','-O2',str(CPP.relative_to(ROOT)),'-o',str(executable)]
        compilation = subprocess.run(compiler_argv,cwd=ROOT,capture_output=True,text=True,check=True)
        run = subprocess.run([str(executable)],capture_output=True,text=True,check=True)
    (out.parent/'ntt_output.txt').write_text(run.stdout)
    (out.parent/'compiler_output.txt').write_text(compilation.stdout+compilation.stderr)
    lines = run.stdout.splitlines()
    modulus = int(lines[0].split()[1])
    assert modulus == 2**19
    comparisons = []
    for line in lines[1:]:
        if line.startswith('seconds'):
            continue
        p,residue = map(int,line.split())
        assert p in exact
        assert exact[p]%modulus == residue, (p,exact[p]%modulus,residue)
        comparisons.append({'prime':p,'residue':residue,'exact_tau':exact[p],
                            'fresh_exact_method':'fourth divisor-sum moment' if p>2411 else 'triangular recurrence'})
    assert len(comparisons) == 19
    p1,p2 = 245759,770047
    u1,u2 = (p1+1)//2**14,(p2+1)//2**14
    f1,f2 = exact[p1]//2**14,exact[p2]//2**14
    assert exact[p1]%2**14 == exact[p2]%2**14 == 0
    v2 = lambda x:(abs(x)&-abs(x)).bit_length()-1
    assert v2(u2-u1) == 5 and v2(f2-f1) == 0
    result = {'status':'PASS','coefficient_domain':'Z and Z/(2^19), exact C++ integer arithmetic',
              'compiler_argv':compiler_argv[:-1]+['<temporary executable>'],
              'coefficient_index_max':1032191,'comparison_count':len(comparisons),'comparisons':comparisons,
              'dyadic_counterexample':{'p1':p1,'p2':p2,'u1':u1,'u2':u2,
                 'F1_mod32':f1%32,'F2_mod32':f2%32,'v2_coordinate_difference':5,'v2_output_difference':0},
              'non_claims':['No integer reconstruction from one2^19 residue',
                            'No universal tau nonvanishing conclusion',
                            'Only integral1-Lipschitz one-coordinate interpolation is obstructed by the selected pair']}
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'},sort_keys=True))

if __name__ == '__main__':
    main()
