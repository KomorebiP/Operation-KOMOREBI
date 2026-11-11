"""Compare pinned browser quantiles to independent high-precision integration."""

import argparse
import json
import subprocess
import sys

import mpmath as mp


def integral(rho, theta, dps):
    with mp.workdps(dps):
        r, end = mp.mpf(rho), mp.mpf(theta)  # Convert the actual binary64 inputs.
        q = r * r
        def density(angle):
            return (1-q*q)/(2*mp.pi*(1-2*q*mp.cos(2*angle)+q*q))
        cuts = [mp.mpf(0)] + [p for p in (mp.pi/2, mp.pi, 3*mp.pi/2) if p < end] + [end]
        return +mp.quad(density, cuts)


parser = argparse.ArgumentParser()
parser.add_argument('--node', required=True)
args = parser.parse_args()
data = json.loads(subprocess.check_output([args.node, 'computations/export_quantiles.js']))
mp.mp.dps = 80
worst = mp.mpf(0)
worst_stability = mp.mpf(0)
for case in data['cases']:
    low = integral(case['rho'], case['theta'], 45)
    high = integral(case['rho'], case['theta'], 75)
    error = abs(high - mp.mpf(case['u']))
    stability = abs(high-low)
    worst, worst_stability = max(worst, error), max(worst_stability, stability)
    if error >= mp.mpf('5e-12') or stability >= mp.mpf('1e-30'):
        raise AssertionError(f"quadrature mismatch {case}, error={error}, precision difference={stability}")

print(json.dumps({
    'status': 'passed', 'cases': len(data['cases']), 'radii': data['radii'],
    'masses': data['masses'], 'source_sha256': data['source_sha256'],
    'python': sys.version.split()[0], 'mpmath': mp.__version__, 'node': data['node'],
    'max_absolute_mass_error': mp.nstr(worst, 18),
    'max_45_vs_75_digit_difference': mp.nstr(worst_stability, 18),
    'limits': 'High-precision numerical quadrature at finitely many binary64 browser quantiles, including points near the half-turn branch; not a formal integral or runtime proof.'
}, indent=2))
