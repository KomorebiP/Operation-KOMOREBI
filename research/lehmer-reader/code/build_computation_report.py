#!/usr/bin/env python3
"""Collect already completed computation evidence and original-output comparisons.

This is a reporting command. It launches no scientific experiment and changes
no historical source. It verifies every recorded manifest and result hash.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'evidence/computation'
RUNS = EVIDENCE/'replays'
FINAL = ROOT/'historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push'
TRANS = ROOT/'historical/Lehmer_Primitive_Content_Transport_2026-09-26/lehmer_transport'
TREE = ROOT/'historical/Lehmer_Packet_Tree_Sharp_Boundary_2026-09-26/lehmer_attempt'
RES = ROOT/'historical/Lehmer_residual_audit_2026-09-26/lehmer_residual_audit'
SYM = ROOT/'historical/Lehmer_null_packet_resolution_2026-09-26/lehmer_residual_audit'
PRIOR = {
 'arithmetic':FINAL/'arithmetic/computation001/results.json',
 'valuations':FINAL/'computations/valuations001/result.json',
 'interpolation':FINAL/'null_span/computations/run001/results.json',
 'packet_tree':TREE/'computations/run001/results.json',
 'transport':TRANS/'computations/run001/results.json',
 'content121':TRANS/'computations/content121/result.json',
 'differential':RES/'differential_results.json',
 'trace_inverse':RES/'trace_inverse_results.json',
 'residual_identity':RES/'results_initial.json',
 'dyadic':RES/'dyadic_results.json',
 'cross_validation':RES/'cross_validation.json',
 'five_core':SYM/'continuation_5core/RESULTS.json',
 'null_kernels':SYM/'continuation_symmetry/VERIFICATION.json',
}

def clean(obj):
    if isinstance(obj,dict):
        return {k:clean(v) for k,v in obj.items() if k not in ('runtime','runtime_seconds','seconds')}
    if isinstance(obj,list):
        return [clean(v) for v in obj]
    return obj

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    records = []
    used = set()
    for directory in sorted(RUNS.iterdir()):
        manifest_path = directory/'manifest.json'
        if not manifest_path.is_file():
            continue
        validation = subprocess.run([sys.executable,str(ROOT/'code/audit_tools/validate_manifest.py'),
             str(manifest_path),'--root',str(ROOT)],capture_output=True,text=True)
        assert validation.returncode==0, validation.stderr+validation.stdout
        manifest = json.loads(manifest_path.read_text())
        assert manifest['schema_version']==2 and manifest['run']['status']=='completed'
        result_path = directory/'results.json'
        result = json.loads(result_path.read_text())
        old = PRIOR.get(directory.name)
        comparison = None
        if old:
            comparison = {'historical_result':str(old.relative_to(ROOT)),
                          'historical_sha256':digest(old),
                          'same_after_excluding_elapsed_time_fields':clean(json.loads(old.read_text()))==clean(result),
                          'excluded_fields':['runtime','runtime_seconds','seconds']}
            assert comparison['same_after_excluding_elapsed_time_fields']
        for obj in manifest['input_artifacts']:
            used.add(obj['path'])
        records.append({'suite':directory.name,
            'manifest_path':str(manifest_path.relative_to(ROOT)),
            'manifest_sha256':digest(manifest_path),'manifest_validation':'valid v2 evidence record with current input/result hashes',
            'results_path':str(result_path.relative_to(ROOT)),'results_sha256':digest(result_path),
            'runtime_seconds':manifest['run']['runtime_seconds'],
            'coefficient_domain':manifest['mathematics']['coefficient_domain'],
            'bounds':manifest['mathematics']['bounds'],'historical_comparison':comparison})
    assert len(records)==16
    inventory = [{'path':str(p.relative_to(ROOT)),'sha256':digest(p),'used_in_fresh_run':str(p.relative_to(ROOT)) in used}
        for p in sorted((ROOT/'historical').rglob('*')) if p.is_file() and p.suffix in ('.py','.cpp','.sh')]
    summary = {'status':'completed','fresh_suites':len(records),'historical_scientific_outputs_matched':len(PRIOR),
        'match_rule':'Exact recursive equality, excluding only runtime/runtime_seconds/seconds metadata fields',
        'all_manifest_hashes_current':True,'records':records,
        'raw_code_inventory':inventory,
        'non_claims':['No solution of Lehmer is established',
                      'Finite evidence counts do not authenticate external theorems',
                      'Not every archived exploratory script was rerun',
                      'Imported symbolic/numerical packages are versioned dependencies. No LP proposals were generated during this replay.']}
    (EVIDENCE/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    text = '''# Lehmer computational audit, Series 07

Release date: 9 October 2026. Arithmetic is exact unless explicitly marked as a display ordinate.

Six preserved research packages supplied the input files. Sixteen newly recorded suites completed, and all sixteen version 2 manifests validate against their current input and scientific-result hashes. Thirteen historical scientific outputs agree exactly with the new outputs after excluding only three names for elapsed-time metadata: `runtime`, `runtime_seconds` and `seconds`. Three additional suites independently check coefficients, the transfer certificate and large modular residues.

The computations support bounded assertions and specific obstruction examples. They do not establish Lehmer's conjecture. The harmonic theta and valence deductions, the class-number trace formula and the congruence-density arguments require their separate mathematical contracts.

## Reader table

| Suite | Executed domain and range | Exact result |
|---|---|---|
| Independent tau coefficients | Integers, every n from 1 through 512 | All 512 coefficients agree among the triangular recurrence, the defining binomial product and an independent divisor-sum logarithmic derivative. All 512 are nonzero. |
| Actual local congruences | Tau through 10000, 24 selected moduli, local exponents 1 through 32 | 22 moduli have a matching prime in the executed range. Those examples supply 704 checks. No matching prime was observed for moduli 11 and 19 in this bounded search. |
| Synthetic local congruences | Integers M from 1 through 256, p=5M−1, a∈{−2M,0,3M}, exponents 1 through 32 | 24576 recurrence checks pass. The synthetic p need not be prime, and a is not claimed to equal tau(p). |
| Trace-zero matrices | All 1229 primes through 10000 | Trace, determinant and square identities pass for the displayed companion matrices. These are local models rather than a realization of the global Delta representation. |
| Valuation barriers | All 13848 primes through 150000 | First discrepancies in the stated candidate sets occur at p=81919 for ell=2, p=8747 for ell=3 and p=499 for ell=5. All four selected coefficients agree with independent Eisenstein convolutions. |
| Divisor-sum moment identities | All 2262 primes through 20000 | Exact moment, Niebur and cusp identities pass. |
| Differential projector | Rational polynomial ring and n=1 through 512 | Four symbolic remainders are zero, with 1024 coefficient checks. |
| Class-number inversion | Matrices of size 32, all primes through 499 plus 2411 | 1056 inverse-entry checks and 96 prime rows pass. |
| Five-core packets | n=1 through 128, all primes through 2000 and five larger primes through 18749 | 405 shell sums, 326585 packet polynomials and 308 prime shell counts pass. Hook partitions independently recover 25 coefficients. |
| Packet tree | Every shell through 512, plus 737 and 2411, depths 1 through 6 | 514 shell sums, 95937 packets and 3084 sector partitions pass. Explicit witnesses pass at 64 depths. Brute shell enumeration agrees on n=1 through 32. |
| Null corrections | Retained degrees 8 through 20, small shells through 128, plus 2411 and 16249 | 14 exact rational sign certificates pass. A 16-weight dual obstructs the seven degree-at-most-16 corrections at p=31. |
| Primitive transport | Degrees through 28, small shells through 128 and odd shells through 499 | 36 symbolic harmonic certificates, 128 primitive Mobius identities, 144 profile ranks and one exact p=31 transfer pass. |
| Independent p=31 transfer | Rationals and prime fields 65537, 1000003, degrees through 22 | Coarse, fine and detail ranks are exactly 5, 15 and 10. Aggregation and both transport stages preserve the required totals. |
| Content obstruction | Exact shell n=121 | Content-one mass is −25439104668 and content-eleven mass is 25937424601. Their sum is tau(121)=498319933. |
| Orbit interpolation | Separation through shell 128, interpolation at n=7 and n=31 | 5847 packets and 2964 involution orbits pass. Both selected homogeneous interpolants fail nullness at shell 1. |
| Dyadic obstruction | Twelve selected primes through 1032191 | All exact coefficients are regenerated by divisor-sum moments. Fresh CRT/NTT residues agree at 19 selected primes modulo 2^19. The selected dyadic pair has coordinate-difference valuation 5 and output-difference valuation 0. |

## Bound accounting

The historical final-arithmetic program independently checked the defining product only through 128. The packet-tree program checked the product through 512. This release independently compares three methods through 512. These are separate executed bounds, and no 256-coefficient claim is inferred from the older summary alone.

The 704 actual congruence checks are 22 selected modulus examples times 32 local exponents. They are not 704 distinct primes or 704 independent density results. Modulus 1 is included as a trivial case. The 24576 synthetic checks are 256 moduli times three trace parameters times 32 exponents. The prime-indexed companion matrices are constructed models, not sampled Frobenius elements from an authenticated global representation.

The modular NTT works with coefficient representatives from 0 through M−1, where M=2^19=524288. In each squaring, a convolution coefficient is a sum of at most L=1032191 products. Its nonnegative integer value is therefore at most L(M−1)^2, strictly below the product 998244353×1004535809. The two finite-field residues consequently determine that integer convolution coefficient before reduction modulo M. This is the reconstruction contract, and the C++ source explicitly rejects an insufficient bound or an unsupported transform length. The common length is 2^21, which divides both prime-field multiplicative periods. Intermediate signed products and residue sums fit the declared 64-bit and 32-bit types. The final output remains a residue modulo 2^19, and is not a reconstruction of the large integer tau value.

At the packet-tree boundary, a sparse check at n=737 supplies a witness. The replay does not enumerate every shell from 513 through 736. The universal sharp-boundary assertion relies on the separate lower-bound proof and symbolic families. At the transport boundary, two coarse rank failures in the odd-index scan occur at the composite indices 9 and 81. No all-prime rank theorem is inferred from that scan.

## Reproduction

From the extracted source-set root, run:

```bash
python3 code/run_replays.py --output-root evidence/computation/reproduced
```

The output directory must be fresh. Individual suites may be named before `--output-root`. The complete replay uses Python 3.12.14, SymPy 1.14.0, the recorded NumPy/SciPy import versions and g++ with C++17 support. The pure integer/rational suites use the standard library. The null-kernel verifier imports proposal-library modules but does not execute linear programming. Software versions and actual argv are recorded in every manifest.

Each suite has a 600-second wall-clock bound, a 570-second per-process CPU-time cap, an inherited one-core affinity cap and a two-million-byte combined log limit. Conventional numerical-library thread caps are cooperative. No address-space cap was requested. The manifests distinguish failed execution, changed inputs, omitted results and resource exhaustion. Every scientific result has its own checksum, and preserved historical inputs are not overwritten.

`SUMMARY.json` indexes each exact result and its manifest. `replays/*/stdout.txt` and `stderr.txt` preserve the execution logs. Wrapper copies used for programs with fixed historical output paths live below each run directory. They are copies, and changes to their output files do not alter the historical originals.

## Interpretation

The p-adic counterexamples refute proposed auxiliary equalities or a specific integral one-coordinate interpolation contract. They are not counterexamples to Lehmer. The n=121 opposite-sign masses demonstrate a content conservation obstruction inside the stated homogeneous-null method. They do not exclude all conceivable correction methods. The p=31 dual concerns the seven stored corrections through invariant degree 16, and the larger-degree certificates show why that degree restriction matters.

The class-number and differential identities compute tau as an exact difference. An exact difference formula does not ensure that every resulting coefficient is nonzero. A prime found for each fixed modulus does not supply a single prime satisfying all moduli. The uniform nonvanishing implication remains a separate mathematical question.
'''
    (EVIDENCE/'REPORT.md').write_text(text)
    # One authoritative, hash-accounted source of plotting data.
    source = RUNS/'tau_independent/results.json'
    target = EVIDENCE/'tau_plot_data_512.json'
    target.write_bytes(source.read_bytes())
    print(json.dumps({'status':'completed','fresh_suites':len(records),'matched_historical_outputs':len(PRIOR),
                      'summary':'evidence/computation/SUMMARY.json','report':'evidence/computation/REPORT.md'}))

if __name__ == '__main__':
    main()
