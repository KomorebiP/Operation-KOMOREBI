"""Independent exhaustive finite checks and validation of the native Lean export."""
from __future__ import annotations
from dataclasses import asdict
from itertools import product
from pathlib import Path
import json
from proof_path_theory import (
    __version__, analyze_affine_realizations, check_obstruction_witness,
    load_proof_field, ProofFieldViews,
)
ROOT = Path(__file__).resolve().parents[1]

def multiply(rows, x):
    return tuple(sum(a*b for a,b in zip(row,x)) % 2 for row in rows)

def main():
    total = positive = negative = 0
    for n in range(4):
        vectors = tuple(product((0,1), repeat=n))
        for m in range(3):
            for packed in product((0,1), repeat=m*n):
                A = tuple(tuple(packed[i*n:(i+1)*n]) for i in range(m))
                for p in vectors:
                    for x in vectors:
                        P = (p,)
                        Q = (tuple((i+1) % 2 for i in range(n)), p)
                        report = analyze_affine_realizations(
                            dimension=n, compatibility=A, protected=P, candidate=x, observation=Q)
                        sols = tuple(y for y in vectors if all(v == 0 for v in multiply(A,y))
                                     and multiply(P,y) == multiply(P,x))
                        total += 1
                        assert report.feasible == bool(sols)
                        if sols:
                            positive += 1
                            assert tuple(report.solution) in sols
                            assert report.realization_count == len(sols)
                            assert len(sols) == 2 ** report.ambiguity_dimension
                            seen = {multiply(Q,y) for y in sols}
                            assert len(seen) == 2 ** report.observation_gain_bits
                            counts = {obs:sum(multiply(Q,y)==obs for y in sols) for obs in seen}
                            assert len(set(counts.values())) == 1
                            assert len(sols) == next(iter(counts.values())) * len(seen)
                        else:
                            negative += 1
                            w=report.obstruction_witness
                            assert check_obstruction_witness(dimension=n, compatibility=A,
                                protected=P,candidate=x,witness=w)
                            rows=A+P; rhs=(0,)*m+multiply(P,x)
                            assert all(sum(w[i]*rows[i][j] for i in range(len(rows)))%2==0 for j in range(n))
                            assert sum(a*b for a,b in zip(w,rhs))%2==1
                            assert not check_obstruction_witness(dimension=n,compatibility=A,
                                protected=P,candidate=x,witness=(0,)*len(rows))
    native = load_proof_field(ROOT/'data/native_lean_field.json')
    views = ProofFieldViews(native)
    assert views.least_model() == native.derive()
    assert native.targets <= views.least_model()
    metadata=native.metadata
    records=metadata['native_records']
    assert {r['declaration'] for r in records} == native.targets
    assert len(records)==5
    for r in records:
        assert set(r['axioms']) <= {'propext','Classical.choice','Quot.sound'}
        rule=native.justifications['native:'+r['declaration']]
        assert set(rule.premises)==set(r['direct_dependencies'])
    report=dict(version=__version__,status='PASS',binary_systems=total,positive_systems=positive,
        infeasible_systems=negative,domain='all binary A with n=0..3,m=0..2; one protected row and all raw vectors; two declared observation rows',
        native_export=dict(nodes=len(native.nodes),justifications=len(native.justifications),roots=len(native.targets),
            scope='Declared closure and extracted direct dependencies; not a semantic proof of the Python importer'))
    (ROOT/'data/bridge_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
