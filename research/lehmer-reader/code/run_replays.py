#!/usr/bin/env python3
"""Portable, explicitly bounded replay launcher for the Lehmer evidence set.

Run from any directory. Defaults to every named suite. Existing run directories
are never overwritten. To reproduce elsewhere, pass --output-root with a fresh
project-relative path. Each scientific input and result receives a SHA-256 hash.
The runner launches explicit argv. No command is read from a historical manifest.
"""
from pathlib import Path
import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = 'historical/'
FINAL = BASE+'Lehmer_Final_Push_2026-09-26/lehmer_final_push/'
TRANS = BASE+'Lehmer_Primitive_Content_Transport_2026-09-26/lehmer_transport/'
TREE = BASE+'Lehmer_Packet_Tree_Sharp_Boundary_2026-09-26/lehmer_attempt/'
RES = BASE+'Lehmer_residual_audit_2026-09-26/lehmer_residual_audit/'
SYM = BASE+'Lehmer_null_packet_resolution_2026-09-26/lehmer_residual_audit/'

SPECS = {
 'arithmetic': {'contract':FINAL+'arithmetic/contract.json',
   'files':[FINAL+'arithmetic/check_arithmetic.py']},
 'valuations': {'contract':FINAL+'contract_valuations.json',
   'files':[FINAL+'checks/valuation_barriers.py',FINAL+'checks/packet_core.py']},
 'interpolation': {'contract':FINAL+'null_span/contract.json',
   'files':[FINAL+'null_span/check_interpolation.py',FINAL+'null_span/packet_core.py']},
 'packet_tree': {'contract':TREE+'contract.json',
   'files':[TREE+'checks/verify_packet_tree.py']},
 'transport': {'contract':TRANS+'contract.json',
   'files':[TRANS+'checks/verify_transport.py',TRANS+'checks/packet_core.py',
            TRANS+'checks/exact_algebra.py',TRANS+'evidence/kernels_through20.json'],
   'results':['results.json','kernels_through28.json','p31_transport_certificate.json']},
 'content121': {'contract':TRANS+'contract_content121.json',
   'files':[TRANS+'checks/content121.py',TRANS+'checks/packet_core.py']},
 'differential': {'files':[RES+'check_differential_projector.py',RES+'explore.py'],
   'assertion':'Exact polynomial Ramanujan-derivation identities and coefficient checks of second/fourth divisor-sum moments',
   'domain':'Q[E2,E4,E6] and Z, exact SymPy rationals and Python integers',
   'bounds':{'coefficient_range':[1,512],'symbolic_identities':4},
   'conventions':'D(E2)=(E2^2-E4)/12, D(E4)=(E2 E4-E6)/3, D(E6)=(E2 E6-E4^2)/2; Delta=(E4^3-E6^2)/1728',
   'dependencies':['sympy']},
 'trace_inverse': {'files':[RES+'check_trace_inverse.py',RES+'explore.py'],
   'assertion':'Exact triangular inverse-matrix entries and reduced-form Hurwitz moment identities',
   'domain':'Z and Q, exact integers and Fraction',
   'bounds':{'matrix_size':32,'prime_bound':499,'additional_prime':2411,'moments':[0,5]},
   'conventions':'Six times Hurwitz class number includes imprimitive forms; x^2+y^2 weight3, x^2+xy+y^2 weight2; moment at t=0 has weight1/2'},
 'residual_identity': {'files':[RES+'explore.py'],
   'assertion':'Divisor-sum prime moments, cusp identity, Niebur identity and Deligne-bound consistency through20000',
   'domain':'Z, exact integers',
   'bounds':{'tau_max':20000,'prime_max':20000,'moment_degrees':[0,4],'direct_product_max':128},
   'conventions':'S_j(p)=sum_{1<=k<p} k^j sigma_1(k) sigma_1(p-k); tau(p)=p^4(p+1)(50p^2-134p+85)-840S_4(p)'},
 'dyadic': {'files':[RES+'dyadic_check.py'],
   'assertion':'Exact fourth-moment coefficients at12 selected dyadic primes and failures of integral1-Lipschitz interpolation',
   'domain':'Z, exact integers',
   'bounds':{'selected_primes':[81919,131071,245759,294911,442367,524287,671743,737279,770047,786431,917503,1032191],
             'prime_coordinate_k':14},
   'conventions':'p=2^14 u-1; F(u)=tau(p)/2^14 on the selected prime arguments; conclusions about analytic functions additionally require the integral power-series contract'},
 'cross_validation': {'files':[RES+'validate_results.py',RES+'results_initial.json',RES+'dyadic_results.json',RES+'eta_ntt_results.txt'],
   'assertion':'Recheck19 recorded exact modular comparisons,12 dyadic primality and valuation rows, and a Lipschitz obstruction',
   'domain':'Z and Z/(2^19), exact integers',
   'bounds':{'recorded_modular_comparisons':19,'recorded_dyadic_rows':12,'selected_pair':[245759,770047]},
   'conventions':'This suite checks stored historical data; fresh generation is provided separately by dyadic and modular_ntt suites'},
 'five_core': {'files':[SYM+'explore.py',SYM+'continuation_5core/check_five_core.py',SYM+'continuation_5core/explore_shell.py'],
   'assertion':'Exact five-core shell counts, weights, packet polynomials, prime-index unit checks, selected Hensel branches and independent hook-partition sums',
   'domain':'Z, Q and Z/(5^k), exact integers and Fraction',
   'bounds':{'all_small_indices':[1,128],'all_primes_through':2000,'additional_primes':[2411,2999,4999,16249,18749],
             'hook_partition_size_max':24,'simple_root_digits':12,'double_root_branch_residues':625},
   'conventions':'v_i=i mod5, sum v_i=0, squared norm10n; W=Vandermonde/288; packet polynomial physical parameter5'},
 'null_kernels': {'files':[SYM+'explore.py',SYM+'continuation_5core/explore_shell.py']+
       [SYM+'continuation_symmetry/'+n for n in ['verify_all.py','kernel_lp.py','KERNELS_EXTENDED.json','KERNELS.json',
       'POSITIVITY_RESULTS.json','EXTENDED_RESULTS.json','DUAL_31.json','FACTORIZATIONS.json','RESEARCH_NOTE.md','SOURCES.md']],
   'assertion':'Exact retained harmonic-null identities, stored rational sign certificates, the degree16 dual obstruction, moments, cosets and stored factorization reports',
   'domain':'Z and Q, exact Python/SymPy arithmetic; no LP proposal generation is executed',
   'bounds':{'all_small_indices':[1,128],'additional_shells':[2411,16249],'null_degrees':[8,20],
             'dual_shell':31,'dual_degree_max':16,'factorization_prime_bound':2000,'discriminant_cosets':3125},
   'conventions':'Universal nullness additionally uses harmonic-theta modularity and the level-one valence argument; LP failure itself is not impossibility',
   'dependencies':['sympy','numpy','scipy']},
 'tau_independent': {'files':['code/check_tau_independently.py',FINAL+'checks/packet_core.py'],
   'assertion':'Three independent coefficient methods agree exactly on every tau(n) through512',
   'domain':'Z, exact integers; normalized ordinate only a display float',
   'bounds':{'tau_min':1,'tau_max':512,'known_benchmark_values':10},
   'conventions':'tau(n) is coefficient of q^n in q product(1-q^k)^24; independent recurrence uses nF_n=-24 sum sigma_1(j)F_(n-j)'},
 'modular_ntt': {'files':['code/check_large_modular.py',RES+'verify_eta_ntt.cpp',FINAL+'checks/packet_core.py'],
   'assertion':'Fresh exact CRT/NTT residues agree with freshly generated exact tau values at19 selected primes and recheck the dyadic obstruction',
   'domain':'Z and Z/(2^19), exact integer arithmetic; two finite-field NTT transforms and bounded CRT',
   'bounds':{'coefficient_index_max':1032191,'selected_comparisons':19,'modulus':2**19,'pair':[245759,770047]},
   'conventions':'Jacobi eta^3 series raised to the eighth power; exact reconstruction bound L(2^19-1)^2 <998244353*1004535809',
   'results':['results.json','ntt_output.txt','compiler_output.txt']},
 'transport_independent': {'files':['code/check_transport_certificate.py'],
   'assertion':'Independent exact equalities, prime-field rank lower bounds and structural upper bounds for the p31 hierarchical transfer certificate',
   'domain':'Q, F_65537 and F_1000003, exact integers and Fraction',
   'bounds':{'shell':31,'degree_max':22,'coarse_sectors':6,'fine_sectors':16,'prime_fields':[65537,1000003]},
   'conventions':'A aggregates fine sectors into nonempty coarse sectors; AM_f=M_c, B=M_f N, AB=0; nonzero prime-field minors establish rational lower rank bounds'},
}

def build_contract(name, spec):
    if 'contract' in spec:
        obj = json.loads((ROOT/spec['contract']).read_text())
        mathematics = obj['mathematics']
        files = spec['files']+[spec['contract']]
    else:
        mathematics = {'assertion_tested':spec['assertion'],'coefficient_domain':spec['domain'],
            'conventions':spec['conventions'],'bounds':spec['bounds'],
            'non_claims':['No proof of Lehmer beyond the finite executed bounds',
                          'External mathematical dependencies need separate source/proof verification',
                          'No priority or historical novelty claim']}
        files = spec['files'][:]
    if name not in ('tau_independent','modular_ntt','transport_independent'):
        files.insert(0,'code/replay_historical.py')
    mathematics['inputs'] = files[:]
    software = [{'name':'CPython','version':sys.version}]
    for dep in spec.get('dependencies',[]):
        software.append({'name':dep,'version':importlib.metadata.version(dep)})
    if name == 'modular_ntt':
        software.append({'name':'g++','version':subprocess.check_output(['g++','--version'],text=True).splitlines()[0]})
    return {'claim_id':'LEHMER-RELEASE07-'+name.upper(),'mathematics':mathematics,
            'execution_artifacts':files,'software':software,
            'randomness':{'used':False,'generator':'none','seed':None}}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suites', nargs='*', choices=sorted(SPECS))
    parser.add_argument('--output-root',default='evidence/computation/replays')
    args = parser.parse_args()
    all_suites = args.suites or list(SPECS)
    failures = []
    for name in all_suites:
        spec = SPECS[name]
        if name == 'modular_ntt':
            spec = dict(spec)
            spec['files'] = spec['files']+[str(Path(args.output_root)/'dyadic/results.json')]
        if name == 'transport_independent':
            spec = dict(spec)
            spec['files'] = spec['files']+[str(Path(args.output_root)/'transport/p31_transport_certificate.json')]
        contract = build_contract(name,spec)
        contract_path = ROOT/args.output_root/'contracts'/f'{name}.json'
        contract_path.parent.mkdir(parents=True,exist_ok=True)
        contract_path.write_text(json.dumps(contract,indent=2)+'\n')
        output = Path(args.output_root)/name
        command = [sys.executable,str(ROOT/'code/audit_tools/run_experiment.py'),
                   '--root',str(ROOT),'--contract',str(contract_path),'--output',str(output),
                   '--timeout','600','--max-output-bytes','2000000',
                   '--max-cpu-seconds','570','--max-cores','1','--max-threads','1']
        for p in contract['execution_artifacts']:
            command += ['--input',p]
        for p in spec.get('results',['results.json']):
            command += ['--result',str(output/p)]
        if name == 'tau_independent':
            child = [sys.executable,'code/check_tau_independently.py',str(output/'results.json')]
        elif name == 'modular_ntt':
            child = [sys.executable,'code/check_large_modular.py',str(output/'results.json'),
                     '--dyadic',str(Path(args.output_root)/'dyadic/results.json')]
        elif name == 'transport_independent':
            child = [sys.executable,'code/check_transport_certificate.py',str(output/'results.json'),
                     '--certificate',str(Path(args.output_root)/'transport/p31_transport_certificate.json')]
        else:
            child = [sys.executable,'code/replay_historical.py',name,str(output)]
        result = subprocess.run(command+['--']+child,cwd=ROOT)
        if result.returncode:
            failures.append({'suite':name,'stage':'run','exit_status':result.returncode})
            continue
        validation = subprocess.run([sys.executable,str(ROOT/'code/audit_tools/validate_manifest.py'),
                       str(ROOT/output/'manifest.json'),'--root',str(ROOT)],cwd=ROOT)
        if validation.returncode:
            failures.append({'suite':name,'stage':'manifest-validation','exit_status':validation.returncode})
    print(json.dumps({'completed_suites':all_suites,'failures':failures},sort_keys=True))
    return bool(failures)

if __name__ == '__main__':
    raise SystemExit(main())
