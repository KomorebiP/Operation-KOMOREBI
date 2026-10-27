#!/usr/bin/env python3
"""Exact-rational observable-state minimization with sparse generation certificates.

Input operators are KNOWN, not inferred from observations.  All arithmetic uses
fractions.Fraction.  The Lean finite-certificate theorem supplies the mathematical
contract, but this Python implementation is not itself Lean-verified.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

Q = Fraction
Word = tuple[int, ...]
Key = tuple[Word, int]
Provenance = dict[Key, Q]


def rational(value: Any) -> Q:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError('Use integers or exact rational strings, not booleans/floats.')
    if not isinstance(value, (int, str, Q)):
        raise ValueError('Unsupported rational coefficient: ' + repr(value))
    return Q(value)


@dataclass(frozen=True)
class Matrix:
    rows: tuple[tuple[Q, ...], ...]
    ncols: int

    def __post_init__(self) -> None:
        if self.ncols < 0 or any(len(row) != self.ncols for row in self.rows):
            raise ValueError('Inconsistent matrix dimensions.')
        if any(not isinstance(x, Q) for row in self.rows for x in row):
            raise TypeError('Matrix entries must be Fractions.')

    @property
    def nrows(self) -> int:
        return len(self.rows)

    @classmethod
    def parse(cls, rows: Sequence[Sequence[Any]], ncols: int) -> 'Matrix':
        return cls(tuple(tuple(rational(x) for x in row) for row in rows), ncols)

    @classmethod
    def zero(cls, m: int, n: int) -> 'Matrix':
        if m < 0 or n < 0:
            raise ValueError('Negative matrix dimension.')
        return cls(tuple(tuple(Q(0) for _ in range(n)) for _ in range(m)), n)

    @classmethod
    def eye(cls, n: int) -> 'Matrix':
        return cls(tuple(tuple(Q(i == j) for j in range(n)) for i in range(n)), n)

    def __matmul__(self, other: 'Matrix') -> 'Matrix':
        if self.ncols != other.nrows:
            raise ValueError('Matrix multiplication dimension mismatch.')
        return Matrix(tuple(tuple(sum((self.rows[i][k] * other.rows[k][j]
                         for k in range(self.ncols)), Q(0))
                         for j in range(other.ncols)) for i in range(self.nrows)), other.ncols)

    def json(self) -> list[list[str]]:
        return [[str(x) for x in row] for row in self.rows]


def scale_provenance(p: Mapping[Key, Q], a: Q) -> Provenance:
    return {key: a * v for key, v in p.items() if a * v}


def add_provenance(p: Mapping[Key, Q], q: Mapping[Key, Q], a: Q) -> Provenance:
    out = dict(p)
    for key, value in q.items():
        out[key] = out.get(key, Q(0)) + a * value
        if not out[key]:
            del out[key]
    return out


def row_basis(matrix: Matrix, proofs: Sequence[Provenance]) -> tuple[Matrix, list[Provenance], list[int]]:
    """Canonical reduced-row basis, carrying exact observation-generation witnesses."""
    if len(proofs) != matrix.nrows:
        raise ValueError('Provenance row mismatch.')
    rows = [list(row) for row in matrix.rows]
    provenance = [dict(p) for p in proofs]
    rank = 0
    pivots: list[int] = []
    for col in range(matrix.ncols):
        found = next((j for j in range(rank, len(rows)) if rows[j][col]), None)
        if found is None:
            continue
        rows[rank], rows[found] = rows[found], rows[rank]
        provenance[rank], provenance[found] = provenance[found], provenance[rank]
        a = Q(1) / rows[rank][col]
        rows[rank] = [a * x for x in rows[rank]]
        provenance[rank] = scale_provenance(provenance[rank], a)
        for j in range(len(rows)):
            if j != rank and rows[j][col]:
                b = -rows[j][col]
                rows[j] = [x + b * y for x, y in zip(rows[j], rows[rank])]
                provenance[j] = add_provenance(provenance[j], provenance[rank], b)
        pivots.append(col)
        rank += 1
        if rank == len(rows):
            break
    return Matrix(tuple(tuple(row) for row in rows[:rank]), matrix.ncols), provenance[:rank], pivots


def word_operator(operators: Sequence[Matrix], word: Word, dimension: int) -> Matrix:
    """Chronological convention: (i,j) applies T_i first, then T_j."""
    result = Matrix.eye(dimension)
    for i in word:
        if not 0 <= i < len(operators):
            raise ValueError('Certificate word has an invalid operator index.')
        result = operators[i] @ result
    return result


@dataclass(frozen=True)
class Model:
    compression: Matrix
    lift: Matrix
    dynamics: tuple[Matrix, ...]
    output: Matrix
    provenance: tuple[Provenance, ...]
    generation_depth: int
    horizon_bound: int
    rank_history: tuple[int, ...]
    closure_checks: int

    def json(self) -> dict[str, Any]:
        return {'schema_version': 1, 'coefficient_domain': 'Q',
                'dimension': self.compression.ncols,
                'model_dimension': self.compression.nrows,
                'output_dimension': self.output.nrows,
                'operator_count': len(self.dynamics),
                'generation_depth': self.generation_depth,
                'horizon_bound': self.horizon_bound,
                'strict_refinements': len(self.rank_history) - 1,
                'rank_history': list(self.rank_history), 'closure_checks': self.closure_checks,
                'compression': self.compression.json(), 'lift': self.lift.json(),
                'dynamics': [u.json() for u in self.dynamics], 'output': self.output.json(),
                'generation': [[{'word': list(w), 'output_row': j, 'coefficient': str(a)}
                                for (w, j), a in sorted(p.items())] for p in self.provenance],
                'trust_boundary': 'Exact Python certificate checks; not an extracted or fully verified Lean program.'}

    @classmethod
    def parse(cls, value: Mapping[str, Any]) -> 'Model':
        if value.get('schema_version') != 1 or value.get('coefficient_domain') != 'Q':
            raise ValueError('Unsupported model schema.')
        n, r = int(value['dimension']), int(value['model_dimension'])
        prov = []
        for row in value['generation']:
            d: Provenance = {}
            for term in row:
                key = (tuple(int(i) for i in term['word']), int(term['output_row']))
                if key in d:
                    raise ValueError('Duplicate generation-certificate key.')
                d[key] = rational(term['coefficient'])
            prov.append(d)
        return cls(Matrix.parse(value['compression'], n), Matrix.parse(value['lift'], r),
                   tuple(Matrix.parse(u, r) for u in value['dynamics']),
                   Matrix.parse(value['output'], r), tuple(prov),
                   int(value['generation_depth']), int(value['horizon_bound']),
                   tuple(int(i) for i in value['rank_history']), int(value['closure_checks']))


def validate_system(operators: Sequence[Matrix], observation: Matrix) -> int:
    n = observation.ncols
    if any(a.nrows != n or a.ncols != n for a in operators):
        raise ValueError('Each operator must be dimension by dimension.')
    return n


def validate_certificate(operators: Sequence[Matrix], observation: Matrix, model: Model) -> int:
    """Check finite matrix identities and sparse finite-observation generation.

    Returning a count means these exact identities passed, not that Python's
    implementation has itself been formally proved.
    """
    n = validate_system(operators, observation)
    c, lift, v = model.compression, model.lift, model.output
    r = c.nrows
    if c.ncols != n or lift.nrows != n or lift.ncols != r:
        raise ValueError('Certificate dimension mismatch.')
    if v.nrows != observation.nrows or v.ncols != r or len(model.dynamics) != len(operators):
        raise ValueError('Output/operator count mismatch.')
    if len(model.provenance) != r or model.generation_depth < 0:
        raise ValueError('Invalid generation certificate.')
    count = 0
    if c @ lift != Matrix.eye(r):
        raise ValueError('Surjectivity certificate C R = I failed.')
    count += 1
    if v @ c != observation:
        raise ValueError('Output certificate V C = O failed.')
    count += 1
    for a, u in zip(operators, model.dynamics):
        if c @ a != u @ c:
            raise ValueError('Dynamic intertwining C T_i = U_i C failed.')
        count += 1
    cache: dict[Word, Matrix] = {}
    for row, proof in zip(c.rows, model.provenance):
        generated = [Q(0)] * n
        for (w, j), coefficient in proof.items():
            if len(w) > model.generation_depth or not 0 <= j < observation.nrows:
                raise ValueError('Generation depth/output index failed.')
            if w not in cache:
                cache[w] = observation @ word_operator(operators, w, n)
            generated = [x + coefficient * y for x, y in zip(generated, cache[w].rows[j])]
        if tuple(generated) != row:
            raise ValueError('Finite observation-generation identity failed.')
        count += 1
    if model.generation_depth > model.horizon_bound:
        raise ValueError('Declared generation depth exceeds the finite horizon.')
    if len(model.rank_history) - 1 > model.horizon_bound:
        raise ValueError('Too many strict refinement steps.')
    if any(a >= b for a, b in zip(model.rank_history, model.rank_history[1:])):
        raise ValueError('Recorded strict refinements are not strict.')
    if not model.rank_history or model.rank_history[-1] != r:
        raise ValueError('Rank history has incorrect final rank.')
    return count


def minimize(operators: Sequence[Matrix], observation: Matrix, *,
             max_dimension: int = 128, max_certificate_terms: int = 200_000) -> Model:
    n = validate_system(operators, observation)
    if n > max_dimension:
        raise ValueError('Dimension exceeds the declared resource cap.')
    c, proof, pivots = row_basis(observation, [{((), j): Q(1)} for j in range(observation.nrows)])
    bound = n - c.nrows
    ranks = [c.nrows]
    depth = 0
    checks = 0
    while True:
        rows = list(c.rows)
        provenance = [dict(p) for p in proof]
        for i, a in enumerate(operators):
            rows.extend((c @ a).rows)
            provenance.extend([{((i,) + w, j): value for (w, j), value in p.items()} for p in proof])
        if sum(len(p) for p in provenance) > max_certificate_terms:
            raise ValueError('Sparse-certificate resource cap reached.')
        new_c, new_proof, new_pivots = row_basis(Matrix(tuple(rows), n), provenance)
        checks += 1
        if new_c == c:
            break
        if new_c.nrows <= c.nrows or depth >= bound:
            raise RuntimeError('Structural termination invariant violated.')
        c, proof, pivots = new_c, new_proof, new_pivots
        depth += 1
        ranks.append(c.nrows)
    lift_rows = [[Q(0)] * c.nrows for _ in range(n)]
    for i, pivot in enumerate(pivots):
        lift_rows[pivot][i] = Q(1)
    lift = Matrix(tuple(tuple(row) for row in lift_rows), c.nrows)
    model = Model(c, lift, tuple(c @ a @ lift for a in operators), observation @ lift,
                  tuple(proof), depth, bound, tuple(ranks), checks)
    validate_certificate(operators, observation, model)
    return model


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--max-dimension', type=int, default=128)
    args = parser.parse_args()
    try:
        raw = json.loads(args.input.read_text())
        n = int(raw['dimension'])
        ops = tuple(Matrix.parse(a, n) for a in raw['operators'])
        obs = Matrix.parse(raw['observation'], n)
        result = minimize(ops, obs, max_dimension=args.max_dimension)
        artifact = result.json()
        artifact['certificate_identity_checks'] = validate_certificate(ops, obs, result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2) + '\n')
        print(json.dumps({'passed': True, 'fine_dimension': n,
                          'model_dimension': result.compression.nrows,
                          'horizon_bound': result.horizon_bound,
                          'strict_refinements': len(result.rank_history) - 1,
                          'certificate': str(args.output)}))
    except (KeyError, ValueError, TypeError, RuntimeError, OSError) as exc:
        parser.exit(1, f'FAILED: {type(exc).__name__}: {exc}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
