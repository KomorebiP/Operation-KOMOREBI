#!/usr/bin/env python3
"""Exact finite audit for the Komorebi Space worked proof companion.

Run: python verify_worked_example.py --output .
Needs NumPy and Matplotlib only to replay the original atlas verifier.
All new algebra and scalar computations use fractions.Fraction.
No graph sampling is used to verify a mathematical identity.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import TypeAlias

Mode: TypeAlias = tuple[str, int, int]
Poly: TypeAlias = dict[Mode, F]
Family: TypeAlias = list[Poly]
CUT = (1, 2, 4, 8)
ROOT = Path(__file__).resolve().parent


def add(*terms: tuple[F | int, Poly]) -> Poly:
    result: Poly = {}
    for scale, poly in terms:
        for key, coefficient in poly.items():
            result[key] = result.get(key, F(0)) + scale * coefficient
    return {key: value for key, value in result.items() if value != 0}


def truncate(poly: Poly, cutoff: int) -> Poly:
    return {k: c for k, c in poly.items() if max(abs(k[1]), abs(k[2])) <= cutoff and c}


def modes(cutoff: int) -> list[Mode]:
    result: list[Mode] = [('const', 0, 0)]
    for a in range(-cutoff, cutoff + 1):
        for b in range(-cutoff, cutoff + 1):
            if a > 0 or (a == 0 and b > 0):
                result += [('cos', a, b), ('sin', a, b)]
    return result


def inner(p: Poly, q: Poly) -> F:
    return sum((c * q.get(k, F(0)) * (F(1) if k[0] == 'const' else F(1, 2))
                for k, c in p.items()), F(0))


def energy(p: Poly) -> F:
    return inner(p, p)


def family_energy(a: Family) -> F:
    return sum((energy(p) for p in a), F(0))


def family_add(a: Family, b: Family, scale: F | int = 1) -> Family:
    if len(a) != len(b):
        raise ValueError('Mismatched family lengths')
    return [add((1, p), (scale, q)) for p, q in zip(a, b)]


def delta(a: Family) -> Family:
    if len(a) != 4:
        raise ValueError('Expected four views')
    return [add((1, truncate(a[n + 1], CUT[n])), (-1, a[n])) for n in range(3)]


def lift(r: Family) -> Family:
    """S(r), with delta S = identity and highest view fixed at zero."""
    if len(r) != 3:
        raise ValueError('Expected three typed residuals')
    return [add((-1, r[0]), (-1, truncate(r[1], 1)), (-1, truncate(r[2], 1))),
            add((-1, r[1]), (-1, truncate(r[2], 2))),
            add((-1, r[2])), {}]


def finest_repair(a: Family) -> Family:
    return [truncate(a[3], q) for q in CUT]


def orthogonal_repair(a: Family) -> Family:
    """Unconstrained least squares repair: average each coefficient across its views."""
    fine: Poly = {}
    for k in modes(8):
        support = [n for n, q in enumerate(CUT) if max(abs(k[1]), abs(k[2])) <= q]
        mean = sum((a[n].get(k, F(0)) for n in support), F(0)) / len(support)
        if mean:
            fine[k] = mean
    return [truncate(fine, q) for q in CUT]


def obstruction_coordinates(r: Family) -> Family:
    """Residual modulo corrections supported only at view 2."""
    return [r[0], add((1, r[1]), (1, truncate(r[2], 2)))]


def serial(poly: Poly) -> list[dict]:
    return [{'kind': k[0], 'frequency': [k[1], k[2]], 'coefficient': str(c)}
            for k, c in sorted(poly.items())]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    spec = importlib.util.spec_from_file_location('atlas_v3', ROOT / 'render_komorebi.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('Original renderer cannot be loaded')
    atlas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(atlas)
    baseline = atlas.exact_verification()

    checks: Counter[str] = Counter()
    def require(ok: bool, label: str) -> None:
        if not ok:
            raise AssertionError(f'Failed exact check: {label}')
        checks[label] += 1

    x: Family = [truncate(atlas.SEED, q) for q in CUT]
    ds = [add((1, x[n + 1]), (-1, x[n])) for n in range(3)]
    eta: Poly = {('cos', 1, 0): F(1, 5)}
    y = [dict(p) for p in x]
    y[2] = add((1, y[2]), (1, eta))
    require(x == atlas.X and ds == atlas.D, 'independent_model_matches_renderer')
    require(delta(x) == [{}, {}, {}], 'reference_is_coherent')
    require(delta(y) == [{}, eta, add((-1, eta))], 'two_signed_defects')
    require(obstruction_coordinates(delta(y)) == [{}, {}], 'protected_obstruction_is_zero')

    # Every basis vector of the whole 404-dimensional raw family space.
    for slot, q in enumerate(CUT):
        for key in modes(q):
            a: Family = [{}, {}, {}, {}]
            a[slot] = {key: F(1)}
            c = finest_repair(a)
            require(delta(c) == [{}, {}, {}], 'finest_repair_coherence')
            require(c[3] == a[3], 'finest_repair_protection')
            require(finest_repair(c) == c, 'finest_repair_idempotence')
            require(family_add(a, c, -1) == lift(delta(a)), 'exact_defect_decomposition')
            o = orthogonal_repair(a)
            require(delta(o) == [{}, {}, {}], 'least_squares_repair_coherence')
            require(orthogonal_repair(o) == o, 'least_squares_repair_idempotence')
            e = family_add(a, o, -1)
            # For this input only one Fourier key is supported. Coefficient
            # cancellation verifies orthogonality to its coherent basis family;
            # all other modes are orthogonal by the proved Fourier identities.
            g = [truncate({key: F(1)}, cutoff) for cutoff in CUT]
            require(sum((inner(ei, gi) for ei, gi in zip(e, g)), F(0)) == 0,
                    'least_squares_error_orthogonal_to_kernel')
            require(family_energy(a) == family_energy(e) + family_energy(o),
                    'least_squares_pythagoras')

    # Every basis vector of the 115-dimensional adjacent-residual space.
    for slot, q in enumerate(CUT[:3]):
        for key in modes(q):
            r: Family = [{}, {}, {}]
            r[slot] = {key: F(1)}
            s = lift(r)
            require(delta(s) == r, 'surjective_differential_right_inverse')
            require(s[3] == {}, 'right_inverse_preserves_finest_view')
            # Quotient by view-2-only correction: remove the third residual.
            correction: Family = [{}, {}, r[2], {}]
            reduced = family_add(r, delta(correction))
            require(reduced == obstruction_coordinates(r) + [{}], 'obstruction_normal_form')

    for key in modes(4):
        k: Poly = {key: F(1)}
        allowed: Family = [{}, {}, k, {}]
        require(obstruction_coordinates(delta(allowed)) == [{}, {}],
                'obstruction_annihilates_allowed_changes')

    parts = [x[0], *ds]
    expected = [F(19, 100), F(17, 400), F(41, 3200), F(113, 25088)]
    for i, p in enumerate(parts):
        require(energy(p) == expected[i], 'component_energy')
        for j in range(i):
            require(inner(p, parts[j]) == 0, 'orthogonal_scale_bands')
    for n in range(4):
        require(energy(x[n]) == sum(expected[:n + 1], F(0)), 'resolution_energy_telescope')

    def origin(p: Poly) -> F:
        return sum((c for k, c in p.items() if k[0] != 'sin'), F(0))
    origins = [F(7, 10), F(17, 20), F(39, 40), F(83, 80)]
    for p, expected_value in zip(x, origins):
        require(origin(p) == expected_value, 'origin_worked_value')

    protected = finest_repair(y)
    closest = orthogonal_repair(y)
    quarter = add((F(1, 4), eta))
    require(protected == x, 'displayed_protected_repair')
    require(closest == [add((1, p), (1, quarter)) for p in x], 'displayed_nearest_repair')
    require(family_energy(family_add(y, protected, -1)) == F(1, 50), 'protected_cost')
    require(family_energy(family_add(y, closest, -1)) == F(3, 200), 'nearest_cost')
    require(family_energy(delta(y)) == F(1, 25), 'residual_energy')

    # These are negative controls: success means detecting a deliberately false claim.
    require(add((1, x[0]), (1, ds[0]), (1, ds[1])) != x[3],
            'negative_control_omitted_finest_detail_detected')
    require(delta(y) != [{}, eta, eta], 'negative_control_wrong_residual_sign_detected')
    require(add((1, x[1]), (-1, x[0])) != {},
            'negative_control_pointwise_difference_not_compatibility_defect')
    def asymmetric(p: Poly) -> Poly:
        return {k: c for k, c in p.items() if abs(k[1]) <= 1 and abs(k[2]) <= 2}
    test = {('cos', 0, 2): F(1)}
    require(asymmetric(atlas.swap_coordinates(test)) != atlas.swap_coordinates(asymmetric(test)),
            'negative_control_asymmetric_cutoff_breaks_swap_naturality')
    for middle in [F(-7), F(0), F(1, 2), F(1), F(3, 2), F(11)]:
        r0, r1 = middle - 1, 2 * middle - 3
        require(2 * r0 - r1 == 1, 'branching_nonzero_obstruction_independent_of_lift')

    report = {
        'status': 'PASS',
        'original_verifier_replayed': baseline,
        'additional_exact_checks': sum(checks.values()),
        'additional_checks_by_type': dict(checks),
        'total_exact_checks': baseline['exact_checks'] + sum(checks.values()),
        'coverage': {'highest_fourier_space': 289, 'raw_family_space': 404,
                     'adjacent_residual_space': 115, 'allowed_view_2_corrections': 81},
        'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in ('render_komorebi.py', 'verify_worked_example.py')},
        'limitations': ['Exact finite coefficient calculations, not a Lean run.',
                        'Infinite convergence statements are proved in the companion, not tested by finite sampling.',
                        'Fourier orthogonality and linearity are justified in the written proof.',
                        'Numerical renderings remain floating-point evaluations of the exact polynomial data.'],
    }
    steps = {
        'cutoffs': list(CUT),
        'view_dimensions': [(2*q+1)**2 for q in CUT],
        'raw_family_dimension': 404, 'residual_dimension': 115,
        'coherent_space_dimension': 289, 'detail_dimensions': [16, 56, 208],
        'reference_coefficients': [serial(p) for p in x],
        'details': [serial(p) for p in ds],
        'component_energies': [str(v) for v in expected],
        'resolution_energies': [str(energy(p)) for p in x],
        'remaining_energy_at_each_view': [str(energy(add((1, x[3]), (-1, p)))) for p in x],
        'values_at_origin': [str(v) for v in origins],
        'perturbation': serial(eta), 'residuals_after_perturbation': [serial(r) for r in delta(y)],
        'protected_repair_cost_squared': '1/50', 'unconstrained_nearest_repair_cost_squared': '3/200',
        'branching_obstruction': '1',
    }
    (args.output / 'verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    (args.output / 'worked_steps.json').write_text(json.dumps(steps, indent=2)+'\n', encoding='utf-8')
    print(f"PASS: {baseline['exact_checks']:,} original exact checks replayed.")
    print(f"PASS: {sum(checks.values()):,} additional exact checks.")
    print(f"TOTAL: {report['total_exact_checks']:,} exact checks, with expected failures detected by negative controls.")
    print('Dimensions: raw 404; residual 115; coherent 289; details 16, 56, 208.')
    print('Values at (0,0): '+', '.join(str(v) for v in origins))
    print('Scale energies: '+', '.join(str(v) for v in expected))
    print('Squared correction costs: protected 1/50; unprotected nearest 3/200.')
    print('No Lean compiler run is claimed.')


if __name__ == '__main__':
    main()
