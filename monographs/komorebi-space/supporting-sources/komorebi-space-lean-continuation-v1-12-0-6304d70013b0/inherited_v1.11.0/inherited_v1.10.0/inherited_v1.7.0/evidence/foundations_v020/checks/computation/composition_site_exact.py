#!/usr/bin/env python3
"""Independent finite audit of the composition topology.

Domain: all labelled preorders on 0..n-1 for n <= 3, plus the discrete,
chain, and indiscrete preorders for n=4. Sieves are literally enumerated
lower ideals of the powerset poset. No infinite or Lean proof is inferred.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
from itertools import product
import hashlib
import json
from pathlib import Path
import platform
import time
from datetime import datetime, timezone


def sub(a: int, b: int) -> bool:
    return (a & b) == a


@lru_cache(None)
def subsets(w: int) -> tuple[int, ...]:
    return tuple(x for x in range(w + 1) if sub(x, w))


@lru_cache(None)
def sieves(w: int) -> tuple[frozenset[int], ...]:
    ss = subsets(w)
    return tuple(frozenset(ss[k] for k in range(len(ss)) if b >> k & 1)
                 for b in range(1 << len(ss))
                 if all(not (b >> k & 1) or all(
                     not sub(ss[j], ss[k]) or (b >> j & 1)
                     for j in range(len(ss))) for k in range(len(ss))))


def preorders(n: int):
    off = [(a,b) for a in range(n) for b in range(n) if a != b]
    for mask in range(1 << len(off)):
        rel = {(a,a) for a in range(n)} | {p for k,p in enumerate(off) if mask >> k & 1}
        if all((a,c) in rel for a,b in rel for bb,c in rel if b == bb):
            yield frozenset(rel)


def run() -> dict:
    counts = {'preorders_up_to_three': 0, 'four_view_models': 0,
              'patches': 0, 'sieves': 0, 'base_changes': 0,
              'transitivity_pairs': 0, 'generated_families': 0}
    assertions = 0
    def check(ok: bool, message: str) -> None:
        nonlocal assertions
        assertions += 1
        if not ok:
            raise AssertionError(message)

    models = [(n,r) for n in range(4) for r in preorders(n)]
    counts['preorders_up_to_three'] = len(models)
    for name in ('discrete','chain','indiscrete'):
        r = frozenset((a,b) for a in range(4) for b in range(4)
                      if (a == b if name == 'discrete' else a <= b if name == 'chain' else True))
        models.append((4,r))
        counts['four_view_models'] += 1

    for n, rel in models:
        triples = tuple((a,b,c) for a in range(n) for b in range(n) for c in range(n)
                        if (a,b) in rel and (b,c) in rel)
        supports = frozenset((1 << a) | (1 << b) | (1 << c) for a,b,c in triples)
        allpatch = (1 << n) - 1
        required = {w:frozenset(t for t in supports if sub(t,w)) for w in subsets(allpatch)}
        covering = lambda w, s: required[w] <= s
        for w in subsets(allpatch):
            counts['patches'] += 1
            ideals = sieves(w)
            check(covering(w,frozenset(subsets(w))), 'maximal sieve is not covering')
            for s in ideals:
                counts['sieves'] += 1
                # Orthogonal implementation uses triples and containing patches,
                # not direct membership of their computed support.
                by_paths = all(any(all(t >> x & 1 for x in (a,b,c)) for t in s)
                               for a,b,c in triples if all(w >> x & 1 for x in (a,b,c)))
                check(covering(w,s) == by_paths, 'path/support coverage disagreement')
                if not covering(w,s):
                    continue
                for z in subsets(w):
                    counts['base_changes'] += 1
                    pulled = frozenset(t for t in s if sub(t,z))
                    check(covering(z,pulled), 'base change law failed')
                for r in ideals:
                    counts['transitivity_pairs'] += 1
                    local = all(covering(z,frozenset(t for t in r if sub(t,z))) for z in s)
                    check(not local or covering(w,r), 'sieve transitivity failed')
            # Every family for <=3 views; a fixed suite at the four-view boundary.
            ss = subsets(w)
            if n <= 3:
                families = [tuple(ss[k] for k in range(len(ss)) if mask >> k & 1)
                            for mask in range(1 << len(ss))]
            else:
                families = [(), (w,), ss, tuple(w & ~(1 << i) for i in range(n)),
                            tuple(required[w])]
            for family in families:
                counts['generated_families'] += 1
                generated = frozenset(z for z in ss if any(sub(z,t) for t in family))
                direct = all(any(sub(t,a) for a in family) for t in required[w])
                check(covering(w,generated) == direct, 'generated-family criterion failed')
            for support in required[w]:
                for s in sieves(support):
                    check(covering(support,s) == (s == frozenset(subsets(support))),
                          'support sieve criterion failed')

    # Rejected stronger claims are exact counterexamples, not random mutations.
    three = tuple(7 & ~(1 << i) for i in range(3))
    objects = all(any(t >> a & 1 for t in three) for a in range(3))
    arrows = all(any((t >> a & 1) and (t >> b & 1) for t in three)
                 for a in range(3) for b in range(a,3))
    triple = any(sub(7,t) for t in three)
    controls = [
        {'claim':'object coverage alone is a composition cover',
         'rejected':objects and not triple},
        {'claim':'arrow coverage alone is a composition cover',
         'rejected':arrows and not triple},
        {'claim':'a covering family must contain the whole patch',
         'rejected':all(any(all((15 & ~(1 << i)) >> x & 1 for x in (a,b,c))
                          for i in range(4))
                        for a in range(4) for b in range(a,4) for c in range(b,4))
                    and all((15 & ~(1 << i)) != 15 for i in range(4))}]
    for c in controls:
        check(c['rejected'], 'counterexample was not detected: '+c['claim'])
    return {'status':'PASS', 'counts':counts, 'assertions':assertions,
            'negative_controls':controls, 'arithmetic':'exact Boolean relations and integer bitsets',
            'bounds':{'all_labelled_preorders_n':[0,1,2,3],
                      'n4_preorders':['discrete','chain','indiscrete'],
                      'sieves':'all lower ideals on every subpatch',
                      'families':'all for n<=3; five deterministic families per n4 patch'},
            'non_claims':['Finite examples do not prove the topology or stack theorem.',
                          'No general category or nonabelian descent is inferred from this audit.']}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    start = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    result = run()
    result.update({'started_at_utc':started, 'runtime_seconds':time.monotonic()-start,
                   'python_version':platform.python_version(), 'randomness':{'used':False},
                   'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
