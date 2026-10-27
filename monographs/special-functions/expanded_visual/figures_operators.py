"""Three operator-contract figures; exact rational checks and rendering only.

Regenerate from the guide directory with:
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python figures_operators.py
The sampled prefixes in O01 are not finite-input cutoffs. O03 separately
distinguishes a periodic vector from a zero-extended, finite causal input.
"""
from datetime import datetime, timezone
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
from pathlib import Path
import hashlib
import json
import os
import platform
import sys
import time

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

from guide_style import ROOT, FIGURES, COLORS, INK, MUTED, PALE, save_figure


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fir_prefix(a, h, length=None):
    """Only requested coefficients, with negative indices zero."""
    if length is None:
        length = len(a)
    return [sum(h[k]*a[n-k] for k in range(min(n, len(h)-1)+1))
            for n in range(length)]


def falling(n, k):
    assert 0 <= k <= n
    return factorial(n)//factorial(n-k)


def B4(x):
    return x**4-2*x**3+x*x-Q(1, 30)


def translate_polynomial(a, shift):
    """Coefficients of P(x+shift), in ascending powers, exactly."""
    return [sum(a[j]*comb(j, k)*shift**(j-k) for j in range(k, len(a)))
            for k in range(len(a))]


def periodic_difference(a):
    return [a[n]-a[(n-1)%len(a)] for n in range(len(a))]


def causal_difference_flushed(a):
    assert a
    return [a[0]] + [a[n]-a[n-1] for n in range(1, len(a))] + [-a[-1]]


def partial_sums(a):
    out = []; total = 0
    for value in a:
        total += value; out.append(total)
    return out


def periodic_recover(y, x0):
    """Return one four-cycle solution, or None for incompatible output."""
    assert len(y) == 4
    if sum(y) != 0:
        return None
    x = [x0]
    for n in range(1, 4):
        x.append(x[-1]+y[n])
    assert x[0]-x[-1] == y[0]
    return x


def box(ax, x, y, label, w=.8, h=.58, fontsize=12, color=PALE):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle='round,pad=.04', facecolor=color,
                 edgecolor=COLORS[0], linewidth=1.2))
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize)


def main():
    start = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    input_names = ['figures_operators.py', 'chapters_operators.tex', 'guide_style.py']
    input_hashes = [{'path':name, 'sha256':sha(ROOT/name)} for name in input_names]
    checks = {}
    stems = []

    # O01: H is stationary on Taylor coefficients. Its pullback is N^-1 H N.
    h = [1, -1]
    counts = [1]*12
    normalized = [Q(a, factorial(n)) for n, a in enumerate(counts)]
    raw_output = fir_prefix(counts, h)
    taylor_output = fir_prefix(normalized, h)
    pulled_counts = [b*factorial(n) for n, b in enumerate(taylor_output)]
    assert raw_output == [1]+[0]*11
    assert pulled_counts == [1-n for n in range(12)]
    rows = [counts[:6], raw_output[:6], list(map(str, normalized[:6])),
            list(map(str, taylor_output[:6])), list(map(str, pulled_counts[:6]))]
    row_labels = [r'Counts $a_n$', r'Count FIR $(Ha)_n$',
                  r'Taylor $b_n=(Na)_n$', r'Taylor FIR $(Hb)_n$',
                  r'Pullback $(N^{-1}HN a)_n$']
    fig, ax = plt.subplots(figsize=(8.1, 4.2), layout='constrained')
    ax.axis('off')
    ax.set_title('Same stationary taps act in different coefficient coordinates', pad=13)
    table = ax.table(cellText=rows, rowLabels=row_labels,
                     colLabels=[f'n = {n}' for n in range(6)],
                     cellLoc='center', rowLoc='right',
                     loc='center', bbox=[.29, .12, .7, .82])
    table.auto_set_font_size(False); table.set_fontsize(12)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('#D1DCDF')
        if i == 0:
            cell.set_facecolor(PALE)
        elif i in (1, 2):
            cell.set_facecolor(matplotlib.colors.to_rgba(COLORS[0], .065))
        elif i in (3, 4):
            cell.set_facecolor(matplotlib.colors.to_rgba(COLORS[2], .065))
        else:
            cell.set_facecolor(matplotlib.colors.to_rgba(COLORS[3], .095))
        if j == -1:
            cell.get_text().set_fontsize(11)
    ax.text(.5, .01, r'Count FIR EGF: $1$     |     Taylor FIR series: $(1-z)e^z$',
            transform=ax.transAxes, ha='center', fontsize=12)
    stem = 'O01_factorial_transport'; save_figure(fig, stem); stems.append(stem)
    families = [list(range(24)), [n*n for n in range(24)],
                [(-1)**n*(n+1) for n in range(24)], [1]*24]
    tap_lists = [[1, -1], [1, 2, 1], [2, -3, 0, 1], [Q(1, 2), Q(-2, 3)]]
    conjugation_instances = 0
    for a in families:
        b = [Q(a[n], factorial(n)) for n in range(24)]
        for taps in tap_lists:
            Hb = fir_prefix(b, taps)
            Ha = fir_prefix(a, taps)
            for n in range(24):
                direct_pullback = sum(taps[k]*falling(n, k)*a[n-k]
                                      for k in range(min(n, len(taps)-1)+1))
                direct_forward = sum(taps[k]*b[n-k]/falling(n, k)
                                     for k in range(min(n, len(taps)-1)+1))
                assert Hb[n]*factorial(n) == direct_pullback
                assert Q(Ha[n], factorial(n)) == direct_forward
                conjugation_instances += 1
    checks['O01'] = {
        'normalization':'N(a)[n]=a[n]/n!',
        'stationary_FIR':'H(b)[n]=sum_k h[k]*b[n-k]',
        'prominent_direction':'Taylor FIR pulled back to counts: N^-1 H N',
        'pullback_weights':'h[k]*(n)_k',
        'opposite_direction':'Count FIR transported to Taylor coefficients: N H N^-1',
        'forward_weights':'h[k]/(n)_k for 0<=k<=n',
        'tap_list':h, 'displayed_original_indices':[0, 5],
        'example_checked_original_indices':[0, 11],
        'count_input':counts, 'count_FIR_output':raw_output,
        'Taylor_input':list(map(str, normalized)),
        'Taylor_FIR_output':list(map(str, taylor_output)),
        'pulled_back_counts':list(map(str, pulled_counts)),
        'additional_families':['n', 'n^2', '(-1)^n*(n+1)', '1'],
        'additional_tap_lists':[[str(v) for v in taps] for taps in tap_lists],
        'additional_indices':[0, 23], 'two_direction_instances':conjugation_instances,
        'input_contract':'Infinite streams; computed prefixes are not finite-input cutoffs.'}

    # O02: a complete degree-four coefficient check determines the polynomial identity.
    coeffs = [Q(-1, 30), Q(0), Q(1), Q(-2), Q(1)]
    shifted = translate_polynomial(coeffs, Q(1))
    difference = [b-a for a, b in zip(coeffs, shifted)]
    assert difference == [0, 0, 0, 4, 0]
    samples = []
    for N in range(51):
        endpoint_sum = (B4(Q(N))-B4(Q(0)))/4
        integer_sum = sum(k**3 for k in range(N))
        assert endpoint_sum == integer_sum
        samples.append({'N':N, 'endpoint_sum':str(endpoint_sum), 'cube_sum':integer_sum})
    assert B4(Q(5)) == Q(11999, 30)
    assert B4(Q(0)) == Q(-1, 30)
    terms = [k**3 for k in range(5)]
    fig, ax = plt.subplots(figsize=(8.1, 4.2), layout='constrained')
    ax.bar(range(5), terms, color=COLORS[0], width=.63)
    for k, value in enumerate(terms):
        ax.text(k, value+1.7, str(value), ha='center', fontsize=15)
    ax.set(xlim=(-.65, 4.65), ylim=(0, 80), xticks=range(5),
           xlabel='Translation index k, with endpoint N = 5',
           ylabel=r'Gap $[B_4(k+1)-B_4(k)]/4$',
           title='Five Bernoulli translation gaps telescope to 100')
    ax.grid(axis='y')
    ax.text(.035, .9, r'Endpoint difference: $\frac{11999}{30}-(-\frac{1}{30})=400$'+'\n'
            r'Divide by four: $0+1+8+27+64=100$', transform=ax.transAxes,
            ha='left', va='top', fontsize=12,
            bbox={'boxstyle':'round,pad=.45','facecolor':PALE,'edgecolor':'#D1DCDF'})
    stem = 'O02_bernoulli_antiderivative'; save_figure(fig, stem); stems.append(stem)
    checks['O02'] = {
        'variable':'Translation argument x; order fixed at four.',
        'polynomial_coefficients_ascending':list(map(str, coeffs)),
        'translated_polynomial_coefficients':list(map(str, shifted)),
        'difference_coefficients':list(map(str, difference)),
        'universal_reduction':'Complete degree-four polynomial coefficient comparison; then telescoping.',
        'sampled_integer_endpoints':[0, 50], 'samples':samples,
        'displayed_terms':terms, 'displayed_sum':sum(terms),
        'B4_at_5':str(B4(Q(5))), 'B4_at_0':str(B4(Q(0)))}

    # O03: the finite causal input is zero outside its four stored values.
    x = [1, 3, 2, 0]; xp = [v+5 for v in x]
    periodic = periodic_difference(x)
    assert periodic == periodic_difference(xp) == [1, 2, -1, -2]
    causal = causal_difference_flushed(x)
    causal_p = causal_difference_flushed(xp)
    assert causal == [1, 2, -1, -2, 0]
    assert causal_p == [6, 2, -1, -2, -5]
    assert periodic_recover(periodic, 1) == x
    assert periodic_recover(periodic, 6) == xp
    assert periodic_recover([1, 0, 0, 0], 1) is None
    fig, axs = plt.subplots(1, 2, figsize=(8.1, 4.2), layout='constrained',
                            gridspec_kw={'width_ratios':[1.03, 1]})
    ax = axs[0]; ax.axis('off')
    ax.set_title('Periodic: identical edge differences', fontsize=13)
    points = [(0, 2), (2, 2), (2, 0), (0, 0)]
    for n, (px, py) in enumerate(points):
        box(ax, px, py, f'n = {n}\n{x[n]} or {xp[n]}', w=.84, h=.66, fontsize=12)
    arcs = [((.5, 2), (1.5, 2)), ((2, 1.6), (2, .4)),
            ((1.5, 0), (.5, 0)), ((0, .4), (0, 1.6))]
    labels = [(1, 2.5, '2'), (2.6, 1, '−1'), (1, -.54, '−2'), (-.58, 1, '1')]
    for a, b in arcs:
        ax.annotate('', xy=b, xytext=a,
                    arrowprops={'arrowstyle':'->','color':COLORS[0],'lw':1.9})
    for px, py, label in labels:
        ax.text(px, py, label, ha='center', va='center', fontsize=16, color=COLORS[1])
    ax.text(1, -.95, r'$\sum y=0$; constants are invisible', ha='center', fontsize=11.5)
    ax.set(xlim=(-1.1, 3.1), ylim=(-1.2, 3.0))
    ax = axs[1]
    n = np.arange(5)
    ax.axvspan(-.45, .45, color=COLORS[1], alpha=.075)
    ax.axvspan(3.55, 4.45, color=COLORS[1], alpha=.075)
    ax.bar(n-.18, causal, width=.35, color=COLORS[0], label='From x')
    ax.bar(n+.18, causal_p, width=.35, color=COLORS[1], label='From x + 5')
    for pos, value in [(-.18, 1), (.18, 6), (3.82, 0), (4.18, -5)]:
        ax.text(pos, value+(.22 if value >= 0 else -.22), str(value),
                ha='center', va='bottom' if value >= 0 else 'top', fontsize=11)
    ax.axhline(0, color=MUTED, lw=.8); ax.grid(axis='y')
    ax.set(xticks=n, xticklabels=['0', '1', '2', '3', 'flush'],
           xlabel='Causal output index / final zero flush', ylabel='Difference',
           ylim=(-6.5, 8), title='Zero extension retains the boundary')
    ax.title.set_fontsize(13)
    ax.legend(loc='upper right', fontsize=10)
    stem = 'O03_boundary_inversion'; save_figure(fig, stem); stems.append(stem)
    causal_cases = periodic_cases = 0
    for values in product(range(-2, 3), repeat=4):
        y = periodic_difference(values)
        assert sum(y) == 0
        assert periodic_recover(y, values[0]) == list(values)
        assert (y == [0]*4) == (len(set(values)) == 1)
        for constant in (-5, 0, 5):
            translated = [v+constant for v in values]
            assert periodic_difference(translated) == y
            flushed = causal_difference_flushed(translated)
            assert partial_sums(flushed) == translated+[0]
            causal_cases += 1
        periodic_cases += 1
    output_cases = compatible_cases = 0
    for values in product(range(-2, 3), repeat=4):
        reconstructed = periodic_recover(values, Q(1, 3))
        assert (reconstructed is not None) == (sum(values) == 0)
        if reconstructed is not None:
            assert periodic_difference(reconstructed) == list(values)
            compatible_cases += 1
        output_cases += 1
    checks['O03'] = {
        'input_x':x, 'input_x_plus5':xp,
        'periodic_output':periodic, 'causal_output_full_flush':causal,
        'causal_shifted_output_full_flush':causal_p,
        'periodic_recovery_fixed_x0_1':periodic_recover(periodic, 1),
        'periodic_recovery_fixed_x0_6':periodic_recover(periodic, 6),
        'incompatible_example':[1, 0, 0, 0],
        'causal_contract':'Four stored values; all other inputs zero; one zero flush.',
        'periodic_contract':'Four stored values repeated with period four.',
        'input_component_range':[-2, 2], 'dimension':4,
        'periodic_input_cases':periodic_cases,
        'constant_shifts_checked':[-5, 0, 5], 'causal_inverse_cases':causal_cases,
        'output_component_range':[-2, 2], 'output_solvability_cases':output_cases,
        'compatible_outputs':compatible_cases,
        'recovery_value_for_solvability_cases':'1/3',
        'universal_reduction':'Telescoping gives zero sum; cumulative sums solve every compatible cycle with a prescribed x0; equal differences force a constant.'}

    for item in input_hashes:
        assert sha(ROOT/item['path']) == item['sha256'], 'An execution input changed during the run.'
    artifacts = []
    for stem in stems:
        for suffix in ('pdf', 'png'):
            p = FIGURES/(stem+'.'+suffix)
            artifacts.append({'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size,
                              'sha256':sha(p)})
    software = {'python':platform.python_version(), 'numpy':np.__version__,
                'matplotlib':matplotlib.__version__}
    nonclaims = ['Bounded coefficient checks do not by themselves prove universal operator identities.',
                 'O02 proves a specific degree-four polynomial identity, not a new general Bernoulli theorem.',
                 'O01 finite prefixes are not finite input supports; no omitted-tail interpretation is made.',
                 'O03 does not assert that every finitely supported output has a finitely supported causal inverse.',
                 'Matplotlib floating-point coordinates only render exact recorded data.']
    elapsed = round(time.monotonic()-start, 4)
    data = {
        'schema':'komorebi-operator-contracts-v1', 'status':'PASS',
        'command':[sys.executable, str(Path(__file__).resolve())],
        'inputs':input_hashes, 'inputs_unchanged_during_execution':True,
        'software':software, 'elapsed_seconds':elapsed, 'checks':checks,
        'artifacts':artifacts, 'nonclaims':nonclaims,
        'resource_caps':{'OPENBLAS_NUM_THREADS':os.environ.get('OPENBLAS_NUM_THREADS'),
                         'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS'),
                         'caps_are_cooperative':True, 'hard_memory_or_cpu_cap':'none'},
        'visual_review':'evidence/operator_author_review.md'}
    data['computation_manifest'] = {
        'schema_version':1, 'claim_id':'three-operator-contract-worked-examples',
        'repository':{'commit':None, 'dirty':True}, 'command':data['command'],
        'environment':{'software':[{'name':k, 'version':v} for k, v in software.items()],
                       'hardware':platform.machine()+' / '+platform.system(),
                       'cooperative_thread_caps':data['resource_caps']},
        'mathematics':{
            'assertion_tested':'The displayed three worked examples, both normalization directions, complete degree-four polynomial coefficients, and bounded boundary contracts agree exactly.',
            'coefficient_domain':'Q for all exact checks; O01 also permits R/C, and O03 permits R.',
            'conventions':'Ascending coefficients; negative FIR indices zero; N is factorial normalization; finite-support causal and periodic domains explicitly distinguished.',
            'inputs':input_hashes,
            'bounds':{'O01_extra_indices':[0, 23], 'O01_extra_families':4,
                      'O01_extra_tap_lists':4, 'O02_complete_polynomial_degree':4,
                      'O02_integer_endpoints':[0, 50], 'O03_dimension':4,
                      'O03_component_range':[-2, 2], 'O03_shifts':[-5, 0, 5]},
            'non_claims':nonclaims},
        'randomness':{'used':False, 'generator':'none', 'seed':None},
        'run':{'started_at':started_at, 'runtime_seconds':elapsed, 'exit_status':0},
        'outputs':[{'path':i['path'], 'sha256':i['sha256']} for i in artifacts],
        'checks':[{'plate':name, 'status':'PASS', 'evidence':record}
                  for name, record in checks.items()],
        'result':'Implementation and finite contracts verified exactly in the declared ranges.',
        'residual_risks':['No git revision identifies the artifact; input and output hashes identify this run.',
                          'Version-1 provenance limitations remain.',
                          'Final assembled-page layout inspection remains an integration step.']}
    out = ROOT/'evidence'/'operator_checks.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps({'status':'PASS', 'plates':len(stems), 'artifacts':len(artifacts),
                      'elapsed_seconds':elapsed, 'evidence':str(out)}))


if __name__ == '__main__':
    main()
