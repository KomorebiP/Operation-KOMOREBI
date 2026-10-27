#!/usr/bin/env python3
"""Independent exact finite controls for Lean Block 02.

No Lean output, finite rank library, solver, or inherited scientific checker is
used. This is finite cross-validation, not the universal proof certificate.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path
import sys

Gate = tuple[str, int, tuple[int, ...]]


def variables(n: int) -> tuple[int, ...]:
    return tuple(sum(((x >> i) & 1) << x for x in range(1 << n)) for i in range(n))


@lru_cache(maxsize=None)
def degree(n: int, table: int) -> int:
    coeff = [(table >> x) & 1 for x in range(1 << n)]
    for i in range(n):
        for s in range(1 << n):
            if s & (1 << i):
                coeff[s] ^= coeff[s ^ (1 << i)]
    return max((s.bit_count() for s, c in enumerate(coeff) if c), default=0)


def alphabet(w: int) -> tuple[Gate, ...]:
    gates: list[Gate] = []
    for t in range(w):
        gates.append(('not', t, ()))
        for c in range(w):
            if c != t:
                gates.append(('cnot', t, (c,)))
        for a, b in combinations([i for i in range(w) if i != t], 2):
            gates.append(('toffoli', t, (a, b)))
    return tuple(gates)


def execute(word: tuple[Gate, ...], state: tuple[int, ...], mask: int) -> tuple[int, ...]:
    s = list(state)
    for op, t, controls in word:
        assert len(set((t,) + controls)) == 1 + len(controls)
        assert len(controls) == {'not': 0, 'cnot': 1, 'toffoli': 2}[op]
        term = mask
        for i in controls:
            term &= s[i]
        s[t] ^= term
    return tuple(s)


def safe_profiles(n: int) -> tuple[list[int], list[int]]:
    count = 1 << (1 << n)
    beta = []
    for f in range(count):
        cover = [0] * (n + 1)
        for h in range(count):
            if h & ~f == 0:
                cover[degree(n, h)] |= h
        seen = 0
        for d in range(n + 1):
            seen |= cover[d]
            if seen == f:
                beta.append(d)
                break
        else:
            raise AssertionError('No safe cover: indicator construction violated')
    vs = variables(n)
    one = count - 1
    affine: set[int] = set()
    for c in (0, one):
        for support in range(1 << n):
            h = c
            for i in range(n):
                if support & (1 << i):
                    h ^= vs[i]
            affine.add(h)
    star = [max(beta[f ^ a] for a in affine) for f in range(count)]
    assert all(0 <= b <= s <= n for b, s in zip(beta, star))
    return beta, star


def main() -> int:
    if not __debug__ or sys.flags.optimize:
        raise RuntimeError('Optimized Python disables proof-control assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    profiles = {n: safe_profiles(n) for n in range(4)}
    and2 = variables(2)[0] & variables(2)[1]
    assert profiles[2][0][and2] == profiles[2][1][and2] == 2
    assert degree(2, and2) == 2

    circuits = products_checked = restored = boundary_cases = reverse_cases = 0
    by_width = {}
    for w, depth in ((3, 3), (4, 2)):
        base = variables(w)
        mask = (1 << (1 << w)) - 1
        local = {'alphabet': len(alphabet(w)), 'max_length': depth,
                 'words': 0, 'restored_oracles': 0, 'functions': set()}
        for length in range(depth + 1):
            for word in product(alphabet(w), repeat=length):
                circuits += 1
                local['words'] += 1
                state = execute(word, base, mask)
                t = sum(g[0] == 'toffoli' for g in word)
                assert execute(tuple(reversed(word)), state, mask) == base
                reverse_cases += 1 << w
                for support in range(1 << w):
                    h = mask
                    for i in range(w):
                        if support & (1 << i):
                            h &= state[i]
                    assert degree(w, h) <= t + support.bit_count()
                    products_checked += 1
                n = w - 1
                delta = state[-1] ^ base[-1]
                smallmask = (1 << (1 << n)) - 1
                f = delta & smallmask
                if state[:-1] == base[:-1] and (delta >> (1 << n)) == f:
                    restored += 1
                    local['restored_oracles'] += 1
                    local['functions'].add(f)
                    boundary_cases += 1 << w
                    beta, star = profiles[n]
                    assert t >= max(0, degree(n, f) - 1, 2 * star[f] - 3)
                    for cut in range(length + 1):
                        a = execute(word[:cut], base, mask)
                        b = execute(tuple(reversed(word[cut:])), base, mask)
                        ta = sum(g[0] == 'toffoli' for g in word[:cut])
                        tb = t - ta
                        cover = 0
                        for ai, bi in zip(a, b):
                            h = (ai ^ bi) & smallmask
                            assert h & ~f == 0
                            assert degree(n, h) <= max(ta, tb) + 1
                            cover |= h
                        assert cover == f
        local['functions'] = sorted(local['functions'])
        by_width[str(w)] = local

    write_checks = 0
    wire_lists = [l for r in range(5) for l in product(range(3), repeat=r)]
    controls = [l for r in range(3) for l in product(range(3), repeat=r)]
    for assignment in range(8):
        s = tuple(bool(assignment & (1 << i)) for i in range(3))
        for target in range(3):
            for control in controls:
                term = all(s[i] for i in control)
                updated = list(s)
                updated[target] ^= term
                for l in wire_lists:
                    actual = all(updated[i] for i in l)
                    rest = tuple(i for i in l if i != target)
                    expected = ((s[target] ^ term) and all(s[i] for i in rest)
                                if target in l else all(s[i] for i in l))
                    assert actual == expected
                    if target in l:
                        assert len(rest) + 1 <= len(l)
                    write_checks += 1
    result = {
        'status': 'PASS', 'arithmetic': 'exact Boolean truth tables; integer Mobius transform',
        'profile_functions': sum(1 << (1 << n) for n in range(4)),
        'profile_input_sizes': [0, 1, 2, 3],
        'profiles': {str(n): {'beta': b, 'betaStar': s} for n, (b, s) in profiles.items()},
        'circuit_words': circuits, 'width_contracts': by_width,
        'final_register_product_bounds': products_checked,
        'reversal_assignment_cases': reverse_cases,
        'restored_oracle_words': restored,
        'restored_boundary_assignment_cases': boundary_cases,
        'target_elimination_cases_including_repeated_wires': write_checks,
        'mathematical_controls': {'beta_andTwo': 2, 'betaStar_andTwo': 2,
                                  'AND_is_not_affine': True},
        'limits': ['Finite controls only; universal results are proved in the Lean sources.',
                   'No circuit optimality or unrestricted P versus NP separation is inferred.']}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('profiles','width_contracts')}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
