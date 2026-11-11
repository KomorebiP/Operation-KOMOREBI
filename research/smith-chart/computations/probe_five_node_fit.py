"""Bounded numerical restarts for one archived five-node candidate.

This experiment cannot certify exact realization or rule out any topology.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import time
import zipfile

import numpy as np
import scipy
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'SmithChart_Complete.zip'
ARCHIVE_SHA256 = '39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e'
PREFIX = 'Smith_Chart_Research_2026-11-11/reproduction/six_state/'
INPUT_HASHES = {'q6_canonical_fits_75_168.json': '4892891c9afd5e5888ee2c207a4e83e20c0417daf213ca2bb14086256559c901',
                'q6_canonical_fits.py': 'a0aed9f85e918f5a0089f5e4355632d1d1a0075724b5bb11495b293f2a4b36dd'}
P = np.array([450, 1385, 2477, 2200, 1142, 335, 75.])
D = np.array([150, 795, 1375, 1720, 1250, 445, 25.])
EDGES = tuple(itertools.combinations(range(5), 2))
REACTIVES = (('L', 1), ('L', 7), ('L', 9), ('C', 2), ('C', 4), ('C', 6))
LOW, HIGH = -25.0, 25.0


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def grid(imaginary_count, real_count, imaginary_range, real_range):
    return np.r_[1j * np.geomspace(*imaginary_range, imaginary_count),
                 np.geomspace(*real_range, real_count)]


TRAIN = grid(36, 12, (.002, 150), (.01, 40))
HOLDOUT = grid(101, 27, (.001, 300), (.005, 80))
B = np.zeros((len(EDGES), 4))
for index, (u, v) in enumerate(EDGES):
    if u:
        B[index, u - 1] += 1
    if v:
        B[index, v - 1] -= 1


def residual(log_values, frequencies, *, jacobian=False):
    conductances = np.exp(log_values[:len(EDGES)])
    reactances = np.exp(log_values[len(EDGES):])
    admittance = np.broadcast_to(conductances, (len(frequencies), len(EDGES))).astype(complex).copy()
    for value, (kind, edge) in zip(reactances, REACTIVES):
        admittance[:, edge] += value * (frequencies if kind == 'C' else 1 / frequencies)
    matrix = np.einsum('ei,fe,ej->fij', B, admittance, B, optimize=True)
    current = np.broadcast_to(np.eye(4)[:, :1], (len(frequencies), 4, 1))
    try:
        voltage = np.linalg.solve(matrix, current)[:, :, 0]
    except np.linalg.LinAlgError:
        return np.zeros((2 * len(frequencies), len(log_values))) if jacobian else np.full(2 * len(frequencies), 1e5)
    target = np.polyval(P, frequencies) / np.polyval(D, frequencies)
    weights = 1 / (1 + np.abs(target))
    if not jacobian:
        error = (voltage[:, 0] - target) * weights
        return np.r_[error.real, error.imag]
    edge_voltage = voltage @ B.T
    derivative = np.c_[-edge_voltage ** 2 * conductances,
                       np.column_stack([-edge_voltage[:, edge] ** 2 * value *
                                        (frequencies if kind == 'C' else 1 / frequencies)
                                        for value, (kind, edge) in zip(reactances, REACTIVES)])] * weights[:, None]
    return np.r_[derivative.real, derivative.imag]


def max_error(log_values, frequencies):
    values = residual(log_values, frequencies)
    count = len(frequencies)
    return float(np.max(np.hypot(values[:count], values[count:])))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--starts', type=int, default=5, help='One archived start plus fresh random starts')
    parser.add_argument('--max-nfev', type=int, default=800)
    parser.add_argument('--seed', type=int, default=20261111)
    parser.add_argument('--output', type=Path, help='Optional new JSON receipt; never overwritten')
    args = parser.parse_args()
    if not 1 <= args.starts <= 50 or not 1 <= args.max_nfev <= 10000:
        parser.error('Choose 1–50 starts and 1–10000 evaluations per start')
    script = Path(__file__).read_bytes()
    if sha(ARCHIVE.read_bytes()) != ARCHIVE_SHA256:
        raise RuntimeError('Research archive checksum mismatch')
    with zipfile.ZipFile(ARCHIVE) as z:
        raw = {name: z.read(PREFIX + name) for name in INPUT_HASHES}
    if any(sha(raw[name]) != expected for name, expected in INPUT_HASHES.items()):
        raise RuntimeError('Archived fit input checksum mismatch')
    matches = [case for case in json.loads(raw['q6_canonical_fits_75_168.json'])['cases'] if case['id'] == 142]
    if len(matches) != 1 or tuple(map(tuple, matches[0]['reactives'])) != REACTIVES:
        raise RuntimeError('Archived candidate 142 differs from the expected topology')
    saved = matches[0]
    initial_values = np.array(saved['conductances'] + saved['reactance'], dtype=float)
    if len(initial_values) != 16 or not np.all(np.isfinite(initial_values)) or not np.all(initial_values > 0):
        raise RuntimeError('Archived candidate contains invalid numeric parameters')
    if np.intersect1d(TRAIN, HOLDOUT).size:
        raise RuntimeError('The training and holdout grids overlap')
    probe = np.linspace(-.5, .5, 16)
    step = 1e-6
    directions = np.eye(16)
    finite_difference = np.column_stack([
        (residual(probe + step * direction, TRAIN) - residual(probe - step * direction, TRAIN)) / (2 * step)
        for direction in directions])
    jacobian_difference = float(np.max(np.abs(residual(probe, TRAIN, jacobian=True) - finite_difference)))
    if jacobian_difference > 5e-7:
        raise RuntimeError('The analytic Jacobian fails its finite-difference check')
    initial = np.clip(np.log(initial_values), LOW + 1e-8, HIGH - 1e-8)
    rng = np.random.default_rng(args.seed)
    starts = [initial] + [np.clip(rng.normal(0, 1.35, 16), LOW + 1e-8, HIGH - 1e-8)
                          for _ in range(args.starts - 1)]
    baseline = {'archived_reported_training_error': saved['error'],
                'recomputed_training_error_after_log_bounds': max_error(initial, TRAIN),
                'holdout_error_after_log_bounds': max_error(initial, HOLDOUT)}
    results = []
    start_time = time.monotonic()
    for index, start in enumerate(starts):
        fit = least_squares(lambda x: residual(x, TRAIN), start,
                            jac=lambda x: residual(x, TRAIN, jacobian=True),
                            bounds=(LOW, HIGH), max_nfev=args.max_nfev,
                            ftol=1e-11, gtol=1e-11, xtol=1e-11)
        record = {'start': index, 'nfev': int(fit.nfev), 'termination_status': int(fit.status),
                  'training_error': max_error(fit.x, TRAIN), 'holdout_error': max_error(fit.x, HOLDOUT),
                  'conductances': np.exp(fit.x[:10]).tolist(),
                  'reactive_admittance_parameters': np.exp(fit.x[10:]).tolist()}
        results.append(record)
        print(f"start {index}: training={record['training_error']:.9g}, holdout={record['holdout_error']:.9g}, nfev={record['nfev']}", flush=True)
    if Path(__file__).read_bytes() != script or sha(ARCHIVE.read_bytes()) != ARCHIVE_SHA256:
        raise RuntimeError('An input changed during the experiment')
    receipt = {'status': 'COMPLETED', 'script_sha256': sha(script), 'archive_sha256': ARCHIVE_SHA256,
               'archived_input_sha256': INPUT_HASHES, 'python': platform.python_version(),
               'numpy': np.__version__, 'scipy': scipy.__version__, 'candidate_id': 142,
               'nodes': 5, 'edges': EDGES, 'reactives': REACTIVES,
               'parameter_convention': 'Conductances on all edges; inductive admittance parameter is 1/L and capacitive parameter is C.',
               'training_grid': {'imaginary_count': 36, 'imaginary_range': [.002, 150],
                                 'positive_real_count': 12, 'positive_real_range': [.01, 40]},
               'holdout_grid': {'imaginary_count': 101, 'imaginary_range': [.001, 300],
                                'positive_real_count': 27, 'positive_real_range': [.005, 80]},
               'metric': 'Maximum |Zcandidate-Ztarget|/(1+|Ztarget|) over the specified grid.',
               'jacobian_check': {'method': 'central difference at one interior log-parameter point',
                                  'step': step, 'maximum_absolute_difference': jacobian_difference,
                                  'tolerance': 5e-7},
               'log_parameter_bounds': [LOW, HIGH], 'seed': args.seed, 'starts': args.starts,
               'max_nfev_per_start': args.max_nfev, 'baseline': baseline, 'results': results,
               'elapsed_seconds': round(time.monotonic() - start_time, 3),
               'scope': 'Finite floating-point optimization for one five-node placement; neither a circuit certificate nor an infeasibility result.'}
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as output:
            json.dump(receipt, output, indent=2, allow_nan=False)
            output.write('\n')
    print('best training error:', min(item['training_error'] for item in results), flush=True)


if __name__ == '__main__':
    main()
