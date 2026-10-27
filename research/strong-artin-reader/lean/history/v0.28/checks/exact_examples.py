#!/usr/bin/env python3
"""Independent exact checks of the two finite controls; no external packages.

This finite enumeration is corroboration of the examples, not evidence for the
universal Lean lifting theorems. Run from any directory with Python 3.10+.
"""
from itertools import product, combinations
from pathlib import Path
import hashlib
import json
import platform


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def matrix_multiply(a: tuple[int, ...], b: tuple[int, ...], modulus: int) -> tuple[int, ...]:
    return tuple(sum(a[2*i+k] * b[2*k+j] for k in range(2)) % modulus
                 for i in range(2) for j in range(2))


def run() -> dict:
    # Additive coordinates in C2 x C2, corresponding to the multiplicative
    # character source used in the Lean example.
    group = list(product(range(2), repeat=2))
    identity = (0, 0)
    first, second, diagonal = (1, 0), (0, 1), (1, 1)
    homomorphisms = []
    examined = 0
    for values in product((1, 3), repeat=4):
        examined += 1
        f = dict(zip(group, values))
        if f[identity] != 1:
            continue
        if all(f[((a[0]+b[0]) % 2, (a[1]+b[1]) % 2)] == f[a]*f[b] % 4
               for a in group for b in group):
            homomorphisms.append(f)
    require(examined == 16, 'Enumeration population mismatch')
    require(len(homomorphisms) == 4, 'Unexpected character count')
    local_generators = (first, second, diagonal)
    prescribed_values = (1, 1, 3)
    full_solutions = [f for f in homomorphisms
                     if all(f[g] == value for g, value in zip(local_generators, prescribed_values))]
    require(not full_solutions, 'The claimed strict gluing obstruction was not present')
    pair_counts = {}
    for indices in combinations(range(3), 2):
        count = sum(all(f[local_generators[i]] == prescribed_values[i] for i in indices)
                    for f in homomorphisms)
        require(count > 0, f'Pair {indices} did not extend')
        pair_counts[','.join(map(str, indices))] = count
    # Each pair of distinct order-two subgroups intersects only at the identity.
    subgroups = [{identity, generator} for generator in local_generators]
    require(all(subgroups[i] & subgroups[j] == {identity}
                for i, j in combinations(range(3), 2)), 'Unexpected subgroup overlap')

    modulus = 9
    identity_matrix = (1, 0, 0, 1)
    a = (8, 0, 0, 1)
    b = (8, 6, 0, 1)
    u = (1, 3, 0, 1)
    u_inverse = (1, 6, 0, 1)
    mul = lambda x, y: matrix_multiply(x, y, modulus)
    require(mul(a, a) == identity_matrix and mul(b, b) == identity_matrix,
            'Local matrices are not involutions')
    require(mul(u, u_inverse) == identity_matrix, 'Wrong inverse')
    require(tuple(v % 3 for v in u) == identity_matrix, 'Conjugator not residual identity')
    require(tuple(v % 3 for v in a) == tuple(v % 3 for v in b), 'Different residues')
    require(mul(mul(u, a), u_inverse) == b, 'Kernel conjugacy failed')
    require(mul(a, b) != mul(b, a), 'Noncommutativity control failed')
    require((4 * 7) % 9 == 1, 'Group order not invertible')

    return {
        'status': 'PASS',
        'method': 'exhaustive finite character enumeration and exact modular integer matrices',
        'python': platform.python_version(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'character_control': {
            'source': 'C2 x C2', 'target': '(Z/4Z)^units',
            'all_functions_examined': examined, 'homomorphisms_found': len(homomorphisms),
            'strict_triple_extensions': len(full_solutions), 'pair_extension_counts': pair_counts,
            'overlap_agreement': True,
        },
        'matrix_control': {
            'coefficient_ring': 'Z/9Z', 'residue_ring': 'Z/3Z',
            'A': a, 'B': b, 'U': u, 'U_inverse': u_inverse,
            'AB': mul(a,b), 'BA': mul(b,a),
            'kernel_conjugacy': True, 'local_matrices_commute': False,
            'source_order_4_is_unit': True,
        },
        'nonclaims': ['not a universal proof', 'not a Strong Artin counterexample',
                      'no arithmetic local Galois group is constructed here'],
    }


if __name__ == '__main__':
    result = run()
    output = Path(__file__).resolve().parent / 'FINITE_CHECKS.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
