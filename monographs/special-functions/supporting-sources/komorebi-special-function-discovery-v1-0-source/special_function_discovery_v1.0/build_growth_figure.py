#!/usr/bin/env python3
"""Exact-formula scientific figures for the v1.0 dilation growth chapter.

Curves use 90-digit coefficient arithmetic. Rational Cauchy envelopes bound
analytic truncation independently; floating evaluation is not ball arithmetic.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

DEP = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
if DEP.is_dir():
    sys.path.insert(0, str(DEP))
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)
mp.mp.dps = 90
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .15, 'pdf.fonttype': 42,
                     'figure.facecolor': 'white', 'axes.titleweight': 'bold',
                     'savefig.facecolor': 'white'})
COLORS = ['#075985', '#e76f51', '#248f83']


def mpf(q):
    return mp.mpf(q.numerator) / q.denominator


def coefficients(channels, last):
    # The exact recurrence is evaluated without subtractive cancellation.
    powers = [(mpf(h), [mpf(q) ** (2*i+1) for i in range(last)],
               [mpf(r) ** (2*i+1) for i in range(last)]) for h, q, r in channels]
    c = [mp.mpf(1)]
    for n in range(1, last + 1):
        c.append(mp.fsum(h * mp.fsum(q[i]*r[n-1-i]*c[i]*c[n-1-i]
                                    for i in range(n))
                         for h, q, r in powers) / (2*n+1))
    return c


def evaluate(c, x, weighted=False):
    x = mp.mpf(str(x))
    if weighted:
        return x * mp.polyval(list(reversed([2*n*a for n, a in enumerate(c)])), x*x)
    return x * mp.polyval(list(reversed(c)), x*x)


def cauchy_envelope(qmax, outer):
    radii = [outer]
    while radii[-1] > 1:
        radii.append(radii[-1]*qmax)
    upper = F(2)  # Tangent domination and tan(1)<2.
    for radius in reversed(radii[:-1]):
        upper = radius*(1+upper*upper)
    return upper


def tails(qmax, display, outer, last):
    upper = cauchy_envelope(qmax, outer)
    x = display / outer
    first = 2*last+3
    ordinary = upper*x**first/(1-x*x)
    weighted = upper*x**first*((first-1)/(1-x*x)+2*x*x/(1-x*x)**2)
    return {'Q': str(qmax), 'display_radius': str(display), 'outer_radius': str(outer),
            'last_n': last, 'last_power': 2*last+1, 'first_omitted_power': first,
            'Cauchy_M_upper_exact': str(upper),
            'function_tail_exact': str(ordinary),
            'Rf_prime_minus_f_tail_exact': str(weighted),
            'function_tail_decimal': mp.nstr(mpf(ordinary), 20),
            'Rf_prime_minus_f_tail_decimal': mp.nstr(mpf(weighted), 20),
            'formulas': {'function': 'U*x^(2N+3)/(1-x^2)',
                         'weighted': 'U*x^(2N+3)*[(2N+2)/(1-x^2)+2*x^2/(1-x^2)^2]'}}


def save(fig, name):
    fig.savefig(FIG / (name+'.pdf'), bbox_inches='tight')
    fig.savefig(FIG / (name+'.png'), dpi=180, bbox_inches='tight')
    plt.close(fig)


record = {'checkpoint': 'SF-DISCOVERY-100', 'mpmath_version': mp.__version__,
          'coefficient_precision_decimal_digits': mp.mp.dps,
          'growth_curves': [], 'compact_curves': [],
          'scope': ['Finite radial windows do not establish a type limit.',
                    'The analytic positive lower-type theorem has a separate full proof.',
                    'Cauchy tails bound analytic truncation exactly over Q.',
                    'mpmath rounding and plotting floats are not ball-certified.']}

# A common range makes different orders comparable without fitted asymptotics.
fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.9), layout='constrained')
radial = np.linspace(2, 12, 220)
definitions = [(F(1,4), F(1,4), mp.mpf('.5'), r'$q=r=1/4,\ \rho=1/2$'),
               (F(1,2), F(1,2), mp.mpf(1), r'$q=r=1/2,\ \rho=1$'),
               (F(1,3), F(2,3), mp.mpf(1), r'$q=1/3,\ r=2/3,\ \rho=1$')]
for color, (q, r, rho, label) in zip(COLORS, definitions):
    last = 500
    c = coefficients([(F(1), q, r)], last)
    shift = max(q/(1-q), r/(1-r))
    seed_end = 1 + 2/min(q,r)
    lower = mp.log(2)/mpf(seed_end+shift)**rho
    logs = [mp.log(evaluate(c, radius)) for radius in radial]
    exact_lower = [lower*(mp.mpf(str(radius))+mpf(shift))**rho for radius in radial]
    normalized = [value/mp.mpf(str(radius))**rho for value, radius in zip(logs, radial)]
    ax[0].plot(radial, list(map(float, logs)), color=color, lw=2.1, label=label)
    ax[0].plot(radial, list(map(float, exact_lower)), color=color, lw=1.55, ls='--')
    ax[1].plot(radial, list(map(float, normalized)), color=color, lw=2.1)
    ax[1].axhline(float(lower), color=color, lw=1.25, ls=':')
    entry = tails(max(q,r), F(12), F(24), last)
    entry.update({'q': str(q), 'r': str(r), 'rho': str(rho),
                  'lower_constant_decimal': mp.nstr(lower, 25),
                  'log_M_at_R2': mp.nstr(logs[0], 25),
                  'log_M_at_R12': mp.nstr(logs[-1], 25)})
    record['growth_curves'].append(entry)
ax[0].set(xlabel='Radius R', ylabel=r'$\log M(R)$',
          title='The function stays above a proved positive bound', xlim=(2,12))
ax[0].legend(fontsize=8.4, loc='upper left')
ax[1].set(xlabel='Radius R', ylabel=r'$\log M(R)/R^{\rho}$',
          title='A finite window does not determine the type limit', xlim=(2,12))
ax[1].legend(handles=[Line2D([0],[0],color='#334155',lw=2,label='computed value'),
                       Line2D([0],[0],color='#334155',lw=1.5,ls=':',label='positive lower-type constant')],
             fontsize=8.4, loc='upper right')
ax[0].text(.98,.02,'Dashed: '+r'$c_-(R+C)^{\rho}$', transform=ax[0].transAxes,
           ha='right', va='bottom', fontsize=8.5, color='#334155')
save(fig, '08_growth_type')

# The weight sensitivity theorem separates compact behavior from distant order.
fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.9), layout='constrained')
compact_radius = np.linspace(0,1.4,220)
last = 180
base = coefficients([(F(1),F(1,4),F(1,4))],last)
majorant = coefficients([(F(1),F(3,4),F(3,4))],last)
bracket = [evaluate(majorant, radius, weighted=True)/2 for radius in compact_radius]
baseline_values = [evaluate(base,radius) for radius in compact_radius]
tap_tail = tails(F(3,4),F(7,5),F(14,5),last)
majorant_weighted_tail = F(tap_tail['Rf_prime_minus_f_tail_exact'])
for color, epsilon in zip(COLORS, (F(1,1000),F(1,100),F(1,10))):
    c = coefficients([(1-epsilon,F(1,4),F(1,4)),
                      (epsilon,F(3,4),F(3,4))],last)
    differences = [evaluate(c,radius)-baseline for radius,baseline
                   in zip(compact_radius,baseline_values)]
    bounds = [mpf(epsilon)*value for value in bracket]
    ax[0].semilogy(compact_radius,list(map(float,differences)),color=color,lw=2.1,
                   label=r'$\varepsilon='+str(float(epsilon))+'$')
    ax[0].semilogy(compact_radius,list(map(float,bounds)),color=color,lw=1.35,ls='--')
    ax[1].plot(compact_radius,[float(value/mpf(epsilon)) for value in differences],
               color=color,lw=2.1,label=r'$\varepsilon='+str(float(epsilon))+'$')
    record['compact_curves'].append({'epsilon':str(epsilon),
        'difference_at_R1_4':mp.nstr(differences[-1],30),
        'theorem_bound_at_R1_4':mp.nstr(bounds[-1],30),
        'difference_function_tail_bound_decimal':mp.nstr(2*mpf(F(tap_tail['function_tail_exact'])),20),
        'bound_weighted_tail_decimal':mp.nstr(mpf(epsilon)*mpf(majorant_weighted_tail)/2,20)})
ax[0].set(xlabel='Disk radius R',ylabel=r'$F_{\varepsilon}(R)-f_{1/4}(R)$',
          title='A weak faster tap is close on each fixed disk',xlim=(0,1.4))
ax[0].legend(fontsize=8.4,loc='lower right')
ax[0].text(.03,.98,'Solid: difference\nDashed: theorem bound',transform=ax[0].transAxes,
           ha='left',va='top',fontsize=8.5,color='#334155')
ax[1].plot(compact_radius,list(map(float,bracket)),color='#334155',lw=1.7,ls='--',
           label='common bound after division by '+r'$\varepsilon$')
ax[1].set(xlabel='Disk radius R',ylabel=r'$[F_{\varepsilon}(R)-f_{1/4}(R)]/\varepsilon$',
          title='The compact error has an explicit linear envelope',xlim=(0,1.4))
ax[1].legend(fontsize=8.2,loc='upper left')
save(fig,'09_tap_continuity')
record['compact_common_cauchy_record']=tap_tail
record['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(ROOT/'evidence/growth_figure_computation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':'completed','figures':['08_growth_type','09_tap_continuity'],
                  'growth_tail_bounds':[x['function_tail_decimal'] for x in record['growth_curves']],
                  'tap_function_tail':tap_tail['function_tail_decimal'],
                  'tap_weighted_tail':tap_tail['Rf_prime_minus_f_tail_decimal']},indent=2))
