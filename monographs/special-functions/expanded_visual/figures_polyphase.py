"""Sixteen worked polyphase plates with exact, bounded coefficient checks.

Run: python figures_polyphase.py
Arithmetic: Python integers and fractions.Fraction; float coordinates only render
the exact examples. No sampled output is treated as a universal proof.
"""
from fractions import Fraction as Q
from datetime import datetime, timezone
from math import factorial, sqrt
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


def fib(count):
    result = [0, 1]
    while len(result) < count:
        result.append(result[-1] + result[-2])
    return result[:count]


def add(a, b):
    return [sum(v[i] if i < len(v) else 0 for v in (a, b))
            for i in range(max(len(a), len(b)))]


def mul(a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i+j] += ai * bj
    return out


def div_series(a, b, count):
    """Exact formal quotient of prefixes, assuming b[0] != 0."""
    result = []
    for n in range(count):
        an = a[n] if n < len(a) else Q(0)
        correction = sum(b[j] * result[n-j]
                         for j in range(1, min(n, len(b)-1)+1))
        result.append((an-correction) / b[0])
    return result


def split(a, modulus):
    return [a[r::modulus] for r in range(modulus)]


def synth(channels):
    modulus = len(channels)
    length = max((modulus*(len(row)-1)+r+1
                  for r, row in enumerate(channels) if row), default=0)
    result = [0] * length
    for r, row in enumerate(channels):
        for m, v in enumerate(row):
            result[modulus*m+r] = v
    return result


def carry(channels):
    return [[0] + channels[-1]] + channels[:-1]


def equal_zero_padded(a, b):
    length = max(len(a), len(b))
    return all((a[i] if i < len(a) else 0) ==
               (b[i] if i < len(b) else 0) for i in range(length))


def product_channels(f, g):
    modulus = len(f)
    h = [[] for _ in f]
    for r, fr in enumerate(f):
        for s, gs in enumerate(g):
            contribution = mul(fr, gs)
            if r+s >= modulus:
                contribution = [0] + contribution
            h[(r+s) % modulus] = add(h[(r+s) % modulus], contribution)
    return h


def matrix_mul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def matrix_pow(a, power):
    result = [[1, 0], [0, 1]]
    for _ in range(power):
        result = matrix_mul(result, a)
    return result


def box(ax, x, y, label, w=1.5, h=.5, color=PALE, fontsize=13,
        edge=None):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle='round,pad=.04', edgecolor=edge or COLORS[0],
                 facecolor=color, linewidth=1.2))
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=INK)


def arrow(ax, a, b, color=COLORS[0], label=None, offset=(0, .13)):
    ax.annotate('', xy=b, xytext=a,
                arrowprops={'arrowstyle':'->', 'color':color, 'lw':1.8})
    if label:
        ax.text((a[0]+b[0])/2+offset[0], (a[1]+b[1])/2+offset[1],
                label, ha='center', va='center', fontsize=12, color=color)


def plain_ax(title, figsize=(8.1, 4.2)):
    fig, ax = plt.subplots(figsize=figsize, layout='constrained')
    ax.set_title(title, pad=14)
    ax.axis('off')
    return fig, ax


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    checks = {}
    stems = []
    values = fib(200)

    # P01: values and their original indices are distinct pieces of metadata.
    fig, ax = plain_ax('Fibonacci values routed by n = 3m + r')
    for r in range(3):
        ax.text(-.63, 2-r, f'r = {r}', ha='right', va='center',
                color=COLORS[r], fontsize=14)
        for m in range(6):
            n = 3*m+r
            box(ax, m, 2-r, str(values[n]), w=.75, h=.62,
                color=matplotlib.colors.to_rgba(COLORS[r], .10),
                edge=COLORS[r], fontsize=17)
            ax.text(m, 2-r-.45, f'n = {n}', ha='center', va='center',
                    fontsize=10, color=MUTED)
    for m in range(6):
        ax.text(m, 2.8, f'm = {m}', ha='center', fontsize=12)
    ax.set(xlim=(-1.2, 5.6), ylim=(-.8, 3.1))
    stem = 'P01_fibonacci_streams'; save_figure(fig, stem); stems.append(stem)
    first18 = values[:18]
    assert synth(split(first18, 3)) == first18
    checks['P01'] = {'original_indices':list(range(18)),
                     'channels':split(first18, 3), 'exact_reconstruction':True}

    # P02: show actual interleaving, not simply an exponent-address diagram.
    fig, axs = plt.subplots(2, 1, figsize=(8.1, 4.2), layout='constrained',
                            gridspec_kw={'height_ratios':[1.35, 1]})
    top, bottom = axs
    top.set_title('Read horizontally inside a channel; interleave below')
    for r in range(3):
        top.text(-.85, 2-r, f'Channel {r}', ha='right', va='center',
                 color=COLORS[r], fontsize=12)
        for m in range(4):
            box(top, m*1.5, 2-r, str(values[3*m+r]), w=.82, h=.54,
                color=matplotlib.colors.to_rgba(COLORS[r], .1),
                edge=COLORS[r], fontsize=15)
    top.set(xlim=(-2.1, 5.4), ylim=(-.6, 2.75)); top.axis('off')
    for n, v in enumerate(values[:12]):
        box(bottom, n, .4, str(v), w=.75, h=.58,
            color=matplotlib.colors.to_rgba(COLORS[n%3], .1),
            edge=COLORS[n%3], fontsize=14)
        bottom.text(n, -.18, str(n), ha='center', fontsize=10, color=MUTED)
    bottom.text(5.5, - .55, 'Original index n:  0 → 1 → 2 → 3 → … → 11',
                ha='center', fontsize=12)
    bottom.set(xlim=(-.6, 11.6), ylim=(-.8, 1.15)); bottom.axis('off')
    stem = 'P02_interleave'; save_figure(fig, stem); stems.append(stem)
    assert synth(split(values[:12], 3)) == values[:12]
    checks['P02'] = {'input_channels':split(values[:12], 3),
                     'output':values[:12], 'support':[0, 11]}

    # P03: column-state convention is explicit: [F_(2m), F_(2m+1)]^T.
    B = [[1, 1], [1, 2]]
    fig, ax = plain_ax('One block step advances two Fibonacci indices')
    for m in range(5):
        x = 1.65*m
        box(ax, x, 1.7, f'{values[2*m]}\n{values[2*m+1]}',
            w=1.04, h=1.03, fontsize=18)
        ax.text(x, .8, f'm = {m}', ha='center', fontsize=12, color=MUTED)
        if m < 4:
            arrow(ax, (x+.58, 1.7), (x+1.07, 1.7), label='B', offset=(0, .33))
    ax.text(3.3, -.03, r'$B:(x,y)\mapsto(x+y,\ x+2y)$',
            ha='center', fontsize=19)
    ax.text(-.82, 1.96, 'Even', fontsize=12, ha='right', color=COLORS[0])
    ax.text(-.82, 1.43, 'Odd', fontsize=12, ha='right', color=COLORS[1])
    ax.set(xlim=(-1.55, 7.35), ylim=(-.7, 2.85))
    stem = 'P03_fibonacci_block'; save_figure(fig, stem); stems.append(stem)
    for m in range(30):
        x = [[values[2*m]], [values[2*m+1]]]
        assert matrix_mul(B, x) == [[values[2*m+2]], [values[2*m+3]]]
    denominator = [Q(1), Q(-3), Q(1)]
    E = div_series([Q(0), Q(1)], denominator, 30)
    O = div_series([Q(1), Q(-1)], denominator, 30)
    assert E == list(map(Q, values[:60:2]))
    assert O == list(map(Q, values[1:60:2]))
    checks['P03'] = {'block_matrix':B, 'states_checked':30,
                     'series_coefficients_checked_per_channel':30,
                     'even_first6':list(map(str, E[:6])),
                     'odd_first6':list(map(str, O[:6]))}

    # P04: arbitrary stride claim has a separate Cayley-Hamilton derivation.
    # The table uses starting offset 1; at M=1 it is not the canonical residue.
    T = [[0, 1], [1, 1]]
    rows = []
    for M in range(1, 7):
        TM = matrix_pow(T, M)
        trace = TM[0][0]+TM[1][1]
        det = TM[0][0]*TM[1][1]-TM[0][1]*TM[1][0]
        rows.append([M, trace, det, values[1], values[M+1], values[2*M+1]])
    fig, ax = plain_ax('Fibonacci jump data: choose stride M, then initial values')
    labels = ['Stride M', 'Trace L(M)', 'Determinant', 'g(0) = F(1)',
              'g(1) = F(M+1)', 'g(2) = F(2M+1)']
    table = ax.table(cellText=rows, colLabels=labels, cellLoc='center',
                     loc='center', bbox=[0, .04, 1, .86])
    table.auto_set_font_size(False); table.set_fontsize(11)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('#D1DCDF')
        cell.set_facecolor(PALE if i == 0 else 'white')
        if i > 0 and j == 2:
            cell.get_text().set_color(COLORS[1] if rows[i-1][2] == -1 else COLORS[0])
    stem = 'P04_jump_recurrences'; save_figure(fig, stem); stems.append(stem)
    stride_cases = 0
    for M in range(1, 11):
        TM = matrix_pow(T, M)
        L = TM[0][0]+TM[1][1]
        det = (-1)**M
        assert TM[0][0]*TM[1][1]-TM[0][1]*TM[1][0] == det
        for r in range(M):
            for m in range(10):
                assert values[M*(m+2)+r] == L*values[M*(m+1)+r]-det*values[M*m+r]
                stride_cases += 1
    checks['P04'] = {'table':rows, 'table_starting_offset':1, 'stride_range':[1, 10],
                     'all_residues_checked':True, 'internal_indices_m':[0, 9],
                     'exact_recurrence_instances':stride_cases}

    # P05: roots are drawn numerically, but cancellation is exact cyclotomic arithmetic.
    powers = [(1, 0), (0, 1), (-1, -1)]  # 1, zeta, zeta^2 in Q[zeta].
    mask = []
    for r in range(3):
        row = []
        for n in range(12):
            total = tuple(sum(powers[((n-r)*j)%3][k] for j in range(3))
                          for k in range(2))
            expected = (3, 0) if n%3 == r else (0, 0)
            assert total == expected
            row.append(int(total == (3, 0)))
        mask.append(row)
    fig, axs = plt.subplots(1, 2, figsize=(8.1, 4.2), layout='constrained',
                            gridspec_kw={'width_ratios':[1, 1.75]})
    roots = np.exp(2j*np.pi*np.arange(3)/3)
    ax = axs[0]
    circle = np.linspace(0, 2*np.pi, 200)
    ax.plot(np.cos(circle), np.sin(circle), color=MUTED, alpha=.35, lw=1)
    for j, root in enumerate(roots):
        ax.plot([0, root.real], [0, root.imag], color=COLORS[j], alpha=.5)
        ax.scatter(root.real, root.imag, color=COLORS[j], s=75)
    ax.text(1.1, 0, '1', va='center', fontsize=14)
    ax.text(-.63, 1.02, r'$\zeta$', ha='center', fontsize=17)
    ax.text(-.98, -1.12, r'$\zeta^2$', ha='center', va='center', fontsize=17)
    ax.axhline(0, color=MUTED, lw=.7); ax.axvline(0, color=MUTED, lw=.7)
    ax.set(aspect='equal', xlim=(-1.3, 1.45), ylim=(-1.3, 1.3),
           xlabel='Real part', ylabel='Imaginary part', title='Three exact phases')
    ax.set_xticks([]); ax.set_yticks([])
    ax = axs[1]
    for r in range(3):
        for n in range(12):
            ax.scatter(n, r, marker='s', s=250,
                       color=COLORS[r] if mask[r][n] else '#F1F4F5')
            if mask[r][n]:
                ax.text(n, r, str(values[n]), ha='center', va='center',
                        color='white', fontsize=8.5)
    ax.set(xlim=(-.7, 11.7), ylim=(2.6, -.6), xticks=range(12),
           yticks=range(3), xlabel='Original exponent n',
           ylabel='Retained residue r', title='Only matching residues survive')
    ax.set_xticklabels([str(n) for n in range(12)], fontsize=9)
    stem = 'P05_root_selector'; save_figure(fig, stem); stems.append(stem)
    checks['P05'] = {'modulus':3, 'indices_checked':[0, 11],
                     'residues_checked':[0, 1, 2], 'mask':mask,
                     'exact_domain':'Q[zeta]/(zeta^2+zeta+1)',
                     'float_use':'root-plane positions only'}

    # P06: show each parent-child row with actual coefficients and original indices.
    fig, ax = plain_ax('Refine modulus 2 by 3: each child retains real coefficients')
    ordered = [0, 2, 4, 1, 3, 5]
    rows = []
    for i, r6 in enumerate(ordered):
        r = r6%2; ell = r6//2; y = 5-i
        label = 'Even parent' if r == 0 else 'Odd parent'
        ax.text(-.35, y, label, color=COLORS[r], ha='right', va='center', fontsize=12)
        box(ax, 1.15, y, f'ell = {ell}  →  child {r6}', w=2.15, h=.56,
            edge=COLORS[r], color=matplotlib.colors.to_rgba(COLORS[r], .09), fontsize=12)
        for j in range(3):
            n = 6*j+r6
            x = 3.35+1.18*j
            ax.text(x, y+.10, str(values[n]), fontsize=16, ha='center', va='center')
            ax.text(x, y-.23, f'n = {n}', color=MUTED, fontsize=9, ha='center')
        rows.append({'parent_residue':r, 'child_internal_residue':ell,
                     'child_address':r6, 'coefficients':values[r6:18:6]})
    for j in range(3):
        ax.text(3.35+1.18*j, 5.7, f'j = {j}', ha='center', fontsize=12)
    ax.set(xlim=(-2, 6.5), ylim=(-.6, 6.1))
    stem = 'P06_refined_coefficients'; save_figure(fig, stem); stems.append(stem)
    for r in range(2):
        parent = values[r:18:2]
        refined = split(parent, 3)
        assert refined == [values[r+2*ell:18:6] for ell in range(3)]
        assert synth(refined) == parent
    checks['P06'] = {'rows':rows, 'original_support':[0, 17],
                     'exact_parent_reconstruction':True}

    # P07: two different index decompositions, same final coefficient address.
    fig, ax = plain_ax('Two refinement orders meet at the same modulus-6 state')
    box(ax, 3.5, 3.25, 'Original n = 17:  F(17) = 1597', w=3.55, h=.47, fontsize=13)
    box(ax, 1.3, 2.23, 'Mod 2:  r = 1,  m = 8', w=2.7, h=.5, edge=COLORS[0])
    box(ax, 5.7, 2.23, 'Mod 3:  r = 2,  m = 5', w=2.7, h=.5, edge=COLORS[1])
    arrow(ax, (2.6, 2.96), (1.5, 2.55)); arrow(ax, (4.4, 2.96), (5.5, 2.55), color=COLORS[1])
    box(ax, 1.3, 1.18, '8 = 3 × 2 + 2\nchild = 1 + 2 × 2 = 5', w=2.8, h=.64,
        edge=COLORS[0], fontsize=12)
    box(ax, 5.7, 1.18, '5 = 2 × 2 + 1\nchild = 2 + 3 × 1 = 5', w=2.8, h=.64,
        edge=COLORS[1], fontsize=12)
    arrow(ax, (1.3, 1.93), (1.3, 1.58)); arrow(ax, (5.7, 1.93), (5.7, 1.58), color=COLORS[1])
    box(ax, 3.5, .12, 'Mod 6:  r = 5,  j = 2,  coefficient = 1597', w=4.75, h=.53)
    arrow(ax, (1.6, .80), (2.4, .44)); arrow(ax, (5.4, .80), (4.6, .44), color=COLORS[1])
    ax.set(xlim=(-.35, 7.35), ylim=(-.45, 3.9))
    stem = 'P07_refinement_routes'; save_figure(fig, stem); stems.append(stem)
    routes = []
    for n in range(18):
        r2, m2 = n%2, n//2
        ell3, j23 = m2%3, m2//3
        r3, m3 = n%3, n//3
        ell2, j32 = m3%2, m3//2
        assert (r2+2*ell3, j23) == (r3+3*ell2, j32) == (n%6, n//6)
        routes.append([n, n%6, n//6, values[n]])
    checks['P07'] = {'indices_checked':[0, 17], 'route_results':routes,
                     'highlight':[17, 5, 2, 1597]}

    # P08: carry action on a real finite Fibonacci prefix, all boundary terms retained.
    poly = values[:6]
    states = [split(poly, 3)]
    for _ in range(3):
        states.append(carry(states[-1]))
    displays = [[r'$2u$', r'$u+5u^2$', r'$u+3u^2$', r'$2u^2$'],
                [r'$1+3u$', r'$2u$', r'$u+5u^2$', r'$u+3u^2$'],
                [r'$1+5u$', r'$1+3u$', r'$2u$', r'$u+5u^2$']]
    fig, ax = plain_ax('Multiplication by z: after three steps every row has one delay')
    for k in range(4):
        ax.text(1.65*k, 2.95, '1 carry' if k == 1 else f'{k} carries', ha='center', fontsize=13)
        for r in range(3):
            box(ax, 1.65*k, 2-r, displays[r][k], w=1.38, h=.67,
                edge=COLORS[r], color=matplotlib.colors.to_rgba(COLORS[r], .08),
                fontsize=15)
    for r in range(3):
        ax.text(-.95, 2-r, f'r = {r}', ha='right', va='center', fontsize=12, color=COLORS[r])
    ax.text(2.48, -.66, 'The last column is u times the first column.', ha='center', fontsize=13)
    ax.set(xlim=(-1.65, 5.95), ylim=(-.95, 3.5))
    stem = 'P08_three_carries'; save_figure(fig, stem); stems.append(stem)
    for k, state in enumerate(states):
        assert equal_zero_padded(synth(state), [0]*k+poly)
    checks['P08'] = {'input_coefficients':poly, 'channel_states':states,
                     'steps':[0, 1, 2, 3], 'full_support_retained':True}

    # P09: all nine cross products, including carries, are visible.
    f = [1, 2, 3]; g = [4, 5, 6]; output = mul(f, g)
    h = product_channels(split(f, 3), split(g, 3))
    assert synth(h) == output
    fig, ax = plain_ax('Nine residue products collect into three output channels')
    for r in range(3):
        ax.text(-.94, 2-r, f'f[{r}] = {f[r]}', ha='right', va='center', fontsize=12)
        for s in range(3):
            t = (r+s)%3; wrap = r+s >= 3
            product = f[r]*g[s]
            text = f'{product}' + ('u' if wrap else '') + f'  →  h[{t}]'
            box(ax, 1.65*s, 2-r, text, w=1.4, h=.65,
                color=matplotlib.colors.to_rgba(COLORS[t], .09),
                edge=COLORS[t], fontsize=13)
    for s in range(3):
        ax.text(1.65*s, 2.75, f'g[{s}] = {g[s]}', ha='center', fontsize=12)
    for t, label in enumerate([r'$h_0=4+27u$', r'$h_1=13+18u$', r'$h_2=28$']):
        ax.text(1.65*t, -.85, label, ha='center', fontsize=16, color=COLORS[t])
    ax.set(xlim=(-2.0, 4.4), ylim=(-1.2, 3.3))
    stem = 'P09_product_carries'; save_figure(fig, stem); stems.append(stem)
    case_count = 0
    for M in range(2, 7):
        for N in range(1, 9):
            left = values[:N]
            right = [(-1)**n*(n+1) for n in range(N+1)]
            assert equal_zero_padded(synth(product_channels(split(left, M), split(right, M))),
                                     mul(left, right))
            case_count += 1
    checks['P09'] = {'input_f':f, 'input_g':g, 'product':output,
                     'product_channels':h, 'additional_exact_cases':case_count,
                     'moduli':[2, 6], 'left_lengths':[1, 8],
                     'right_lengths':[2, 9]}

    # P10: raw values versus ORIGINAL-index factorial normalization.
    fig, ax = plain_ax('One sequence, two coefficient conventions')
    rows = [[n, values[n], str(Q(values[n], factorial(n))),
             f'{n%2} / m={n//2}'] for n in range(8)]
    table = ax.table(cellText=rows,
                     colLabels=['Original n', 'OGF coefficient F(n)',
                                'EGF coefficient F(n)/n!', 'Residue / index'],
                     cellLoc='center', loc='center', bbox=[0, .02, 1, .9])
    table.auto_set_font_size(False); table.set_fontsize(13)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('#D1DCDF')
        if i == 0:
            cell.set_facecolor(PALE); cell.get_text().set_fontsize(11)
        else:
            cell.set_facecolor(matplotlib.colors.to_rgba(COLORS[(i-1)%2], .06))
    stem = 'P10_ogf_egf'; save_figure(fig, stem); stems.append(stem)
    normalized = [Q(v, factorial(n)) for n, v in enumerate(values[:14])]
    assert synth(split(normalized, 2)) == normalized
    assert normalized[6] == Q(1, 90) != Q(values[6], factorial(3))
    checks['P10'] = {'raw_values':values[:14],
                     'egf_coefficients':list(map(str, normalized)),
                     'normalization':'a[n]/n!, not a[M*m+r]/m!',
                     'exact_reconstruction':True}

    # P11: derive secant and tangent coefficients by exact formal division.
    count = 12
    cos = [Q(0)]*count; sin = [Q(0)]*count
    for n in range(count):
        if n%2 == 0:
            cos[n] = Q((-1)**(n//2), factorial(n))
        else:
            sin[n] = Q((-1)**((n-1)//2), factorial(n))
    sec = div_series([Q(1)], cos, count)
    tan = div_series(sin, cos, count)
    A = [(sec[n]+tan[n])*factorial(n) for n in range(count)]
    expected = [1, 1, 1, 2, 5, 16, 61, 272, 1385, 7936, 50521, 353792]
    assert A == list(map(Q, expected))
    assert all(sec[n] == 0 for n in range(1, count, 2))
    assert all(tan[n] == 0 for n in range(0, count, 2))
    fig, ax = plain_ax('Up/down counts separate into secant and tangent parity rows')
    for m in range(5):
        ax.text(m*1.3, 2.45, f'm = {m}', ha='center', fontsize=12)
        for r, y in [(0, 1.55), (1, .1)]:
            n = 2*m+r
            box(ax, m*1.3, y, str(expected[n]), w=.96, h=.64,
                edge=COLORS[r], color=matplotlib.colors.to_rgba(COLORS[r], .10),
                fontsize=17)
            ax.text(m*1.3, y-.64, f'divide by {n}!', fontsize=11, ha='center', color=MUTED)
    ax.text(-.9, 1.55, 'Secant\neven n', ha='right', va='center', fontsize=13, color=COLORS[0])
    ax.text(-.9, .1, 'Tangent\nodd n', ha='right', va='center', fontsize=13, color=COLORS[1])
    ax.set(xlim=(-2, 6), ylim=(-1.0, 3.05))
    stem = 'P11_secant_tangent'; save_figure(fig, stem); stems.append(stem)
    checks['P11'] = {'counts':expected, 'original_exponents':[0, 11],
                     'independent_construction':'formal 1/cos(z) and sin(z)/cos(z) over Q',
                     'secant_coefficients':list(map(str, sec)),
                     'tangent_coefficients':list(map(str, tan)),
                     'tangent_native_oeis_index':'n=m+1; exponent 2m+1'}

    # P12: each parent bit and its two children are aligned vertically.
    bits = [n.bit_count()%2 for n in range(256)]
    fig, ax = plain_ax('Thue–Morse: even children copy; odd children complement')
    for m in range(8):
        x = m
        box(ax, x, 2.1, str(bits[m]), w=.59, h=.57, fontsize=17)
        box(ax, x, .9, str(bits[2*m]), w=.59, h=.57,
            edge=COLORS[0], color=matplotlib.colors.to_rgba(COLORS[0], .1), fontsize=17)
        box(ax, x, -.3, str(bits[2*m+1]), w=.59, h=.57,
            edge=COLORS[1], color=matplotlib.colors.to_rgba(COLORS[1], .1), fontsize=17)
        ax.text(x, 2.8, f'm={m}', ha='center', fontsize=10)
    ax.text(-.7, 2.1, 'Parent t(m)', ha='right', va='center', fontsize=12)
    ax.text(-.7, .9, 't(2m)', ha='right', va='center', fontsize=12, color=COLORS[0])
    ax.text(-.7, -.3, 't(2m+1)', ha='right', va='center', fontsize=12, color=COLORS[1])
    ax.text(3.5, -1.08, 'Interleave the child rows to recover indices 0 through 15.',
            ha='center', fontsize=12)
    ax.set(xlim=(-2.5, 7.65), ylim=(-1.4, 3.35))
    stem = 'P12_thue_morse'; save_figure(fig, stem); stems.append(stem)
    for m in range(128):
        assert bits[2*m] == bits[m]
        assert bits[2*m+1] == 1-bits[m]
    rhs = [0]*256
    for m in range(128):
        rhs[2*m] += bits[m]
        rhs[2*m+1] += 1-bits[m]
    assert rhs == bits
    checks['P12'] = {'prefix':bits[:16], 'checked_original_indices':[0, 255],
                     'parent_indices':[0, 127], 'both_refinements_exact':True,
                     'generating_identity_coefficients_checked':256}

    # P13: retain integer weights rather than silently changing to parity.
    weights = [n.bit_count() for n in range(256)]
    fig, axs = plt.subplots(1, 2, figsize=(8.1, 4.2), layout='constrained')
    m = np.arange(8)
    axs[0].bar(m, weights[:8], color=COLORS[0], width=.7)
    axs[0].set(xticks=m, xlabel='Parent m', ylabel='Binary digit sum',
               title='Parent weights s₂(m)', ylim=(0, 4.6))
    even = weights[:16:2]; odd = weights[1:16:2]
    axs[1].bar(m-.18, even, width=.35, color=COLORS[0], label='Even child')
    axs[1].bar(m+.18, odd, width=.35, color=COLORS[1], label='Odd child')
    axs[1].set(xticks=m, xlabel='Parent m', ylabel='Child digit sum',
               title='Odd children add one', ylim=(0, 4.6))
    axs[1].legend(loc='upper left', fontsize=10)
    for i in range(8):
        axs[0].text(i, weights[i]+.08, str(weights[i]), ha='center', fontsize=11)
    for ax in axs:
        ax.set_yticks(range(5)); ax.grid(axis='y')
    stem = 'P13_binary_weight'; save_figure(fig, stem); stems.append(stem)
    for m in range(128):
        assert weights[2*m] == weights[m]
        assert weights[2*m+1] == weights[m]+1
        assert matrix_mul([[1, 1], [0, 1]], [[weights[m]], [1]]) == [[weights[2*m+1]], [1]]
    assert [w%2 for w in weights] == bits
    checks['P13'] = {'prefix':weights[:16], 'checked_original_indices':[0, 255],
                     'parent_indices':[0, 127], 'odd_augmented_matrix':[[1, 1], [0, 1]],
                     'parity_matches_thue_morse':True}

    # P14: represent each transformed amplitude as rational q times sqrt(2).
    x = [1, 3, 2, 0]
    a_q = [Q(x[2*m]+x[2*m+1], 2) for m in range(2)]
    d_q = [Q(x[2*m]-x[2*m+1], 2) for m in range(2)]
    energy_a = sum(2*q*q for q in a_q)
    energy_d = sum(2*q*q for q in d_q)
    assert energy_a+energy_d == sum(v*v for v in x) == 14
    inverse = []
    for aq, dq in zip(a_q, d_q):
        inverse.extend([aq+dq, aq-dq])
    assert inverse == list(map(Q, x))
    fig, axs = plt.subplots(1, 2, figsize=(8.1, 4.2), layout='constrained')
    axs[0].bar(range(4), x, color=[COLORS[0], COLORS[0], COLORS[1], COLORS[1]], width=.65)
    axs[0].set(xticks=range(4), xlabel='Original sample index', ylabel='Amplitude',
               title='Input energy = 14', ylim=(-2, 4))
    for n, v in enumerate(x):
        axs[0].text(n, v+.15, str(v), ha='center', fontsize=14)
    pair = np.arange(2)
    means = [float(q)*sqrt(2) for q in a_q]
    details = [float(q)*sqrt(2) for q in d_q]
    axs[1].bar(pair-.18, means, width=.34, label='Average', color=COLORS[0])
    axs[1].bar(pair+.18, details, width=.34, label='Detail', color=COLORS[1])
    labels = [(0-.18, means[0], r'$2\sqrt{2}$'), (0+.18, details[0], r'$-\sqrt{2}$'),
              (1-.18, means[1], r'$\sqrt{2}$'), (1+.18, details[1], r'$\sqrt{2}$')]
    for px, py, label in labels:
        axs[1].text(px, py+(.15 if py >= 0 else -.15), label, ha='center',
                    va='bottom' if py >= 0 else 'top', fontsize=13)
    axs[1].axhline(0, color=MUTED, lw=.8)
    axs[1].set(xticks=pair, xticklabels=['Pair (1, 3)', 'Pair (2, 0)'],
               ylabel='Normalized amplitude', title='Average energy 10 + detail energy 4',
               ylim=(-2, 4))
    axs[1].legend(loc='upper right', fontsize=10)
    for ax in axs:
        ax.grid(axis='y')
    stem = 'P14_haar_bank'; save_figure(fig, stem); stems.append(stem)
    checks['P14'] = {'input':x, 'average_q_times_sqrt2':list(map(str, a_q)),
                     'detail_q_times_sqrt2':list(map(str, d_q)),
                     'average_energy':str(energy_a), 'detail_energy':str(energy_d),
                     'total_energy':14, 'exact_inverse':list(map(str, inverse)),
                     'float_use':'plot positions of exact algebraic amplitudes'}

    # P15: explicit kernel element proves a real loss, rather than a visual impression.
    A = [1, 2, 3, 4]; Bp = [1, 9, 3, -7]
    assert A[::2] == Bp[::2] and A[1::2] != Bp[1::2]
    fig, axs = plt.subplots(1, 2, figsize=(8.1, 4.2), layout='constrained')
    axs[0].plot(range(4), A, marker='o', label='Input A')
    axs[0].plot(range(4), Bp, marker='s', ls='--', label='Input B')
    axs[0].set(xticks=range(4), xlabel='Original exponent n', ylabel='Coefficient',
               title='Distinct inputs differ in odd positions', ylim=(-9, 11))
    axs[0].legend(loc='lower left'); axs[0].grid()
    axs[1].plot(range(2), A[::2], marker='o', ms=11, label='Retained from A')
    axs[1].plot(range(2), Bp[::2], marker='s', ls='--', ms=5, label='Retained from B')
    axs[1].set(xticks=range(2), xlabel='Even-channel index m', ylabel='Coefficient',
               title='Same output: 1 + 3u', ylim=(0, 4.4))
    axs[1].legend(loc='upper left', fontsize=10); axs[1].grid()
    axs[1].text(.5, .30, 'Discarded odds:\nA: 2, 4     B: 9, −7',
                ha='center', fontsize=12,
                bbox={'boxstyle':'round,pad=.4','facecolor':PALE,'edgecolor':'#D1DCDF'})
    stem = 'P15_discarded_channel'; save_figure(fig, stem); stems.append(stem)
    checks['P15'] = {'input_A':A, 'input_B':Bp, 'same_even_channel':A[::2],
                     'odd_A':A[1::2], 'odd_B':Bp[1::2],
                     'B_minus_A':[b-a for a, b in zip(A, Bp)],
                     'counterexample_proves_noninjectivity':True}

    # P16: a complete finite operation square, including the seventh output coefficient.
    P = values[:6]; bank = split(P, 2)
    Qp = mul([1, 1], P)
    out_bank = [add(bank[0], [0]+bank[1]), add(bank[0], bank[1])]
    assert synth(out_bank) == Qp == [0, 1, 2, 3, 5, 8, 5]
    fig, ax = plain_ax('A full finite operation agrees before or after channel splitting')
    box(ax, 1.65, 2.72, '$P=z+z^2+2z^3$\n$+3z^4+5z^5$', w=3.02, h=.86, fontsize=14)
    box(ax, 6.05, 2.72, '$E=u+3u^2$\n$O=1+2u+5u^2$', w=3.0, h=.86, fontsize=14)
    box(ax, 1.65, .47, '$Q=z+2z^2+3z^3$\n$+5z^4+8z^5+5z^6$', w=3.02, h=.92, fontsize=14)
    box(ax, 6.05, .47, "$E'=2u+5u^2+5u^3$\n$O'=1+3u+8u^2$", w=3.0, h=.92, fontsize=14)
    arrow(ax, (3.25, 2.72), (4.46, 2.72), label='Split', offset=(0, .26))
    arrow(ax, (3.25, .47), (4.46, .47), label='Split', offset=(0, .28))
    arrow(ax, (1.65, 2.18), (1.65, 1.06))
    ax.text(.33, 1.64, r'$\times(1+z)$', ha='left', fontsize=14)
    arrow(ax, (6.05, 2.18), (6.05, 1.06))
    ax.text(6.28, 1.65, "$E'=E+uO$\n$O'=E+O$",
            ha='left', va='center', fontsize=14)
    ax.set(xlim=(-.15, 7.85), ylim=(-.2, 3.5))
    stem = 'P16_commuting_operation'; save_figure(fig, stem); stems.append(stem)
    bank_cases = 0
    for N in range(1, 41):
        prefix = values[:N]
        e, o = split(prefix, 2)
        result = [add(e, [0]+o), add(e, o)]
        assert equal_zero_padded(synth(result), mul([1, 1], prefix))
        bank_cases += 1
    checks['P16'] = {'input':P, 'input_channels':bank, 'output':Qp,
                     'output_channels':out_bank, 'input_support':[0, 5],
                     'output_support':[0, 6], 'final_boundary_coefficient':5,
                     'additional_lengths_checked':[1, 40],
                     'additional_exact_cases':bank_cases}

    artifacts = []
    for stem in stems:
        for ext in ('pdf', 'png'):
            path = FIGURES/(stem+'.'+ext)
            artifacts.append({'path':str(path.relative_to(ROOT)),
                              'bytes':path.stat().st_size, 'sha256':sha(path)})
    metadata = {
        'schema':'komorebi-polyphase-worked-checks-v1',
        'status':'PASS',
        'command':[sys.executable, str(Path(__file__).resolve())],
        'coefficient_domains':['Z', 'Q', 'Q[zeta]/(zeta^2+zeta+1)', 'Q(sqrt(2))'],
        'conventions':{'sequence_index':'n>=0 except explicitly reindexed OEIS tangent stream',
                       'channel_index':'m>=0; 0<=r<M; M positive integer',
                       'polynomial_coefficients':'ascending powers; zero-filled outside finite support',
                       'channel_variable':'u=z^M', 'state_orientation':'column vectors'},
        'software':{'python':platform.python_version(), 'numpy':np.__version__,
                    'matplotlib':matplotlib.__version__},
        'resource_caps':{'OPENBLAS_NUM_THREADS':os.environ.get('OPENBLAS_NUM_THREADS'),
                         'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS'),
                         'thread_caps_are_cooperative':True,
                         'hard_memory_or_cpu_cap':'not imposed; deterministic bounded prefix checks'},
        'elapsed_seconds':round(time.monotonic()-started, 3),
        'inputs':[{'path':name, 'sha256':sha(ROOT/name)}
                  for name in ('figures_polyphase.py', 'chapters_polyphase.tex', 'guide_style.py')],
        'checks':checks,
        'artifacts':artifacts,
        'nonclaims':['The finite checks do not prove universal identities.',
                     'Uniform identities are justified by the coefficient derivations in the author review.',
                     'No analytic convergence or asymptotic estimate is inferred from finite coefficient prefixes.',
                     'Floating point is used for visual layout and stated algebraic-value rendering only.'],
        'visual_review':'Recorded separately in evidence/polyphase_author_review.md.'}
    metadata['computation_manifest'] = {
        'schema_version':1,
        'claim_id':'polyphase-atlas-16-worked-examples',
        'repository':{'commit':None, 'dirty':True},
        'command':metadata['command'],
        'environment':{'software':[{'name':k, 'version':v}
                                   for k, v in metadata['software'].items()],
                       'hardware':platform.machine()+' / '+platform.system(),
                       'cooperative_thread_caps':metadata['resource_caps']},
        'mathematics':{
            'assertion_tested':'The 16 displayed coefficient examples and explicitly bounded extensions satisfy their exact identities.',
            'coefficient_domain':'; '.join(metadata['coefficient_domains']),
            'conventions':json.dumps(metadata['conventions'], sort_keys=True),
            'inputs':metadata['inputs'],
            'bounds':{'source_fibonacci_prefix':200,
                      'jump_M':[1, 10], 'jump_m':[0, 9], 'jump_r':'all canonical residues',
                      'binary_original_n':[0, 255], 'formal_sec_tan_exponents':[0, 11],
                      'full_bounds':'Additional bounds and exact examples are in the per-plate checks.'},
            'non_claims':metadata['nonclaims']},
        'randomness':{'used':False, 'generator':'none', 'seed':None},
        'run':{'started_at':started_at, 'runtime_seconds':metadata['elapsed_seconds'],
               'exit_status':0},
        'outputs':[{'path':item['path'], 'sha256':item['sha256']} for item in artifacts],
        'checks':[{'plate':plate, 'status':'PASS', 'evidence':evidence}
                  for plate, evidence in checks.items()],
        'result':'Implementation and finite assertions verified in the declared ranges.',
        'residual_risks':['No git revision identifies this scratch artifact; generator, chapter, and style hashes are recorded.',
                          'Version-1 manifest limitations remain; bounded computation is not a universal proof.',
                          'The authored figures require the final master-PDF layout review.']}
    target = ROOT/'evidence'/'polyphase_checks.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({'status':'PASS', 'plates':len(stems),
                      'artifacts':len(artifacts), 'evidence':str(target),
                      'elapsed_seconds':metadata['elapsed_seconds']}))


if __name__ == '__main__':
    main()
