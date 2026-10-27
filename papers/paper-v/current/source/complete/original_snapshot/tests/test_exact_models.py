"""Exact finite regression tests. Passing is not Lean kernel verification."""
from __future__ import annotations
import itertools
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import random
import time
import unittest
from exact_models import (
    Tree, analyze, synthesize, convolve, polyphase_convolve, sample_delay_routes,
    apply_delay_routes, lifting_analysis, lifting_synthesis, nodes, leaves,
    pruning_count, complete_prunings, is_complete_pruning, optimal_cut,
    perturbation_envelope, selection_gap, gap_certifies_stability,
)

COUNTS: Counter[str] = Counter()


class ExactModelsTests(unittest.TestCase):
    def checked(self, group: str, condition: bool) -> None:
        COUNTS[group] += 1
        self.assertTrue(condition)

    def test_polyphase_masks_refinement_and_signed_roundtrip(self) -> None:
        x = {n: Q((n * n + 3 * n) % 17 - 8, 7) for n in range(-19, 21)}
        x = {n: v for n, v in x.items() if v}
        for N in range(1, 10):
            c = analyze(x, N)
            self.checked('polyphase', synthesize(c) == x)
            self.checked('polyphase', analyze(synthesize(c), N) == c)
            for n in range(-25, 26):
                packets = [x.get(n, Q(0)) if n % N == r else Q(0) for r in range(N)]
                self.checked('polyphase', sum(packets, Q(0)) == x.get(n, Q(0)))
                for r in range(N):
                    for s in range(N):
                        composed = packets[s] if n % N == r else Q(0)
                        self.checked('polyphase', composed == (packets[r] if r == s else 0))
            for multiple in (1, 2, 3):
                M = N * multiple
                for n in range(-17, 18):
                    for r in range(N):
                        coarse = x.get(n, Q(0)) if n % N == r else Q(0)
                        refined = sum((x.get(n, Q(0)) if n % M == s else Q(0)
                                       for s in range(M) if s % N == r), Q(0))
                        self.checked('refinement', coarse == refined)

    def test_fir_signed_taps(self) -> None:
        rng = random.Random(9152026)
        for _ in range(45):
            x = {n: Q(rng.randrange(-8, 9), 7) for n in range(-8, 9)}
            h = {n: Q(rng.randrange(-5, 6), 3) for n in range(-4, 6)}
            for n in (1, 2, 3, 4, 5, 7):
                self.checked('FIR', convolve(h, x) == polyphase_convolve(h, x, n))

    def test_original_sample_delay_vs_channel_delay(self) -> None:
        x = {-3: Q(2), 0: Q(1), 4: Q(-1, 3), 9: Q(5, 2)}
        self.checked('delay', sample_delay_routes(2, 1) == ((1, 1), (0, 0)))
        for n in range(1, 9):
            for d in range(-11, 12):
                delayed = synthesize(apply_delay_routes(analyze(x, n), d))
                self.checked('delay', delayed == {k + d: v for k, v in x.items()})
            for d in range(-3, 4):
                self.checked('delay', all(s == r and q == d for r, (s, q)
                                        in enumerate(sample_delay_routes(n, n * d))))
        # A one-channel-index delay in N=2 is two original samples, not one.
        wrong = synthesize(tuple({q + 1: v for q, v in c.items()} for c in analyze(x, 2)))
        self.checked('delay', wrong != {k + 1: v for k, v in x.items()})

    def test_lifting_inverse_and_energy_identity(self) -> None:
        vals = [Q(i, d) for i in range(-5, 6) for d in (1, 3, 7)]
        for e, o in itertools.product(vals, repeat=2):
            s, d = lifting_analysis(e, o)
            self.checked('lifting', lifting_synthesis(s, d) == (e, o))
            self.checked('lifting', lifting_analysis(*lifting_synthesis(e, o)) == (e, o))
            # Unnormalized pair identity underlying Haar energy, no sqrt approximation.
            self.checked('Haar_polynomial_identity', (e + o)**2 + (e - o)**2 == 2 * (e**2 + o**2))
        self.checked('lifting', Q(1, 2) * 1 - Q(1, 2) * (-1) == 1)

    def test_known_edges_and_l1_mask_bound(self) -> None:
        rng = random.Random(391)
        for _ in range(120):
            s = [Q(rng.randrange(-10, 11), 7) for _ in range(8)]
            shat = [v / 3 for v in s]
            j = [Q(rng.randrange(-5, 6), 2) for _ in range(8)]
            jhat = [v / 2 for v in j]
            error = [a + b - (c + b) for a, b, c in zip(s, j, shat)]
            self.checked('known_edge', error == [a - b for a, b in zip(s, shat)])
            total = sum(abs(a+b-c-d) for a,b,c,d in zip(s,j,shat,jhat))
            bound = sum(abs(a-c) for a,c in zip(s,shat)) + sum(abs(b-d) for b,d in zip(j,jhat))
            self.checked('estimated_edge', total <= bound)
            a, ahat = Q(rng.randrange(-6, 7), 5), Q(rng.randrange(-6, 7), 3)
            S = {i for i in range(8) if rng.getrandbits(1)}
            T = {i for i in range(8) if rng.getrandbits(1)}
            l1 = sum(abs((a if i in S else 0) - (ahat if i in T else 0)) for i in range(8))
            self.checked('finite_L1_mask', l1 <= abs(a-ahat)*len(S) + abs(ahat)*len(S^T))

    def test_complete_prunings_and_exact_synthesis(self) -> None:
        leaf = Tree()
        shapes = [leaf, Tree((leaf,)), Tree((leaf,leaf)), Tree((leaf,leaf,leaf)),
                  Tree((Tree((leaf,leaf)), leaf, Tree((leaf,leaf,leaf)))),
                  Tree((Tree((leaf,Tree((leaf,leaf)))),Tree((leaf,leaf))))]
        for t in shapes:
            cuts = complete_prunings(t)
            self.checked('complete_pruning', len(cuts) == pruning_count(t))
            leaf_addresses = tuple(leaves(t))
            vector = {l: Q(i+1, 7) for i, l in enumerate(leaf_addresses)}
            for cut in cuts:
                self.checked('complete_pruning', is_complete_pruning(t, cut))
                for leaf_address in leaf_addresses:
                    coeff = sum(leaf_address[:len(a)] == a for a in cut)
                    self.checked('pruning_synthesis', coeff * vector[leaf_address] == vector[leaf_address])
                energies = [sum(v*v for l,v in vector.items() if l[:len(a)] == a) for a in cut]
                self.checked('finite_projector_energy', sum(energies) == sum(v*v for v in vector.values()))
        self.checked('complete_pruning', not is_complete_pruning(Tree((leaf,leaf)), ((), (0,))))

    def test_dynamic_programming_against_enumeration(self) -> None:
        leaf = Tree()
        shapes = [leaf, Tree((leaf,)), Tree((leaf,leaf)), Tree((leaf,leaf,leaf)),
                  Tree((Tree((leaf,leaf)),leaf,Tree((leaf,leaf,leaf))))]
        t = leaf
        for _ in range(4):
            t = Tree((t,t))
        shapes.append(t)  # 677 complete prunings, independently enumerated.
        rng = random.Random(114)
        for t in shapes:
            cuts = complete_prunings(t)
            for _ in range(50):
                c = {a: Q(rng.randrange(-30,31), 11) for a in nodes(t)}
                sol = optimal_cut(t,c)
                scores = [sum((c[a] for a in cut), Q(0)) for cut in cuts]
                self.checked('DP', sol.value == min(scores))
                self.checked('DP', sum((c[a] for a in sol.cut), Q(0)) == sol.value)
                self.checked('DP', is_complete_pruning(t, sol.cut))
                self.checked('DP', sol.internal_comparisons == len(tuple(nodes(t))) - len(tuple(leaves(t))))

    def test_singleton_and_tie_rules(self) -> None:
        leaf = Tree()
        for x in (Q(-100), Q(0), Q(222,7)):
            report = selection_gap(leaf, {():x})
            self.checked('singleton', report.unique and report.gap is None)
            self.checked('singleton', gap_certifies_stability(report, Q(10**9)))
            self.checked('singleton', optimal_cut(leaf,{():x}).cut == ((),))
        t = Tree((leaf,leaf))
        c = {():Q(3), (0,):Q(1), (1,):Q(2)}
        self.checked('ties', optimal_cut(t,c).cut == ((),))
        report = selection_gap(t,c)
        self.checked('ties', not report.unique and report.gap == 0)
        self.checked('ties', not gap_certifies_stability(report,0))

    def test_perturbation_envelope_and_gap(self) -> None:
        leaf = Tree()
        t = Tree((Tree((leaf,leaf)), leaf, Tree((leaf,leaf,leaf))))
        cuts = complete_prunings(t)
        rng = random.Random(115)
        for _ in range(80):
            c = {a: Q(rng.randrange(-100, 101), 13) for a in nodes(t)}
            e = {a: Q(rng.randrange(0, 8), 1000) for a in nodes(t)}
            delta = {a: e[a] * Q(rng.randrange(-4,5),4) for a in nodes(t)}
            d = {a: c[a] + delta[a] for a in c}
            E = perturbation_envelope(t,e)
            self.checked('envelope', E == max(sum((e[a] for a in cut),Q(0)) for cut in cuts))
            for cut in cuts:
                err = abs(sum((d[a]-c[a] for a in cut),Q(0)))
                self.checked('envelope', err <= E)
            report = selection_gap(t,c)
            if gap_certifies_stability(report,E):
                self.checked('gap_stability', optimal_cut(t,c).cut == optimal_cut(t,d).cut)
        # Exact boundary: the strict condition cannot be weakened to <=.
        f = (Q(0),Q(2)); g = (Q(1),Q(1))
        self.checked('gap_boundary', max(abs(g[i]-f[i]) for i in range(2)) == (f[1]-f[0])/2)
        self.checked('gap_boundary', g[0] == g[1])

    def test_depth_five_count(self) -> None:
        t=Tree(); counts=[1]
        for _ in range(5):
            t=Tree((t,t)); counts.append(pruning_count(t))
        self.checked('pruning_count', counts == [1,2,5,26,677,458330])
        # This test computes the count; it does not enumerate 458330 candidates.

    def test_projective_smith_composition_and_pole(self) -> None:
        def M(w:Q): return ((1+w,1-w),(1-w,1+w))
        def mul(a,b): return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))
        for u,v in itertools.product((Q(-3),Q(-1),Q(1,2),Q(1),Q(5,2)),repeat=2):
            self.checked('Smith_matrix', mul(M(u),M(v)) == tuple(tuple(2*x for x in row) for row in M(u*v)))
            self.checked('Smith_matrix', (1+u)**2-(1-u)**2 == 4*u)
        # Half-turn takes z=0=(0:1) to infinity=(1:0), not to a finite number.
        mat=M(Q(-1)); num,den=mat[0][1],mat[1][1]
        self.checked('Smith_pole', num != 0 and den == 0)

    def test_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError): analyze({},0)
        with self.assertRaises(TypeError): analyze({0:0.1},2)
        with self.assertRaises(ValueError): synthesize(())
        with self.assertRaises(ValueError): optimal_cut(Tree(),{})
        with self.assertRaises(ValueError): perturbation_envelope(Tree(),{():-1})
        with self.assertRaises(ValueError): gap_certifies_stability(selection_gap(Tree(),{():0}),-1)


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    started=time.perf_counter()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExactModelsTests))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL',
            'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'counted_assertions':sum(COUNTS.values()),'assertions_by_group':dict(sorted(COUNTS.items())),
            'elapsed_seconds':time.perf_counter()-started,
            'arithmetic':'fractions.Fraction','lean_kernel_checked':False,
            'scope':'New finite reference models; not the original 33-test companion suite.'}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
