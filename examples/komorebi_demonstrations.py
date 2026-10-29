#!/usr/bin/env python3
"""Three fixed, exact integer demonstrations for the Komorebi reading guide.

Python 3.10 or later. Standard library only. No files or network are used.
These calculations illustrate existing tutorials. They do not run Lean,
qualify production software or verify the collection's general theorems.
"""
import argparse


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def multiply(a, b):
    return tuple(tuple(sum(x*y for x, y in zip(row, column))
                       for column in zip(*b)) for row in a)


def apply(a, vector):
    return tuple(sum(x*y for x, y in zip(row, vector)) for row in a)


def add_matrices(matrices):
    return tuple(tuple(sum(a[i][j] for a in matrices)
                       for j in range(len(matrices[0][0])))
                 for i in range(len(matrices[0])))


def add_vectors(vectors):
    return tuple(map(sum, zip(*vectors)))


def packets():
    x = (2, 3)
    p = (((1, 0), (0, 0)), ((0, 0), (0, 1)))
    identity, zero = ((1, 0), (0, 1)), ((0, 0), (0, 0))
    t = ((1, 2), (3, 4))
    require(add_matrices(p) == identity, 'Packets must sum to the identity')
    for j in range(2):
        for i in range(2):
            require(multiply(p[j], p[i]) == (p[i] if i == j else zero),
                    'Packet multiplication identity failed')
    # Rows are target packets and columns are source packets.
    blocks = tuple(multiply(multiply(p[j], t), p[i])
                   for j in range(2) for i in range(2))
    require(add_matrices(blocks) == t, 'Block reconstruction failed')
    direct = apply(t, x)
    rebuilt = add_vectors(tuple(apply(b, x) for b in blocks))
    missing = add_vectors(tuple(apply(b, x) for b in blocks[:-1]))
    require(direct == rebuilt == (8, 18), 'Unexpected reconstructed result')
    require(missing == (8, 6) and missing != direct, 'Missing-block control failed')
    return '\n'.join([
        f'Input: {x}',
        f'Packet parts: {tuple(apply(q, x) for q in p)}',
        f'Block contributions: {tuple(apply(b, x) for b in blocks)}',
        f'Direct result: {direct}',
        f'Reconstructed result: {rebuilt}',
        f'Without the final block: {missing}',
        'PASS: packets',
    ])


def refinement():
    x = tuple(range(1, 9))
    coarse = tuple(x[r::2] for r in range(2))
    fine = tuple(x[r::4] for r in range(4))
    # Interleave by original addresses. No padding or boundary extension.
    rebuilt = tuple(fine[i % 4][i // 4] for i in range(len(x)))
    lifted = tuple(tuple(v if i % 4 == r else 0 for i, v in enumerate(x))
                   for r in range(4))
    for r in range(2):
        require(add_vectors((lifted[r], lifted[r+2])) ==
                tuple(v if i % 2 == r else 0 for i, v in enumerate(x)),
                'Coarse packet differs from its fine children')
    kept = add_vectors((lifted[0], lifted[1], lifted[3]))
    residual = tuple(a-b for a, b in zip(x, kept))
    energy = sum(v*v for v in residual)
    require(rebuilt == x, 'Interleaving failed')
    require(residual == lifted[2] and energy == 58, 'Discarded-packet control failed')
    return '\n'.join([
        f'Input: {x}', f'Two packets: {coarse}', f'Four packets: {fine}',
        f'Interleaved: {rebuilt}', f'Without remainder 2: {kept}',
        f'Residual: {residual}', f'Squared residual norm: {energy}',
        'PASS: refinement',
    ])


def recovery():
    r, f, h = ((1, 1),), ((1, 0),), ((2, 2),)
    u, v = (1, 0), (0, 1)
    summary = apply(r, u)[0]
    answers = (apply(f, u)[0], apply(f, v)[0])
    w = tuple(a-b for a, b in zip(u, v))
    rw, fw = apply(r, w)[0], apply(f, w)[0]
    require(summary == apply(r, v)[0] == 1, 'Collision is missing')
    require(answers == (1, 0) and rw == 0 and fw == 1, 'Witness failed')
    # The matrix identity proves the compatible linear rule for every vector.
    require(multiply(((2,),), r) == h, 'Compatible observation identity failed')
    return '\n'.join([
        f'Inputs: {u} and {v}', f'Same summary: {summary}',
        f'Requested first coordinates: {answers}', f'Kernel witness: {w}',
        f'R(w): {rw}', f'F(w): {fw}',
        f'Compatible observation coefficients: {h[0]}',
        'PASS: recovery',
    ])


DEMOS = {'packets': packets, 'refinement': refinement, 'recovery': recovery}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('demo', nargs='?', choices=(*DEMOS, 'all'), default='all')
    args = parser.parse_args()
    names = DEMOS if args.demo == 'all' else (args.demo,)
    print('\n\n'.join(DEMOS[name]() for name in names))


if __name__ == '__main__':
    main()
