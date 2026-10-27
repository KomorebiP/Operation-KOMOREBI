from __future__ import annotations

from pathlib import Path
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif'],
    'mathtext.fontset': 'dejavuserif',
    'font.size': 9,
    'axes.titlesize': 11,
    'axes.labelsize': 9,
    'figure.dpi': 140,
    'savefig.dpi': 240,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

PALETTE = {
    'navy': '#17324d',
    'blue': '#3d6c8e',
    'lightblue': '#dbeaf4',
    'teal': '#2f7a78',
    'lightteal': '#dcefed',
    'orange': '#b56a2b',
    'lightorange': '#f4e4d3',
    'red': '#9d4b4b',
    'lightred': '#f1dddd',
    'green': '#4f774f',
    'lightgreen': '#e2eee2',
    'gray': '#5f6870',
    'lightgray': '#edf0f2',
    'dark': '#22272b',
}


def box(ax, xy, wh, text, fc, ec=None, fontsize=9, lw=1.2, radius=0.02, z=2, align='center'):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=lw,
        edgecolor=ec or PALETTE['navy'],
        facecolor=fc,
        zorder=z,
    )
    ax.add_patch(patch)
    ha = 'center' if align == 'center' else 'left'
    tx = x + w/2 if ha == 'center' else x + 0.03*w
    ax.text(tx, y+h/2, text, ha=ha, va='center', fontsize=fontsize, color=PALETTE['dark'], zorder=z+1, linespacing=1.2)
    return patch


def arrow(ax, start, end, color=None, lw=1.4, style='-|>', connectionstyle='arc3', ls='-'):
    arr = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=11,
                          linewidth=lw, color=color or PALETTE['navy'],
                          connectionstyle=connectionstyle, linestyle=ls, zorder=1)
    ax.add_patch(arr)
    return arr


def save(fig, name):
    fig.savefig(FIG / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(FIG / f'{name}.png', bbox_inches='tight')
    plt.close(fig)


# Figure 1: architecture
fig, ax = plt.subplots(figsize=(10.7, 3.25))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
xs = [0.015, 0.215, 0.415, 0.615, 0.815]
labels = [
    'Resolved syntax\n$\\mathbb{K}$\n\npackets, refinements,\nresiduals, certificates',
    'Profiled strata\n$\\mathbf{S}_{\\alpha}$\n\nmodels with declared\npreservation profiles',
    'Typed atlas\n$\\mathfrak{R}$\n\nreversible overlaps and\ndirectional bridges',
    'Coherence and\neffective descent\n\nobjects, morphisms,\nand local isomorphisms',
    'Global resolved\ncategory\n$\\mathrm{Desc}(\\mathfrak{R})$\n\ncompatible invariants',
]
fcs = [PALETTE['lightblue'], PALETTE['lightteal'], PALETTE['lightorange'], PALETTE['lightred'], PALETTE['lightgreen']]
for x, lab, fc in zip(xs, labels, fcs):
    box(ax, (x, 0.28), (0.17, 0.47), lab, fc, fontsize=8.4)
for i in range(4):
    arrow(ax, (xs[i]+0.17, 0.515), (xs[i+1], 0.515), lw=1.7)
ax.text(0.5, 0.92, 'Relative stratified universality', ha='center', va='center', fontsize=14, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.09,
        'Universality is relative to the declared grammar, strata, bridges, preservation profiles, and normalization targets.',
        ha='center', va='center', fontsize=8.6, color=PALETTE['gray'])
save(fig, 'architecture')


# Figure 2: status counts
json_path = ROOT / 'Komorebi_Theorem_Concordance_v0.2.json'
data = json.loads(json_path.read_text(encoding='utf-8'))
status_counts = data['summary']['status_counts']
row_count = int(data['summary']['row_count'])
order = [
    'proved internally',
    'classical theorem imported and reinterpreted',
    'proved conditionally',
    'definition or framework only',
    'conjectural',
]
short = ['Internal proof', 'Imported classical', 'Conditional proof', 'Framework only', 'Conjectural']
vals = [status_counts[k] for k in order]
fig, ax = plt.subplots(figsize=(8.5, 3.35))
bars = ax.barh(range(len(vals)), vals, color=[PALETTE['blue'], PALETTE['teal'], PALETTE['orange'], PALETTE['gray'], PALETTE['red']])
ax.set_yticks(range(len(vals)), short)
ax.invert_yaxis()
ax.set_xlabel('Number of concordance components')
ax.set_title('Theorem-concordance status distribution')
ax.set_xlim(0, max(vals) * 1.14)
ax.grid(axis='x', alpha=0.22)
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
for bar, val in zip(bars, vals):
    ax.text(val + 0.4, bar.get_y() + bar.get_height()/2, str(val), va='center', fontsize=9)
ax.text(0.99, -0.18, f'{row_count} audited components total', transform=ax.transAxes, ha='right', fontsize=8.5, color=PALETTE['gray'])
save(fig, 'status_counts')


# Figure 3: dependency graph
fig, ax = plt.subplots(figsize=(11.2, 6.7))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
# Source layer
source_x = [0.025, 0.22, 0.415, 0.61, 0.805]
source_labels = [
    'Paper I\nlinear syntax and\npreservation profiles',
    'Resolution Theory\ncorners, completion,\nnonlinear operad',
    'Paper III / Core Transfer\nobstructions, holonomy,\nverified finite atlases',
    'Galois / Projector Calculus\nsemilinear descent, Brauer,\nresolution limits',
    'Sequence / Cartier strata\nexact bridges and\nrestricted invariants',
]
for x, lab in zip(source_x, source_labels):
    box(ax, (x, 0.80), (0.17, 0.12), lab, PALETTE['lightblue'], fontsize=7.5)
# obligation chain
chain_x = [0.045, 0.225, 0.405, 0.585, 0.765]
chain_w = [0.145, 0.145, 0.145, 0.145, 0.205]
chain_labels = [
    'Profile-indexed\nenvelope',
    'Declared atlas\nand morphisms',
    'Bridge laws and\nhigher coherence',
    'Effective descent\nobjects + morphisms',
    'Invariant comparisons\nand isomorphism descent',
]
chain_fc = [PALETTE['lightteal'], PALETTE['lightteal'], PALETTE['lightorange'], PALETTE['lightred'], PALETTE['lightgreen']]
for x, w, lab, fc in zip(chain_x, chain_w, chain_labels, chain_fc):
    box(ax, (x, 0.48), (w, 0.12), lab, fc, fontsize=7.8 if w < 0.2 else 7.4)
for i in range(4):
    arrow(ax, (chain_x[i]+chain_w[i], 0.54), (chain_x[i+1], 0.54), lw=1.5)
# source arrows
for sx in source_x[:2]:
    arrow(ax, (sx+0.085, 0.80), (chain_x[0]+chain_w[0]/2, 0.60), lw=1.0, color=PALETTE['gray'])
arrow(ax, (source_x[4]+0.085, 0.80), (chain_x[1]+chain_w[1]/2, 0.60), lw=1.0, color=PALETTE['gray'])
arrow(ax, (source_x[2]+0.085, 0.80), (chain_x[2]+chain_w[2]/2, 0.60), lw=1.0, color=PALETTE['gray'])
arrow(ax, (source_x[3]+0.085, 0.80), (chain_x[3]+chain_w[3]/2, 0.60), lw=1.0, color=PALETTE['gray'])
# theorem / global
box(ax, (0.295, 0.20), (0.225, 0.13), 'Finite Profiled Resolved\nAtlas Assembly Theorem', PALETTE['lightorange'], fontsize=8.9, lw=1.5)
box(ax, (0.575, 0.20), (0.245, 0.13), 'Relative stratified universality\non declared normalized domains', PALETTE['lightgreen'], fontsize=8.8, lw=1.5)
for x, w in zip(chain_x, chain_w):
    arrow(ax, (x+w/2, 0.48), (0.407, 0.33), lw=0.95, color=PALETTE['gray'])
arrow(ax, (0.520, 0.265), (0.575, 0.265), lw=1.8)
# directional side lane
box(ax, (0.02, 0.145), (0.22, 0.18), 'Directed transformations\n\nquotient, truncation, completion\nalgebraic $\\to$ D-finite\nfunctional Mahler $\\to$ automaton', PALETTE['lightgray'], fontsize=6.8, ec=PALETTE['gray'])
arrow(ax, (0.24, 0.235), (0.295, 0.235), lw=1.0, color=PALETTE['gray'], ls='--')
ax.text(0.5, 0.965, 'Correct dependency order', ha='center', fontsize=14, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.06, 'Pairwise formulas do not by themselves define a coherent atlas, and local completeness does not by itself glue local isomorphisms.',
        ha='center', fontsize=8.3, color=PALETTE['gray'])
save(fig, 'dependency_graph')


# Figure 4: obstruction taxonomy
fig, ax = plt.subplots(figsize=(10.2, 4.3))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.38, 0.72), (0.24, 0.14), 'Failure of global\ntrivialization or gluing', PALETTE['lightgray'], fontsize=11, lw=1.6)
centers = [(0.12, 0.25), (0.37, 0.25), (0.62, 0.25), (0.87, 0.25)]
labels = [
    ('Holonomy', 'path dependence in a finite\ntransport or chart graph', PALETTE['lightblue']),
    ('Relative cokernel class', r'$[r]\in\mathrm{coker}\,D$' + '\nfor a declared correction map', PALETTE['lightorange']),
    ('Brauer class', 'failure to lift a projective\nGalois atlas to a linear one', PALETTE['lightred']),
    ('Higher coherence defect', 'failure of comparison\n$2$-cells on triple or\nquadruple overlaps', PALETTE['lightgreen']),
]
for (cx, cy), (title, body, fc) in zip(centers, labels):
    box(ax, (cx-0.105, cy-0.12), (0.21, 0.24), f'{title}\n\n{body}', fc, fontsize=7.8)
    arrow(ax, (0.50, 0.72), (cx, cy+0.12), lw=1.2, color=PALETTE['gray'])
ax.text(0.5, 0.94, 'Distinct obstruction objects belong to distinct failure modes', ha='center', fontsize=13, fontweight='bold', color=PALETTE['navy'])
save(fig, 'obstruction_taxonomy')


# Figure 5: C-finite triangle
fig, ax = plt.subplots(figsize=(7.6, 5.9))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
pts = {
    'rec': (0.17, 0.73),
    'rat': (0.83, 0.73),
    'state': (0.50, 0.19),
}
box(ax, (pts['rec'][0]-0.14, pts['rec'][1]-0.095), (0.28, 0.19), 'Normalized minimal\nrecurrence + initial data', PALETTE['lightblue'], fontsize=9.2, lw=1.5)
box(ax, (pts['rat'][0]-0.14, pts['rat'][1]-0.095), (0.28, 0.19), 'Reduced rational OGF\n$P(z)/Q(z)$, $Q(0)=1$', PALETTE['lightteal'], fontsize=9.2, lw=1.5)
box(ax, (pts['state'][0]-0.16, pts['state'][1]-0.095), (0.32, 0.19), 'Minimal reachable-observable\nstate $(C,v,\\lambda)$ up to similarity', PALETTE['lightorange'], fontsize=9.0, lw=1.5)
# double arrows
arrow(ax, (0.31, 0.75), (0.69, 0.75), style='<|-|>', lw=1.6)
arrow(ax, (0.25, 0.64), (0.43, 0.30), style='<|-|>', lw=1.6)
arrow(ax, (0.75, 0.64), (0.57, 0.30), style='<|-|>', lw=1.6)
ax.text(0.50, 0.82, 'clearing / recovering the denominator', ha='center', fontsize=7.7, color=PALETTE['gray'])
ax.text(0.285, 0.45, 'companion\nconstruction', ha='center', fontsize=7.6, color=PALETTE['gray'])
ax.text(0.715, 0.45, 'resolvent +\nminimal reduction', ha='center', fontsize=7.6, color=PALETTE['gray'])
# center invariant
circ = Circle((0.50, 0.52), 0.105, facecolor=PALETTE['lightgreen'], edgecolor=PALETTE['green'], lw=1.4, zorder=3)
ax.add_patch(circ)
ax.text(0.50, 0.52, 'shared semantics\n+ minimal dimension\n+ torsion--Fourier\npacket profile', ha='center', va='center', fontsize=7.7, zorder=4)
ax.text(0.5, 0.95, 'The normalized C-finite three-chart atlas', ha='center', fontsize=13.5, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.035, 'The state-side composite closes by the unique similarity between minimal realizations.', ha='center', fontsize=8.2, color=PALETTE['gray'])
save(fig, 'cfinite_triangle')


# Figure 6: Mahler models
fig, ax = plt.subplots(figsize=(10.5, 4.1))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
# left groupoid
ax.text(0.25, 0.92, 'Affine-Mahler chart groupoid', ha='center', fontsize=11.5, fontweight='bold', color=PALETTE['navy'])
coords = [(0.08, 0.56), (0.32, 0.68), (0.32, 0.38)]
for i, (x,y) in enumerate(coords):
    box(ax, (x, y), (0.15, 0.14), f'chart {i+1}\n$A_{{m,s}}^{{(d)}}$', PALETTE['lightblue'], fontsize=8.5)
arrow(ax, (0.23, 0.63), (0.32, 0.73), style='<|-|>', lw=1.4)
arrow(ax, (0.23, 0.60), (0.32, 0.45), style='<|-|>', lw=1.4)
arrow(ax, (0.395, 0.52), (0.395, 0.66), style='<|-|>', lw=1.4)
ax.text(0.245, 0.21, '$A_{n,t}^{(d)}A_{m,s}^{(d)}=A_{mn,mt+s}^{(d)}$\nCRT diamonds commute exactly', ha='center', fontsize=8.4)
# divider
ax.plot([0.50,0.50],[0.08,0.92], color=PALETTE['lightgray'], lw=2)
# right split
ax.text(0.75, 0.92, 'Integral split packet descent', ha='center', fontsize=11.5, fontweight='bold', color=PALETTE['navy'])
box(ax, (0.56, 0.52), (0.17, 0.17), 'source chart\n$\\mathbb{Z}^{d+1}$', PALETTE['lightteal'], fontsize=9)
box(ax, (0.80, 0.52), (0.17, 0.17), 'packet space\n$\\mathbb{Z}^{|S|(d+1)}$', PALETTE['lightorange'], fontsize=8.7)
arrow(ax, (0.73, 0.63), (0.80, 0.63), lw=1.5)
arrow(ax, (0.80, 0.57), (0.73, 0.57), lw=1.5)
ax.text(0.765, 0.68, '$A$', fontsize=9, ha='center')
ax.text(0.765, 0.50, '$L$', fontsize=9, ha='center')
box(ax, (0.63, 0.20), (0.24, 0.14), r'$\mathrm{im}\,A$' + '\nconsistent packet core', PALETTE['lightgreen'], fontsize=9)
box(ax, (0.88, 0.20), (0.10, 0.14), '$\\ker L$\nnamed\nresidual', PALETTE['lightred'], fontsize=7.8)
arrow(ax, (0.885, 0.52), (0.75, 0.34), lw=1.1, color=PALETTE['gray'])
arrow(ax, (0.91, 0.52), (0.93, 0.34), lw=1.1, color=PALETTE['gray'])
ax.text(0.75, 0.09, r'$LA=I$, $\Pi=AL$, and $Y=\mathrm{im}\,A\oplus\ker L$', ha='center', fontsize=8.4)
save(fig, 'mahler_models')



# Figure 7: stratum passport
fig, ax = plt.subplots(figsize=(10.8, 4.8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.37, 0.38), (0.26, 0.24),
    'Profiled stratum passport\n$\\mathbf{S}_\\alpha$\n\nrealization data\nclassification data',
    PALETTE['lightgray'], fontsize=9.3, lw=1.7)
items = [
    ((0.03, 0.69), (0.23, 0.16), 'Ambient category\n$\\mathcal{C}_\\alpha$', PALETTE['lightblue']),
    ((0.03, 0.39), (0.23, 0.16), 'Admissible models\n$\\mathcal{M}_\\alpha$', PALETTE['lightteal']),
    ((0.03, 0.09), (0.23, 0.16), 'Preservation profile\n$\\Pi_\\alpha$', PALETTE['lightorange']),
    ((0.74, 0.69), (0.23, 0.16), 'Native semantics\n$\\mathrm{Sem}_\\alpha$', PALETTE['lightblue']),
    ((0.74, 0.39), (0.23, 0.16), 'Normalized slice\n$\\mathcal{N}_\\alpha$', PALETTE['lightgreen']),
    ((0.74, 0.09), (0.23, 0.16), 'Invariant target\n$\\mathcal{I}_\\alpha:\\mathcal{N}_\\alpha^\\simeq\\to\\mathcal{D}_\\alpha$', PALETTE['lightred']),
]
for (xy, wh, label, fc) in items:
    box(ax, xy, wh, label, fc, fontsize=8.6)
    sx = xy[0] + wh[0] if xy[0] < 0.5 else xy[0]
    ex = 0.37 if xy[0] < 0.5 else 0.63
    y = xy[1] + wh[1] / 2
    arrow(ax, (sx, y), (ex, 0.50), lw=1.15, color=PALETTE['gray'])
ax.text(0.5, 0.94, 'A chart is a typed passport, not merely a collection of examples',
        ha='center', fontsize=13.2, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.025,
        'Normalization and completeness are optional theorem fields; they are not inferred from the existence of a realization.',
        ha='center', fontsize=8.2, color=PALETTE['gray'])
save(fig, 'stratum_passport')


# Figure 8: bridge passport and information loss
fig, ax = plt.subplots(figsize=(11.0, 5.15))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.03, 0.56), (0.20, 0.22), 'Source chart\n$\\mathcal{U}_\\mathfrak{b}$\n\nmodels + native certificates', PALETTE['lightblue'], fontsize=9.0)
box(ax, (0.77, 0.56), (0.20, 0.22), 'Target chart\n$\\mathcal{V}_\\mathfrak{b}$\n\nimage + target certificates', PALETTE['lightteal'], fontsize=9.0)
box(ax, (0.36, 0.49), (0.28, 0.34),
    'Bridge passport $\\mathfrak{b}$\n\nclass and exact domain\npreserved / reflected structure\nsemantic comparison\nnormalization and certificate law\ninformation-loss profile',
    PALETTE['lightorange'], fontsize=8.6, lw=1.6)
arrow(ax, (0.23, 0.67), (0.36, 0.67), lw=1.8)
arrow(ax, (0.64, 0.67), (0.77, 0.67), lw=1.8)
# reversible lane
box(ax, (0.30, 0.80), (0.40, 0.09), 'Reversible core: equivalence only after an inverse or recognition theorem', PALETTE['lightgreen'], fontsize=8.2, ec=PALETTE['green'])
arrow(ax, (0.40, 0.80), (0.28, 0.78), style='<|-|>', lw=1.2, color=PALETTE['green'])
arrow(ax, (0.60, 0.80), (0.72, 0.78), style='<|-|>', lw=1.2, color=PALETTE['green'])
# loss boxes
losses = [
    (0.03, 'morphism\ncollapse', PALETTE['lightred']),
    (0.23, 'object\ncollapse', PALETTE['lightred']),
    (0.43, 'essential-image\nrestriction', PALETTE['lightgray']),
    (0.63, 'constructor /\nbranch loss', PALETTE['lightgray']),
    (0.83, 'residual /\ncertificate loss', PALETTE['lightred']),
]
for x, lab, fc in losses:
    box(ax, (x, 0.12), (0.14, 0.16), lab, fc, fontsize=7.7, ec=PALETTE['gray'])
    arrow(ax, (0.50, 0.49), (x+0.07, 0.28), lw=0.95, color=PALETTE['gray'])
ax.text(0.5, 0.985, 'Typed bridges: reversible equivalence above, directional information loss below',
        ha='center', va='top', fontsize=12.2, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.035,
        'A later constructor may attach auxiliary data, but it does not retroactively make an earlier forgetful functor faithful.',
        ha='center', fontsize=8.1, color=PALETTE['gray'])
save(fig, 'bridge_passport_and_loss')


# Figure 9: maximal flat core and holonomy rank
fig, ax = plt.subplots(figsize=(10.7, 4.8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
# graph panel
nodes = {'o': (0.10, 0.55), 'u': (0.28, 0.78), 'v': (0.43, 0.55), 'w': (0.28, 0.30)}
for name, (x, y) in nodes.items():
    circ = Circle((x, y), 0.038, facecolor=PALETTE['lightblue'], edgecolor=PALETTE['navy'], lw=1.4, zorder=3)
    ax.add_patch(circ)
    ax.text(x, y, name, ha='center', va='center', fontsize=9, zorder=4)
# spanning tree edges
for a, b in [('o','u'),('u','v'),('o','w')]:
    arrow(ax, nodes[a], nodes[b], style='-|>', lw=2.0, color=PALETTE['blue'])
# non-tree edges
for a, b in [('w','v'),('v','o')]:
    arrow(ax, nodes[a], nodes[b], style='-|>', lw=2.0, color=PALETTE['red'])
ax.text(0.27, 0.84, 'Tree gauge + non-tree cycle edges', ha='center', fontsize=11.2, fontweight='bold', color=PALETTE['navy'])
ax.text(0.20, 0.15, 'blue: spanning tree', color=PALETTE['blue'], fontsize=8.2)
ax.text(0.34, 0.15, 'red: fundamental cycles', color=PALETTE['red'], fontsize=8.2)
# arrow to holonomy
arrow(ax, (0.48, 0.55), (0.55, 0.55), lw=1.7)
box(ax, (0.55, 0.63), (0.18, 0.18), 'Fundamental holonomies\n$H_e=G_v^{-1}T_eG_u$', PALETTE['lightorange'], fontsize=8.6)
box(ax, (0.55, 0.31), (0.18, 0.18), 'Stacked defect map\n$\\Delta_Sx=((H_e-I)x)_e$', PALETTE['lightred'], fontsize=8.2)
arrow(ax, (0.64, 0.63), (0.64, 0.49), lw=1.4)
box(ax, (0.79, 0.47), (0.18, 0.22), 'Maximal path-flat core\n$C_o=\\ker\\Delta_S$\n\n$\\dim C_o=\\dim F_o-\\mathrm{rank}\\,\\Delta_S$', PALETTE['lightgreen'], fontsize=8.1, lw=1.5)
arrow(ax, (0.73, 0.40), (0.79, 0.53), lw=1.5)
ax.text(0.5, 0.985, 'Finite holonomy selects the greatest path-independent subfamily',
        ha='center', va='top', fontsize=12.3, fontweight='bold', color=PALETTE['navy'])
ax.text(0.79, 0.16, 'Full global frame iff every $H_e=I$', ha='center', fontsize=8.5, color=PALETTE['gray'])
save(fig, 'flat_core_holonomy')


# Figure 10: obstruction comparison pipelines
fig, ax = plt.subplots(figsize=(11.2, 5.4))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
cols = [0.02, 0.265, 0.51, 0.755]
width = 0.225
pipelines = [
    ('Finite transport', 'edge isomorphisms\n+ graph cycles', 'holonomies $H_e$\n/ fixed core', 'identity holonomy\n$\\Rightarrow$ global frame', PALETTE['lightblue']),
    ('Correction problem', 'map $D:U\\to V$\n+ defect $r$', '$[r]\\in\\mathrm{coker}\\,D$\n/ cone class', 'zero class\n$\\Rightarrow$ correction exists', PALETTE['lightorange']),
    ('Projective descent', '$PGL_n$ cocycle\nover $L/K$', '$\\delta(\\alpha)\\in\\mathrm{Br}(L/K)$', 'zero class\n$\\Rightarrow$ linear lift', PALETTE['lightred']),
    ('Atlas coherence', 'pairwise equivalences\n+ comparison $2$-cells', '$\\Omega_{\\alpha\\beta\\gamma\\delta}$\nnatural automorphism', '$\\Omega=\\mathrm{id}$\n$\\Rightarrow$ pseudofunctor coherence', PALETTE['lightgreen']),
]
for x, (title, datum, obs, vanish, fc) in zip(cols, pipelines):
    box(ax, (x, 0.78), (width, 0.12), title, PALETTE['lightgray'], fontsize=9.2, lw=1.4)
    box(ax, (x, 0.56), (width, 0.14), datum, fc, fontsize=8.0)
    arrow(ax, (x+width/2, 0.56), (x+width/2, 0.48), lw=1.2)
    box(ax, (x, 0.34), (width, 0.14), obs, fc, fontsize=8.2, lw=1.4)
    arrow(ax, (x+width/2, 0.34), (x+width/2, 0.26), lw=1.2)
    box(ax, (x, 0.08), (width, 0.18), vanish, PALETTE['lightgreen'], fontsize=8.0, ec=PALETTE['green'])
ax.text(0.5, 0.98, 'Four obstruction roles with different inputs and different vanishing conclusions',
        ha='center', va='top', fontsize=13.0, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.015, 'No cross-comparison is canonical until a typed map between the underlying data has been supplied.',
        ha='center', fontsize=8.2, color=PALETTE['gray'])
save(fig, 'obstruction_comparison')

print(f'Generated figures in {FIG}')

# Figure 11: first heterogeneous periodic atlas
fig, ax = plt.subplots(figsize=(10.8, 6.0))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
charts = {
    'rec': (0.06, 0.69, 0.24, 0.17, 'Linear stratum\nminimal invertible recurrence\n' + r'$\mathbf{Rec}^{\times,\mathrm{per}}_p$', PALETTE['lightblue']),
    'rat': (0.38, 0.76, 0.24, 0.17, 'Linear stratum\nreduced periodic OGF\n' + r'$\mathbf{Rat}^{\times,\mathrm{per}}_p$', PALETTE['lightteal']),
    'aut': (0.70, 0.69, 0.24, 0.17, 'Digital stratum\nminimal LSD-first ' + r'$p$' + '-DFAO\n' + r'$\mathbf{Aut}^{\times,\mathrm{per}}_p$', PALETTE['lightorange']),
    'mask': (0.38, 0.20, 0.24, 0.17, 'Functional-Mahler stratum\nreduced rational mask\n' + r'$\mathbf{Mask}^{\times,\mathrm{per}}_p$', PALETTE['lightred']),
}
for _, (x0, y0, w, h, lab, fc) in charts.items():
    box(ax, (x0, y0), (w, h), lab, fc, fontsize=8.5, lw=1.5)
arrow(ax, (0.30, 0.775), (0.38, 0.825), style='<|-|>', lw=1.6)
arrow(ax, (0.62, 0.825), (0.70, 0.775), style='<|-|>', lw=1.6)
arrow(ax, (0.18, 0.69), (0.45, 0.37), style='<|-|>', lw=1.35, connectionstyle='arc3,rad=0.05')
arrow(ax, (0.82, 0.69), (0.55, 0.37), style='<|-|>', lw=1.35, connectionstyle='arc3,rad=-0.05')
arrow(ax, (0.50, 0.76), (0.50, 0.37), style='<|-|>', lw=1.7)
circ = Circle((0.50, 0.54), 0.11, facecolor=PALETTE['lightgreen'], edgecolor=PALETTE['green'], lw=1.5, zorder=4)
ax.add_patch(circ)
ax.text(0.50, 0.54, 'shared semantic doctrine\nunit purely periodic\nsequences over ' + r'$\mathbb{F}_p$', ha='center', va='center', fontsize=8.2, zorder=5)
for key in ['rec', 'rat', 'aut', 'mask']:
    x0, y0, w, h, _, _ = charts[key]
    cx, cy = x0 + w/2, y0 + h/2
    arrow(ax, (cx, cy), (0.50, 0.54), lw=0.9, color=PALETTE['gray'], ls='--')
box(ax, (0.70, 0.18), (0.24, 0.19), 'Directional compiler lane\nCartier numerator states\n' + r'$D+1$' + ' dimensional bound\nthen reachable/output minimization', PALETTE['lightgray'], fontsize=7.8, ec=PALETTE['gray'])
arrow(ax, (0.62, 0.285), (0.70, 0.285), lw=1.5, color=PALETTE['gray'])
arrow(ax, (0.82, 0.37), (0.82, 0.69), lw=1.5, color=PALETTE['gray'])
ax.text(0.82, 0.47, 'quotient to\nminimal kernel', ha='center', fontsize=7.2, color=PALETTE['gray'])
ax.text(0.5, 0.97, 'The first finite heterogeneous effective-descent atlas', ha='center', va='top', fontsize=13.2, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.07, 'The reversible core spans linear, digital, and functional-Mahler strata. The raw Cartier compiler remains directional.', ha='center', fontsize=8.2, color=PALETTE['gray'])
save(fig, 'periodic_heterogeneous_atlas')

# Figure 12: coherence tetrahedron
fig, ax = plt.subplots(figsize=(9.2, 6.35))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
pts = {'Rec': (0.16, 0.70), 'Rat': (0.50, 0.82), 'Aut': (0.84, 0.70), 'Mask': (0.50, 0.16)}
fcmap = {'Rec': PALETTE['lightblue'], 'Rat': PALETTE['lightteal'], 'Aut': PALETTE['lightorange'], 'Mask': PALETTE['lightred']}
edges = [('Rec','Rat'),('Rat','Aut'),('Aut','Mask'),('Mask','Rec'),('Rec','Aut'),('Rat','Mask')]
for a,b in edges:
    arrow(ax, pts[a], pts[b], style='<|-|>', lw=1.15, color=PALETTE['gray'])
for name,(x0,y0) in pts.items():
    box(ax, (x0-0.095,y0-0.05),(0.19,0.10), name, fcmap[name], fontsize=9.5, lw=1.4)
face_data = [((0.50,0.69),'Rec--Rat--Aut'),((0.34,0.43),'Rec--Rat--Mask'),((0.66,0.43),'Rat--Aut--Mask'),((0.50,0.55),'Rec--Aut--Mask')]
for (x0,y0),lab in face_data:
    ax.text(x0,y0,lab,ha='center',va='center',fontsize=7.5,color=PALETTE['gray'],bbox=dict(boxstyle='round,pad=0.18',facecolor='white',edgecolor='none',alpha=0.9))
circ = Circle((0.50,0.49),0.085,facecolor=PALETTE['lightgreen'],edgecolor=PALETTE['green'],lw=1.4,zorder=4)
ax.add_patch(circ)
ax.text(0.50,0.49,'contractible\nnormalized fiber',ha='center',va='center',fontsize=8.0,zorder=5)
ax.text(0.5,0.965,'All four triple overlaps and the quadruple coherence law',ha='center',va='top',fontsize=12.5,fontweight='bold',color=PALETTE['navy'])
ax.text(0.5,0.035,'Each normalized presentation over a fixed sequence has only the identity automorphism; every comparison cell is therefore unique.',ha='center',fontsize=8.0,color=PALETTE['gray'])
save(fig,'periodic_coherence_tetrahedron')

# Figure 13: Cartier compiler reduction
fig, ax = plt.subplots(figsize=(10.7, 5.6))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
# Top row
box(ax,(0.035,0.58),(0.22,0.22),'Reduced rational mask\n' + r'$R=A/B$',PALETTE['lightred'],fontsize=9.0,lw=1.35)
box(ax,(0.39,0.55),(0.24,0.28),'Invariant numerator space\n' + r'$\deg P\leq D$' + '\n' + r'$D=\max\{b,\lceil(a+(p-2)b)/(p-1)\rceil\}$',PALETTE['lightorange'],fontsize=7.7,lw=1.35)
box(ax,(0.745,0.58),(0.22,0.22),'Reachable output automaton\n' + r'$\leq p^{D+1}$' + ' states',PALETTE['lightblue'],fontsize=8.6,lw=1.35)
arrow(ax,(0.255,0.69),(0.39,0.69),lw=1.7)
arrow(ax,(0.63,0.69),(0.745,0.69),lw=1.7)
ax.text(0.32,0.76,'Frobenius\nstabilization',ha='center',fontsize=7.4,color=PALETTE['gray'])
# Bottom row
box(ax,(0.22,0.17),(0.25,0.22),'Reachable restriction\nremoves ambient states\nnot generated from the mask',PALETTE['lightgray'],fontsize=8.2,lw=1.35,ec=PALETTE['gray'])
box(ax,(0.58,0.17),(0.25,0.22),'Canonical minimal ' + r'$p$' + '-kernel DFAO\n' + r'$|\mathcal{K}_p(a)|$' + ' states',PALETTE['lightgreen'],fontsize=8.5,lw=1.35)
arrow(ax,(0.855,0.58),(0.455,0.39),lw=1.5,connectionstyle='arc3,rad=-0.12')
arrow(ax,(0.47,0.28),(0.58,0.28),lw=1.7)
ax.text(0.72,0.45,'preserve all coefficients\nretain the exact reachable core',ha='center',fontsize=7.6,color=PALETTE['gray'])
ax.text(0.5,0.94,'The directional compiler and its reversible minimal core',ha='center',fontsize=12.7,fontweight='bold',color=PALETTE['navy'])
ax.text(0.5,0.055,'The raw compiler is directional. Block 04 proves that fixed-denominator injectivity makes the reachable core itself minimal.',ha='center',fontsize=8.1,color=PALETTE['gray'])
save(fig,'cartier_compiler_reduction')
# Figure 14: exact periodic examples and their minimal automata
validation_path = ROOT / 'generated' / 'block03_periodic_atlas_validation.json'
validation = json.loads(validation_path.read_text(encoding='utf-8'))
example_specs = [
    ('even_indicator_F2', r'$p=2$, word $10$', r'$F=1/(1+z^2)$' + '\n' + r'$R=1+z^2$'),
    ('alternating_unit_F3', r'$p=3$, word $12$', r'$F=1/(1+z)$' + '\n' + r'$R=1+2z+z^2$'),
    ('period_three_F2', r'$p=2$, word $110$', r'$F=1/(1+z+z^2)$' + '\n' + r'$R=1+z+z^2$'),
]
fig, axes = plt.subplots(1,3,figsize=(11.5,4.2))
for ax, (key,title,formula) in zip(axes,example_specs):
    row = validation['named_examples'][key]
    aut = row['automaton']
    trans = {int(k): v for k,v in aut['transitions'].items()}
    outs = {int(k): v for k,v in aut['outputs'].items()}
    nstates = aut['state_count']
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    coords={0:(0.30,0.52),1:(0.70,0.52)} if nstates == 2 else {0:(0.50,0.73),1:(0.25,0.34),2:(0.75,0.34)}
    for s in range(nstates):
        targets={}
        for d,t in enumerate(trans[s]):
            targets.setdefault(t,[]).append(str(d))
        for t,digs in targets.items():
            if s==t:
                x0,y0=coords[s]
                arr=FancyArrowPatch((x0-0.025,y0+0.055),(x0+0.025,y0+0.055),arrowstyle='-|>',mutation_scale=9,connectionstyle='arc3,rad=-1.3',linewidth=1.0,color=PALETTE['gray'])
                ax.add_patch(arr)
                ax.text(x0,y0+0.17,','.join(digs),ha='center',fontsize=7.2)
            else:
                x0,y0=coords[s]; x1,y1=coords[t]
                rad=0.16 if s<t else -0.16
                arr=FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=9,connectionstyle=f'arc3,rad={rad}',linewidth=1.0,color=PALETTE['gray'])
                ax.add_patch(arr)
                ax.text((x0+x1)/2,(y0+y1)/2 + (0.07 if rad>0 else -0.07),','.join(digs),ha='center',fontsize=7.2)
    for s,(x0,y0) in coords.items():
        circ=Circle((x0,y0),0.065,facecolor=PALETTE['lightblue'] if s==aut['start_state'] else PALETTE['lightgreen'],edgecolor=PALETTE['navy'],lw=1.2,zorder=4)
        ax.add_patch(circ)
        ax.text(x0,y0,f'{s}|{outs[s]}',ha='center',va='center',fontsize=8.0,zorder=5)
    ax.set_title(title,fontsize=10.5,fontweight='bold',color=PALETTE['navy'])
    ax.text(0.5,0.08,formula,ha='center',va='center',fontsize=7.9)
    ax.text(0.5,0.95,f"minimal kernel: {row['p_kernel_states']} states; compiler bound: {row['compiler_automaton_bound']}",ha='center',fontsize=7.3,color=PALETTE['gray'])
fig.suptitle('Exact unit-periodic examples across linear, digital, and functional-Mahler charts',fontsize=13.0,fontweight='bold',color=PALETTE['navy'],y=1.02)
fig.tight_layout()
save(fig,'periodic_example_automata')

# Figure 15: rational-mask digital atlas beyond periodicity
fig, ax = plt.subplots(figsize=(10.9, 5.8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.055, 0.61), (0.25, 0.20), 'Functional-Mahler chart\nreduced rational mask\n' + r'$R=A/B$', PALETTE['lightred'], fontsize=9.0, lw=1.5)
box(ax, (0.375, 0.69), (0.25, 0.20), 'Finite linear digit chart\nminimal Cartier module\n' + r'$\mathcal{V}_p(F)$', PALETTE['lightblue'], fontsize=8.9, lw=1.5)
box(ax, (0.695, 0.61), (0.25, 0.20), 'Digital chart\nminimal ' + r'$p$' + '-kernel DFAO\n' + r'$\mathcal{A}_p(F)$', PALETTE['lightorange'], fontsize=8.9, lw=1.5)
arrow(ax, (0.305, 0.72), (0.375, 0.79), style='<|-|>', lw=1.6)
arrow(ax, (0.625, 0.79), (0.695, 0.72), style='<|-|>', lw=1.6)
arrow(ax, (0.18, 0.61), (0.78, 0.61), style='<|-|>', lw=1.2, connectionstyle='arc3,rad=0.18', color=PALETTE['gray'])
circ = Circle((0.50, 0.45), 0.13, facecolor=PALETTE['lightgreen'], edgecolor=PALETTE['green'], lw=1.5, zorder=4)
ax.add_patch(circ)
ax.text(0.50, 0.45, 'unit formal series\nwith rational canonical mask\n' + r'$F/F(z^p)\in\mathbb{F}_p(z)$', ha='center', va='center', fontsize=8.4, zorder=5)
for cx, cy in [(0.18, 0.71), (0.50, 0.79), (0.82, 0.71)]:
    arrow(ax, (cx, cy), (0.50, 0.45), lw=0.9, color=PALETTE['gray'], ls='--')
box(ax, (0.09, 0.12), (0.31, 0.18), 'Directional compiler lane\nambient numerator space ' + r'$\mathbb{F}_p[z]_{\leq D}$' + '\nfixed denominator and digit matrices', PALETTE['lightgray'], fontsize=8.1, ec=PALETTE['gray'])
box(ax, (0.60, 0.12), (0.31, 0.18), 'Exact normalized core\nreachable numerator states ' + r'$\cong\mathcal{K}_p(F)$' + '\nreachable span ' + r'$\cong\mathcal{V}_p(F)$', PALETTE['lightteal'], fontsize=8.0, ec=PALETTE['teal'])
arrow(ax, (0.40, 0.21), (0.60, 0.21), lw=1.7, color=PALETTE['gray'])
ax.text(0.50, 0.27, 'reachability only', ha='center', fontsize=7.4, color=PALETTE['gray'])
arrow(ax, (0.755, 0.30), (0.755, 0.61), lw=1.2, color=PALETTE['gray'])
ax.text(0.5, 0.965, 'Rational-mask digital descent beyond pure periodicity', ha='center', va='top', fontsize=13.2, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.045, 'The reversible core spans functional-Mahler, finite linear digit, and digital strata. The full polynomial compiler remains a directional construction.', ha='center', fontsize=8.1, color=PALETTE['gray'])
save(fig, 'rational_mask_digital_atlas')

# Figure 16: exact state-complexity hierarchy
fig, ax = plt.subplots(figsize=(10.8, 5.0))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.035, 0.57), (0.20, 0.22), 'Reduced mask\n' + r'$R=A/B$' + '\n\n' + r'$D=\max\{b,\lceil(a+(p-2)b)/(p-1)\rceil\}$', PALETTE['lightred'], fontsize=7.9, lw=1.4)
box(ax, (0.285, 0.57), (0.20, 0.22), 'Ambient compiler\n' + r'$\mathbb{F}_p[z]_{\leq D}$' + '\n\ndimension ' + r'$D+1$', PALETTE['lightgray'], fontsize=8.4, lw=1.4, ec=PALETTE['gray'])
box(ax, (0.535, 0.57), (0.20, 0.22), 'Reachable span\n' + r'$W(A,B)$' + '\n\nCartier rank ' + r'$r_p(F)$', PALETTE['lightblue'], fontsize=8.4, lw=1.4)
box(ax, (0.785, 0.57), (0.18, 0.22), 'Reachable states\n' + r'$\mathcal{R}(A,B)$' + '\n\nkernel size ' + r'$\kappa_p(F)$', PALETTE['lightorange'], fontsize=8.2, lw=1.4)
for x0, x1 in [(0.235,0.285),(0.485,0.535),(0.735,0.785)]:
    arrow(ax, (x0, 0.68), (x1, 0.68), lw=1.6)
ax.text(0.385, 0.49, 'restrict to the orbit of the initial numerator', ha='center', fontsize=7.5, color=PALETTE['gray'])
box(ax, (0.11, 0.17), (0.78, 0.18), r'$r_p(F)\leq\kappa_p(F)\leq p^{r_p(F)}\leq p^{D+1}$' + '\n\n' + r'$W(A,B)\cong\mathcal{V}_p(F)$ and $\mathcal{R}(A,B)\cong\mathcal{K}_p(F)$', PALETTE['lightgreen'], fontsize=10.0, lw=1.5, ec=PALETTE['green'])
arrow(ax, (0.635, 0.57), (0.58, 0.35), lw=1.1, color=PALETTE['gray'])
arrow(ax, (0.875, 0.57), (0.70, 0.35), lw=1.1, color=PALETTE['gray'])
ax.text(0.5, 0.955, 'The fixed-denominator compiler has an exact reachable core', ha='center', va='top', fontsize=13.0, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.06, 'Distinct reachable numerators define distinct formal series, so no additional behavioral quotient survives after reachability restriction.', ha='center', fontsize=8.2, color=PALETTE['gray'])
save(fig, 'cartier_state_hierarchy')

# Figure 17: rational-collapse obstruction
fig, ax = plt.subplots(figsize=(10.5, 5.35))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.055, 0.61), (0.25, 0.20), 'Unit rational mask\n' + r'$R=A/B$' + '\n\n' + r'$F^{p-1}=B/A$', PALETTE['lightred'], fontsize=9.2, lw=1.5)
box(ax, (0.375, 0.61), (0.25, 0.20), 'Divisor residue class\n' + r'$\omega_{p-1}(R)$' + '\n\n' + r'$\mathrm{div}(B/A)\ \mathrm{mod}\ (p-1)$', PALETTE['lightorange'], fontsize=8.5, lw=1.5)
arrow(ax, (0.305, 0.71), (0.375, 0.71), lw=1.7)
box(ax, (0.695, 0.68), (0.25, 0.17), 'Vanishing class\n' + r'$B/A=G^{p-1}$' + '\n' + r'$F=G\in\mathbb{F}_p(z)$', PALETTE['lightgreen'], fontsize=8.6, lw=1.5, ec=PALETTE['green'])
box(ax, (0.695, 0.38), (0.25, 0.17), 'Nonzero class\n' + r'$F\notin\mathbb{F}_p(z)$' + '\nnon-C-finite automatic sequence', PALETTE['lightblue'], fontsize=8.5, lw=1.5, ec=PALETTE['blue'])
arrow(ax, (0.625, 0.71), (0.695, 0.765), lw=1.5)
arrow(ax, (0.625, 0.67), (0.695, 0.465), lw=1.5)
ax.text(0.66, 0.79, r'$\omega=0$', fontsize=8.0, color=PALETTE['green'])
ax.text(0.66, 0.50, r'$\omega\neq0$', fontsize=8.0, color=PALETTE['blue'])
box(ax, (0.10, 0.13), (0.34, 0.19), 'Characteristic two\n' + r'$p-1=1$' + '\nEvery rational mask collapses to a rational series.', PALETTE['lightteal'], fontsize=8.4, lw=1.3, ec=PALETTE['teal'])
box(ax, (0.56, 0.13), (0.34, 0.19), 'Odd characteristic\nNonzero divisor residues are possible.\nThey certify genuinely nonperiodic automatic objects.', PALETTE['lightgray'], fontsize=8.3, lw=1.3, ec=PALETTE['gray'])
ax.text(0.5, 0.96, 'A finite divisor obstruction separates collapse from genuinely nonrational mask series', ha='center', va='top', fontsize=12.6, fontweight='bold', color=PALETTE['navy'])
save(fig, 'rational_collapse_obstruction')

# Figure 18: two nonperiodic rational-mask automata
b4_path = ROOT / 'generated' / 'block04_rational_mask_atlas_validation.json'
b4 = json.loads(b4_path.read_text(encoding='utf-8'))
fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8))
example_specs = [
    ('cantor_digit_indicator_F3', 'Cantor-digit indicator', r'$R=1+z$, $F^2=(1+z)^{-1}$'),
    ('square_root_denominator_F3', 'Square-root denominator', r'$R=(1+z)^{-1}$, $F^2=1+z$'),
]
for ax, (key, title, formula) in zip(axes, example_specs):
    row = b4['named_examples'][key]
    p = row['p']
    states = [tuple(s) for s in row['states']]
    state_to_id = {s: i for i, s in enumerate(states)}
    trans_raw = row['transitions']
    outs_raw = row['outputs']
    trans = {}
    outs = {}
    for s in states:
        skey = ','.join(map(str, s))
        trans[state_to_id[s]] = [state_to_id[tuple(t)] for t in trans_raw[skey]]
        outs[state_to_id[s]] = outs_raw[skey]
    start = state_to_id[tuple(row['B'])]
    nstates = len(states)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    if nstates == 2:
        coords = {0: (0.32, 0.52), 1: (0.72, 0.52)}
    else:
        coords = {0: (0.50, 0.76), 1: (0.22, 0.46), 2: (0.78, 0.46), 3: (0.50, 0.19)}
    for s in range(nstates):
        targets = {}
        for d, t in enumerate(trans[s]):
            targets.setdefault(t, []).append(str(d))
        for t, digs in targets.items():
            if s == t:
                x0, y0 = coords[s]
                arr = FancyArrowPatch((x0-0.025, y0+0.06), (x0+0.025, y0+0.06), arrowstyle='-|>', mutation_scale=9, connectionstyle='arc3,rad=-1.3', linewidth=1.0, color=PALETTE['gray'])
                ax.add_patch(arr)
                ax.text(x0, y0+0.17, ','.join(digs), ha='center', fontsize=7.2)
            else:
                x0, y0 = coords[s]
                x1, y1 = coords[t]
                rad = 0.13 if s < t else -0.13
                arr = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=9, connectionstyle=f'arc3,rad={rad}', linewidth=1.0, color=PALETTE['gray'])
                ax.add_patch(arr)
                ax.text((x0+x1)/2, (y0+y1)/2 + (0.055 if rad > 0 else -0.055), ','.join(digs), ha='center', fontsize=7.0)
    for s, (x0, y0) in coords.items():
        circ = Circle((x0, y0), 0.062, facecolor=PALETTE['lightblue'] if s == start else PALETTE['lightgreen'], edgecolor=PALETTE['navy'], lw=1.2, zorder=4)
        ax.add_patch(circ)
        poly_label = ''.join(str(x) for x in states[s])
        ax.text(x0, y0, f'{poly_label}|{outs[s]}', ha='center', va='center', fontsize=7.4, zorder=5)
    ax.set_title(title, fontsize=10.8, fontweight='bold', color=PALETTE['navy'])
    ax.text(0.5, 0.07, formula + '\n' + f"Cartier rank {row['cartier_rank']}; kernel states {row['reachable_numerator_states']}; compiler bound {row['ambient_state_bound']}", ha='center', va='center', fontsize=7.8)
    ax.text(0.5, 0.88, 'prefix: ' + ''.join(str(x) for x in row['prefix'][:24]), ha='center', fontsize=7.2, color=PALETTE['gray'])
fig.suptitle('Exact nonperiodic rational-mask examples in characteristic three', fontsize=13.0, fontweight='bold', color=PALETTE['navy'], y=1.02)
fig.tight_layout()
save(fig, 'rational_mask_nonperiodic_examples')

# Block 04 figure generation complete.

# Figure 19: fixed-radix regular atlas
fig, ax = plt.subplots(figsize=(11.0, 5.9))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.045, 0.64), (0.23, 0.20), 'Semantic chart\nfixed-radix regular sequence\n' + r'$a\in\mathbf{Reg}_k(\mathbb{K})$', PALETTE['lightgreen'], fontsize=9.0, lw=1.5)
box(ax, (0.385, 0.68), (0.23, 0.20), 'Canonical section module\n' + r'$\mathcal{V}_k(a)=\operatorname{span}\mathcal{K}_k(a)$' + '\nsection operators ' + r'$\Lambda_d$', PALETTE['lightblue'], fontsize=8.6, lw=1.5)
box(ax, (0.725, 0.64), (0.23, 0.20), 'Reachable-observable\ndigit-linear realization\nminimal dimension ' + r'$r_k(a)$', PALETTE['lightorange'], fontsize=8.7, lw=1.5)
arrow(ax, (0.275, 0.74), (0.385, 0.78), style='<|-|>', lw=1.7)
arrow(ax, (0.615, 0.78), (0.725, 0.74), style='<|-|>', lw=1.7)
box(ax, (0.385, 0.34), (0.23, 0.19), 'Strict shortlex normal form\ngreedy kernel basis\ncanonical digit matrices', PALETTE['lightteal'], fontsize=8.6, lw=1.5)
arrow(ax, (0.50, 0.68), (0.50, 0.53), style='<|-|>', lw=1.7)
box(ax, (0.045, 0.15), (0.31, 0.18), 'Automatic finite-orbit subatlas\n' + r'$|\mathcal{K}_k(a)|<\infty$' + '\nminimal DFAO recovered as the orbit', PALETTE['lightred'], fontsize=8.5, lw=1.4)
box(ax, (0.645, 0.15), (0.31, 0.18), 'Regular nonautomatic locus\nfinite span, infinite orbit\nexamples: ' + r'$n$, $s_k(n)$, $n^m$', PALETTE['lightgray'], fontsize=8.5, lw=1.4, ec=PALETTE['gray'])
arrow(ax, (0.16, 0.64), (0.20, 0.33), lw=1.3, color=PALETTE['gray'])
arrow(ax, (0.84, 0.64), (0.80, 0.33), lw=1.3, color=PALETTE['gray'])
arrow(ax, (0.356, 0.24), (0.385, 0.43), lw=1.1, color=PALETTE['gray'], ls='--')
arrow(ax, (0.645, 0.24), (0.615, 0.43), lw=1.1, color=PALETTE['gray'], ls='--')
ax.text(0.5, 0.975, 'Fixed-radix regular normalization and the automatic finite-orbit boundary', ha='center', va='top', fontsize=13.0, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.055, 'The same minimal linear module supports a finite orbit in the automatic case and an infinite orbit in genuinely regular examples.', ha='center', fontsize=8.2, color=PALETTE['gray'])
save(fig, 'regular_fixed_radix_atlas')

# Figure 20: word Hankel rank and minimal realization
fig, ax = plt.subplots(figsize=(10.7, 5.4))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
box(ax, (0.05, 0.61), (0.24, 0.21), 'Shortlex prefix words\n' + r'$u\in\{0,\ldots,k-1\}^{*}$' + '\nrows are section behaviors', PALETTE['lightblue'], fontsize=8.8, lw=1.4)
box(ax, (0.38, 0.61), (0.24, 0.21), 'Word Hankel matrix\n' + r'$H_a(u,v)=a_{\operatorname{val}(uv)}$' + '\nrank ' + r'$r_k(a)$', PALETTE['lightorange'], fontsize=8.8, lw=1.4)
box(ax, (0.71, 0.61), (0.24, 0.21), 'Shortlex continuation words\n' + r'$v\in\{0,\ldots,k-1\}^{*}$' + '\ncolumns separate sections', PALETTE['lightteal'], fontsize=8.8, lw=1.4)
arrow(ax, (0.29, 0.715), (0.38, 0.715), lw=1.6)
arrow(ax, (0.62, 0.715), (0.71, 0.715), lw=1.6)
box(ax, (0.18, 0.21), (0.27, 0.19), 'Invertible finite minor\n' + r'$\det H_a[U,V]\neq0$' + '\nfinite rank certificate', PALETTE['lightgreen'], fontsize=8.7, lw=1.4, ec=PALETTE['green'])
box(ax, (0.56, 0.21), (0.27, 0.19), 'Minimal factorization\n' + r'$H_a=P Q$' + '\nunique up to ' + r'$GL_{r_k(a)}$', PALETTE['lightgray'], fontsize=8.7, lw=1.4, ec=PALETTE['gray'])
arrow(ax, (0.50, 0.61), (0.315, 0.40), lw=1.4, connectionstyle='arc3,rad=0.10')
arrow(ax, (0.50, 0.61), (0.695, 0.40), lw=1.4, connectionstyle='arc3,rad=-0.10')
arrow(ax, (0.45, 0.305), (0.56, 0.305), style='<|-|>', lw=1.5)
ax.text(0.5, 0.96, 'The regular rank is simultaneously a section-module, Hankel, and minimal-state dimension', ha='center', va='top', fontsize=12.6, fontweight='bold', color=PALETTE['navy'])
ax.text(0.5, 0.065, 'A finite nonsingular minor certifies the lower bound; reachable-observable reduction supplies the matching realization.', ha='center', fontsize=8.2, color=PALETTE['gray'])
save(fig, 'regular_hankel_rank')

# Figure 21: exhaustive automatic state count versus regular rank
b5_path = ROOT / 'generated' / 'block05_regular_atlas_validation.json'
b5 = json.loads(b5_path.read_text(encoding='utf-8'))
fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.8), sharey=True)
global_lim = 3.35
for ax, cfg in zip(axes, b5['automata_enumeration']):
    points = []
    for key, count in cfg['distribution'].items():
        rpart, spart = key.split('_')
        r = int(rpart[1:])
        s_state = int(spart[1:])
        points.append((r, s_state, count))
    max_count = max(c for _, _, c in points)
    for r, s_state, count in points:
        size = 45 + 320 * (count / max_count) ** 0.65
        ax.scatter([r], [s_state], s=size, alpha=0.72, edgecolors=PALETTE['navy'], linewidths=0.7)
        ax.text(r, s_state, str(count), ha='center', va='center', fontsize=7.1)
    ax.plot([0, global_lim], [0, global_lim], color=PALETTE['gray'], lw=1.0, ls='--')
    ax.set_xlim(-0.2, global_lim)
    ax.set_ylim(0.7, global_lim)
    ax.set_xticks(range(0, 4))
    ax.set_yticks(range(1, 4))
    ax.grid(alpha=0.18)
    ax.set_xlabel('regular rank $r_k(a)$')
    ax.set_title(f"base {cfg['k']} over $\\mathbb{{F}}_{cfg['p']}$\n{cfg['unique_minimal_automata']} minimized automata", fontsize=9.5, color=PALETTE['navy'])
axes[0].set_ylabel('minimal DFAO states $\\kappa_k(a)$')
fig.suptitle('Exact state-to-rank compression in the finite automatic overlap', fontsize=12.7, fontweight='bold', color=PALETTE['navy'], y=1.03)
fig.text(0.5, -0.02, 'Bubble labels count canonical minimized automata. Points above the diagonal have linearly dependent but behavior-distinct kernel states.', ha='center', fontsize=8.0, color=PALETTE['gray'])
fig.tight_layout()
save(fig, 'automatic_regular_rank_distribution')

# Figure 22: finite rank does not imply finite kernel over infinite fields
ells = list(range(1, 9))
fig, ax = plt.subplots(figsize=(9.4, 4.5))
ax.plot(ells, [2] * len(ells), marker='o', label='Thue-Morse: 2 states, rank 2')
ax.plot(ells, [ell + 1 for ell in ells], marker='s', label=r'$s_2(n)$: $\ell+1$ depth states, rank 2')
ax.plot(ells, [2 ** ell for ell in ells], marker='^', label=r'$n$: $2^\ell$ depth states, rank 2')
ax.plot(ells, [2 ** ell for ell in ells], marker='d', fillstyle='none', label=r'$n^2$: $2^\ell$ depth states, rank 3')
ax.set_yscale('log', base=2)
ax.set_xlabel(r'fixed low-digit depth $\ell$')
ax.set_ylabel(r'distinct section states at depth $\ell$')
ax.set_title('Finite section rank can coexist with an infinite kernel orbit', fontsize=12.0, fontweight='bold', color=PALETTE['navy'])
ax.grid(alpha=0.22)
ax.legend(fontsize=8.0, loc='upper left')
ax.text(0.99, 0.04, 'Characteristic-zero examples', transform=ax.transAxes, ha='right', fontsize=8.0, color=PALETTE['gray'])
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
save(fig, 'regular_infinite_orbit_examples')

print('Generated Block 05 figures')
