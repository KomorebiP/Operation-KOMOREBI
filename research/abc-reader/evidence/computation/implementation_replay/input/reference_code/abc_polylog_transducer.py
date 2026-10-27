from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import mpmath as mp
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

mp.mp.dps = 100

INK = '#1C2730'
BLUE = '#2E6F9E'
TEAL = '#2A8C82'
ORANGE = '#D88745'
MAGENTA = '#9B4F83'
RED = '#C95C54'
MUTED = '#66727C'
PALE_BLUE = '#E8F0F5'
PALE_TEAL = '#E7F3F0'
PALE_ORANGE = '#FAF0E7'
PAPER = '#FAFAF7'
GRID = '#D8DEE3'


def exact_int(value: object, name: str = 'value') -> int:
    if isinstance(value, bool):
        raise TypeError(f'{name} must be an integer, not bool')
    try:
        result = int(value)
    except Exception as exc:
        raise TypeError(f'{name} must be integer-like') from exc
    if hasattr(value, 'item'):
        raw = value.item()
        if isinstance(raw, float) and not raw.is_integer():
            raise TypeError(f'{name} must be integral')
    return result


def mobius(n: int) -> int:
    n = exact_int(n, 'n')
    if n == 1:
        return 1
    count = 0
    p = 2
    x = n
    while p * p <= x:
        if x % p == 0:
            x //= p
            count += 1
            if x % p == 0:
                return 0
            while x % p == 0:
                x //= p
        p += 1 if p == 2 else 2
    if x > 1:
        count += 1
    return -1 if count % 2 else 1


def divisors(n: int) -> list[int]:
    out = []
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            out.append(d)
            if d * d != n:
                out.append(n // d)
    return sorted(out)


def free_lie_dimension(weight: int, generators: int = 2) -> int:
    return sum(mobius(d) * generators ** (weight // d) for d in divisors(weight)) // weight


def free_lie_cumulative(max_weight: int, generators: int = 2) -> list[int]:
    total = 0
    out = []
    for n in range(1, max_weight + 1):
        total += free_lie_dimension(n, generators)
        out.append(total)
    return out


def polylog_packet_dimension(max_weight: int) -> int:
    """Dimension of the displayed depth-one polylogarithmic quotient.

    It keeps two Kummer logarithms and one distinguished classical
    polylogarithm in each weight at least two.  This is a selected quotient,
    not a complete coordinate system for all three-point path data.
    """
    if max_weight <= 0:
        return 0
    return 2 + max(0, max_weight - 1)


def li(weight: int, z: complex | mp.mpf | mp.mpc) -> mp.mpf | mp.mpc:
    return mp.polylog(weight, z)


def polylog_distribution(weight: int, M: int, u: mp.mpc) -> tuple[mp.mpc, mp.mpc, mp.mpf]:
    M = exact_int(M, 'M')
    zeta = mp.e ** (2j * mp.pi / M)
    lhs = mp.fsum([li(weight, zeta ** j * u) for j in range(M)])
    rhs = mp.mpf(M) ** (1 - weight) * li(weight, u ** M)
    return lhs, rhs, abs(lhs - rhs)


def distribution_gain(weight: int, M: int) -> int:
    return exact_int(M, 'M') ** max(0, weight - 1)


def distribution_determinant(max_weight: int, M: int) -> int:
    exponent = max_weight * (max_weight - 1) // 2
    return exact_int(M, 'M') ** exponent


def rogers_dilog(z: mp.mpf) -> mp.mpf:
    return li(2, z) + mp.log(z) * mp.log(1 - z) / 2


def rogers_residual(z: mp.mpf) -> mp.mpf:
    return abs(rogers_dilog(z) + rogers_dilog(1 - z) - mp.pi ** 2 / 6)


def trilog_closure_residual(z: mp.mpf) -> mp.mpf:
    lhs = li(3, z) + li(3, 1 - z) + li(3, 1 - 1 / z)
    rhs = (
        mp.zeta(3)
        + mp.log(z) ** 3 / 6
        + mp.pi ** 2 * mp.log(z) / 6
        - mp.log(z) ** 2 * mp.log(1 - z) / 2
    )
    return abs(lhs - rhs)


def trilog_packet(a: int, b: int, c: int) -> dict[str, mp.mpf]:
    a, b, c = map(int, (a, b, c))
    z = mp.mpf(a) / c
    one_minus = mp.mpf(b) / c
    third = -mp.mpf(b) / a
    values = {
        'z': z,
        'one_minus_z': one_minus,
        'log_z': mp.log(z),
        'log_one_minus_z': mp.log(one_minus),
        'li2_z': li(2, z),
        'li2_one_minus_z': li(2, one_minus),
        'li3_z': li(3, z),
        'li3_one_minus_z': li(3, one_minus),
        'li3_third': li(3, third),
    }
    values['envelope'] = max(abs(v) for k, v in values.items() if k not in {'z', 'one_minus_z'})
    logc = mp.log(c)
    values['envelope_bound'] = max(
        logc,
        mp.zeta(2),
        mp.zeta(3) + mp.pi ** 2 * logc / 6 + logc ** 3 / 6,
    )
    values['rogers_residual'] = rogers_residual(z)
    values['trilog_residual'] = trilog_closure_residual(z)
    return values


@dataclass
class CorpusRecord:
    a: int
    b: int
    c: int
    quality: float
    radical: int
    M: int
    kummer_kernel: int
    z: str
    li2_z: str
    li2_one_minus_z: str
    li3_z: str
    li3_one_minus_z: str
    li3_third: str
    period_envelope: float
    envelope_bound: float
    envelope_ratio: float
    linear_character_channels: int
    polylog_channels_weight3: int
    compression_log10: float
    weight3_synthesis_gain_digits: int
    distribution_determinant_digits: int
    rogers_residual: float
    trilog_residual: float
    source: str


def process_corpus(input_csv: Path) -> list[CorpusRecord]:
    df = pd.read_csv(input_csv)
    records: list[CorpusRecord] = []
    for row in df.itertuples(index=False):
        a, b, c = exact_int(row.a), exact_int(row.b), exact_int(row.c)
        M = exact_int(row.powerful_part_M)
        packet = trilog_packet(a, b, c)
        linear_channels = M * M
        poly_channels = polylog_packet_dimension(3)
        compression_log10 = 2 * math.log10(M) - math.log10(poly_channels) if M > 0 else 0.0
        gain3 = M * M
        det3 = M ** 3
        records.append(
            CorpusRecord(
                a=a,
                b=b,
                c=c,
                quality=float(row.quality),
                radical=exact_int(row.radical),
                M=M,
                kummer_kernel=exact_int(row.kummer_kernel),
                z=mp.nstr(packet['z'], 40),
                li2_z=mp.nstr(packet['li2_z'], 40),
                li2_one_minus_z=mp.nstr(packet['li2_one_minus_z'], 40),
                li3_z=mp.nstr(packet['li3_z'], 40),
                li3_one_minus_z=mp.nstr(packet['li3_one_minus_z'], 40),
                li3_third=mp.nstr(packet['li3_third'], 40),
                period_envelope=float(packet['envelope']),
                envelope_bound=float(packet['envelope_bound']),
                envelope_ratio=float(packet['envelope'] / packet['envelope_bound']),
                linear_character_channels=linear_channels,
                polylog_channels_weight3=poly_channels,
                compression_log10=compression_log10,
                weight3_synthesis_gain_digits=len(str(gain3)),
                distribution_determinant_digits=len(str(det3)),
                rogers_residual=float(packet['rogers_residual']),
                trilog_residual=float(packet['trilog_residual']),
                source=str(row.source),
            )
        )
    return records


def save_records(records: list[CorpusRecord], path: Path) -> None:
    rows = [asdict(r) for r in records]
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def box(ax, xy, width, height, text, color=BLUE, fill=PALE_BLUE, fontsize=11):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle='round,pad=0.012,rounding_size=0.018',
        facecolor=fill,
        edgecolor=color,
        linewidth=1.7,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha='center', va='center', fontsize=fontsize, color=INK)
    return patch


def arrow(ax, start, end, color=INK, lw=1.6):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=13, linewidth=lw, color=color))


def save_fig(fig, out: Path, stem: str) -> None:
    fig.savefig(out / f'{stem}.pdf', bbox_inches='tight')
    fig.savefig(out / f'{stem}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def figure_architecture(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.5, 0.96, 'Nonlinear polylogarithmic compression of the Kummer-Fermat bank', ha='center', fontsize=20, weight='bold', color=INK)
    box(ax, (0.03, 0.62), 0.16, 0.18, 'Witt contact\npacket $W_c$\norder $M$', TEAL, PALE_TEAL, 12)
    box(ax, (0.24, 0.62), 0.16, 0.18, 'global Kummer\nclass of $z=a/c$\nand $1-z=b/c$', BLUE, PALE_BLUE, 11)
    box(ax, (0.45, 0.62), 0.17, 0.18, '$M$ root branches\n$u,\\zeta u,\\ldots$\nlinear bank', ORANGE, PALE_ORANGE, 11)
    box(ax, (0.68, 0.62), 0.15, 0.18, 'polylog packet\n$\\log,\\mathrm{Li}_2,\\mathrm{Li}_3$\nconstant dimension', MAGENTA, '#F4EAF1', 11)
    box(ax, (0.87, 0.62), 0.10, 0.18, 'integral\nperiod\ndefect', RED, '#F7EAE8', 11)
    for x0, x1 in [(0.19, 0.24), (0.40, 0.45), (0.62, 0.68), (0.83, 0.87)]:
        arrow(ax, (x0, 0.71), (x1, 0.71))
    ax.text(0.535, 0.50, r'$\sum_{j=0}^{M-1}\mathrm{Li}_n(\zeta_M^j u)=M^{1-n}\mathrm{Li}_n(u^M)$', ha='center', fontsize=16, color=BLUE)
    box(ax, (0.18, 0.20), 0.24, 0.16, 'weight 2\nbounded closure\nbut rational pure rank $0$', ORANGE, PALE_ORANGE, 11)
    box(ax, (0.58, 0.20), 0.24, 0.16, 'weight 3\nbounded archimedean packet\nfirst rational regulator rank $1$', TEAL, PALE_TEAL, 11)
    arrow(ax, (0.57, 0.62), (0.30, 0.36), ORANGE)
    arrow(ax, (0.57, 0.62), (0.70, 0.36), TEAL)
    ax.text(0.5, 0.08, 'The remaining theorem is integral, not analytic: control the lattice defect of the weight-three distribution packet at every finite place.', ha='center', fontsize=12, color=MUTED)
    save_fig(fig, out, '01_polylog_architecture')


def figure_distribution_gains(out: Path) -> None:
    Ms = np.arange(2, 65)
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    for n, color in [(1, BLUE), (2, ORANGE), (3, TEAL), (4, MAGENTA)]:
        ax.plot(Ms, [distribution_gain(n, int(M)) for M in Ms], label=f'weight {n}: $M^{{{n-1}}}$', lw=2.2, color=color)
    ax.set_yscale('log')
    ax.set_xlabel('Kummer order $M$')
    ax.set_ylabel('exact synthesis gain')
    ax.set_title('Polylogarithmic distribution gains by weight', weight='bold')
    ax.grid(alpha=0.2, which='both')
    ax.legend()
    save_fig(fig, out, '02_distribution_gains')


def figure_dimension_comparison(out: Path) -> None:
    weights = np.arange(1, 14)
    full = np.array(free_lie_cumulative(13, 2), dtype=float)
    poly = np.array([polylog_packet_dimension(int(w)) for w in weights], dtype=float)
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.plot(weights, full, marker='o', lw=2.1, color=RED, label='full two-generator free Lie packet')
    ax.plot(weights, poly, marker='o', lw=2.1, color=TEAL, label='classical polylog packet')
    ax.set_yscale('log')
    ax.set_xlabel('maximum weight')
    ax.set_ylabel('cumulative channel count')
    ax.set_title('Nonabelian compression by the polylog quotient', weight='bold')
    ax.grid(alpha=0.2, which='both')
    ax.legend()
    save_fig(fig, out, '03_lie_vs_polylog_dimensions')


def figure_identity_residuals(out: Path) -> None:
    zs = [mp.mpf(k) / 101 for k in range(1, 101)]
    rr = [float(rogers_residual(z)) for z in zs]
    tr = [float(trilog_closure_residual(z)) for z in zs]
    floor = 1e-100
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.semilogy([float(z) for z in zs], np.maximum(rr, floor), lw=2, color=ORANGE, label='Rogers dilogarithm closure')
    ax.semilogy([float(z) for z in zs], np.maximum(tr, floor), lw=2, color=TEAL, label='three-channel trilogarithm closure')
    ax.set_xlabel('$z$')
    ax.set_ylabel('absolute residual')
    ax.set_title('High-precision closure checks on $0<z<1$', weight='bold')
    ax.grid(alpha=0.2)
    ax.legend()
    save_fig(fig, out, '04_functional_identity_residuals')


def figure_corpus_compression(records: list[CorpusRecord], out: Path) -> None:
    q = np.array([r.quality for r in records])
    comp = np.array([r.compression_log10 for r in records])
    M = np.array([r.M for r in records], dtype=object)
    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    sc = ax.scatter(q, comp, s=24, c=np.log10(np.array([float(min(m, 10**300)) for m in M])), cmap='viridis', alpha=0.72)
    ax.set_xlabel('$abc$ quality')
    ax.set_ylabel(r'$\log_{10}(M^2/4)$')
    ax.set_title('Linear Fermat channels versus the weight-three polylog packet', weight='bold')
    ax.grid(alpha=0.18)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label(r'$\log_{10}M$')
    save_fig(fig, out, '05_corpus_compression')


def figure_archimedean_envelope(records: list[CorpusRecord], out: Path) -> None:
    logc = np.array([math.log(r.c) for r in records], dtype=float)
    env = np.array([r.period_envelope for r in records])
    bound = np.array([r.envelope_bound for r in records])
    order = np.argsort(logc)
    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    ax.scatter(logc, env, s=21, alpha=0.65, color=TEAL, label='measured depth-three envelope')
    ax.plot(logc[order], bound[order], color=RED, lw=2.2, label=r'explicit $O((\log c)^3)$ bound')
    ax.set_yscale('log')
    ax.set_xlabel(r'$\log c$')
    ax.set_ylabel('archimedean packet size')
    ax.set_title('The nonlinear three-point packet is archimedeanly inexpensive', weight='bold')
    ax.grid(alpha=0.2, which='both')
    ax.legend()
    save_fig(fig, out, '06_archimedean_envelope')


def figure_weight_hierarchy(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.5, 6.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.5, 0.94, 'Why weight three is the first viable global regulator channel over $Q$', ha='center', fontsize=19, weight='bold')
    entries = [
        (0.06, 'weight 1', 'Kummer logarithms', 'retains valuations\nbut no nonlinear compression', BLUE, PALE_BLUE),
        (0.37, 'weight 2', 'dilogarithmic closure', 'synthesis gain $M$\npure rational rank $0$', ORANGE, PALE_ORANGE),
        (0.68, 'weight 3', 'trilogarithmic path packet', 'synthesis gain $M^2$\nfirst rational regulator rank $1$', TEAL, PALE_TEAL),
    ]
    for x, head, body, foot, color, fill in entries:
        box(ax, (x, 0.43), 0.25, 0.32, f'{head}\n\n{body}\n\n{foot}', color, fill, 12)
    arrow(ax, (0.31, 0.59), (0.37, 0.59))
    arrow(ax, (0.62, 0.59), (0.68, 0.59))
    ax.text(0.5, 0.20, 'The weight-two packet closes too efficiently and loses the unbounded rational regulator direction. Weight three keeps a nontrivial global regulator while remaining polylogarithmically small at infinity.', ha='center', fontsize=12, color=MUTED, wrap=True)
    save_fig(fig, out, '07_weight_hierarchy')


def figure_branch_packet(out: Path, M: int = 12, z: float = 0.37) -> None:
    u = mp.mpf(z) ** (mp.mpf(1) / M)
    zeta = mp.e ** (2j * mp.pi / M)
    vals2 = np.array([complex(li(2, zeta ** j * u)) for j in range(M)])
    vals3 = np.array([complex(li(3, zeta ** j * u)) for j in range(M)])
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.0))
    axes[0].scatter(vals2.real, vals2.imag, c=np.arange(M), cmap='twilight', s=55)
    axes[0].scatter([vals2.real.mean()], [vals2.imag.mean()], color=RED, marker='*', s=160, label='invariant average')
    axes[0].set_title('weight-two root channels', weight='bold')
    axes[1].scatter(vals3.real, vals3.imag, c=np.arange(M), cmap='twilight', s=55)
    axes[1].scatter([vals3.real.mean()], [vals3.imag.mean()], color=RED, marker='*', s=160, label='invariant average')
    axes[1].set_title('weight-three root channels', weight='bold')
    for ax in axes:
        ax.axhline(0, color=GRID, lw=1)
        ax.axvline(0, color=GRID, lw=1)
        ax.set_xlabel('real part')
        ax.set_ylabel('imaginary part')
        ax.grid(alpha=0.15)
        ax.legend()
    fig.suptitle(f'One nonlinear invariant packet from {M} Kummer branches', fontsize=17, weight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_fig(fig, out, '08_root_branch_packets')


def figure_final_barrier(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 6.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.5, 0.95, 'The corrected final barrier after nonlinear polylogarithmic compression', ha='center', fontsize=20, weight='bold')
    box(ax, (0.04, 0.58), 0.18, 0.20, 'contact packet\n$Z/MZ$\nKummer kernel $\\leq \\log_2 c$', TEAL, PALE_TEAL, 12)
    box(ax, (0.29, 0.58), 0.19, 0.20, 'three-point path\n$z=a/c$ and $1-z=b/c$\nno degree-$M$ curve', BLUE, PALE_BLUE, 11)
    box(ax, (0.55, 0.58), 0.18, 0.20, 'depth-three\npolylog packet\ngain determinant $M^3$', MAGENTA, '#F4EAF1', 11)
    box(ax, (0.80, 0.58), 0.16, 0.20, 'integral motivic\nand syntomic\ndistribution defect', RED, '#F7EAE8', 11)
    for x0, x1 in [(0.22,0.29),(0.48,0.55),(0.73,0.80)]:
        arrow(ax,(x0,0.68),(x1,0.68))
    box(ax, (0.18, 0.18), 0.25, 0.18, 'proved analytic side\nconstant channel count\n$O((\\log c)^3)$ archimedean envelope', TEAL, PALE_TEAL, 11)
    box(ax, (0.57, 0.18), 0.25, 0.18, 'missing arithmetic side\npreserve $M$ through integral lattices\nwith only $R^\\varepsilon$ loss', RED, '#F7EAE8', 11)
    arrow(ax, (0.64,0.58),(0.31,0.36),TEAL)
    arrow(ax, (0.88,0.58),(0.69,0.36),RED)
    ax.text(0.5, 0.07, 'The Fermat canonical-degree payback is gone. The remaining cost is the integral distribution lattice, not the complex period size.', ha='center', fontsize=12, color=MUTED)
    save_fig(fig, out, '09_final_barrier')


def generate_figures(records: list[CorpusRecord], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    figure_architecture(out)
    figure_distribution_gains(out)
    figure_dimension_comparison(out)
    figure_identity_residuals(out)
    figure_corpus_compression(records, out)
    figure_archimedean_envelope(records, out)
    figure_weight_hierarchy(out)
    figure_branch_packet(out)
    figure_final_barrier(out)


def run_checks(records: list[CorpusRecord]) -> dict[str, object]:
    checks: dict[str, bool] = {}
    # Distribution formulas.
    for M in range(2, 13):
        u = mp.mpf('0.63') ** (mp.mpf(1) / M)
        for n in range(1, 5):
            _, _, residual = polylog_distribution(n, M, u)
            checks[f'distribution_M{M}_n{n}'] = residual < mp.mpf('1e-80')
    # Functional equations.
    for k in range(1, 100):
        z = mp.mpf(k) / 100
        checks[f'rogers_{k}'] = rogers_residual(z) < mp.mpf('1e-80')
        checks[f'trilog_{k}'] = trilog_closure_residual(z) < mp.mpf('1e-80')
    # Dimension formulas and determinant formulas.
    checks['free_lie_weight1'] = free_lie_dimension(1, 2) == 2
    checks['free_lie_weight2'] = free_lie_dimension(2, 2) == 1
    checks['free_lie_weight3'] = free_lie_dimension(3, 2) == 2
    checks['distribution_det_3_7'] = distribution_determinant(3, 7) == 7 ** 3
    checks['distribution_det_4_5'] = distribution_determinant(4, 5) == 5 ** 6
    # Corpus bounds.
    checks['corpus_nonempty'] = len(records) > 300
    checks['all_envelopes_bounded'] = all(r.period_envelope <= r.envelope_bound * (1 + 1e-12) for r in records)
    checks['rogers_corpus'] = max(r.rogers_residual for r in records) < 1e-80
    checks['trilog_corpus'] = max(r.trilog_residual for r in records) < 1e-80
    checks['all_M_positive'] = all(r.M >= 1 for r in records)
    checks['compression_identity'] = all(abs(r.compression_log10 - (2 * math.log10(r.M) - math.log10(4))) < 1e-10 for r in records)
    failed = [name for name, ok in checks.items() if not ok]
    return {
        'checks_total': len(checks),
        'checks_passed': len(checks) - len(failed),
        'failed': failed,
        'all_passed': not failed,
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=Path('.'))
    parser.add_argument('--input', type=Path, default=None)
    args = parser.parse_args()
    base = args.base.resolve()
    input_csv = args.input.resolve() if args.input else base / 'input_corpus.csv'
    (base / 'figures').mkdir(exist_ok=True)
    (base / 'tables').mkdir(exist_ok=True)
    (base / 'results').mkdir(exist_ok=True)

    records = process_corpus(input_csv)
    save_records(records, base / 'tables' / 'polylog_corpus.csv')
    generate_figures(records, base / 'figures')
    checks = run_checks(records)

    top = sorted(records, key=lambda r: r.quality, reverse=True)[:10]
    results = {
        'status': 'exact nonlinear compression and conditional arithmetic target; abc not proved',
        'corpus_rows': len(records),
        'figure_pairs': 9,
        'distribution_theorem': 'sum_j Li_n(zeta_M^j u) = M^(1-n) Li_n(u^M)',
        'depth_three_distribution_determinant': 'M^3',
        'weight_two_boundary': 'pure rational regulator rank zero',
        'weight_three_direction': 'first rational regulator rank one',
        'max_rogers_residual': max(r.rogers_residual for r in records),
        'max_trilog_residual': max(r.trilog_residual for r in records),
        'max_envelope_ratio': max(r.envelope_ratio for r in records),
        'median_compression_log10': float(np.median([r.compression_log10 for r in records])),
        'max_compression_log10': max(r.compression_log10 for r in records),
        'checks': checks,
        'top_quality': [asdict(r) for r in top],
        'remaining_obstruction': 'integral motivic and syntomic lattice defect of the weight-three distribution packet',
    }
    (base / 'results' / 'attack_x_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2)[:5000])


if __name__ == '__main__':
    main()
