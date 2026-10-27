#!/usr/bin/env python3
"""Independent exact regression checks for Paper V's second source block.

Not a Lean runner and not a proof of universal mathematical statements.
Author: Komorebi P.
"""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import random
import time
import unittest

from exact_models import (
    Tree, analyze, synthesize, nodes, leaves, complete_prunings, pruning_count,
    optimal_cut, perturbation_envelope, selection_gap, gap_certifies_stability,
    lifting_analysis, lifting_synthesis, transfer_kernels, convolve,
    polyphase_convolve, sample_delay_routes, apply_delay_routes,
)
COUNTS: Counter[str] = Counter()
DETAILS: dict[str, object] = {}


def compositions(n: int):
    if n == 0:
        yield ()
    else:
        for first in range(1, n + 1):
            for tail in compositions(n - first):
                yield (first,) + tail


@lru_cache(maxsize=None)
def ordered_shapes(n: int) -> tuple[Tree, ...]:
    if n < 1:
        return ()
    if n == 1:
        return (Tree(),)
    return tuple(Tree(tuple(children)) for sizes in compositions(n - 1)
                 for children in product(*(ordered_shapes(k) for k in sizes)))


def independently_valid_subset(addresses: tuple[tuple[int, ...], ...], mask: int,
                               terminals: tuple[tuple[int, ...], ...]) -> bool:
    """Direct path incidence, with no call to the recursive pruning generator."""
    chosen = [addresses[i] for i in range(len(addresses)) if mask & (1 << i)]
    return all(sum(a == terminal[:len(a)] for a in chosen) == 1
               for terminal in terminals)


def aggregate_leaf_values(t: Tree, leaf_values: dict, a=()):
    if not t.children:
        return {a: leaf_values[a]}
    merged = {}
    for i, child in enumerate(t.children):
        merged.update(aggregate_leaf_values(child, leaf_values, a + (i,)))
    merged[a] = sum((merged[a + (i,)] for i in range(len(t.children))), Q(0))
    return merged


@dataclass(frozen=True)
class QRoot2:
    """Exact a + b*sqrt(2), implemented with rational coefficients."""
    a: Q = Q(0)
    b: Q = Q(0)

    def __add__(self, other: QRoot2) -> QRoot2:
        return QRoot2(self.a + other.a, self.b + other.b)

    def __sub__(self, other: QRoot2) -> QRoot2:
        return QRoot2(self.a - other.a, self.b - other.b)

    def __mul__(self, other: QRoot2) -> QRoot2:
        return QRoot2(self.a * other.a + 2 * self.b * other.b,
                      self.a * other.b + self.b * other.a)

    def square(self) -> QRoot2:
        return self * self


def haar_pair(x: tuple[QRoot2, QRoot2]) -> tuple[QRoot2, QRoot2]:
    factor = QRoot2(Q(0), Q(1, 2))
    return (x[0] + x[1]) * factor, (x[0] - x[1]) * factor


def flat_pairs(x: tuple):
    if len(x) % 2:
        raise ValueError('Flat signals must have even length.')
    return tuple((x[2*i], x[2*i+1]) for i in range(len(x)//2))


def flatten(pairs):
    return tuple(value for pair in pairs for value in pair)


class SecondBlockTests(unittest.TestCase):
    def check(self, group, truth, msg=None):
        COUNTS[group] += 1
        self.assertTrue(truth, msg)

    def test_all_ordered_trees_through_eight_nodes(self):
        counts = [len(ordered_shapes(n)) for n in range(1, 9)]
        self.check('tree_census', counts == [1, 1, 2, 5, 14, 42, 132, 429])
        shape_count, subsets, valid_total, max_arity = 0, 0, 0, 0
        rng = random.Random(52026)
        for n in range(1, 9):
            self.check('unique_shapes', len(set(ordered_shapes(n))) == counts[n-1])
            for t in ordered_shapes(n):
                shape_count += 1
                a = tuple(nodes(t)); terminal = tuple(leaves(t))
                self.check('node_count', len(a) == n)
                arities = Counter(path[:-1] for path in a if path)
                max_arity = max(max_arity, max(arities.values(), default=0))
                generated = {frozenset(cut) for cut in complete_prunings(t)}
                independently_valid = set()
                for mask in range(1 << n):
                    subsets += 1
                    cut = frozenset(a[i] for i in range(n) if mask & (1 << i))
                    valid = independently_valid_subset(a, mask, terminal)
                    self.check('independent_path_subset', (cut in generated) == valid)
                    if valid:
                        independently_valid.add(cut)
                valid_total += len(independently_valid)
                self.check('pruning_count', len(generated) == pruning_count(t))
                # Root synthesis by values assigned only at terminal leaves.
                leaf_values = {p: Q(rng.randint(-20,20), rng.randint(1,9)) for p in terminal}
                packets = aggregate_leaf_values(t, leaf_values)
                for cut in independently_valid:
                    self.check('all_cut_synthesis', sum((packets[p] for p in cut), Q(0)) == packets[()])
                # Five independently generated rational objectives per topology.
                for trial in range(5):
                    c = {p: Q(rng.randint(-12,12),rng.randint(1,7)) for p in a}
                    chosen = optimal_cut(t, c)
                    exhaustive = min(sum((c[p] for p in cut),Q(0)) for cut in independently_valid)
                    self.check('global_optimality', chosen.value == exhaustive)
                    self.check('admissible_best', frozenset(chosen.cut) in independently_valid)
                    self.check('comparison_count', chosen.internal_comparisons == len(arities))
                    e = {p: Q(rng.randint(0,8),rng.randint(1,7)) for p in a}
                    envelope = perturbation_envelope(t,e)
                    exact_max = max(sum((e[p] for p in cut),Q(0)) for cut in independently_valid)
                    self.check('exact_envelope', envelope == exact_max)
                    d = {p:c[p] + e[p]*Q(rng.randint(-3,3),3) for p in a}
                    changed = optimal_cut(t,d)
                    self.check('value_lipschitz', abs(changed.value-chosen.value) <= envelope)
                    gap = selection_gap(t,c)
                    if gap_certifies_stability(gap,envelope):
                        self.check('certified_stability', changed.cut == chosen.cut)
        DETAILS['tree_census'] = {'ordered_shapes':shape_count,'sizes':counts,
            'node_subsets_checked':subsets,'complete_prunings_across_shapes':valid_total,
            'cost_assignments':5*shape_count,'maximum_branch_arity':max_arity,
            'coverage':'All ordered rooted tree topologies with 1 through 8 nodes, not all finite trees.'}

    def test_exhaustive_small_integer_objectives(self):
        shapes = ordered_shapes(1)+ordered_shapes(2)+ordered_shapes(3)+ordered_shapes(4)
        assignments = 0
        for t in shapes:
            addresses = tuple(nodes(t)); cuts = complete_prunings(t)
            for weights in product((-1,0,1),repeat=len(addresses)):
                assignments += 1
                c = dict(zip(addresses,weights)); best=optimal_cut(t,c)
                costs = [sum(c[a] for a in cut) for cut in cuts]
                self.check('small_objectives',best.value == min(costs))
                # Root equality must choose stop, regardless of child tie decisions.
                child_cost = sum(optimal_cut(ch,{a[len((i,)):]:v for a,v in c.items()
                    if a and a[0]==i}).value for i,ch in enumerate(t.children))
                if t.children and c[()] == child_cost:
                    self.check('stop_on_ties',best.cut == ((),))
        DETAILS['exhaustive_integer_assignments'] = assignments

    def test_signed_coordinate_and_tap_bijections(self):
        rng=random.Random(615)
        zs=list(range(-160,161))+[-10**70-13,10**70+17,-10**100,10**100]
        for n in (1,2,3,4,5,7,8,11,16):
            for z in zs:
                q,r=divmod(z,n)
                self.check('integer_address',0<=r<n and n*q+r==z)
            for k in range(n):
                for tap in zs:
                    q,s=divmod(k-tap,n); m=-q
                    self.check('tap_inverse',n*m+k-s==tap)
                    for time_index in (-10**30-1,-3,0,7,10**30+3):
                        self.check('tap_signal_address',n*time_index+k-tap == n*(time_index-m)+s)
                for s in range(n):
                    for m in (-10**30-7,-3,0,4,10**30+1):
                        tap=n*m+k-s
                        q2,s2=divmod(k-tap,n)
                        self.check('tap_forward',(s2,-q2)==(s,m))
            for _ in range(12):
                h={rng.randrange(-70,71):Q(rng.randint(-9,9),rng.randint(1,9)) for _ in range(14)}
                h={i:v for i,v in h.items() if v}
                kernel=transfer_kernels(h,n)
                for k in range(n):
                    encoded={(divmod(k-t,n)[1],-divmod(k-t,n)[0]) for t in h}
                    expected={(s,m) for s in range(n) for m in kernel[k][s]}
                    self.check('exact_channel_support',encoded==expected)
                    for s,m in expected:
                        self.check('kernel_value',kernel[k][s][m]==h[n*m+k-s])

    def test_sparse_fir_cancellation_and_channel_resynthesis(self):
        rng=random.Random(77)
        for n in range(1,10):
            for trial in range(24):
                x={rng.randrange(-40,41):Q(rng.randint(-5,5),rng.randint(1,6)) for _ in range(12)}
                h={rng.randrange(-30,31):Q(rng.randint(-5,5),rng.randint(1,6)) for _ in range(9)}
                self.check('new_fir_cases',convolve(h,x)==polyphase_convolve(h,x,n))
                self.check('signal_roundtrip',synthesize(analyze(x,n))=={i:v for i,v in x.items() if v})
                # Start with arbitrary channels rather than only analyzed data.
                channels=tuple({rng.randrange(-20,21):Q(rng.randrange(-4,5)) for _ in range(5)} for _ in range(n))
                expected=tuple({i:v for i,v in c.items() if v} for c in channels)
                self.check('channel_roundtrip',analyze(synthesize(channels),n)==expected)
        self.check('zero_fir',polyphase_convolve({}, {-3:Q(1)},3)=={})
        self.check('zero_signal',polyphase_convolve({-1:Q(1)}, {},3)=={})

    def test_general_delay_composition(self):
        for n in range(1,10):
            channels=tuple({-10:Q(r+1),0:Q(2*r+3),11:Q(-r-2)} for r in range(n))
            for a,b in product((-31,-7,-1,0,1,5,34),repeat=2):
                self.check('delay_group_law',apply_delay_routes(apply_delay_routes(channels,a),b)
                           ==apply_delay_routes(channels,a+b))
                original=synthesize(channels)
                shifted={i+a:v for i,v in original.items()}
                self.check('delay_resynthesis',synthesize(apply_delay_routes(channels,a))==shifted)
            for d in range(-7,8):
                self.check('channel_delay_units',sample_delay_routes(n,n*d)==tuple((r,d) for r in range(n)))
        self.check('one_sample_two_channels',sample_delay_routes(2,1)==((1,1),(0,0)))

    def test_flat_lifting_and_normalized_haar(self):
        rng=random.Random(82026)
        lens=(0,2,4,6,8,14,16,30,32,62,64,126,128)
        for length in lens:
            for trial in range(12):
                x=tuple(Q(rng.randint(-20,20),rng.randint(1,9)) for _ in range(length))
                pairs=flat_pairs(x)
                self.check('flat_indexing',flatten(pairs)==x)
                encoded=tuple(lifting_analysis(*pair) for pair in pairs)
                self.check('flat_lifting',flatten(lifting_synthesis(*p) for p in encoded)==x)
                decoded=tuple(lifting_synthesis(*pair) for pair in pairs)
                self.check('flat_inverse_lifting',flatten(lifting_analysis(*p) for p in decoded)==x)
                z=tuple(QRoot2(Q(rng.randint(-8,8),rng.randint(1,7)),
                              Q(rng.randint(-8,8),rng.randint(1,7))) for _ in range(length))
                hp=tuple(haar_pair(p) for p in flat_pairs(z))
                self.check('normalized_haar_roundtrip',flatten(haar_pair(p) for p in hp)==z)
                old_energy=sum((v.square() for v in z),QRoot2())
                new_energy=sum((v.square() for v in flatten(hp)),QRoot2())
                self.check('normalized_haar_energy',old_energy==new_energy)
        with self.assertRaises(ValueError): flat_pairs((Q(1),))
        DETAILS['haar']={'exact_field':'Q(sqrt(2))','tested_lengths':list(lens),
                          'trials_per_length':12,'infinite_l2_claim':False}

    def test_sharp_stability_boundary_and_singleton(self):
        singleton=Tree()
        for a,b in product((-100,0,100),repeat=2):
            c={():Q(a)}; d={():Q(b)}
            self.check('singleton_unchanged',optimal_cut(singleton,c).cut==optimal_cut(singleton,d).cut)
            self.check('singleton_gap',selection_gap(singleton,c).gap is None)
        # Unary tree costs make the strict gamma > 2E boundary sharp.
        t=Tree((Tree(),)); c={():Q(2),(0,):Q(0)}
        for eps in (Q(0),Q(1,4),Q(3,4),Q(1),Q(5,4)):
            e={():eps,(0,):eps}; d={():2-eps,(0,):eps}
            E=perturbation_envelope(t,e)
            stable=optimal_cut(t,c).cut==optimal_cut(t,d).cut
            self.check('strict_gap_boundary',stable==(eps<1))
            self.check('strict_gap_certificate',gap_certifies_stability(selection_gap(t,c),E)==(eps<1))

    def test_matrix_criterion_on_standard_basis(self):
        rng=random.Random(416)
        for n in range(0,8):
            for _ in range(12):
                M=tuple(tuple(Q(rng.randint(-3,3),rng.randint(1,5)) for _ in range(n)) for _ in range(n))
                D=tuple(tuple(Q(rng.randint(-3,3),rng.randint(1,5)) for _ in range(n)) for _ in range(n))
                def mv(A,v): return tuple(sum((A[i][j]*v[j] for j in range(n)),Q(0)) for i in range(n))
                basis_equal=all(mv(M,tuple(Q(int(i==j)) for i in range(n)))==
                                mv(D,tuple(Q(int(i==j)) for i in range(n))) for j in range(n))
                self.check('matrix_basis_extensionality',basis_equal==(M==D))
                for j in range(n):
                    self.check('matrix_column',mv(M,tuple(Q(int(i==j)) for i in range(n)))==tuple(M[i][j] for i in range(n)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    start=time.perf_counter()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SecondBlockTests))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),
            'counted_assertions':sum(COUNTS.values()),'assertions_by_group':dict(sorted(COUNTS.items())),
            'details':DETAILS,'elapsed_seconds':time.perf_counter()-start,
            'lean_kernel_checked':False,'scope':'Finite exact regression checks independent of Lean source execution.'}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
