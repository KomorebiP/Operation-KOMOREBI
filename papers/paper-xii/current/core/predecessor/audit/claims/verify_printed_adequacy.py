"""Exact check of the printed S3/F7 matrices, with no numerical tolerances.

This checks the finite printed identities, not a universal adequacy theorem.
"""

from itertools import permutations
import json


def determinant_mod7(matrix):
    size = len(matrix)
    value = 0
    for permutation in permutations(range(size)):
        term = (-1) ** sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        for index in range(size):
            term *= matrix[index][permutation[index]]
        value += term
    return value % 7


def multiply(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(2)) % 7 for j in range(2)]
        for i in range(2)
    ]


def flatten(matrix):
    return sum(matrix, [])


def trace(matrix):
    return (matrix[0][0] + matrix[1][1]) % 7


identity = [[1, 0], [0, 1]]
s = [[6, 1], [0, 1]]
t = [[0, 6], [1, 6]]
z = [[2, 3], [4, 5]]
standard_witness = [[6, 4], [3, 1]]
projectors = [
    [[2, 4], [3, 6]],
    [[0, 4], [0, 1]],
    [[1, 3], [0, 0]],
    [[1, 0], [4, 0]],
]
result = {
    "arithmetic": "exact F_7",
    "tested_object": "printed S3 standard/adjoint/projector matrices",
    "endomorphism_span_determinant": determinant_mod7(
        list(map(list, zip(*[flatten(m) for m in [identity, s, t, multiply(s, t)]])))
    ),
    "projector_trace_pairing_determinant": determinant_mod7(
        [[p[0][0], p[1][0], p[0][1], p[1][1]] for p in projectors]
    ),
    "adjoint_constituent_determinant": determinant_mod7(
        [[2, 1, 1], [3, 1, 5], [4, 2, 6]]
    ),
    "sign_witness_trace": trace(multiply(projectors[0], z)),
    "standard_witness_trace": trace(multiply(projectors[1], standard_witness)),
    "projectors_idempotent": [multiply(p, p) == p for p in projectors],
    "sign_conjugation_transposition": multiply(multiply(s, z), s)
    == [[(-x) % 7 for x in row] for row in z],
    "sign_conjugation_three_cycle": multiply(multiply(t, z), multiply(t, t)) == z,
    "universal_claim": False,
}
print(json.dumps(result, indent=2))
