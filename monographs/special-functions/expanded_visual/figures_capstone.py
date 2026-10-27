"""Six exact capstone plates: one finite record through operation and repair.

Scientific values use native Python integers. Floating coordinates are used
only to render explicit diagrams and stems. Every output retains the full
finite convolution tail. The model-repair domain is stated separately from
the arbitrary finite polynomial domain used by the projection counterexample.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import time

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from guide_style import COLORS, INK, MUTED, PALE, save_figure

ROOT = Path(__file__).resolve().parent
START = time.perf_counter()
STARTED_AT = datetime.now(timezone.utc).isoformat()
INPUT_PATHS = [Path(__file__), ROOT / 'guide_style.py', ROOT / 'chapters_capstone.tex']
INPUT_HASHES = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in INPUT_PATHS}
CHECKS = []
plt.rcParams.update({'font.size': 15, 'axes.labelsize': 14,
                     'axes.titlesize': 17, 'xtick.labelsize': 12,
                     'ytick.labelsize': 12, 'legend.fontsize': 12})


def check(name, condition, details):
    assert condition, name
    CHECKS.append({'name': name, 'status': 'PASS', 'details': details})


def fibonacci(count):
    a, b = 0, 1
    values = []
    for _ in range(count):
        values.append(a)
        a, b = b, a + b
    return values


def convolution(taps, values):
    result = [0] * (len(taps) + len(values) - 1)
    for k, tap in enumerate(taps):
        for n, value in enumerate(values):
            result[n + k] += tap * value
    return result


def polynomial_add(p, q):
    return [(p[n] if n < len(p) else 0) + (q[n] if n < len(q) else 0)
            for n in range(max(len(p), len(q)))]


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def polynomial_matrix_product(left, right):
    size = len(left)
    result = []
    for r in range(size):
        row = []
        for s in range(size):
            entry = [0]
            for k in range(size):
                entry = polynomial_add(entry, convolution(left[r][k], right[k][s]))
            row.append(trim(entry))
        result.append(row)
    return result


def polynomial_matrix_vector(matrix, vector):
    result = []
    for row in matrix:
        value = [0]
        for entry, phase in zip(row, vector):
            value = polynomial_add(value, convolution(entry, phase))
        result.append(trim(value))
    return result


def synthesize(phases, modulus, length):
    result = [0] * length
    for r, phase in enumerate(phases):
        for m, value in enumerate(phase):
            n = modulus * m + r
            if n < length:
                result[n] = value
            else:
                assert value == 0, 'nonzero output beyond declared support'
    return result


def model_record(a, b):
    result = [a, b]
    for _ in range(6):
        result.append(result[-1] + result[-2])
    return result


def model_completion(evens):
    if evens[2] != 3 * evens[1] - evens[0]:
        return None
    if evens[3] != 3 * evens[2] - evens[1]:
        return None
    return model_record(evens[0], evens[1] - evens[0])


def positive_compositions(total):
    if total == 0:
        yield ()
        return
    for first in range(1, total + 1):
        for rest in positive_compositions(total - first):
            yield (first,) + rest


def stream_chunks(values, sizes, modulus=3):
    assert sum(sizes) == len(values) and all(size > 0 for size in sizes)
    history = [0, 0]  # oldest first; state BEFORE processing the next sample.
    next_index = 0
    outputs = []
    phases = [[] for _ in range(modulus)]
    snapshots = []
    start = 0

    def process(value):
        nonlocal next_index
        output = value - history[1] - history[0]
        outputs.append(output)
        phases[next_index % modulus].append(output)
        history[:] = [history[1], value]
        next_index += 1

    for size in sizes:
        for value in values[start:start + size]:
            process(value)
        start += size
        snapshots.append({'processed_real_samples': start,
                          'history_oldest_first': list(history),
                          'next_index': next_index,
                          'next_phase': next_index % modulus})
    for _ in range(2):
        process(0)
    return outputs, phases, snapshots


def frame(size=(10, 5.0)):
    return plt.figure(figsize=size)


def blank(ax):
    ax.set_xlim(-0.025, 1.025)
    ax.set_ylim(-0.035, 1.035)
    ax.axis('off')


def box(ax, x, y, width, height, label, color=COLORS[0], fill=PALE, fontsize=16):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                 boxstyle='round,pad=0.013,rounding_size=0.014',
                 edgecolor=color, facecolor=fill, linewidth=1.4))
    ax.text(x + width / 2, y + height / 2, label, ha='center', va='center',
            fontsize=fontsize, color=INK)


def arrow(ax, start, stop, color=COLORS[0]):
    ax.annotate('', xy=stop, xytext=start,
                arrowprops={'arrowstyle': '-|>', 'color': color, 'lw': 1.8})


def stem(ax, values, title, color=COLORS[0], colors=None, labels=True):
    positions = list(range(len(values)))
    if colors is None:
        colors = [color] * len(values)
    ax.vlines(positions, 0, values, colors=colors, linewidth=2)
    ax.scatter(positions, values, c=colors, s=37, zorder=3)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set_title(title, pad=12)
    ax.set_xticks(positions)
    ax.set_xlim(-0.5, len(values) - 0.5)
    ax.grid(axis='y')
    if labels:
        spread = max(max(values) - min(values), 1)
        for n, value in enumerate(values):
            offset = spread * 0.06
            ax.text(n, value + (offset if value >= 0 else -offset), str(value),
                    ha='center', va='bottom' if value >= 0 else 'top', fontsize=13)


STEMS = [
    'C01_finite_residual', 'C02_three_phase_residual', 'C03_interior_defect',
    'C04_projection_obstruction', 'C05_model_repair', 'C06_streaming_clock']


def save(fig, index):
    save_figure(fig, STEMS[index - 1])


X = fibonacci(8)
A = [1, -1, -1]
Y = convolution(A, X)
check('Fixed record and full finite residual',
      X == [0, 1, 1, 2, 3, 5, 8, 13]
      and Y == [0, 1, 0, 0, 0, 0, 0, 0, -21, -13],
      {'input_support': [0, 7], 'output_support': [0, 9],
       'input': X, 'taps': A, 'full_output': Y})
boundary_cases = []
for count in range(2, 21):
    f = fibonacci(count + 1)
    actual = convolution(A, f[:count])
    expected = [0] * (count + 2)
    expected[1] = 1
    expected[count] = -f[count]
    expected[count + 1] = -f[count - 1]
    assert actual == expected
    boundary_cases.append({'N': count, 'tail': expected[-2:]})
check('Finite-prefix boundary formula', True,
      {'N_range_inclusive': [2, 20], 'case_count': len(boundary_cases),
       'results': boundary_cases,
       'proof_scope': 'Coefficient derivation supplies the general identity separately.'})

# C01: declare zero extension and retain both cutoff impulses.
fig = frame()
axes = fig.subplots(2, 1, gridspec_kw={'height_ratios': [1, 1.1]})
stem(axes[0], X + [0, 0], 'The eight real input samples, then zero extension')
axes[0].axvspan(7.5, 9.5, color='#F1F3F4', zorder=0)
axes[0].set_ylim(-1.5, 16)
axes[0].set_ylabel('input x[n]')
stem(axes[1], Y, 'Full causal residual: the interior cancels', COLORS[1])
axes[1].axvspan(0.5, 1.5, color=PALE, zorder=0)
axes[1].axvspan(7.5, 9.5, color='#FAEFEA', zorder=0)
axes[1].set_ylim(-26, 5)
axes[1].set_ylabel('output y[n]')
axes[1].set_xlabel('fine index n')
fig.tight_layout(h_pad=1.2)
save(fig, 1)

# C02: build A(C3) by actual polynomial matrix arithmetic.
C3 = [[[0], [0], [0, 1]], [[1], [0], [0]], [[0], [1], [0]]]
C3_squared = polynomial_matrix_product(C3, C3)
transfer = []
for r in range(3):
    row = []
    for s in range(3):
        value = [int(r == s)]
        value = polynomial_add(value, [-n for n in C3[r][s]])
        value = polynomial_add(value, [-n for n in C3_squared[r][s]])
        row.append(trim(value))
    transfer.append(row)
INPUT_PHASES = [X[r::3] for r in range(3)]
OUTPUT_PHASES = polynomial_matrix_vector(transfer, INPUT_PHASES)
EXPECTED_MATRIX = [[[1], [0, -1], [0, -1]],
                   [[-1], [1], [0, -1]], [[-1], [-1], [1]]]
check('Three-phase annihilator and complete reconstruction',
      transfer == EXPECTED_MATRIX
      and OUTPUT_PHASES == [[0, 0, 0, -13], [1], [0, 0, -21]]
      and synthesize(OUTPUT_PHASES, 3, 10) == Y,
      {'modulus': 3, 'input_phases_coefficients': INPUT_PHASES,
       'transfer_matrix_polynomial_coefficients': transfer,
       'output_phases_trimmed': OUTPUT_PHASES,
       'output_phases_full_support': [Y[r::3] for r in range(3)],
       'synthesized_output': synthesize(OUTPUT_PHASES, 3, 10)})
fig = frame()
ax = fig.add_subplot()
blank(ax)
ax.text(0.14, 0.94, 'Input bank f', ha='center', fontsize=18)
ax.text(0.53, 0.94, r'$A(C_3)=I-C_3-C_3^2$', ha='center', fontsize=18)
ax.text(0.89, 0.94, 'Output bank', ha='center', fontsize=18)
input_labels = [r'$2u+8u^2$', r'$1+3u+13u^2$', r'$1+5u$']
matrix_labels = [['1', '-u', '-u'], ['-1', '1', '-u'], ['-1', '-1', '1']]
output_labels = [r'$-13u^3$', r'$1$', r'$-21u^2$']
for r, y0 in enumerate([0.67, 0.43, 0.19]):
    box(ax, 0.012, y0, 0.25, 0.14, input_labels[r], color=COLORS[r], fontsize=16)
    for s in range(3):
        box(ax, 0.365 + s * 0.125, y0, 0.095, 0.14,
            '$' + matrix_labels[r][s] + '$',
            color=COLORS[1] if s > r else COLORS[0],
            fill='#FAEFEA' if s > r else PALE, fontsize=19)
    box(ax, 0.785, y0, 0.20, 0.14, output_labels[r], color=COLORS[r], fontsize=19)
arrow(ax, (0.278, 0.5), (0.344, 0.5))
arrow(ax, (0.735, 0.5), (0.766, 0.5))
ax.text(0.53, 0.090, 'Rows: output phases     Columns: input phases', ha='center', fontsize=14)
ax.text(0.53, 0.005, r'Synthesis: $-13z^9+z-21z^8$', ha='center', fontsize=17)
save(fig, 2)

# C03: show a single changed sample and the exact change in output.
Q = list(X)
Q[5] += 1
YQ = convolution(A, Q)
DELTA_Y = [b - a for a, b in zip(Y, YQ)]
check('One-sample perturbation and linear residual difference',
      Q == [0, 1, 1, 2, 3, 6, 8, 13]
      and DELTA_Y == [0, 0, 0, 0, 0, 1, -1, -1, 0, 0]
      and YQ[:2] == Y[:2] and YQ[8:] == Y[8:],
      {'changed_index': 5, 'increment': 1, 'perturbed_input': Q,
       'full_perturbed_output': YQ, 'output_difference': DELTA_Y})
fig = frame()
axes = fig.subplots(2, 1)
colors = [COLORS[0]] * 10
colors[5] = COLORS[1]
stem(axes[0], Q + [0, 0], 'Change only index 5: five becomes six', colors=colors)
axes[0].axvspan(4.5, 5.5, color='#FAEFEA', zorder=0)
axes[0].set_ylim(-1.5, 16)
axes[0].set_ylabel('perturbed input')
stem(axes[1], DELTA_Y, 'Change in residual: one impulse meets three taps', COLORS[1])
axes[1].axvspan(4.5, 7.5, color='#FAEFEA', zorder=0)
axes[1].set_ylim(-1.55, 1.65)
axes[1].set_ylabel('output difference')
axes[1].set_xlabel('fine index n')
fig.tight_layout(h_pad=1.4)
save(fig, 3)

# C04: equal observations cannot determine different filtered observations.
EVEN_INPUT = X[::2]
EVEN_OUTPUT = Y[::2]
EVEN_OUTPUT_Q = YQ[::2]
check('Projection obstruction after the filter',
      X[::2] == Q[::2] == [0, 1, 3, 8]
      and EVEN_OUTPUT == [0, 0, 0, 0, -21]
      and EVEN_OUTPUT_Q == [0, 0, 0, -1, -21],
      {'projection': 'keep original indices 0,2,4,...',
       'same_even_input': EVEN_INPUT, 'even_output_P8': EVEN_OUTPUT,
       'even_output_Q': EVEN_OUTPUT_Q,
       'even_output_difference': [b - a for a, b in zip(EVEN_OUTPUT, EVEN_OUTPUT_Q)],
       'logical_consequence': 'No map on even observations reproduces all even outputs of A on arbitrary finite integer polynomials.'})
fig = frame()
ax = fig.add_subplot()
blank(ax)
columns = [(0.02, 0.23), (0.325, 0.29), (0.70, 0.28)]
for (x0, width), title in zip(columns, ['Full record', 'Retained even input', 'Filtered even output']):
    ax.text(x0 + width / 2, 0.92, title, ha='center', fontsize=17)
for y0, label, output in [(0.60, r'$P_8$', r'$-21u^4$'),
                         (0.29, r'$Q=P_8+z^5$', r'$-u^3-21u^4$')]:
    box(ax, columns[0][0], y0, columns[0][1], 0.18, label, fontsize=19)
    box(ax, columns[1][0], y0, columns[1][1], 0.18,
        r'$u+3u^2+8u^3$', fontsize=18)
    box(ax, columns[2][0], y0, columns[2][1], 0.18, output,
        color=COLORS[1], fill='#FAEFEA', fontsize=19)
    arrow(ax, (0.27, y0 + 0.09), (0.305, y0 + 0.09))
ax.text(0.47, 0.185, 'Equal inputs', ha='center', fontsize=16, color=COLORS[0])
ax.text(0.84, 0.185, 'Different outputs', ha='center', fontsize=16, color=COLORS[1])
ax.text(0.5, 0.045, 'The discarded odd coefficient re-enters an even output.',
        ha='center', fontsize=17)
save(fig, 4)

# C05: recovery is unique only inside the stated recurrence family.
MODEL_CASES = 0
REJECTED_CASES = 0
for a in range(-3, 4):
    for b in range(-3, 4):
        record = model_record(a, b)
        evens = record[::2]
        assert model_completion(evens) == record
        MODEL_CASES += 1
        for position in [2, 3]:
            for delta in [-1, 1]:
                bad = list(evens)
                bad[position] += delta
                assert model_completion(bad) is None
                REJECTED_CASES += 1
check('Model-constrained repair and consistency rejection',
      model_completion(EVEN_INPUT) == X and MODEL_CASES == 49 and REJECTED_CASES == 196
      and any(Q[n + 2] != Q[n + 1] + Q[n] for n in range(6)),
      {'model': 'length-eight records with x[n+2]=x[n+1]+x[n], n=0,...,5',
       'seed_range_inclusive': [-3, 3], 'valid_seed_pairs': MODEL_CASES,
       'invalid_observation_cases': REJECTED_CASES,
       'invalid_case_rule': 'For each seed pair, change E2 or E3 by +1 or -1.',
       'observations': EVEN_INPUT, 'inferred_seeds': [EVEN_INPUT[0], EVEN_INPUT[1] - EVEN_INPUT[0]],
       'completion': model_completion(EVEN_INPUT),
       'nonclaim': 'No arbitrary-record or noisy-observation recovery guarantee.'})
fig = frame()
ax = fig.add_subplot()
blank(ax)
ax.text(0.5, 0.955, 'Observe evens, infer seeds, check the model, restore odds',
        ha='center', fontsize=17)
for j, (index, value) in enumerate(zip([0, 2, 4, 6], EVEN_INPUT)):
    box(ax, 0.12 + 0.20 * j, 0.735, 0.16, 0.13,
        f'x[{index}] = {value}', fontsize=17)
ax.text(0.50, 0.655, r'Consistency: $3\cdot1-0=3$ and $3\cdot3-1=8$',
        ha='center', fontsize=17)
box(ax, 0.025, 0.405, 0.225, 0.15, 'Seeds\na = 0, b = 1', fontsize=16)
arrow(ax, (0.27, 0.48), (0.35, 0.48))
for j, value in enumerate(X[1::2]):
    box(ax, 0.385 + 0.155 * j, 0.405, 0.12, 0.15,
        f'{value}', color=COLORS[1], fill='#FAEFEA', fontsize=20)
ax.text(0.68, 0.335, 'Recovered odd values: 1, 2, 5, 13', ha='center', fontsize=15)
for n, value in enumerate(X):
    x0 = 0.067 + 0.113 * n
    box(ax, x0, 0.10, 0.080, 0.125, str(value),
        color=COLORS[n % 2], fill=PALE if n % 2 == 0 else '#FAEFEA', fontsize=20)
    ax.text(x0 + 0.040, 0.043, f'n={n}', ha='center', fontsize=12, color=MUTED)
save(fig, 5)

# C06: all positive chunk partitions, retaining both history and phase clock.
STREAM_OUTPUT, STREAM_PHASES, SNAPSHOTS = stream_chunks(X, (2, 3, 3))
partition_count = 0
for sizes in positive_compositions(8):
    out, phases, snapshots = stream_chunks(X, sizes)
    assert out == Y
    assert phases == [Y[r::3] for r in range(3)]
    assert snapshots[-1]['history_oldest_first'] == [8, 13]
    assert snapshots[-1]['next_index'] == 8 and snapshots[-1]['next_phase'] == 2
    partition_count += 1
check('Chunked execution and continuous phase clock',
      partition_count == 128 and STREAM_OUTPUT == Y
      and STREAM_PHASES == [Y[r::3] for r in range(3)],
      {'record_length': 8, 'all_positive_chunk_compositions': partition_count,
       'example_chunks': [2, 3, 3], 'state_snapshots': SNAPSHOTS,
       'full_output': STREAM_OUTPUT, 'phase_outputs': STREAM_PHASES,
       'flush_input': [0, 0], 'flush_output': [-21, -13],
       'flush_phases': [2, 0], 'initial_history': [0, 0],
       'state_convention': 'Oldest preceding input first; phase is next global index modulo three.'})
fig = frame(size=(10, 5.1))
axes = fig.subplots(2, 1, gridspec_kw={'height_ratios': [1.5, 0.9]})
phase_colors = [COLORS[n % 3] for n in range(10)]
stem(axes[0], STREAM_OUTPUT, 'Chunks change storage; output indices keep advancing', colors=phase_colors)
for boundary in [1.5, 4.5, 7.5]:
    axes[0].axvline(boundary, color=MUTED, linestyle='--', linewidth=1.3)
axes[0].axvspan(7.5, 9.5, color='#FAEFEA', zorder=0)
axes[0].set_ylim(-26, 5)
axes[0].set_ylabel('output y[n]')
axes[0].set_xlabel('fine index n; output phase = n mod 3')
ax = axes[1]
blank(ax)
labels = [f"After {s['processed_real_samples']} inputs\nhistory {tuple(s['history_oldest_first'])}\nnext phase {s['next_phase']}"
          for s in SNAPSHOTS]
labels.append('Two-zero flush\n-21 at phase 2\n-13 at phase 0')
for j, label in enumerate(labels):
    box(ax, 0.01 + 0.25 * j, 0.19, 0.22, 0.60, label,
        color=COLORS[1] if j == 3 else COLORS[0],
        fill='#FAEFEA' if j == 3 else PALE, fontsize=14)
fig.tight_layout(h_pad=1.1)
save(fig, 6)

figures = []
for stem_name in STEMS:
    for extension in ['pdf', 'png']:
        path = ROOT / 'figures' / (stem_name + '.' + extension)
        figures.append({'path': str(path.relative_to(ROOT)),
                        'bytes': path.stat().st_size,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
NONCLAIMS = [
    'Finite computational ranges do not prove universal identities; direct derivations are separate.',
    'Arbitrary even observations do not determine all filtered even observations.',
    'Model completion is restricted to exact length-eight Fibonacci-recurrence records.',
    'No noisy recovery guarantee or universal minimal state bound is asserted.',
    'The phase clock routes outputs; arithmetic sample equality alone does not check addresses.',
    'Figures illustrate exact integer coefficients; no continuous approximation is used.']
record = {
    'schema_version': 1,
    'claim_id': 'C01--C06 exact finite-record capstone and declared model repair',
    'status': 'PASS',
    'repository': {'commit': None, 'dirty': True,
                   'revision_note': 'Unversioned artifact workspace; input hashes supplied.'},
    'command': 'env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python figures_capstone.py',
    'environment': {
        'software': [{'name': 'python', 'version': platform.python_version()},
                     {'name': 'matplotlib', 'version': matplotlib.__version__}],
        'hardware': platform.machine() + '; CPU-only Matplotlib; ' + str(os.cpu_count()) + ' logical CPUs',
        'cooperative_thread_caps': {'OPENBLAS_NUM_THREADS': os.environ.get('OPENBLAS_NUM_THREADS'),
                                    'OMP_NUM_THREADS': os.environ.get('OMP_NUM_THREADS')},
        'machine_enforced_limits': 'No separate CPU or memory cap; fixed bounded loops and six figures.'},
    'mathematics': {
        'assertion_tested': 'Exact finite convolution, complete phase reconstruction, projection obstruction witnesses, model completion, and chunked output addressing.',
        'coefficient_domain': 'Native Python integers; floats only position rendered marks.',
        'conventions': 'Version 1: fine index starts at zero; values zero outside the finite record; z is a fine delay, u a coarse delay; rows are output phases, columns input phases; direct FIR history is oldest first.',
        'inputs': ['Eight-value Fibonacci record', 'Taps [1,-1,-1]',
                   'Perturbation +1 at index 5', 'Length-eight recurrence model',
                   'All positive chunk compositions of eight'],
        'bounds': {'finite_prefix_lengths_inclusive': [2, 20],
                   'fixed_input_indices': [0, 7], 'fixed_full_output_indices': [0, 9],
                   'modulus': 3, 'model_seed_range_inclusive': [-3, 3],
                   'model_cases': MODEL_CASES, 'invalid_model_observation_cases': REJECTED_CASES,
                   'all_positive_chunk_compositions': partition_count,
                   'flush_zeros': 2},
        'non_claims': NONCLAIMS},
    'randomness': {'used': False, 'generator': 'not used', 'seed': None},
    'run': {'started_at': STARTED_AT, 'runtime_seconds': time.perf_counter() - START, 'exit_status': 0},
    'outputs': [{'path': p['path'], 'sha256': p['sha256']} for p in figures],
    'checks': CHECKS,
    'figure_count': 6,
    'figures': figures,
    'input_artifacts': [],
    'result': 'Implementation and finite assertions verified in the stated bounds. The direct coefficient, linearity, contradiction, recurrence-state, and streaming-induction derivations are supplied separately in the author review.',
    'residual_risks': [
        'Version 1 manifests do not supply a git revision or machine-checkable resource limits.',
        'Author self-review is not an independent mathematical or final assembled-page audit.',
        'No claim about arbitrary noisy recovery follows from exact model-completion checks.']}
for name, before in INPUT_HASHES.items():
    after = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert before == after, 'Input changed during capstone generation: ' + name
    record['input_artifacts'].append({'path': name, 'sha256': before, 'sha256_after': after})
(ROOT / 'evidence').mkdir(exist_ok=True)
(ROOT / 'evidence' / 'capstone_checks.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'plates': 6, 'checks': len(CHECKS),
                  'boundary_cases': len(boundary_cases), 'model_cases': MODEL_CASES,
                  'invalid_model_cases': REJECTED_CASES, 'chunk_compositions': partition_count}))
