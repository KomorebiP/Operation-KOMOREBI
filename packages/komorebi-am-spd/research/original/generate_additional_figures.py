from pathlib import Path
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from infinite_packet_gibbs_reconstruction import (
    InfinitePacketGenerator,
    PacketSpec,
    synthetic_geometry,
    synthetic_text_curves,
    normalize_atom,
    save_figure,
)

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'

# 16. Dyadic perturbation schedule.
image = synthetic_geometry(56)
generator = InfinitePacketGenerator(image, max_seed_masks=80)
seed_id = sorted(generator.seed_masks)[0]
mask = generator.seed_masks[seed_id]
fig, axes = plt.subplots(3, 5, figsize=(13.0, 7.4))
for column, depth in enumerate(range(1, 6)):
    translation = max(generator.height, generator.width) / (2.0 ** (depth + 4))
    angle = 45.0 / (2.0 ** depth)
    scale = math.exp(math.log(2.0) / (2.0 ** (depth + 2)))
    moved = generator.affine_mask(mask, translation, 0.0, 0.0, 1.0)
    rotated = generator.affine_mask(mask, 0.0, 0.0, angle, 1.0)
    scaled = generator.affine_mask(mask, 0.0, 0.0, 0.0, scale)
    for row, value, label in [
        (0, moved, rf'$\Delta x={translation:.3f}$'),
        (1, rotated, rf'$\Delta\theta={angle:.3f}^\circ$'),
        (2, scaled, rf'$s={scale:.5f}$'),
    ]:
        axes[row, column].imshow(value, cmap='viridis', vmin=0, vmax=1)
        axes[row, column].set_title(f'depth {depth}\n{label}', fontsize=9.5, weight='bold')
        axes[row, column].set_xticks([])
        axes[row, column].set_yticks([])
fig.suptitle('Dyadic perturbations form an endlessly refinable parameter atlas', fontsize=17, weight='bold')
fig.text(0.5, 0.018, 'The step size halves with depth. Finite compositions approximate bounded translations, rotations, and log-scales to arbitrary precision.', ha='center', fontsize=10.5)
fig.tight_layout(rect=[0, 0.045, 1, 0.93])
save_figure(fig, FIG, '16_dyadic_dense_perturbations')

# 17. Boolean composition grammar.
image2 = synthetic_text_curves(56)
generator2 = InfinitePacketGenerator(image2, max_seed_masks=100)
ids = sorted(generator2.seed_masks)
# Select two masks with moderate overlap but not identical.
left_id, right_id = ids[0], ids[1]
best_score = -1.0
for i in ids[:40]:
    for j in ids[:40]:
        if i >= j:
            continue
        left = generator2.seed_masks[i] > 0.5
        right = generator2.seed_masks[j] > 0.5
        union = np.logical_or(left, right).sum()
        inter = np.logical_and(left, right).sum()
        if union == 0:
            continue
        overlap = inter / union
        score = 1.0 - abs(overlap - 0.18)
        if 0.02 < overlap < 0.65 and score > best_score:
            best_score = score
            left_id, right_id = i, j
left = generator2.seed_masks[left_id]
right = generator2.seed_masks[right_id]
specs = [
    ('parent A', normalize_atom(left)),
    ('parent B', normalize_atom(right)),
    ('union', generator2.atom_from_spec(PacketSpec('combine', (left_id, right_id, 'union')))),
    ('intersection', generator2.atom_from_spec(PacketSpec('combine', (left_id, right_id, 'intersection')))),
    ('A minus B', generator2.atom_from_spec(PacketSpec('combine', (left_id, right_id, 'left_difference')))),
    ('symmetric difference', generator2.atom_from_spec(PacketSpec('combine', (left_id, right_id, 'xor')))),
]
fig, axes = plt.subplots(2, 3, figsize=(10.8, 6.8))
for ax, (title, atom) in zip(axes.ravel(), specs, strict=True):
    if atom is None:
        ax.text(0.5, 0.5, 'degenerate', ha='center', va='center')
    else:
        value = atom.copy()
        value = (value - value.min()) / (value.max() - value.min() + 1e-12)
        ax.imshow(value, cmap='viridis', vmin=0, vmax=1)
    ax.set_title(title, weight='bold')
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle('Binary packet composition grows local parts into global objects', fontsize=17, weight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.93])
save_figure(fig, FIG, '17_compositional_packet_grammar')

# 18. Soft boundary packet continuum.
seed_id = sorted(generator.seed_masks)[0]
scales = [8.0, 4.0, 2.0, 1.0, 0.5, 0.25]
fig, axes = plt.subplots(2, 3, figsize=(10.8, 6.8))
for ax, scale in zip(axes.ravel(), scales, strict=True):
    atom = generator.atom_from_spec(PacketSpec('soft_mask', (seed_id, scale, 1.0)))
    if atom is not None:
        value = atom.copy()
        value = (value - value.min()) / (value.max() - value.min() + 1e-12)
        im = ax.imshow(value, cmap='viridis', vmin=0, vmax=1)
    ax.set_title(rf'boundary scale $\sigma={scale:g}$', weight='bold')
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle('A hard packet is approached through a nested family of soft boundaries', fontsize=17, weight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.93])
save_figure(fig, FIG, '18_soft_boundary_continuum')

# 19. Three-layer global reconstruction contract.
fig, ax = plt.subplots(figsize=(12.0, 5.8))
ax.axis('off')
boxes = [
    (0.06, 0.61, 0.20, 0.20, 'generative atlas\nimage seeds + perturbations', '#E6F0F4'),
    (0.40, 0.61, 0.20, 0.20, 'adaptive packet core\nglobal refit', '#E6F3F1'),
    (0.74, 0.61, 0.20, 0.20, 'residual completion\nDCT or local packets', '#FBF0E6'),
    (0.40, 0.20, 0.20, 0.20, 'exact archive\n$f=\widehat f_K+r_K$', '#F4EAF1'),
    (0.74, 0.20, 0.20, 0.20, 'finite closure\npixel-depth fallback', '#FCE8E2'),
]
for x, y, w, h, text, color in boxes:
    patch = plt.Rectangle((x, y), w, h, transform=ax.transAxes, facecolor=color, edgecolor='#17202A', lw=1.6)
    ax.add_patch(patch)
    ax.text(x+w/2, y+h/2, text, transform=ax.transAxes, ha='center', va='center', fontsize=12, weight='bold')
for start, end, label in [(0,1,'select'), (1,2,'complete'), (1,3,'store residual'), (3,1,'refine'), (3,4,'close exactly'), (2,3,'new residual')]:
    x0,y0,w0,h0,_,_=boxes[start]
    x1,y1,w1,h1,_,_=boxes[end]
    ax.annotate('', xy=(x1+w1/2,y1+h1/2), xytext=(x0+w0/2,y0+h0/2), xycoords=ax.transAxes, arrowprops=dict(arrowstyle='->', lw=1.5, color='#17202A', shrinkA=35, shrinkB=35, connectionstyle='arc3,rad=0.08'))
    ax.text((x0+w0/2+x1+w1/2)/2, (y0+h0/2+y1+h1/2)/2+0.035, label, transform=ax.transAxes, ha='center', fontsize=9.5, color='#566573', bbox=dict(facecolor='white', edgecolor='none', alpha=0.9, pad=1.0))
ax.text(0.5, 0.92, 'Global unknown-image reconstruction has three distinct guarantees', transform=ax.transAxes, ha='center', fontsize=18, weight='bold')
ax.text(0.5, 0.06, 'Sparse approximation, exact residual accounting, and exact finite closure are different claims and remain separately visible.', transform=ax.transAxes, ha='center', fontsize=10.8, color='#566573')
save_figure(fig, FIG, '19_global_reconstruction_contract')

print('generated 4 additional figure pairs')
