#!/usr/bin/env python3
"""Exact-formula sieve figures for SF-DISCOVERY-100.

Geometric and detector inputs use fractions.Fraction. The region mesh and
rendering use ordinary floats. This is a visual display of proved bounds,
not an inference of a universal claim from sampled points.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import prod
import hashlib
import json
import platform

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

ROOT = Path(__file__).resolve().parent
FIG = ROOT/'figures'
FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.alpha': .16, 'pdf.fonttype': 42,
    'figure.facecolor': 'white', 'axes.titleweight': 'bold',
    'savefig.facecolor': 'white'})
BLUE = '#075985'
RED = '#e76f51'
TEAL = '#248f83'
GOLD = '#e9b949'
LIGHT_TEAL = '#d4eee8'
LIGHT_RED = '#f8ddd6'
GRAY = '#64748b'


def save(fig, name):
    paths = [FIG/(name+'.pdf'), FIG/(name+'.png')]
    fig.savefig(paths[0], bbox_inches='tight')
    fig.savefig(paths[1], dpi=190, bbox_inches='tight')
    plt.close(fig)
    return [{'path': str(path.relative_to(ROOT)),
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]


def rational(value):
    return str(value.numerator) if value.denominator == 1 else f'{value.numerator}/{value.denominator}'


def node(n):
    return (1-Q(1, n*n))**2


def squarefree(n):
    return all(n % (d*d) != 0 for d in range(2, int(n**.5)+1))


def lagrange_value(p, x):
    return prod((x-node(n))/(node(p)-node(n)) for n in range(1, p))


record = {'claim_id': 'SF-DISCOVERY-100-MULTI-PRIME-FIGURES',
    'software': {'python': platform.python_version(), 'numpy': np.__version__,
                 'matplotlib': matplotlib.__version__},
    'arithmetic': 'Rational bound and nodal values exact in Fraction; rendered floats only.',
    'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'non_claims': ['Region meshes do not establish positivity.',
                   'The detector bound is proved in new_results/multi_prime_sieve.md.',
                   'Sufficient detector degree is not asserted minimal.'],
    'outputs': [],
    'visual_qa_history': [
        {'iteration': 1, 'status': 'labels-corrected',
         'observed_issue': 'Several lambda labels rendered as Latin letters because a source string lost its backslash during authoring.',
         'correction': 'Restored explicit mathtext lambda commands and regenerated both figures.'},
        {'iteration': 2, 'status': 'rendered-for-review',
         'scope': 'Exact formulas and nodal values checked in code; parent and author inspect rendered layouts.'}]}

# Figure12: unrestricted H1 test versus exact positive-measure domain.
fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.1), layout='constrained')
left, right = axes
lambda2 = np.linspace(-43, 8, 300)
lambda3 = np.linspace(-195, 18, 300)
xx, yy = np.meshgrid(lambda2, lambda3)
positive = ((1+xx/17)*(1+yy/82) > 0).astype(int)
left.pcolormesh(xx, yy, positive, shading='nearest',
               cmap=ListedColormap([LIGHT_RED, LIGHT_TEAL]), vmin=0, vmax=1, rasterized=True)
left.axvline(-17, color=GRAY, lw=1.2, ls=':')
left.axhline(-82, color=GRAY, lw=1.2, ls=':')
left.add_patch(Rectangle((-1, -1), 9, 19, facecolor=GOLD, edgecolor='#9a6700',
                         alpha=.9, linewidth=1.1))
left.plot([0, -34], [0, -164], color=BLUE, ls='--', lw=1.6, zorder=3)
for x, y, label, text_x, text_y in [
        (0, 0, r'$A=(0,0)$', -15, 9),
        (-34, -164, r'$B=(-34,-164)$', -40, -189),
        (-17, -82, r'$C=(-17,-82)$', -38, -61)]:
    left.scatter([x], [y], color=BLUE if label[1]=='A' else GRAY, s=42,
                 edgecolors='white', linewidths=.8, zorder=5)
    left.annotate(label, (x, y), xytext=(text_x, text_y), fontsize=9,
                  arrowprops={'arrowstyle': '-', 'color': GRAY, 'lw': .9})
left.set(xlim=(-43, 8), ylim=(-195, 18), xlabel=r'Strength $\lambda_2$',
         ylabel=r'Strength $\lambda_3$', title='A positive mass test can hide signed atoms')
left.text(-40, -108, r'$H_1>0$', color=TEAL, fontsize=12, fontweight='bold')
left.text(-10, -118, r'$H_1<0$', color='#b84b35', fontsize=12, fontweight='bold')
left.legend(handles=[Patch(facecolor=LIGHT_TEAL, label=r'Order 1 test: $H_1>0$'),
                     Patch(facecolor=LIGHT_RED, label=r'Order 1 test: $H_1<0$'),
                     Patch(facecolor=GOLD, label='Positive measure')],
            loc='lower right', fontsize=8, framealpha=.96)

right.set_facecolor(LIGHT_TEAL)
right.add_patch(Rectangle((-1, -1), 4.3, 4.3, facecolor=GOLD, alpha=.75,
                          edgecolor='#9a6700', linewidth=1.3))
right.axvline(-1, color='#9a6700', lw=1.3)
right.axhline(-1, color='#9a6700', lw=1.3)
right.text(.85, 1.65, 'Positive measure\n'+r'$\lambda_2,\lambda_3\geq-1$',
           ha='center', va='center', fontsize=11, color='#6a4d00')
right.text(-1.85, .8, 'Negative\n2-atom', ha='center', va='center',
           fontsize=9, color='#854437')
right.text(.9, -1.87, 'Negative 3-atom', ha='center', va='center',
           fontsize=9, color='#854437')
right.scatter([0], [0], color=BLUE, s=42, edgecolors='white', linewidths=.8, zorder=4)
right.set(xlim=(-2.6, 3.3), ylim=(-2.6, 3.3), xlabel=r'Strength $\lambda_2$',
          ylabel=r'Strength $\lambda_3$', title='Nearby: every point passes the mass test')
right.set_aspect('equal', adjustable='box')
right.text(.4, -2.4, 'Boundaries include exact prime deletion', ha='center', fontsize=8)
record['outputs'] += save(fig, '12_multi_prime_domain')
record['domain_figure'] = {
    'hankel_order': 1,
    'mass_factor_exact': '(1+lambda2/17)*(1+lambda3/82)',
    'exact_measure_domain': 'lambda2>=-1 and lambda3>=-1',
    'positive_definite_nonconvexity_points': [[0, 0], [-34, -164], [-17, -82]],
    'mass_factors': ['1', '1', '0'],
    'mesh_size': [300, 300],
    'interpretation': 'A,B pass positive-definiteness; midpointC fails positive-definiteness. C is semidefinite.'}

# Figure13: exact isolating polynomial for lambda3=-1.1, lambda2=1.
p = 3
strengths = {2: Q(1), 3: Q(-11, 10)}
cp = lagrange_value(p, Q(1))
rp = (1-node(p+1))/(1-node(p))
cf = prod(max(Q(1), abs(1+value)) for value in strengths.values())
negative_mass = Q(1+strengths[p], p**4)


def norm_bound(m):
    return negative_mass+cf*cp*cp*rp**(2*m)/Q(3*p**3)


first_m = 0
while norm_bound(first_m) >= 0:
    first_m += 1
assert first_m < 200
assert norm_bound(first_m) < 0
if first_m:
    assert norm_bound(first_m-1) >= 0

nodal_values = []
for n in range(1, 19):
    value = lagrange_value(p, node(n))*((1-node(n))/(1-node(p)))**first_m
    weight = Q(1, n**4) if squarefree(n) else Q(0)
    for q, lam in strengths.items():
        if n % q == 0:
            weight *= 1+lam
    nodal_values.append((n, value, weight))
assert all(value == 0 for n, value, _ in nodal_values if n < p)
assert nodal_values[p-1][1] == 1
assert all(abs(value) <= cp*rp**first_m for n, value, _ in nodal_values if n > p)

fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.9), layout='constrained')
left, right = axes
for n, value, weight in nodal_values:
    if not weight:
        left.scatter([n], [float(value)], marker='x', color='#94a3b8', s=24, zorder=4)
    else:
        color = RED if weight < 0 else TEAL
        left.vlines(n, 0, float(value), color=color, lw=1.4, alpha=.85)
        left.scatter([n], [float(value)], color=color, s=29, zorder=4)
left.axhline(float(cp*rp**first_m), color=BLUE, lw=1.4, ls='--')
left.annotate('Negative prime atom\n'+r'$f(x_3)=1$', (3, 1), xytext=(7.7, .91),
              arrowprops={'arrowstyle': '->', 'color': RED, 'lw': 1},
              fontsize=9, color='#9f4230')
left.text(8.5, float(cp*rp**first_m)+.045, 'Proved higher-node bound',
          color=BLUE, fontsize=8, ha='center')
left.set(xlim=(.5, 18.6), ylim=(-.04, 1.13), xlabel='Arithmetic node index n',
         ylabel=r'Isolating polynomial $f_{3,m}(x_n)$',
         title=f'Lower nodes vanish; first certificate m={first_m}')
left.set_xticks([1, 3, 6, 9, 12, 15, 18])
left.legend(handles=[Patch(facecolor=TEAL, label='Positive atom'),
                     Patch(facecolor=RED, label='Negative atom'),
                     plt.Line2D([], [], color='#94a3b8', marker='x', linestyle='',
                                label='No squarefree atom')],
            loc='upper right', bbox_to_anchor=(1, .71), fontsize=8, framealpha=.96)

ms = list(range(first_m+11))
bounds = [norm_bound(m) for m in ms]
right.plot(ms, list(map(float, bounds)), color=BLUE, lw=1.8)
right.scatter(ms[:first_m], list(map(float, bounds[:first_m])), color=TEAL, s=20)
right.scatter(ms[first_m:], list(map(float, bounds[first_m:])), color=RED, s=20)
right.axhline(0, color=GRAY, lw=1.2)
right.axhline(float(negative_mass), color=GRAY, ls=':', lw=1)
right.set_yscale('symlog', linthresh=float(abs(negative_mass))/5)
right.annotate(f'First negative upper bound\nm={first_m}; Hankel order={p+first_m}',
               (first_m, float(bounds[first_m])), xytext=(first_m+3, .007),
               arrowprops={'arrowstyle': '->', 'color': RED, 'lw': 1},
               fontsize=9, color='#9f4230')
right.set(xlabel='Suppression exponent m', ylabel=r'Proved upper bound on $\int f_{3,m}^{\,2}\,d\nu$',
          title=r'Exact rational bound crosses below zero')
right.text(.59, .97, r'$\lambda_2=1,\quad\lambda_3=-1.1$', transform=right.transAxes,
           fontsize=10, va='top', ha='center')
record['outputs'] += save(fig, '13_signed_detector')
record['detector_figure'] = {
    'prime_target': p, 'strengths': {str(q): rational(value) for q, value in strengths.items()},
    'C_p_exact': rational(cp), 'r_p_exact': rational(rp), 'C_F_exact': rational(cf),
    'negative_atom_mass_exact': rational(negative_mass),
    'first_certifying_m': first_m, 'polynomial_degree': p-1+first_m,
    'hankel_order': p+first_m,
    'first_negative_upper_bound_exact': rational(bounds[first_m]),
    'preceding_upper_bound_exact': rational(bounds[first_m-1]) if first_m else None,
    'nodal_values_exact': [{'n': n, 'value': rational(value), 'atom_weight': rational(weight)}
                           for n, value, weight in nodal_values],
    'norm_upper_bounds_exact': [{'m': m, 'bound': rational(bound)} for m, bound in zip(ms, bounds)],
    'interpretation': 'The displayed bound is a proved constructive inequality evaluated exactly; no floating eigenvalue certificate is used.'}
(ROOT/'evidence'/'sieve_figure_record.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({'status': 'created', 'outputs': [item['path'] for item in record['outputs']],
                  'detector_m': first_m, 'detector_hankel_order': p+first_m}, indent=2))
