"""Exact finite quantum phase, measurement, and information-loss example.

Python 3.10+, standard library only. All calculations use Q(i); no complex
floating-point arithmetic, sampling, simulator, or Lean replay is involved.
Run with --output DIRECTORY to reproduce the CSV, JSON, and SVG records.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from fractions import Fraction as Q
import json
from pathlib import Path


@dataclass(frozen=True)
class C:
    """A Gaussian rational, stored as exact real and imaginary fractions."""
    re: Q = Q(0)
    im: Q = Q(0)

    def __post_init__(self):
        object.__setattr__(self, "re", Q(self.re))
        object.__setattr__(self, "im", Q(self.im))

    def __add__(self, other):
        other = other if isinstance(other, C) else C(other)
        return C(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return C(-self.re, -self.im)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        other = other if isinstance(other, C) else C(other)
        return C(self.re*other.re - self.im*other.im,
                 self.re*other.im + self.im*other.re)

    __rmul__ = __mul__

    def __truediv__(self, real):
        return C(self.re/Q(real), self.im/Q(real))

    def conj(self):
        return C(self.re, -self.im)

    def abs2(self):
        return self.re**2 + self.im**2

    def __str__(self):
        if not self.im:
            return str(self.re)
        return f"{self.re}{'+' if self.im > 0 else '-'}{abs(self.im)}i"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def matrix(rows):
    return tuple(tuple(x if isinstance(x, C) else C(x) for x in row)
                 for row in rows)


def multiply(a, b):
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(len(b))), C())
                       for j in range(len(b[0]))) for i in range(len(a)))


def scale(t, a):
    return tuple(tuple(t*x for x in row) for row in a)


def add(a, b):
    return tuple(tuple(x+y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def adjoint(a):
    return tuple(tuple(a[j][i].conj() for j in range(len(a)))
                 for i in range(len(a[0])))


def trace(a):
    return sum((a[i][i] for i in range(len(a))), C())


def purity(a):
    result = trace(multiply(a, a))
    require(result.im == 0, "Purity must be real")
    return result.re


def outer(v):
    return tuple(tuple(x*y.conj() for y in v) for x in v)


def state(a=Q(3, 5), b=Q(4, 5), phase=C(1)):
    a, b = Q(a), Q(b)
    if a*a+b*b != 1 or phase.abs2() != 1:
        raise ValueError("Use normalized real amplitudes and a unit phase")
    return outer((C(a), b*phase))


def dephase(rho, groups=None):
    """Keep exactly the blocks belonging to a declared address partition."""
    n = len(rho)
    if groups is None:
        groups = tuple((i,) for i in range(n))
    addresses = [i for group in groups for i in group]
    if sorted(addresses) != list(range(n)):
        raise ValueError("Packet groups must partition all matrix addresses")
    packet = {i: k for k, group in enumerate(groups) for i in group}
    return tuple(tuple(rho[i][j] if packet[i] == packet[j] else C()
                       for j in range(n)) for i in range(n))


def partial_dephase(rho, t):
    """D_t = t id + (1-t) D, with t the retained coherence fraction."""
    t = Q(t)
    if not 0 <= t <= 1:
        raise ValueError("Retained coherence t must lie in [0, 1]")
    return add(scale(t, rho), scale(1-t, dephase(rho)))


H0 = matrix(((1, 1), (1, -1)))
X_PLUS = scale(Q(1, 2), matrix(((1, 1), (1, 1))))
Y_PLUS = scale(Q(1, 2), matrix(((1, C(0, -1)), (C(0, 1), 1))))
Z_PLUS = matrix(((1, 0), (0, 0)))
EFFECTS = (X_PLUS, Y_PLUS, Z_PLUS)


def hadamard(rho):
    # H = H0/sqrt(2); the density-matrix conjugation has only rational factors.
    return scale(Q(1, 2), multiply(multiply(H0, rho), H0))


def probabilities(rho):
    """Plus probabilities in the X, Y, Z settings, evaluated by trace."""
    values = tuple(trace(multiply(effect, rho)) for effect in EFFECTS)
    require(all(value.im == 0 for value in values), "Probabilities must be real")
    return tuple(value.re for value in values)


def reconstruct(px, py, pz):
    """Linear tomography from ideal ensemble probabilities, not one shot."""
    c = C(Q(px)-Q(1, 2), Q(1, 2)-Q(py))
    return matrix(((Q(pz), c), (c.conj(), 1-Q(pz))))


def coherent_record(rho):
    """|j> -> |j>|j>, in system-first order 00, 01, 10, 11."""
    return tuple(tuple(rho[i//3][j//3] if i in (0, 3) and j in (0, 3)
                       else C() for j in range(4)) for i in range(4))


def uncompute_record(joint):
    # CNOT is its own inverse and swaps the addresses 10 and 11.
    order = (0, 1, 3, 2)
    return tuple(tuple(joint[order[i]][order[j]] for j in range(4))
                 for i in range(4))


def forget_record(joint):
    return tuple(tuple(sum((joint[2*i+k][2*j+k] for k in range(2)), C())
                       for j in range(2)) for i in range(2))


def circle(u):
    u = Q(u)
    return C((1-u*u)/(1+u*u), 2*u/(1+u*u))


def amplitude_damp(rho, survival=Q(4, 5), jump=Q(3, 5)):
    """Kraus channel with gamma=jump**2 and sqrt(1-gamma)=survival."""
    survival, jump = Q(survival), Q(jump)
    if min(survival, jump) < 0 or survival**2+jump**2 != 1:
        raise ValueError('Use nonnegative survival/jump amplitudes of squared norm one')
    k0 = matrix(((1, 0), (0, survival)))
    k1 = matrix(((0, jump), (0, 0)))
    return add(multiply(multiply(k0, rho), adjoint(k0)),
               multiply(multiply(k1, rho), adjoint(k1)))


ARITHMETIC_C = (4, 0, 2, 0, -2, 0, -4, 0, -2, 0, 2, 0)
ARITHMETIC_P = matrix(tuple(tuple(Q(ARITHMETIC_C[(n-m) % 12], 12)
                                     for m in range(12)) for n in range(12)))


def arithmetic_state(phase=C(1)):
    """Unnormalized v_+ + phase*v_-; its squared norm is 48."""
    if phase.abs2() != 1:
        raise ValueError('Use a unit relative phase')
    return tuple(C(abs(x)) if x >= 0 else abs(x)*phase for x in ARITHMETIC_C)


def arithmetic_probability(phase):
    v = arithmetic_state(phase)
    projected = multiply(ARITHMETIC_P, tuple((x,) for x in v))
    return sum(row[0].abs2() for row in projected)/48


SYNDROME_MASKS = (0, 4, 2, 1)
SYNDROME_GROUPS = tuple((mask, 7 ^ mask) for mask in SYNDROME_MASKS)


def encode(rho):
    return tuple(tuple(rho[i//7][j//7] if i in (0, 7) and j in (0, 7)
                       else C() for j in range(8)) for i in range(8))


def bit_flip(rho, mask):
    if mask not in range(8):
        raise ValueError('Use a three-bit error mask')
    return tuple(tuple(rho[i ^ mask][j ^ mask] for j in range(8)) for i in range(8))


def recover_logical(rho):
    """Syndrome measurement, matching bit flip, then logical decoding."""
    return tuple(tuple(sum((rho[group[i]][group[j]] for group in SYNDROME_GROUPS), C())
                       for j in range(2)) for i in range(2))


def check():
    counts = dict(states=0, partial_channels=0, records=0, controls=0,
                  damping=0, arithmetic=0, syndrome=0)
    phases = [circle(Q(k, 4)) for k in range(-6, 7)] + [C(-1)]
    for k in range(-6, 7):
        amplitudes = circle(Q(k, 4))
        a, b = amplitudes.re, amplitudes.im
        for phase in phases:
            rho = state(a, b, phase)
            require(adjoint(rho) == rho and trace(rho) == C(1), "Density matrix")
            require(multiply(rho, rho) == rho, "Pure-state idempotence")
            require(reconstruct(*probabilities(rho)) == rho, "Tomography")
            require(hadamard(hadamard(rho)) == rho, "Hadamard inverse")
            require(hadamard(rho)[0][0].re == probabilities(rho)[0], "X setting")
            require(dephase(dephase(rho)) == dephase(rho), "Dephasing projection")
            counts['states'] += 1
            for t in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
                channel = partial_dephase(rho, t)
                require(channel[0][1] == t*rho[0][1], "Coherence transfer")
                require(purity(channel) == a**4+b**4+2*t*t*a*a*b*b, "Purity law")
                # Independent random-unitary implementation, Z rho Z.
                z = matrix(((1, 0), (0, -1)))
                random_phase = add(scale((1+t)/2, rho),
                    scale((1-t)/2, multiply(multiply(z, rho), z)))
                require(channel == random_phase, "Random-unitary channel")
                require(reconstruct(*probabilities(channel)) == channel, "Mixed tomography")
                counts['partial_channels'] += 1
            joint = coherent_record(rho)
            require(purity(joint) == 1, "Coherent record stays pure")
            require(forget_record(joint) == dephase(rho), "Partial trace")
            require(forget_record(uncompute_record(joint)) == rho, "Uncomputation")
            require(forget_record(uncompute_record(dephase(joint))) == dephase(rho),
                    "Classical record does not restore phase")
            counts['records'] += 1
            for survival, jump in ((Q(1), Q(0)), (Q(4, 5), Q(3, 5)), (Q(0), Q(1))):
                damped = amplitude_damp(rho, survival, jump)
                closed = matrix(((a*a+jump*jump*b*b, survival*rho[0][1]),
                                 (survival*rho[1][0], survival*survival*b*b)))
                require(damped == closed and trace(damped) == C(1), 'Damping transfer')
                require(purity(damped) == 1-2*jump**2*survival**2*b**4, 'Damping purity')
                counts['damping'] += 1

    require(multiply(ARITHMETIC_P, ARITHMETIC_P) == ARITHMETIC_P,
            'Arithmetic selector is a projector')
    require(adjoint(ARITHMETIC_P) == ARITHMETIC_P and trace(ARITHMETIC_P) == C(4),
            'Arithmetic orthogonal projector rank')
    require(sum(x*abs(x) for x in ARITHMETIC_C) == 0, 'Signed/unsigned orthogonality')
    counts['arithmetic'] += 1
    for phase in phases:
        require(arithmetic_probability(phase) == (1-phase.re)/2, 'Arithmetic phase response')
        rho12 = scale(Q(1, 48), outer(arithmetic_state(phase)))
        require(trace(multiply(ARITHMETIC_P, dephase(rho12))) == C(Q(1, 3)),
                'Arithmetic complete dephasing')
        counts['arithmetic'] += 1
        logical = state(phase=phase)
        encoded = encode(logical)
        noisy = scale(0, encoded)
        for mask, weight in zip(SYNDROME_MASKS, (Q(1, 2), Q(1, 4), Q(1, 8), Q(1, 8))):
            error = bit_flip(encoded, mask)
            require(recover_logical(error) == logical, 'Single-error recovery')
            require(dephase(error, SYNDROME_GROUPS) == error, 'Syndrome preserves logical coherence')
            noisy = add(noisy, scale(weight, error))
            counts['syndrome'] += 1
        require(recover_logical(noisy) == logical, 'Mixed-error recovery')
        require(recover_logical(dephase(noisy)) == dephase(logical), 'Fine measurement loses logical phase')
        counts['syndrome'] += 1
    require(recover_logical(bit_flip(encode(state()), 6)) != state(), 'Two-flip failure')
    phase_error = state(phase=C(-1))
    require(recover_logical(encode(phase_error)) == phase_error != state(), 'Logical phase-error failure')
    counts['syndrome'] += 2

    real, imaginary = state(), state(phase=C(0, 1))
    require(dephase(real) == dephase(imaginary), "Equal summaries")
    require(probabilities(real)[0] != probabilities(imaginary)[0], "Recovery obstruction")
    require(probabilities(real) == (Q(49, 50), Q(1, 2), Q(9, 25)), "Real phase")
    require(probabilities(imaginary) == (Q(1, 2), Q(49, 50), Q(9, 25)), "Imaginary phase")
    oblique = state(phase=C(Q(3, 5), Q(4, 5)))
    require(probabilities(oblique) == (Q(197, 250), Q(221, 250), Q(9, 25)), "Oblique phase")
    require(purity(partial_dephase(real, Q(1, 2))) == Q(409, 625), "Half coherence")
    before = dephase(hadamard(real))
    after = hadamard(dephase(real))
    require(before[0][0] == C(Q(49, 50)) and after[0][0] == C(Q(1, 2)), "Order witness")
    # Attempting to double all coherences is not a channel on all input states.
    invalid = matrix(((Q(1, 2), 1), (1, Q(1, 2))))
    minus = (C(1), C(-1))
    witness = sum((minus[i].conj()*invalid[i][j]*minus[j]
                   for i in range(2) for j in range(2)), C())
    require(witness == C(-1), "Inverse fails positivity")
    bell = matrix(((Q(1, 2), 0, 0, Q(1, 2)), (0, 0, 0, 0),
                   (0, 0, 0, 0), (Q(1, 2), 0, 0, Q(1, 2))))
    require(dephase(bell, ((0, 3), (1, 2))) == bell, "Within-packet coherence")
    require(purity(dephase(bell)) == Q(1, 2), "Refined measurement")
    counts['controls'] = 10
    return counts


def phase_rows():
    phases = (('1', C(1)), ('i', C(0, 1)), ('-1', C(-1)),
              ('-i', C(0, -1)), ('(3+4i)/5', C(Q(3, 5), Q(4, 5))))
    return [(label, *probabilities(state(phase=z)),
             purity(state(phase=z)), purity(dephase(state(phase=z))))
            for label, z in phases]


FILES = ('measurement-settings.csv', 'partial-dephasing.csv', 'results.json',
         'measurement-comparison.svg', 'amplitude-damping.csv',
         'arithmetic-phase.csv', 'syndrome-recovery.csv')


def save(folder, counts):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    def csv_file(name, header, rows):
        with (folder/name).open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(header)
            writer.writerows(rows)
    csv_file(FILES[0], ('phase', 'p_X_plus', 'p_Y_plus', 'p_Z_plus',
                        'input_purity', 'dephased_purity'), phase_rows())
    rows = []
    for j in range(9):
        t = Q(j, 8)
        rho = partial_dephase(state(), t)
        rows.append((t, *probabilities(rho), purity(rho), Q(288, 625)*(1-t)**2))
    csv_file(FILES[1], ('retained_coherence', 'p_X_plus', 'p_Y_plus',
                        'p_Z_plus', 'purity', 'squared_HS_error'), rows)
    phases = (('1', C(1)), ('i', C(0, 1)), ('-1', C(-1)),
              ('-i', C(0, -1)), ('(3+4i)/5', C(Q(3, 5), Q(4, 5))))
    csv_file('amplitude-damping.csv', ('phase', 'p_X_plus', 'p_Y_plus', 'p_Z_plus', 'purity'),
             [(label, *probabilities(amplitude_damp(state(phase=z))),
               purity(amplitude_damp(state(phase=z)))) for label, z in phases])
    csv_file('arithmetic-phase.csv', ('phase', 'coherent_selected_probability', 'dephased_selected_probability'),
             [(label, arithmetic_probability(z), Q(1, 3)) for label, z in phases])
    csv_file('syndrome-recovery.csv', ('bit_flip_mask', 'first_address', 'second_address',
                                      'noise_probability', 'recovered_p0', 'recovered_upper_right'),
             [(mask, f'{group[0]:03b}', f'{group[1]:03b}', weight,
               recover_logical(bit_flip(encode(state()), mask))[0][0],
               recover_logical(bit_flip(encode(state()), mask))[0][1])
              for mask, group, weight in zip(SYNDROME_MASKS, SYNDROME_GROUPS,
                                            (Q(1, 2), Q(1, 4), Q(1, 8), Q(1, 8)))])
    result = dict(scope='Exact finite teaching example; no sampling or Lean replay.',
                  checks_by_group=counts, total_cases=sum(counts.values()),
                  phase_rows=[[str(x) for x in row] for row in phase_rows()],
                  order_p0=['49/50', '1/2'],
                  tomography_oblique=['197/250', '221/250', '9/25'],
                  coarse_bell_purity='1', fine_bell_purity='1/2',
                  damping_purity=str(purity(amplitude_damp(state()))),
                  arithmetic_selected=['0', '1', '1/3'],
                  syndrome_groups=SYNDROME_GROUPS)
    (folder/FILES[2]).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    # Static scientific chart; exact labels carry the data, geometry is rounded.
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 510" role="img" aria-labelledby="title desc">',
           '<title id="title">One state family, three measurement settings</title>',
           '<desc id="desc">Five phases have the same Z-plus probability 9/25. X and Y measurements distinguish them. Exact fractions label every bar.</desc>',
           '<rect width="780" height="510" fill="#faf8f2"/>',
           '<g font-family="sans-serif" fill="#173b32"><text x="30" y="34" font-size="23">Relative phase changes the observable probabilities</text>',
           '<text x="30" y="62" font-size="15">State: (3/5, 4z/5). Each labelled bar shows an exact plus probability.</text>']
    colors = ('#245f50', '#95632a', '#536caa')
    for index, row in enumerate(phase_rows()):
        y = 102+index*77
        svg.append(f'<text x="30" y="{y+18}" font-size="16">z = {row[0]}</text>')
        for j, p in enumerate(row[1:4]):
            x = 170+j*200
            svg.append(f'<rect x="{x}" y="{y}" width="{float(p)*140:.3f}" height="22" fill="{colors[j]}"/>')
            svg.append(f'<text x="{x}" y="{y+43}" font-size="14">{"XYZ"[j]}+: {p}</text>')
    svg.append('</g></svg>')
    (folder/FILES[3]).write_text('\n'.join(svg)+'\n', encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    counts = check()
    print('Coordinate probabilities: 9/25, 16/25')
    print('X-plus, phase 1: 49/50; phase i: 1/2')
    print('Y-plus, phase 1: 1/2; phase i: 49/50')
    print('Purity: original 1; dephased 337/625; half coherence 409/625')
    print('Order witness, outcome 0: 49/50 versus 1/2')
    print('Coherent record: reversible; classical record: phase lost')
    print('Bell purity: parity packets 1; individual addresses 1/2')
    print('Damping: ground population 369/625; purity 316897/390625')
    print('Arithmetic selector: unsigned 0; signed 1; dephased 1/3')
    print('Syndrome recovery: four single-error branches preserve the logical state')
    print(f'PASS: {sum(counts.values())} exact cases')
    if args.output:
        save(args.output, counts)
        print('Saved: '+', '.join(FILES))


if __name__ == '__main__':
    main()
