"""Exact symbolic and finite-rational checks for the first-order RL formulas."""
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

import sympy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='Optional new JSON receipt; never overwritten')
    args = parser.parse_args()
    source = Path(__file__).read_bytes()
    a, b, s = sympy.symbols('a b s')
    g = a + b * (s - 1) / (s + 1)
    target = (1 + g) / (1 - g)
    rs = (1 + a - b) / (1 - a + b)
    rp = 4 * b / ((1 - a - b) * (1 - a + b))
    inductance = 4 * b / (1 - a + b) ** 2
    network = rs + rp * s * inductance / (rp + s * inductance)
    if sympy.factor(target - network) != 0:
        raise AssertionError('Symbolic rational functions differ')

    parameter_pairs = points = 0
    for aa in (Q(k, 10) for k in range(-9, 10)):
        for bb in (Q(k, 100) for k in range(1, 100) if Q(k, 100) < 1 - abs(aa)):
            resistance = (1 + aa - bb) / (1 - aa + bb)
            shunt = 4 * bb / ((1 - aa - bb) * (1 - aa + bb))
            coil = 4 * bb / (1 - aa + bb) ** 2
            if min(resistance, shunt, coil) <= 0:
                raise AssertionError('A component is not positive')
            parameter_pairs += 1
            for ss in (Q(0), Q(1, 3), Q(1), Q(10)):
                reflection = aa + bb * (ss - 1) / (ss + 1)
                impedance = (1 + reflection) / (1 - reflection)
                circuit = resistance + shunt * ss * coil / (shunt + ss * coil)
                if impedance != circuit:
                    raise AssertionError('An exact rational operating point differs')
                points += 1
    if (parameter_pairs, points) != (981, 3924):
        raise AssertionError('Unexpected finite test range')
    if (Q(5, 4), Q(9, 4), Q(9, 8)) != (
            (1 + Q(1, 3) - Q(2, 9)) / (1 - Q(1, 3) + Q(2, 9)),
            4 * Q(2, 9) / ((1 - Q(1, 3) - Q(2, 9)) * (1 - Q(1, 3) + Q(2, 9))),
            4 * Q(2, 9) / (1 - Q(1, 3) + Q(2, 9)) ** 2):
        raise AssertionError('Normalized component example differs')
    if Path(__file__).read_bytes() != source:
        raise RuntimeError('The check changed during execution')
    receipt = {'status': 'PASS', 'script_sha256': hashlib.sha256(source).hexdigest(),
               'python': platform.python_version(), 'sympy': sympy.__version__,
               'symbolic': 'The rational difference factors to zero.',
               'parameter_grid': 'a=k/10, -9<=k<=9; b=k/100, 1<=k<=99, 0<b<1-|a|',
               'frequencies': ['0', '1/3', '1', '10'],
               'parameter_pairs': parameter_pairs, 'operating_points': points,
               'scope': 'Exact finite diagnostics and a symbolic identity; not a proof of the full arbitrary-order theorem.'}
    text = json.dumps(receipt, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as output:
            output.write(text)
    sys.stdout.write(text)


if __name__ == '__main__':
    main()
