"""Bounded independent audit of the teaching lab, using NumPy FFT and support vectors.

Run: python -B tools/audit_signal_lab.py --node NODE --output REPORT.json
Requires NumPy. Writes a finite numerical report; it does not change proof status.
"""
import argparse
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

import numpy as np


SIZES = [16, 32, 64, 128, 256]
BASES = ['haar', 'cosine', 'samples']
POLICIES = ['energy', 'magnitude', 'prefix']
SEEDS = [0, 17, 12345, 4294967295]


def configurations():
    for n in SIZES:
        step = [2]*(n//4)+[6]*(n//4)+[-4]*(n//4)+[4]*(n//4)
        step[5*n//8] = 12
        fixtures = [step, [8 if i % 2 == 0 else -8 for i in range(n)],
                    [(i*i+7*i+3) % 33-16 for i in range(n)],
                    [1 if i == n//3 else 0 for i in range(n)]]
        for fixture, seed in zip(fixtures, SEEDS):
            for noise in [0, 4, 16]:
                for policy in POLICIES:
                    yield dict(v=1, n=n, shape='custom', custom=fixture, amplitude=16, cycles=3,
                               noise=noise, seed=seed, budget=n//4, policy=policy, basis='haar', coefficient=1, address=0)


def independent_noise(n, amplitude, seed):
    result = []
    for _ in range(n):
        seed = (1664525*seed+1013904223) & 0xffffffff
        result.append(math.floor(seed/2**32*(2*amplitude+1))-amplitude)
    return np.array(result, dtype=float)


def support_basis(n):
    rows = [np.ones(n)]
    for width in [n//2**j for j in range(int(math.log2(n)))]:
        for start in range(0, n, width):
            row = np.zeros(n)
            row[start:start+width//2] = 1
            row[start+width//2:start+width] = -1
            rows.append(row)
    return np.array(rows)


def fft_coefficients(values):
    n = len(values)
    extended = np.concatenate((values, values[::-1]))
    unscaled = (np.fft.fft(extended)[:n]*np.exp(-1j*np.pi*np.arange(n)/(2*n))).real
    unscaled[0] /= 2*np.sqrt(n)
    unscaled[1:] /= np.sqrt(2*n)
    return unscaled


def fft_basis(n):
    # Synthesize each unit coefficient through a conjugate-symmetric 2N-point IFFT.
    factors = np.full(n, np.sqrt(2*n)); factors[0] = 2*np.sqrt(n)
    positive = np.eye(n)*factors*np.exp(1j*np.pi*np.arange(n)/(2*n))
    spectrum = np.zeros((n, 2*n), dtype=complex)
    spectrum[:, :n] = positive
    spectrum[:, n+1:] = positive[:, 1:][:, ::-1].conjugate()
    spatial = np.fft.ifft(spectrum, axis=1)
    assert np.max(np.abs(spatial.imag)) < 1e-12
    return spatial.real[:, :n]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default=shutil.which('node'))
    parser.add_argument('--git', default=shutil.which('git'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.node:
        parser.error('Provide an installed Node.js executable with --node')
    root = Path(__file__).resolve().parents[1]
    tests = subprocess.run([args.node, '--test', 'tools/test_signal_lab.cjs'], cwd=root, capture_output=True, text=True, check=True, timeout=30)
    configs = list(configurations())
    process = subprocess.run([args.node, 'tools/signal_lab_probe.cjs'], cwd=root, input=json.dumps(configs), capture_output=True, text=True, check=True, timeout=30)
    cases = json.loads(process.stdout)
    assert len(cases) == len(configs)
    assert len(cases) == 180 and len({json.dumps(c, sort_keys=True) for c in configs}) == 180
    cache = {n: {'haar': support_basis(n), 'cosine': fft_basis(n), 'samples': np.eye(n)} for n in SIZES}
    maxima = {b: dict(coefficient_absolute=0., curve_absolute=0., reconstruction_absolute=0., normalized_error=0.) for b in BASES}
    comparisons = 0
    for requested, case in zip(configs, cases):
        assert case['config'] == requested
        n = requested['n']; reference = np.array(requested['custom'], dtype=float)
        observed = reference+independent_noise(n, requested['noise'], requested['seed'])
        assert np.array_equal(reference, case['reference'])
        assert np.array_equal(observed, case['observed'])
        assert float(np.sum((observed-reference)**2)) == case['noiseEnergy']
        scale = max(1., float(np.sum(observed**2)), float(np.sum(reference**2)))
        for basis in BASES:
            actual = case['analyses'][basis]; vectors = cache[n][basis]
            weights = np.sum(vectors**2, axis=1)
            gram = vectors@vectors.T
            assert np.max(np.abs(gram-np.diag(weights))) < 1e-9
            coefficients = fft_coefficients(observed) if basis == 'cosine' else vectors@observed/weights
            coefficient_error = float(np.max(np.abs(coefficients-actual['values'])))
            assert coefficient_error <= 1e-9*max(1., float(np.max(np.abs(coefficients))))
            assert np.max(np.abs(weights-actual['weights'])) < 1e-10
            order = np.array(actual['order'], dtype=int)
            assert sorted(order.tolist()) == list(range(n))
            if requested['policy'] == 'prefix':
                assert np.array_equal(order, np.arange(n))
            else:
                scores = weights*coefficients**2 if requested['policy'] == 'energy' else np.abs(coefficients)
                assert np.all(scores[order][1:] <= scores[order][:-1]+1e-9*scale)
            components = coefficients[order, None]*vectors[order]
            reconstructed = np.concatenate((np.zeros((1, n)), np.cumsum(components, axis=0)))
            expected_reference = np.sum((reconstructed-reference)**2, axis=1)
            expected_observed = np.sum((reconstructed-observed)**2, axis=1)
            actual_reference = np.array([p['referenceError'] for p in actual['curve']])
            actual_observed = np.array([p['observedError'] for p in actual['curve']])
            assert [p['budget'] for p in actual['curve']] == list(range(n+1))
            curve_error = max(float(np.max(np.abs(expected_reference-actual_reference))), float(np.max(np.abs(expected_observed-actual_observed))))
            reconstruction_error = float(np.max(np.abs(reconstructed[requested['budget']]-actual['reconstruction'])))
            assert curve_error <= 1e-9*scale
            assert reconstruction_error <= 1e-9*max(1., float(np.max(np.abs(observed))))
            minimum_tolerance = 1e-10*max(1., float(np.sum(reference**2)))
            expected_best = int(np.flatnonzero(expected_reference <= np.min(expected_reference)+minimum_tolerance)[0])
            assert actual['bestBudget'] == expected_best
            if basis != 'cosine':
                assert coefficient_error == curve_error == reconstruction_error == 0
            maxima[basis]['coefficient_absolute'] = max(maxima[basis]['coefficient_absolute'], coefficient_error)
            maxima[basis]['curve_absolute'] = max(maxima[basis]['curve_absolute'], curve_error)
            maxima[basis]['reconstruction_absolute'] = max(maxima[basis]['reconstruction_absolute'], reconstruction_error)
            maxima[basis]['normalized_error'] = max(maxima[basis]['normalized_error'], curve_error/scale)
            comparisons += n+1
    assert comparisons == 54108
    revision = subprocess.check_output([args.git, 'rev-parse', 'HEAD'], cwd=root, text=True).strip() if args.git else None
    dirty = bool(subprocess.check_output([args.git, 'status', '--porcelain'], cwd=root, text=True)) if args.git else None
    report = dict(outcome='implementation and finite assertion verified in the stated range', configurations=len(cases),
                  representations=len(cases)*len(BASES), budget_comparisons=comparisons, sizes=SIZES,
                  noise_amplitudes=[0, 4, 16], seeds=SEEDS, selection_policies=POLICIES,
                  maximum_errors=maxima, relative_energy_tolerance=1e-9,
                  independent_implementation='NumPy even-extension FFT / conjugate-symmetric IFFT and explicit Haar support vectors',
                  exhaustive_mask_checks='Node tests enumerate all 65536 masks of one 16-sample benchmark in each representation',
                  software=dict(python=platform.python_version(), numpy=np.__version__, node=subprocess.check_output([args.node, '--version'], text=True).strip()),
                  hardware=dict(platform=platform.platform(), machine=platform.machine(), logical_cpus=os.cpu_count()),
                  source_revision=revision, source_dirty=dirty,
                  non_claims=['Not a proof for all inputs.', 'Does not establish statistical denoising performance for unknown signals.',
                              'Noise is a deterministic bounded integer generator, not a Gaussian model.'])
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['outcome', 'configurations', 'representations', 'budget_comparisons', 'maximum_errors']}))
    print(tests.stdout)


if __name__ == '__main__':
    main()
