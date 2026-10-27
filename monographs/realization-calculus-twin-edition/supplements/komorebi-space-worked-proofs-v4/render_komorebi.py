#!/usr/bin/env python3
"""Reproducible Komorebi Space plates, using an explicit finite Fourier tower.

Run:
    python render_komorebi.py --output . --dpi 300

Dependencies: numpy, matplotlib. Python 3.10 or newer.

The surfaces are graphs of individual functions, not depictions of whole
function spaces. All drawn geometry is computed in 3D and orthographically
projected by an explicit camera. Matplotlib's default artist colors are used.
No image generator, stock illustration, or external network is involved.

Source framework: Komorebi Space Monograph v1.13.0, sections 1, 6 and 10.
This finite Fourier example and its figures are an illustration of that
framework, not a claim of a new Fourier theorem or a Lean verification.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.text import Text

Key = Tuple[str, int, int]
Polynomial = Dict[Key, Fraction]

# A real Fourier basis of the square torus. Positive representative of {k,-k}.
CUTOFFS = (1, 2, 4, 8)
SEED: Polynomial = {
    ('cos', 1, 0): Fraction(1, 2),
    ('sin', 0, 1): Fraction(3, 10),
    ('cos', 1, 1): Fraction(1, 5),
    ('sin', 2, 1): Fraction(1, 4),
    ('cos', 1, -2): Fraction(3, 20),
    ('cos', 4, 2): Fraction(1, 8),
    ('sin', 3, -4): Fraction(1, 10),
    ('sin', 8, 3): Fraction(1, 14),
    ('cos', 5, -7): Fraction(1, 16),
}
PERTURBATION: Polynomial = {('cos', 1, 0): Fraction(1, 5)}


def clean(p: Polynomial) -> Polynomial:
    return {k: v for k, v in p.items() if v}


def plus(p: Polynomial, q: Polynomial, multiplier: Fraction = Fraction(1)) -> Polynomial:
    out = dict(p)
    for k, v in q.items():
        out[k] = out.get(k, Fraction(0)) + multiplier * v
    return clean(out)


def project(p: Polynomial, cutoff: int) -> Polynomial:
    """Exact Fourier restriction. Inclusion J is the identity on functions."""
    return {k: v for k, v in p.items() if max(abs(k[1]), abs(k[2])) <= cutoff}


def swap_coordinates(p: Polynomial) -> Polynomial:
    """Exact transfer T f(u,v) = f(v,u), including sine sign conventions."""
    result: Polynomial = {}
    for (kind, a, b), c in p.items():
        a, b = b, a
        if a < 0 or (a == 0 and b < 0):
            a, b = -a, -b
            if kind == 'sin':
                c = -c
        k = (kind, a, b)
        result[k] = result.get(k, Fraction(0)) + c
    return clean(result)


def basis(cutoff: int) -> list[Key]:
    out: list[Key] = [('const', 0, 0)]
    for a in range(0, cutoff + 1):
        for b in range(-cutoff, cutoff + 1):
            if a == 0 and b <= 0:
                continue
            out.extend([('cos', a, b), ('sin', a, b)])
    return out


def evaluate(p: Polynomial, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    u, v = np.broadcast_arrays(u, v)
    values = np.zeros_like(u, dtype=float)
    for (kind, a, b), coeff in p.items():
        phase = 2 * np.pi * (a * u + b * v)
        term = np.ones_like(phase) if kind == 'const' else (
            np.cos(phase) if kind == 'cos' else np.sin(phase))
        values += float(coeff) * term
    return values


X = [project(SEED, c) for c in CUTOFFS]
D = [plus(X[n + 1], X[n], Fraction(-1)) for n in range(3)]
Y = [dict(p) for p in X]
Y[2] = plus(Y[2], PERTURBATION)


def residual(family: list[Polynomial]) -> list[Polynomial]:
    return [plus(project(family[n + 1], CUTOFFS[n]), family[n], Fraction(-1))
            for n in range(3)]


def exact_verification() -> dict:
    count = 0
    checks: dict[str, int] = {}

    def require(condition: bool, label: str) -> None:
        nonlocal count
        if not condition:
            raise AssertionError(label)
        count += 1
        checks[label] = checks.get(label, 0) + 1

    for q in CUTOFFS:
        require(len(basis(q)) == (2 * q + 1) ** 2, 'basis_dimension')

    # Checking every basis vector verifies these finite-dimensional linear
    # operator identities, not just the particular plotted seed.
    for k in basis(CUTOFFS[-1]):
        p = {k: Fraction(1)}
        for q in CUTOFFS:
            require(project(project(p, q), q) == project(p, q), 'projector_idempotence')
            require(project(swap_coordinates(p), q) == swap_coordinates(project(p, q)),
                    'transfer_naturality')
            for r in CUTOFFS:
                require(project(project(p, q), r) == project(p, min(q, r)),
                        'nested_projectors')
        for n in range(3):
            fine = project(p, CUTOFFS[n + 1])
            coarse = project(fine, CUTOFFS[n])
            detail = plus(fine, coarse, Fraction(-1))
            require(project(detail, CUTOFFS[n]) == {}, 'detail_in_projection_kernel')
            require(plus(coarse, detail) == fine, 'split_reconstruction')
        require(swap_coordinates(swap_coordinates(p)) == p, 'transfer_involution')

    for r in residual(X):
        require(r == {}, 'plotted_family_coherence')
    reconstructed = dict(X[0])
    for detail in D:
        reconstructed = plus(reconstructed, detail)
    require(reconstructed == X[3], 'plotted_full_reconstruction')
    require(residual(Y) == [{}, PERTURBATION,
                            {k: -v for k, v in PERTURBATION.items()}],
            'perturbed_family_residual')
    repaired = [dict(p) for p in Y]
    repaired[2] = plus(repaired[2], PERTURBATION, Fraction(-1))
    require(repaired == X and residual(repaired) == [{}, {}, {}], 'protected_repair')
    return {
        'status': 'PASS',
        'method': 'Exact rational Fourier coefficients; identities on all 289 basis vectors',
        'exact_checks': count,
        'checks_by_type': checks,
        'cutoffs': list(CUTOFFS),
        'space_dimensions': [(2 * q + 1) ** 2 for q in CUTOFFS],
        'nonzero_seed_modes': len(SEED),
        'coherent_family_residual': ['0', '0', '0'],
        'perturbed_family_residual': ['0', '(1/5) cos(2 pi u)', '-(1/5) cos(2 pi u)'],
        'formal_status': 'Python exact arithmetic checks, not a Lean compiler run',
    }


# ---- Orthographic renderer -------------------------------------------------
# Two orthonormal camera rows. World z is true signal height, not an arbitrary
# 2D deformation. Sheet displacements are exploded-view translations.
AZ = np.deg2rad(35)
EL = np.deg2rad(12)
CAMERA = np.array([
    [np.cos(AZ), -np.sin(AZ), 0.0],
    [np.sin(EL) * np.sin(AZ), np.sin(EL) * np.cos(AZ), np.cos(EL)]
])
assert np.allclose(CAMERA @ CAMERA.T, np.eye(2))


def render_coords(u: np.ndarray, v: np.ndarray, z: np.ndarray,
                  center: tuple[float, float], scale: float) -> np.ndarray:
    u, v, z = np.broadcast_arrays(u, v, z)
    xyz = np.stack((u - .5, v - .5, z), axis=-1)
    return (xyz @ CAMERA.T) * scale + np.asarray(center)


def sheet(ax, p: Polynomial, center: tuple[float, float], scale: float,
          height: float, mesh: int, fine: int = 241,
          linewidth: float = .52, opacity: float = .62, layer: float = 1.0) -> None:
    """Draw a 3D graph as a translucent surface with a vector wire mesh."""
    def on_page(uu, vv, zz):
        coords = render_coords(uu, vv, zz, center, scale)
        ratio = ax.figure.get_figwidth() / ax.figure.get_figheight()
        coords[..., 1] = center[1] + ratio * (coords[..., 1] - center[1])
        return coords

    ss = np.linspace(0, 1, 49)
    u, v = np.meshgrid(ss, ss)
    points = on_page(u, v, height * evaluate(p, u, v))
    faces = np.stack((points[:-1, :-1], points[:-1, 1:],
                      points[1:, 1:], points[1:, :-1]), axis=2).reshape(-1, 4, 2)
    ax.add_collection(PolyCollection(faces, linewidths=0, alpha=.065, zorder=layer))

    t = np.linspace(0, 1, fine)
    lines = []
    for s in np.linspace(0, 1, mesh):
        for uu, vv in ((t, np.full_like(t, s)), (np.full_like(t, s), t)):
            lines.append(on_page(uu, vv, height * evaluate(p, uu, vv)))
    ax.add_collection(LineCollection(lines, linewidths=linewidth, alpha=opacity,
                                     zorder=layer + .1))
    edges = []
    for uu, vv in ((t, t*0), (t, t*0 + 1), (t*0, t), (t*0 + 1, t)):
        edges.append(on_page(uu, vv, height * evaluate(p, uu, vv)))
    ax.add_collection(LineCollection(edges, linewidths=.9, alpha=.8, zorder=layer + .2))


def canvas(width: float, height: float):
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('auto')
    ax.axis('off')
    return fig, ax


def text(ax, x: float, y: float, s: str, size: float = 12,
         *, family: str = 'DejaVu Sans', weight: str = 'normal',
         alpha: float = 1, ha: str = 'left', va: str = 'center', **kw):
    return ax.text(x, y, s, fontsize=size, fontfamily=family, fontweight=weight,
                   alpha=alpha, ha=ha, va=va, zorder=20, **kw)


def rule(ax, x1: float, x2: float, y: float, alpha: float = .25):
    # A patch path rather than an extra data series; no custom color or style.
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle='-', linewidth=.7,
                                alpha=alpha, zorder=10))


def arrow(ax, start, end, *, alpha=.65, linewidth=.9, dashed=False):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=9,
                                linewidth=linewidth, alpha=alpha,
                                linestyle='--' if dashed else '-', zorder=15))


def resolution_plate():
    fig, ax = canvas(14, 15.5)
    text(ax, 5.2, 96.4, 'O P E R A T I O N   K O M O R E B I', 9.2, alpha=.62)
    text(ax, 94.8, 96.4, '01  /  REALIZATION', 9.2, ha='right', alpha=.62)
    text(ax, 5.2, 92.0, 'Komorebi Space', 37, family='DejaVu Serif')
    text(ax, 5.4, 87.8, 'One realization, seen at four resolutions.', 15, alpha=.72)
    rule(ax, 5.2, 94.8, 85.1)

    text(ax, 17.0, 82.8, 'C O H E R E N T   V I E W S', 9.0, alpha=.65)
    text(ax, 75.0, 82.8, 'R E T A I N E D   D E T A I L', 9.0, ha='center', alpha=.65)
    text(ax, 75.0, 80.8, 'Detail height magnified 2×', 8.4, ha='center', alpha=.55)
    centers = [(38.0, 21.0), (38.0, 38.0), (38.0, 55.0), (38.0, 72.0)]
    # Main field height in paper coordinates: 34 * .12. Detail uses 14 * h,
    # with h chosen to give exactly twice the main vertical gain.
    main_scale, main_height, detail_scale = 34.0, .12, 14.0
    detail_height = 2.0 * main_scale * main_height / detail_scale

    for n in range(4):
        cx, cy = centers[n]
        # Sampling density resolves the highest frequency, rather than making
        # an increasingly decorative but unrelated mesh.
        sheet(ax, X[n], (cx, cy), main_scale, main_height,
              mesh=(17, 23, 33, 49)[n], linewidth=(.63, .54, .46, .34)[n],
              opacity=(.60, .61, .62, .63)[n], layer=n + 1)
        text(ax, 4.8, cy + 1.6, rf'$x_{n}$', 23, family='DejaVu Serif')
        text(ax, 4.9, cy - 1.1, rf'$|k|_\infty\leq {CUTOFFS[n]}$', 9.4, alpha=.6)
        text(ax, 4.9, cy - 3.0, rf'$\dim X_{n}={((2*CUTOFFS[n]+1)**2)}$', 8.2, alpha=.5)
        if n:
            ymid = (cy + centers[n-1][1]) / 2
            arrow(ax, (10.5, ymid+3.2), (10.5, ymid-3.2), alpha=.55)
            text(ax, 7.8, ymid, rf'$P_{n-1}$', 11.5, ha='right', alpha=.7)
            # Extracted detail belongs to ker P_(n-1).
            sheet(ax, D[n-1], (77.0, cy), detail_scale, detail_height,
                  mesh=(19, 29, 39)[n-1], linewidth=(.48, .4, .32)[n-1],
                  opacity=.63, layer=n+1)
            arrow(ax, (64.2, cy), (66.8, cy), alpha=.45, linewidth=.8)
            text(ax, 77.0, cy-5.6, rf'$d_{n-1}=x_{n}-J_{n-1}x_{n-1}$',
                 13.6, ha='center')
            text(ax, 77.0, cy-7.7, rf'$P_{n-1}d_{n-1}=0$', 10.5, ha='center', alpha=.6)

    # White space beside the coarse sheet carries the key interpretation.
    text(ax, 68.0, 25.7, 'Detail is information,', 14.6, family='DejaVu Serif')
    text(ax, 68.0, 23.3, 'not inconsistency.', 14.6, family='DejaVu Serif')
    text(ax, 68.0, 19.7, r'$P_nx_{n+1}=x_n$', 17)
    text(ax, 68.0, 17.3, 'Every restriction agrees exactly.', 9.5, alpha=.65)

    rule(ax, 5.2, 94.8, 11.5)
    text(ax, 5.4, 9.15, 'THE POINT IS THE WHOLE FAMILY', 9, alpha=.62)
    text(ax, 5.4, 6.3,
         r'$\mathcal{K}_3=\{(x_0,x_1,x_2,x_3)\in\prod_{n=0}^{3}X_n'
         r'\;:\;P_nx_{n+1}=x_n\quad(n=0,1,2)\}$', 16.8)
    text(ax, 5.4, 3.25,
         'Each sheet is one Fourier function on the square torus, not the entire space '
         r'$X_n$' + '.  Main sheets share one height scale.', 8.9, alpha=.58)
    text(ax, 5.4, 1.75,
         'Finite illustration of the realization construction. Geometry and identities are reproducible in Python.',
         8.7, alpha=.58)
    return fig


def defect_plate():
    fig, ax = canvas(14, 11)
    text(ax, 5.2, 96.0, 'O P E R A T I O N   K O M O R E B I', 9.2, alpha=.62)
    text(ax, 94.8, 96.0, '02  /  COMPATIBILITY', 9.2, ha='right', alpha=.62)
    text(ax, 5.2, 90.2, 'Detail is not inconsistency', 30, family='DejaVu Serif')
    text(ax, 5.4, 85.4, 'Change one view. The compatibility differential records exactly where agreement fails.',
         12.0, alpha=.7)
    rule(ax, 5.2, 94.8, 82.2)
    text(ax, 13.0, 78.5, 'V I E W S   O F   T H E   S A M E   F A M I L Y', 9.0, alpha=.65)
    text(ax, 74.2, 78.5, 'T Y P E D   D E F E C T S', 9.0, alpha=.65)
    text(ax, 13.0, 75.6, r'Signal slice at $v=3/16$', 9.3, alpha=.6)
    text(ax, 74.2, 75.6, r'$r_n=P_n\widetilde{x}_{n+1}-\widetilde{x}_n$', 12.3)

    t = np.linspace(0, 1, 1601)
    lane_y = [27.8, 40.8, 53.8, 66.8]
    xx, yy = [], []
    for n, y0 in enumerate(lane_y):
        xx.extend((13 + 47*t).tolist() + [np.nan])
        yy.extend((y0 + 4.7*evaluate(X[n], t, 3/16)).tolist() + [np.nan])
        text(ax, 5.6, y0, rf'$x_{n}$', 20)
        rule(ax, 13, 60, y0, alpha=.1)
        if n:
            mid = (y0 + lane_y[n-1])/2
            arrow(ax, (9.0, mid+2.0), (9.0, mid-2.0), alpha=.5)
            text(ax, 6.8, mid, rf'$P_{n-1}$', 10, alpha=.6)
    # Default color cycle distinguishes the exact and perturbed curves.
    exact, = ax.plot(xx, yy, linewidth=1.65, zorder=5)
    altered, = ax.plot(13+47*t, lane_y[2]+4.7*evaluate(Y[2], t, 3/16),
                       linewidth=1.9, linestyle=(0,(4,2)), zorder=6)
    text(ax, 13, 62.0, r'Only view 2 is changed:  $\widetilde{x}_2=x_2+\eta$',
         11.3)

    # The residual is represented in its correctly typed coarse view. It is
    # displayed with the same vertical gain as the reference waveform.
    residuals = residual(Y)
    for n in range(3):
        yc = (lane_y[n] + lane_y[n+1])/2
        rr = evaluate(residuals[n], t, 3/16)
        rule(ax, 74.2, 94.5, yc, alpha=.14)
        ax.plot(74.2+20.3*t, yc+4.7*rr, linewidth=1.65)
        label = [r'$r_0=0$', r'$r_1=+\eta$', r'$r_2=-\eta$'][n]
        text(ax, 74.2, yc+3.2, label, 13.5)
        arrow(ax, (63.3, yc), (70.5, yc), alpha=.45)
    text(ax, 74.2, 27.6, r'$\eta(u,v)=\frac{1}{5}\cos(2\pi u)$', 14)

    # Restrained legend with actual plotted handles, no boxes.
    ax.legend([exact, altered], ['coherent reference', 'altered view'],
              loc='lower left', bbox_to_anchor=(.125,.205),
              frameon=False, ncol=2, fontsize=9.5, handlelength=2.6,
              borderaxespad=0, columnspacing=2.0)

    rule(ax, 5.2, 94.8, 17.8)
    text(ax, 5.4, 14.4, 'RETAINED DETAIL', 9.1, alpha=.6)
    text(ax, 5.4, 10.9, r'$d_n=x_{n+1}-J_nx_n\in\ker P_n$', 15)
    text(ax, 5.4, 7.4, 'May be nonzero even when the family is perfectly coherent.',
         9.8, alpha=.7)
    text(ax, 55.0, 14.4, 'COMPATIBILITY DEFECT', 9.1, alpha=.6)
    text(ax, 55.0, 10.9, r'$\delta\widetilde{x}=(0,\eta,-\eta)\ne 0$', 15)
    text(ax, 55.0, 7.4, 'Subtracting '+r'$\eta$'+' from view 2 repairs this family exactly.',
         9.8, alpha=.7)
    text(ax, 5.4, 3.0,
         'This defect is repairable. A nonzero residual alone is not evidence of a nonzero extension obstruction.',
         9.4, alpha=.6)
    return fig


def check_text_bounds(fig) -> None:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bb = fig.bbox
    offenders = []
    for item in fig.findobj(Text):
        if not item.get_visible() or not item.get_text().strip():
            continue
        ext = item.get_window_extent(renderer)
        # Tick labels on disabled axes are not visible in the result.
        if (ext.x0 < bb.x0-1 or ext.y0 < bb.y0-1 or
            ext.x1 > bb.x1+1 or ext.y1 > bb.y1+1):
            offenders.append(item.get_text())
    if offenders:
        raise RuntimeError('Text outside page: '+repr(offenders))


def export(fig, stem: str, folder: Path, dpi: int) -> dict:
    check_text_bounds(fig)
    for ext in ('png', 'svg', 'pdf'):
        fig.savefig(folder / f'{stem}.{ext}', dpi=dpi)
    fig.savefig(folder / f'{stem}_preview.png', dpi=125)
    return {'name': stem, 'pixel_dimensions': [round(v*dpi) for v in fig.get_size_inches()]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--dpi', type=int, default=300)
    args = parser.parse_args()
    if not 100 <= args.dpi <= 600:
        parser.error('--dpi must be between 100 and 600')
    args.output.mkdir(parents=True, exist_ok=True)
    report = exact_verification()
    figures = [resolution_plate(), defect_plate()]
    names = ['komorebi_space_resolution', 'komorebi_space_compatibility']
    report['exports'] = [export(fig, name, args.output, args.dpi)
                         for fig, name in zip(figures, names)]
    with PdfPages(args.output / 'komorebi_space_visual_atlas.pdf') as pdf:
        pdf.infodict()['Title'] = 'Komorebi Space | Resolution and Compatibility'
        pdf.infodict()['Subject'] = 'Two explicit, reproducible mathematical visualizations'
        for fig in figures:
            pdf.savefig(fig)
    for fig in figures:
        plt.close(fig)
    (args.output / 'verification.json').write_text(json.dumps(report, indent=2)+'\n',
                                                   encoding='utf-8')
    print(f"PASS: {report['exact_checks']:,} exact rational checks.")
    print('Finite Fourier dimensions: 9, 25, 81, 289.')
    print('Coherent residual: (0, 0, 0). Altered residual: (0, eta, -eta).')
    print('Exported two figures and a two-page vector PDF to:', args.output)


if __name__ == '__main__':
    main()
