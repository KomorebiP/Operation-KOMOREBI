#!/usr/bin/env python3
"""Bounded release checks. Does not prove general mathematical statements.

Imports archived scientific functions without invoking figure/PDF rebuilds.
The independent exact suite uses only Fraction arithmetic, including its own
Gaussian-rational field operations and elimination, rather than FFT or Prony.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import importlib.util
import json
import math
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load(alias: str, relative: str):
    spec = importlib.util.spec_from_file_location(alias, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if hasattr(value, "tolist"):
        return clean(value.tolist())
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, F):
        return str(value)
    if isinstance(value, G):
        return {"real": str(value.re), "imag": str(value.im)}
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


class Checks:
    def __init__(self):
        self.rows = []

    def check(self, name, condition, detail=None):
        passed = bool(condition)
        self.rows.append({"name": name, "passed": passed, "detail": clean(detail)})
        if not passed:
            raise AssertionError(f"{name}: {detail}")


@dataclass(frozen=True)
class G:
    re: F = F(0)
    im: F = F(0)

    @staticmethod
    def cast(x):
        return x if isinstance(x, G) else G(F(x))

    def __add__(self, x):
        x = G.cast(x)
        return G(self.re + x.re, self.im + x.im)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.re, -self.im)

    def __sub__(self, x):
        return self + -G.cast(x)

    def __rsub__(self, x):
        return G.cast(x) + -self

    def __mul__(self, x):
        x = G.cast(x)
        return G(self.re*x.re - self.im*x.im, self.re*x.im + self.im*x.re)

    __rmul__ = __mul__

    def __truediv__(self, x):
        x = G.cast(x)
        q = x.re*x.re + x.im*x.im
        if q == 0:
            raise ZeroDivisionError
        return G((self.re*x.re + self.im*x.im)/q,
                 (self.im*x.re - self.re*x.im)/q)

    def __pow__(self, n):
        if n < 0:
            return (G(1)/self) ** -n
        result = G(1)
        for _ in range(n):
            result = result*self
        return result

    def conjugate(self):
        return G(self.re, -self.im)

    def norm2(self):
        return self.re*self.re + self.im*self.im

    def __complex__(self):
        return complex(float(self.re), float(self.im))


def solve(a, b):
    """Independent exact Gauss-Jordan elimination in Q(i)."""
    m = [[G.cast(v) for v in row] + [G.cast(rhs)] for row, rhs in zip(a, b)]
    n = len(b)
    for k in range(n):
        pivot = next(r for r in range(k, n) if m[r][k] != G())
        m[k], m[pivot] = m[pivot], m[k]
        divisor = m[k][k]
        m[k] = [v/divisor for v in m[k]]
        for r in range(n):
            if r != k:
                factor = m[r][k]
                m[r] = [v-factor*w for v, w in zip(m[r], m[k])]
    return [row[-1] for row in m]


def dft_exact(values):
    n = len(values)
    roots = {1: G(1), 2: G(-1), 4: G(0, -1)}
    root = roots[n]
    return [sum((G.cast(v)*root**(j*k) for j, v in enumerate(values)), G())/n
            for k in range(n)]


def packet_values(locations, jumps, x):
    # Canonical mean-zero periodic primitive on [0,1).
    base = -sum(a*(1-t) for t, a in zip(locations, jumps))
    return base + sum(a for t, a in zip(locations, jumps) if x >= t)


def packet_l1(left_locs, left_jumps, right_locs, right_jumps):
    boundaries = sorted({F(0), F(1), *left_locs, *right_locs})
    return sum((b-a)*abs(packet_values(left_locs, left_jumps, (a+b)/2)
                         - packet_values(right_locs, right_jumps, (a+b)/2))
               for a, b in zip(boundaries, boundaries[1:]))


def exact_invariants(c):
    rng = random.Random(20261006)
    matrices = []
    for case in range(24):
        values = [G(F(rng.randint(-6, 6), rng.randint(1, 7)),
                    F(rng.randint(-6, 6), rng.randint(1, 7))) for _ in range(4)]
        transformed = dft_exact(values)
        root = G(0, 1)
        inverse = [sum((transformed[k]*root**(j*k) for k in range(4)), G())
                   for j in range(4)]
        c.check(f"exact DFT inversion {case}", inverse == values)
        c.check(f"exact normalized Parseval {case}",
                sum(v.norm2() for v in values)/4 == sum(v.norm2() for v in transformed))
        lanes = [dft_exact(values[r::2]) for r in range(2)]
        expected = [[sum((transformed[k+q*2]*root**((k+q*2)*r) for q in range(2)), G())
                     for k in range(2)] for r in range(2)]
        c.check(f"exact polyphase alias normalization {case}", lanes == expected)
        matrices.append({"input": values, "DFT": transformed, "lanes": lanes})

    # Unit nodes not confined to a roots-of-unity grid.
    nodes_all = [G(F(3, 5), F(4, 5)), G(F(-5, 13), F(12, 13)),
                 G(F(8, 17), F(-15, 17)), G(F(-7, 25), F(-24, 25))]
    for length in (2, 3, 4):
        nodes = nodes_all[:length]
        amplitudes = [F(j+1) for j in range(length-1)]
        amplitudes.append(-sum(amplitudes))
        n0 = 5
        moments = [sum((a*z**n for a, z in zip(amplitudes, nodes)), G())
                   for n in range(n0, n0+3*length+2)]
        hankel = [[moments[r+s] for s in range(length)] for r in range(length)]
        factored = [[sum((a*z**n0*z**r*z**s for a, z in zip(amplitudes, nodes)), G())
                     for s in range(length)] for r in range(length)]
        c.check(f"exact off-grid Hankel factorization L={length}", hankel == factored)
        q = solve(hankel, [-moments[length+r] for r in range(length)]) + [G(1)]
        c.check(f"exact off-grid annihilator roots L={length}",
                all(sum((q[k]*z**k for k in range(length+1)), G()) == G() for z in nodes))
        c.check(f"exact unused off-grid recurrence L={length}",
                all(sum((q[k]*moments[r+k] for k in range(length+1)), G()) == G()
                    for r in range(len(moments)-length)))
        v = [[z**(n0+r) for z in nodes] for r in range(length)]
        recovered = solve(v, moments[:length])
        c.check(f"exact off-grid amplitudes L={length}", recovered == [G(a) for a in amplitudes])

    # A concrete rejection of the coefficient-one L1 location bound.
    delta = F(1, 10)
    left = [F(1, 4), F(3, 4)]
    right = [F(1, 4)+delta, F(3, 4)]
    exact_l1 = packet_l1(left, [F(1), F(-1)], right, [F(1), F(-1)])
    c.check("false factor-one L1 certificate rejected", exact_l1 > delta,
            {"L1": exact_l1, "old_bound": delta})
    c.check("correct centered-step L1 formula", exact_l1 == 2*delta*(1-delta))
    l1_cases = []
    for case in range(24):
        tau = [F(1, 8), F(3, 8), F(5, 8), F(7, 8)]
        moved = [t+F(rng.randint(-4, 4), 100) for t in tau]
        jumps = [F(rng.randint(1, 5), 3), F(-rng.randint(1, 5), 3), F(2, 3)]
        jumps.append(-sum(jumps))
        changed = [a+F(rng.randint(-3, 3), 50) for a in jumps[:-1]]
        changed.append(-sum(changed))
        l1 = packet_l1(tau, jumps, moved, jumps)
        bound = 2*sum(abs(a)*abs(t-u) for a, t, u in zip(jumps, tau, moved))
        c.check(f"corrected zero-mean L1 location bound {case}", l1 <= bound)
        total = packet_l1(tau, jumps, moved, changed)
        amp_bound = sum(abs(a-b) for a, b in zip(jumps, changed))
        c.check(f"zero-mean L1 location-amplitude bound {case}", total <= bound+amp_bound)
        l1_cases.append({"L1_location": l1, "location_bound": bound,
                         "L1_total": total, "combined_bound": bound+amp_bound})
    return {"DFT_polyphase_cases": matrices, "off_grid_orders": [2, 3, 4],
            "L1_counterexample": {"delta": delta, "L1": exact_l1, "old_bound": delta},
            "L1_cases": l1_cases}


def unknown_edge(c):
    m = load("signal_unknown_edge", "sources/unknown_edge/universal_unknown_edge_recovery.py")
    rows, rep = m.run_exact_examples()
    dictionary = m.build_dictionary_example()
    multi = m.build_multichannel_example()
    rectangle = m.build_2d_rectangle_example()
    tests = m.run_tests(rows, rep, dictionary, multi, rectangle)
    for row in tests:
        c.check(row["name"], row["passed"], row["detail"])
    # Orthogonal normalization: numerical integral with jump breakpoints,
    # independent of the closed derivative-moment formula used by the code.
    from scipy.integrate import quad
    import numpy as np
    edge = rep["edge"]
    for n in (-7, -2, 0, 2, 7):
        coeff = quad(lambda t: float(edge.values(np.array([t]))[0])*math.cos(n*t),
                     0, m.TAU, points=edge.locations, epsabs=1e-11)[0]/m.TAU
        coeff -= 1j*quad(lambda t: float(edge.values(np.array([t]))[0])*math.sin(n*t),
                        0, m.TAU, points=edge.locations, epsabs=1e-11)[0]/m.TAU
        c.check(f"independent piecewise Fourier quadrature n={n}", abs(coeff-edge.fourier(n)) < 1e-10,
                {"quadrature": coeff, "closed": edge.fourier(n)})
    return {"exact_cases": rows, "native_named_checks": len(tests),
            "symbolic": m.exact_symbolic_example(), "dictionary_gamma": dictionary[-1],
            "independent_piecewise_quadrature_modes": [-7, -2, 0, 2, 7]}


def self_calibration(c):
    m = load("signal_self_calibration", "sources/self_calibration/polyphase_gibbs_breakthrough.py")
    edge = m.exact_edge()
    exact = m.reorder_result(m.recover_polyphase(m.SignalModel(m.bandlimited_background(), edge),
                             10, samples_per_offset=22, offsets=6, order_upper_bound=7, refine=True), edge)
    analytic = m.reorder_result(m.recover_polyphase(m.SignalModel(m.analytic_background(), edge),
                                10, samples_per_offset=22, offsets=6, order_upper_bound=7, refine=True), edge)
    symbolic = m.symbolic_confluent_check()
    rate = m.run_rate_experiment(edge)
    noise = m.run_noise_experiment(edge)
    offset = m.run_offset_averaging_experiment(edge)
    oracle = m.run_oracle_equivalence_experiment(edge)
    stress = m.run_random_stress_experiment(100)
    budget = m.run_finite_budget_experiment(edge)
    reconstruction = m.run_reconstruction_experiment(edge)
    tests = m.run_tests(edge, exact, analytic, symbolic, rate, noise, offset, oracle, stress, budget, reconstruction)
    for row in tests:
        c.check(row["name"], row["passed"], row["detail"])
    return {"native_named_checks": len(tests), "rate": rate, "noise": noise,
            "offset": offset, "oracle": oracle, "stress": stress, "finite_budget": budget,
            "reconstruction": reconstruction, "symbolic": symbolic}


def singularity(c):
    m = load("signal_singularity", "sources/singularity_dictionary/gibbs_projector_closed.py")
    import numpy as np
    rows = []
    for size in (128, 256, 512):
        grid = np.arange(size)/size
        truth = m.signal(grid)
        mask = m.interval_mask(grid)
        resolved, smooth, edge, amplitude = m.singularity_exact_reconstruction(truth, mask)
        c.check(f"declared singularity amplitude N={size}", abs(amplitude-m.AMP) < 1e-11)
        c.check(f"declared singularity exact synthesis N={size}", np.max(np.abs(resolved-truth)) < 1e-11)
        c.check(f"smooth complement N={size}", np.max(np.abs(smooth-m.smooth(grid))) < 1e-11)
        best, candidates = m.discover_interval(truth, grid)
        c.check(f"finite dyadic dictionary best N={size}", best == (4, 12), best)
        c.check(f"finite dyadic dictionary residual N={size}", candidates[0]["residual_l2"] < 1e-10)
        scale, detail = m.haar_forward(truth)
        inverse = m.haar_inverse(scale, detail)
        c.check(f"orthogonal Haar inversion N={size}", np.max(np.abs(inverse-truth)) < 1e-11)
        c.check(f"orthogonal Haar energy N={size}", abs(np.sum(truth**2)-scale**2-sum(np.sum(d**2) for d in detail)) < 1e-10)
        rows.append({"size": size, "amplitude": amplitude, "max_error": float(np.max(np.abs(resolved-truth))),
                     "dictionary_best": best, "dictionary_candidates": len(candidates)})
    for n in (-7, -3, 0, 3, 7):
        c.check(f"independent continuous coefficient n={n}",
                abs(m.numerical_continuous_coefficient(n)-m.fhat_continuous(n)) < 1e-10)
    return {"cases": rows, "independent_quadrature_modes": [-7, -3, 0, 3, 7]}


def gibbs_case(c):
    m = load("signal_gibbs_case", "sources/gibbs_case/gibbs_packet_case.py")
    import numpy as np
    grid = np.linspace(-m.PI, m.PI, 2048, endpoint=False)
    for n in (5, 8, 16):
        resolved = m.packet_reconstruction(grid, n)
        c.check(f"declared packet reconstruction N={n}", np.max(np.abs(resolved-m.full_signal(grid))) < 1e-11)
    library = m.CandidateLibrary.build(size=48, degree=5, min_length=4, max_length=24)
    _, smooth, edge, truth = m.true_discrete_signal(48)
    found = library.search(truth)
    c.check("finite sampled interval metadata", (found["start"], found["length"]) == (16, 16))
    c.check("finite sampled interval amplitude", abs(found["amplitude"]-1) < 1e-10)
    c.check("finite sampled interval synthesis", np.max(np.abs(found["reconstruction"]-truth)) < 1e-10)
    c.check("finite sampled positive objective gap", found["gap"] > 1e-8, found["gap"])
    c.check("independent residual orthogonality", np.max(np.abs(library.design.T@library.residualize(truth))) < 1e-10)
    return {"sample_size": 48, "candidate_count": len(library.masks),
            "found_start": found["start"], "found_length": found["length"],
            "amplitude": found["amplitude"], "gap": found["gap"]}


def complex_benchmark(c):
    m = load("signal_complex_benchmark", "sources/complex_benchmark/complex_signal_image_benchmark.py")
    import numpy as np
    rows, details = m.run_complex_1d_cases()
    for row in rows:
        name = row["case"]
        c.check(f"complex finite output {name}", all(math.isfinite(float(row[key]))
                for key in ("raw_rmse", "resolved_rmse", "location_error", "jump_error")))
        c.check(f"complex known test order {name}", row["true_order"] == row["recovered_order"])
        # Stress models get reported errors, without an invented guarantee.
        if row["scope"] == "controlled":
            c.check(f"controlled complex location {name}", row["location_error"] < 1e-6, row["location_error"])
            c.check(f"controlled complex native synthesis improvement {name}", row["resolved_rmse"] < row["raw_rmse"])
    # A small explicitly in-dictionary geometric control. Observation here is
    # the complete finite raster, as in native OMP's least-squares input.
    shape = (32, 32)
    smooth_order = 3
    dictionary = m.build_geometry_dictionary(shape, smooth_order)
    index = dictionary.names.index("rect_c16_16_s16_24")
    smooth = m.smooth_background_2d(shape, seed=20261006, order=smooth_order)
    truth = smooth + 0.7*dictionary.masks[index]
    selected, alpha, reconstruction, history = m.omp_unknown_order(dictionary, truth, smooth_order,
                                max_atoms=2, improvement_tolerance=0.01)
    c.check("small in-dictionary raster support", selected == [index], selected)
    c.check("small in-dictionary raster coefficient", abs(alpha[index]-0.7) < 1e-9)
    c.check("small in-dictionary raster synthesis", np.max(np.abs(reconstruction-truth)) < 1e-9)
    # DCT orthogonal projector is independently checked against idempotence,
    # self-adjointness and complement orthogonality.
    rng = np.random.default_rng(20261006)
    x, y = rng.normal(size=shape), rng.normal(size=shape)
    px, py = m.dct_lowpass(x, smooth_order), m.dct_lowpass(y, smooth_order)
    c.check("finite DCT projector idempotence", np.max(np.abs(m.dct_lowpass(px, smooth_order)-px)) < 1e-11)
    c.check("finite DCT projector self-adjointness", abs(np.sum(px*y)-np.sum(x*py)) < 1e-10)
    c.check("finite DCT complement orthogonality", abs(np.sum(px*(x-px))) < 1e-10)
    return {"complex_1d_cases": rows, "small_raster": {"shape": shape, "candidate_atoms": len(dictionary.names),
            "selected": selected, "true_index": index, "max_error": float(np.max(np.abs(reconstruction-truth)))},
            "out_of_model_and_natural_image_benchmarks": "archived only; not freshly replayed"}


def infinite_packet(c, spd=False):
    name = "infinite_packet_gibbs_reconstruction_spd.py" if spd else "infinite_packet_gibbs_reconstruction.py"
    m = load("signal_packet_spd" if spd else "signal_packet", "sources/infinite_packet/"+name)
    import numpy as np
    native = m.run_tests()
    # The native test function already executes sixteen groups with multiple
    # diagnostics. They are recorded once per variant, never counted twice as
    # new independent assertions across the almost-identical variants.
    c.check("native sixteen test groups", native["test_groups"] == 16, native)
    image = m.synthetic_geometry(16)
    solver = m.InfinitePacketReconstructor(image, max_candidates_per_iteration=40, random_seed=20261006)
    result = solver.run(max_packets=8)
    matrix = np.column_stack([atom.ravel() for atom in result.active_atoms])
    residual = result.residual.reshape(-1, image.shape[2])
    normal_equation = matrix.T@residual - solver.ridge*result.coefficients
    c.check("independent ridge normal equation", np.max(np.abs(normal_equation)) < 1e-9,
            float(np.max(np.abs(normal_equation))))
    independent = np.linalg.lstsq(np.vstack([matrix, math.sqrt(solver.ridge)*np.eye(matrix.shape[1])]),
                                    np.vstack([image.reshape(-1, image.shape[2]), np.zeros((matrix.shape[1], image.shape[2]))]), rcond=None)[0]
    c.check("independent augmented ridge solve", np.max(np.abs(matrix@(independent-result.coefficients))) < 1e-9)
    c.check("packet archive identity independently checked", np.max(np.abs(result.reconstruction+result.residual-image)) < 1e-12)
    c.check("stored packet synthesis independently checked", np.max(np.abs(matrix@result.coefficients-result.reconstruction.reshape(-1, image.shape[2]))) < 1e-12)
    # Ideal mathematical projection on an active finite packet span is tested
    # separately from the source's regularized solver.
    ideal, *_ = np.linalg.lstsq(matrix, image.reshape(-1, image.shape[2]), rcond=None)
    ideal_residual = image.reshape(-1, image.shape[2])-matrix@ideal
    c.check("unregularized control projection stationarity", np.max(np.abs(matrix.T@ideal_residual)) < 1e-9)
    c.check("unregularized control no worse residual", np.linalg.norm(ideal_residual) <= np.linalg.norm(residual)+1e-10)
    return {"variant": name, "native": native, "small_control": {"shape": image.shape,
            "packets": len(result.active_atoms), "ridge": solver.ridge,
            "ridge_stationarity_error": float(np.max(np.abs(normal_equation))),
            "ridge_residual_norm": float(np.linalg.norm(residual)), "ideal_residual_norm": float(np.linalg.norm(ideal_residual))},
            "scope": "complete input rasters are known; finite approximation, not blind Fourier recovery or universal convergence"}


SUITES = {"exact_invariants": exact_invariants, "unknown_edge": unknown_edge,
          "self_calibration": self_calibration, "singularity_dictionary": singularity,
          "gibbs_case": gibbs_case, "complex_benchmark": complex_benchmark,
          "infinite_packet": lambda c: infinite_packet(c, False),
          "infinite_packet_spd": lambda c: infinite_packet(c, True)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=SUITES, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    checks = Checks()
    try:
        details = SUITES[args.suite](checks)
        record = {"status": "PASS", "suite": args.suite, "fresh_explicit_check_count": len(checks.rows),
                  "checks": checks.rows, "scientific_details": details,
                  "interpretation": "bounded computation evidence, not a universal proof or formally verified Python"}
    except Exception as error:
        record = {"status": "FAIL", "suite": args.suite, "fresh_explicit_check_count": len(checks.rows),
                  "checks": checks.rows, "failure": {"type": type(error).__name__, "message": str(error)}}
        args.result.write_text(json.dumps(clean(record), indent=2, allow_nan=False)+"\n")
        raise
    args.result.write_text(json.dumps(clean(record), indent=2, allow_nan=False)+"\n")
    print(json.dumps({"suite": args.suite, "status": record["status"], "fresh_explicit_check_count": len(checks.rows)}))


if __name__ == "__main__":
    main()
