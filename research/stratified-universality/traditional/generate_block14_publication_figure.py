from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(10.6, 6.7))
ax.set_xlim(0, 10.6)
ax.set_ylim(0, 6.7)
ax.axis('off')

navy = '#17324D'
blue = '#3D6C8E'
teal = '#2F7A78'
orange = '#B56A2B'
red = '#9D4B4B'
pale_blue = '#E7F0F6'
pale_teal = '#E7F2F1'
pale_orange = '#F7EADF'
pale_red = '#F5E6E6'
gray = '#5F6870'

ax.text(5.3, 6.35, 'Certified relative universality and lane-transport architecture', ha='center', va='center',
        fontsize=17, fontweight='bold', color=navy)
ax.text(5.3, 6.05, 'Each downward step has an explicit theorem or verification gate',
        ha='center', va='center', fontsize=10.5, color=gray)

boxes = [
    (5.3, 5.45, 5.2, 0.66, 'Resolved syntax, finite lanes, and preservation profiles',
     'analysis, synthesis, transfer blocks, refinements, residuals, declared constructors', pale_blue, blue),
    (5.3, 4.48, 5.2, 0.66, 'Normalized realization strata',
     'semantic functors, classification targets, faithful or conservative normalizers', pale_teal, teal),
    (5.3, 3.51, 5.2, 0.66, 'Typed finite atlas',
     'reversible overlaps plus directional bridges with loss passports', pale_orange, orange),
    (5.3, 2.54, 5.2, 0.66, 'Coherence and effective descent',
     'comparison 2-cells, object gluing, morphism gluing, obstruction checks', pale_blue, blue),
    (5.3, 1.57, 5.2, 0.66, 'Compatible native invariants',
     'local completeness, bridge comparison, descent-compatible isomorphisms', pale_teal, teal),
    (5.3, 0.60, 5.2, 0.66, 'Componentwise global completeness',
     'complete tagged invariant on the five-component certified semantic union', '#EAF2EA', '#4F774F'),
]
for cx, cy, w, h, title, subtitle, fill, edge in boxes:
    patch = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                           boxstyle='round,pad=0.03,rounding_size=0.08',
                           facecolor=fill, edgecolor=edge, linewidth=1.6)
    ax.add_patch(patch)
    ax.text(cx, cy+0.10, title, ha='center', va='center', fontsize=11.2,
            fontweight='bold', color=navy)
    ax.text(cx, cy-0.14, subtitle, ha='center', va='center', fontsize=8.5, color=gray)

for i in range(len(boxes)-1):
    x = boxes[i][0]
    y1 = boxes[i][1] - boxes[i][3]/2
    y2 = boxes[i+1][1] + boxes[i+1][3]/2
    ax.add_patch(FancyArrowPatch((x, y1-0.02), (x, y2+0.02),
                                 arrowstyle='-|>', mutation_scale=12,
                                 linewidth=1.35, color=navy))

# Directional satellites.
left = FancyBboxPatch((0.25, 2.0), 2.05, 2.15,
                      boxstyle='round,pad=0.04,rounding_size=0.08',
                      facecolor='#F1F3F4', edgecolor=gray, linewidth=1.2)
ax.add_patch(left)
ax.text(1.275, 3.88, 'Directional satellites', ha='center', va='center',
        fontsize=11, fontweight='bold', color=navy)
ax.text(0.42, 3.55,
        '• reduction and completion\n'
        '• differentiation or forgetting\n'
        '• functional / Newton-Mahler\n'
        '• projective and tensor lifts\n\n'
        'These do not enter the\nreversible core without a\nseparate recognition theorem.',
        ha='left', va='top', fontsize=8.8, color=gray, linespacing=1.35)
ax.add_patch(FancyArrowPatch((2.31, 3.08), (2.67, 3.43), arrowstyle='-|>',
                             mutation_scale=11, linewidth=1.1, color=gray))

right = FancyBboxPatch((8.30, 2.0), 2.05, 2.15,
                       boxstyle='round,pad=0.04,rounding_size=0.08',
                       facecolor=pale_red, edgecolor=red, linewidth=1.2)
ax.add_patch(right)
ax.text(9.325, 3.88, 'Typed obstruction data', ha='center', va='center',
        fontsize=11, fontweight='bold', color=navy)
ax.text(8.48, 3.55,
        '• graph holonomy\n'
        '• relative cokernel class\n'
        '• Brauer class\n'
        '• higher coherence defect\n\n'
        'Different failures remain\ndistinct unless an explicit\ncomparison theorem is proved.',
        ha='left', va='top', fontsize=8.8, color=gray, linespacing=1.35)
ax.add_patch(FancyArrowPatch((8.29, 3.43), (7.93, 3.08), arrowstyle='-|>',
                             mutation_scale=11, linewidth=1.1, color=red))

ax.text(5.3, 0.10,
        'Classification target: the declared finite normalized atlas, not arbitrary mathematical presentations',
        ha='center', va='center', fontsize=9.2, fontweight='bold', color=navy)

fig.tight_layout(pad=0.25)
for ext in ('pdf', 'png'):
    fig.savefig(FIG / f'publication_proof_architecture.{ext}', dpi=240, bbox_inches='tight')
plt.close(fig)
print('Generated publication proof architecture figure.')
