#!/usr/bin/env python3
"""Computed arithmetic inverse figures for SF-DISCOVERY-100.

Recovery and conditioning use the already checked JSON.  Only the inexpensive
proved prime-deletion envelope is evaluated anew, at 90 decimal digits.
No finite figure is a proof or a ball-arithmetic certificate.
"""
from pathlib import Path
import hashlib
import json
import math
import platform
import sys
import time

DEPENDENCIES = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
if DEPENDENCIES.is_dir():
    sys.path.insert(0, str(DEPENDENCIES))
import mpmath as mp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT/'figures'
EVIDENCE = ROOT/'evidence'
COLORS = ['#075985', '#e76f51', '#248f83', '#8b5cf6']


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primes_to(limit):
    flags = bytearray(b'\x01')*(limit+1)
    flags[:2] = b'\x00\x00'
    for p in range(2, math.isqrt(limit)+1):
        if flags[p]:
            for multiple in range(p*p, limit+1, p):
                flags[multiple] = 0
    return [p for p in range(2, limit+1) if flags[p]]


def save(fig, stem):
    paths = [FIGURES/(stem+'.pdf'), FIGURES/(stem+'.png')]
    fig.savefig(paths[0])
    fig.savefig(paths[1], dpi=180)
    plt.close(fig)
    return [{'path':str(path.relative_to(ROOT)), 'sha256':sha256(path)} for path in paths]


def main():
    started = time.monotonic()
    FIGURES.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    source = EVIDENCE/'arithmetic_inverse_checks.json'
    data = json.loads(source.read_text())
    if data['status'] != 'PASS':
        raise ValueError('Arithmetic inverse checks must pass before plotting.')
    mp.mp.dps = 90
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                         'axes.spines.top':False, 'axes.spines.right':False,
                         'axes.grid':True, 'grid.alpha':0.16, 'pdf.fonttype':42,
                         'axes.titleweight':'bold', 'figure.facecolor':'white',
                         'savefig.facecolor':'white'})

    fig, axes = plt.subplots(1, 2, figsize=(9.3, 3.6))
    fig.subplots_adjust(left=.082, right=.985, bottom=.31, top=.85, wspace=.33)
    rank_records = []
    condition_records = []
    for color, q in zip(COLORS, (1,2,6,30)):
        ranks = sorted((x for x in data['rank_recovery_examples']
                        if x['q']==q and mp.mpf(x['beta'])==2), key=lambda x:x['rank_j'])
        assert [x['rank_j'] for x in ranks] == [100,1000,10000]
        axes[0].plot([x['rank_j'] for x in ranks],
                     [float(x['beta_rank_ratio_estimate']) for x in ranks],
                     color=color, marker='o', markersize=4.8, lw=1.8, label=f'Q = {q}')
        rank_records.extend(ranks)
        costs = sorted((x for x in data['negative_depth_peeling_examples']
                        if x['q']==q and x['t']==500), key=lambda x:x['atom_index'])
        assert [x['atom_index'] for x in costs] == [1,2,3]
        axes[1].plot([x['n'] for x in costs],
                     [float(x['log10_subtraction_condition_factor']) for x in costs],
                     color=color, marker='o', markersize=4.8, lw=1.8, label=f'Q = {q}')
        condition_records.extend(costs)
    axes[0].axhline(2, color='#334155', ls='--', lw=1.2, label='True β = 2')
    axes[0].set(xscale='log', xlabel='Rank j in the ordered spectrum',
                ylabel=r'Two-rank estimate of $\beta$',
                title='The ranked spectrum recovers β')
    axes[0].legend(loc='best', fontsize=7.9, ncol=2, framealpha=.95)
    axes[1].set(xlabel=r'Support integer $n_j$ of the peeled atom',
                ylabel=r'Condition cost $\log_{10}\kappa_j(500)$',
                title='Later atoms need more precision',
                xlim=(1.7,13.5), ylim=(-3,116))
    axes[1].set_xticks([2,3,5,7,11,13])
    axes[1].legend(loc='upper right', fontsize=8, ncol=2, framealpha=.95)
    axes[1].annotate('Atom 3, Q = 1:\nabout 109 decimal digits',
                     xy=(5,108.801729011), xytext=(7.0,70),
                     fontsize=8.5, ha='left', va='center',
                     arrowprops={'arrowstyle':'->','color':'#475569','lw':.9})
    fig.text(.5,.10,
             'a = β = 2   ·   negative depth t = 500   ·   previous atoms removed exactly',
             ha='center', fontsize=9, color='#334155')
    fig.text(.5,.035,
             'Checked high-precision examples. Exact recovery uses the full analytic germ.',
             ha='center', fontsize=8.8, color='#475569')
    outputs = save(fig, '10_arithmetic_inverse')

    primes = primes_to(10007)
    assert primes[-1] == 10007 and 1009 in primes and 101 in primes
    z4 = mp.zeta(4)/mp.zeta(8)
    radius = mp.mpf(5)
    rows = []
    for p in primes:
        lam = -2*mp.log1p(-mp.mpf(p)**-2)
        mass = z4/(mp.mpf(p)**4+1)
        envelope = mp.exp(radius*lam)*mass
        rows.append({'prime':p, 'lambda_p':mp.nstr(lam,32),
                     'actual_depth_zero_difference':mp.nstr(mass,32),
                     'proved_radius_five_envelope':mp.nstr(envelope,32)})
    fig, ax = plt.subplots(figsize=(9.3,3.6))
    fig.subplots_adjust(left=.09, right=.985, bottom=.30, top=.85)
    ax.loglog(primes, [float(r['actual_depth_zero_difference']) for r in rows],
              color=COLORS[0], lw=2.2, label='Exact difference at depth s = 0')
    ax.loglog(primes, [float(r['proved_radius_five_envelope']) for r in rows],
              color=COLORS[1], ls='--', lw=1.8,
              label='Proved uniform envelope on |s| ≤ 5')
    selected = [r for r in rows if r['prime'] in (101,1009,10007)]
    ax.scatter([r['prime'] for r in selected],
               [float(r['proved_radius_five_envelope']) for r in selected],
               color=COLORS[1], s=28, zorder=5)
    final_bound = float(rows[-1]['proved_radius_five_envelope'])
    ax.annotate(r'$p=10007:\ B_5(p)=1.0749\times10^{-16}$',
                 xy=(10007,final_bound), xytext=(45,2.0e-13),
                 fontsize=10, ha='left', va='center',
                 bbox={'boxstyle':'round,pad=.35','facecolor':'white',
                       'edgecolor':'#cbd5e1','alpha':.96},
                 arrowprops={'arrowstyle':'->','color':'#475569','lw':1})
    ax.set(xlabel='Newly excluded prime p', ylabel='Absolute difference bound',
           title='Different excluded primes can be invisible on a bounded window',
           xlim=(1.7,16000), ylim=(4e-18,4))
    ax.legend(loc='upper right', fontsize=9, framealpha=.95)
    fig.text(.5,.095,
             r'$Q=1,\ a=\beta=2:\quad B_5(p)=e^{5\lambda_p}\,Z_1(4)/(p^4+1)$',
             ha='center', fontsize=10, color='#334155')
    fig.text(.5,.03,
             'Exact theorem envelopes evaluated at 90 decimal digits; numerical display is not ball-certified.',
             ha='center', fontsize=8.5, color='#475569')
    outputs.extend(save(fig,'11_prime_instability'))

    record = {'checkpoint':'SF-DISCOVERY-100', 'status':'PASS',
              'generator':'build_inverse_figures.py', 'generator_sha256':sha256(Path(__file__)),
              'source_record':str(source.relative_to(ROOT)), 'source_record_sha256':sha256(source),
              'source_status':data['status'], 'rank_plot_records':rank_records,
              'conditioning_plot_records':condition_records,
              'prime_envelope_records':rows, 'prime_envelope_parameters':{'Q':1,'a':2,'beta':2,
                  'radius':5,'decimal_precision':90,'prime_range':[2,10007],
                  'prime_count':len(primes),'formula':'exp(5*lambda_p)*Z_1(4)/(p^4+1)'},
              'outputs':outputs, 'software':{'python':sys.version.split()[0],
                  'mpmath':mp.__version__,'matplotlib':matplotlib.__version__,
                  'platform':platform.platform()},
              'runtime_seconds':round(time.monotonic()-started,6),
              'visual_qa_history':['Initial render showed footer text overlapping x-axis labels, and a legend covered the highest conditioning point. Increased the bottom plot margin and moved that legend. A second inspection found the moved legend touching an annotation, which was moved lower. No mathematical data changed.'],
              'non_claims':['No recovery theorem is inferred from the finite rank plots.',
                  'The conditioning plot assumes exact removal of previous atoms.',
                  'The analytic prime envelopes are proved in arithmetic_inverse.md.',
                  'Ordinary high precision and plotting floats are not ball arithmetic.']}
    path = EVIDENCE/'inverse_figure_record.json'
    path.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':'PASS','outputs':outputs,
                      'record':str(path),'prime_count':len(primes),
                      'final_prime_bound':rows[-1]['proved_radius_five_envelope'],
                      'runtime_seconds':record['runtime_seconds']},indent=2))


if __name__ == '__main__':
    main()
