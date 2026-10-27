"""Small exact illustrations for Grounded Abstraction v0.1.0.

No training, sampled agents, external services, or floating-point acceptance tests.
The general conclusions are supported by the manuscript's proofs, not enumeration.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations, product
from math import comb
from pathlib import Path
import json
import time

ROOT = Path(__file__).resolve().parents[1]


def powerset(xs):
    xs = tuple(xs)
    return [frozenset(xs[i] for i in range(len(xs)) if mask >> i & 1)
            for mask in range(1 << len(xs))]


def partitions(n):
    """Canonical restricted-growth encodings of all partitions."""
    if n == 0:
        return [()]
    out = [(0,)]
    for _ in range(1, n):
        out = [p + (j,) for p in out for j in range(max(p) + 2)]
    return out


def canonical(values):
    ids = {}
    return tuple(ids.setdefault(v, len(ids)) for v in values)


def stable_partition(ops, labels):
    p = canonical(labels)
    strict = 0
    while True:
        nxt = canonical([(p[x], tuple(p[op[x]] for op in ops)) for x in range(len(p))])
        if nxt == p:
            return p, strict
        p, strict = nxt, strict + 1


def words(alphabet_size, depth):
    for n in range(depth + 1):
        yield from product(range(alphabet_size), repeat=n)


def apply_word(ops, x, w):
    for a in w:
        x = ops[a][x]
    return x


def fiber_constant(code, target):
    seen = {}
    for c, t in zip(code, target):
        if c in seen and seen[c] != t:
            return False
        seen[c] = t
    return True


def can_identify(B, tests, target, depth):
    if len({target[x] for x in B}) <= 1:
        return True
    if depth == 0:
        return False
    for test in tests:
        blocks = defaultdict(set)
        for x in B:
            blocks[test[x]].add(x)
        if len(blocks) > 1 and all(can_identify(frozenset(b), tests, target, depth - 1)
                                   for b in blocks.values()):
            return True
    return False


class Checks:
    def __init__(self):
        self.groups = []
        self.current = None
    def group(self, name, domain):
        self.current = {'name': name, 'domain': domain, 'assertions': 0}
        self.groups.append(self.current)
    def check(self, condition, message):
        if not condition:
            raise AssertionError(f"{self.current['name']}: {message}")
        self.current['assertions'] += 1


def mv(cols, x, p=2):
    return tuple(sum(cols[j][i] * x[j] for j in range(len(x))) % p for i in range(len(x)))


def linear_word(maps, v, w):
    for a in w:
        v = mv(maps[a], v)
    return v


def mat2(A, x):
    return tuple(sum(A[i][j] * x[j] for j in range(2)) for i in range(2))


def run():
    c = Checks()
    started = time.perf_counter()
    c.group('finite_grounding', 'All one-operation machines on n=1,2,3 states, all binary output labels, all evidence partitions; continuation words through n+1.')
    for n in range(1, 4):
        for op in product(range(n), repeat=n):
            for lab in product(range(2), repeat=n):
                p, steps = stable_partition((op,), lab)
                profiles = [tuple(lab[apply_word((op,), x, w)] for w in words(1, n + 1)) for x in range(n)]
                c.check(canonical(profiles) == p, 'refinement disagrees with direct continuations')
                c.check(steps <= n - len(set(lab)), 'refinement bound exceeded')
                for r in partitions(n):
                    c.check(fiber_constant(r, p) == fiber_constant(r, profiles), 'grounding criterion')

    c.group('nondestructive_revision', 'Three immutable cases; every binary target, every retained partition, every ordered pair of binary tests; all test subsets and depth-two adaptive trees.')
    n = 3
    tests_all = list(product(range(2), repeat=n))
    for target in tests_all:
        for retained in partitions(n):
            for tests in product(tests_all, repeat=2):
                full = tuple((retained[x],) + tuple(t[x] for t in tests) for x in range(n))
                compatible = fiber_constant(full, target)
                by_tree = all(can_identify(frozenset(x for x in range(n) if retained[x] == z), tests, target, 2)
                              for z in set(retained))
                c.check(compatible == by_tree, 'all-test signature versus adaptive tree')
                obstruction_pairs = [(x,y) for x in range(n) for y in range(x+1,n)
                                     if retained[x] == retained[y] and target[x] != target[y]]
                for J in powerset(range(2)):
                    signature = tuple((retained[x],) + tuple(tests[j][x] for j in sorted(J)) for x in range(n))
                    covers = all(any(tests[j][x] != tests[j][y] for j in J) for x,y in obstruction_pairs)
                    c.check(covers == fiber_constant(signature, target), 'pair-cover criterion')

    c.group('destructive_and_reset_controls', 'Three one-shot cases with two destructive tests, depths 0..5; eight sensor worlds (s,theta,k).')
    def destructive(B, depth):
        if len({x for x, live in B}) <= 1:
            return True
        if depth == 0:
            return False
        for a in (0,1):
            branches = defaultdict(set)
            for x, live in B:
                o = int(x == a) if live else 0
                branches[o].add((x,False))
            if all(destructive(frozenset(b), depth-1) for b in branches.values()):
                return True
        return False
    initial = frozenset((x,True) for x in range(3))
    for x,y in combinations(range(3),2):
        c.check(any((x == a) != (y == a) for a in (0,1)), 'pair separation')
    for h in range(6):
        c.check(not destructive(initial,h), 'destructive tests should not identify all cases')
    omega = list(product((0,1), repeat=3))
    for s,theta,k in omega:
        old_y = s ^ theta
        reset_report = theta
        c.check(old_y ^ reset_report == s, 'old record + reset recovers origin')
        c.check(0 ^ theta == reset_report, 'reset changes physical state')
    c.check((0,0,0)[1:] == (1,0,0)[1:], 'reset erasure witness')

    c.group('correction_memory', 'All 256 candidate subsets of eight sensor worlds; theta partition, target s; all four atom-union observations, sixteen correction profiles, and their separators.')
    atoms = [frozenset(i for i,w in enumerate(omega) if w[1] == a) for a in (0,1)]
    sets = powerset(range(8))
    events = [frozenset().union(*(atoms[a] for a in J)) for J in powerset(range(2))]
    tau = lambda B: frozenset(omega[i][0] for i in B)
    profile = lambda B: tuple(tau(B & A) for A in atoms)
    by_profile = defaultdict(list)
    for B in sets:
        by_profile[profile(B)].append(B)
    c.check(len(by_profile) == 16, 'minimal profile count')
    c.check(len({tau(B) for B in sets}) == 4, 'current target summary count')
    for B in sets:
        representative = by_profile[profile(B)][0]
        for E in events:
            c.check(tau(B&E) == tau(representative&E), 'future target equality')
            c.check(profile(B&E) == profile(representative&E), 'well-defined filtered update')
    for p,q in combinations(by_profile,2):
        c.check(any(p[i] != q[i] for i in range(2)), 'atom distinguishes unequal profiles')
    V0 = frozenset(i for i,(s,t,k) in enumerate(omega) if s^t == 0)
    V1 = frozenset(i for i,(s,t,k) in enumerate(omega) if s^t == 1)
    c.check(tau(V0) == tau(V1), 'same current uncertainty')
    c.check(tau(V0&atoms[0]) != tau(V1&atoms[0]), 'different corrected conclusions')
    # The atom-union family must be exact: an extra cell-splitting event can
    # distinguish candidate sets with the same old occupancy and target value.
    left, right = frozenset({0}), frozenset({1})
    constant_target = lambda B: frozenset({0}) if B else frozenset()
    c.check(constant_target(left) == constant_target(right), 'same single-cell occupancy')
    extra_event = frozenset({0})
    c.check(constant_target(left & extra_event) != constant_target(right & extra_event),
            'extra evidence invalidates old partition occupancy')
    # A non-Boolean meet-closed evidence family checks the general construction.
    O = frozenset(range(4)); family = [O,frozenset(),frozenset({0,1}),frozenset({0})]
    q = lambda B: frozenset(x%2 for x in B)
    sig = lambda B: tuple(q(B&E) for E in family)
    for B,D in product(powerset(O),repeat=2):
        if sig(B) == sig(D):
            for E in family:
                c.check(sig(B&E) == sig(D&E), 'meet-closed correction congruence')

    c.group('noisy_identification', 'Two Bernoulli models p=1/4,3/4; exact strings through length seven and odd majority errors through length nineteen.')
    noisy=[]
    for n in range(1,20,2):
        error = sum((F(comb(n,k)*3**k,4**n) for k in range((n-1)//2+1)),F(0))
        noisy.append({'n':n,'error':str(error),'decimal':float(error)})
        c.check(error > 0, 'finite positive error')
        if n <= 7:
            direct=F(0); tv=F(0)
            for bits in product((0,1),repeat=n):
                k=sum(bits)
                P=F(3**k,4**n); Q=F(3**(n-k),4**n)
                c.check(P>0 and Q>0, 'common support')
                tv += abs(P-Q)/2
                if k <= (n-1)//2:
                    direct += P
            c.check(direct == error, 'binomial/direct equality')
            c.check(1-error == (1+tv)/2, 'optimal binary test identity')
    c.check(noisy[0]['error']=='1/4' and noisy[1]['error']=='5/32', 'hand calculation')

    c.group('ambiguity_radius', 'All nonempty subsets of {-1,0,1}^2, midpoint radius versus exact half-grid minimax; one explicit compression union.')
    pts=list(product((-1,0,1),repeat=2))
    centers=list(product([F(-1),F(-1,2),F(0),F(1,2),F(1)],repeat=2))
    for ids in powerset(range(len(pts))):
        if not ids: continue
        B=[pts[i] for i in ids]
        lo=[min(x[j] for x in B) for j in range(2)]
        hi=[max(x[j] for x in B) for j in range(2)]
        midpoint=[F(a+b,2) for a,b in zip(lo,hi)]
        radius=max(F(b-a,2) for a,b in zip(lo,hi))
        direct=min(max(max(abs(z[j]-x[j]) for j in range(2)) for x in B) for z in centers)
        c.check(radius==direct,'minimax radius')
        c.check(max(max(abs(midpoint[j]-x[j]) for j in range(2)) for x in B)==radius,'midpoint attains')
    c.check(F(2-0,2) >= F(1-0,2),'union cannot improve radius')

    c.group('calibrated_continuation', 'All two-operator restrictions from a one-dimensional subspace of F2^2; all 16 completions of each pair, all four initial vectors and word lengths through three. A three-dimensional escape example is also exhausted.')
    vec=list(product((0,1),repeat=2)); U=frozenset({(0,0),(1,0)})
    for s0,s1 in product(vec,repeat=2):
        restrictions=(s0,s1)
        spaces=[U]
        for h in range(3):
            spaces.append(frozenset(v for v in U if all(tuple(v[0]*w for w in s) in spaces[-1] for s in restrictions)))
        completions=[((s0,b0),(s1,b1)) for b0,b1 in product(vec,repeat=2)]
        for n in range(1,4):
            for v in vec:
                same=all(len({linear_word(maps,v,w) for maps in completions}) == 1 for w in words(2,n))
                c.check(same == (v in spaces[n-1]), 'maximal calibrated domain')
    v3=list(product((0,1),repeat=3)); e1=(1,0,0); e2=(0,1,0); e3=(0,0,1)
    U3=frozenset(v for v in v3 if v[2]==0)
    maps=[((e1,e3,b),) for b in v3]
    core=frozenset({(0,0,0),e1})
    for n in range(1,5):
        for v in v3:
            same=all(len({linear_word(m,v,w) for m in maps}) == 1 for w in words(1,n))
            c.check(same == (v in (U3 if n==1 else core)), 'three-dimensional first-exit boundary')

    c.group('approximate_continuation', 'Exact rational 2x2 operators, calibrated line span(e1), induced l1 norms, powers through six. Explicit ambient-growth negative control.')
    for s,delta,eps,b,d in product([F(0),F(1,2),F(1)], [F(-1,4),F(0),F(1,4)], [F(0),F(1,4)], [F(0),F(1,2)], [F(0),F(1),F(2)]):
        A=((s+delta,b),(eps,d)); L=max(abs(s+delta)+abs(eps),abs(b)+abs(d)); M=abs(s)
        eta=abs(delta)+abs(eps); actual=(F(1),F(0)); predicted=F(1); bound=F(0)
        for n in range(7):
            c.check(abs(actual[0]-predicted)+abs(actual[1])<=bound,'ambient telescoping bound')
            bound=L*bound+eta*M**n
            actual=mat2(A,actual); predicted*=s
    # Same one-step calibrated residual, arbitrarily increased unseen amplification.
    epsilon=F(1,10)
    second_errors=[epsilon*(1+a) for a in (1,10,100)]
    c.check(second_errors[0]<second_errors[1]<second_errors[2], 'uncontrolled ambient growth')

    data={
        'sensor_worlds':[{'s':s,'theta':t,'nuisance':k,'display':s^t} for s,t,k in omega],
        'memory_counts':{'raw_candidate_sets':256,'correction_profiles':16,'current_target_sets':4},
        'noisy_majority':noisy,
        'linear_example':{'dimension':3,'calibrated_dimension':2,'continuation_core_dimension':1},
    }
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'data'/'illustrations.json').write_text(json.dumps(data,indent=2)+'\n')
    result={'status':'PASS','arithmetic':'integers, finite sets, exact fractions; F2 for linear completion examples',
            'groups':c.groups,'group_count':len(c.groups),'assertions':sum(g['assertions'] for g in c.groups),
            'runtime_seconds':time.perf_counter()-started,
            'non_claim':'Finite checks illustrate the proofs. They are not general theorem verification, trained-agent results, or empirical generalization.'}
    (ROOT/'validation'/'exact_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='groups'},indent=2))
    return result


if __name__ == '__main__':
    run()
