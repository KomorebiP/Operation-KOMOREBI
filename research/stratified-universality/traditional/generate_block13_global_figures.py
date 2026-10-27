from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def save(fig, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def box(ax, xy, w, h, title, lines, fc="#f4f7f9", ec="#17324d"):
    x, y = xy
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02", linewidth=1.2, facecolor=fc, edgecolor=ec)
    ax.add_patch(p)
    ax.text(x+w/2, y+h-0.055, title, ha="center", va="top", fontsize=11, fontweight="bold")
    ax.text(x+0.03, y+h-0.115, "\n".join(lines), ha="left", va="top", fontsize=8.6, linespacing=1.35)
    return p


def arrow(ax, a, b, text=None, style="-|>", rad=0.0, color="#3d6c8e", lw=1.3, dashed=False):
    p = FancyArrowPatch(a, b, arrowstyle=style, connectionstyle=f"arc3,rad={rad}", mutation_scale=12, linewidth=lw, color=color, linestyle="--" if dashed else "-")
    ax.add_patch(p)
    if text:
        mx=(a[0]+b[0])/2; my=(a[1]+b[1])/2
        ax.text(mx, my+0.018, text, ha="center", va="bottom", fontsize=7.8, color=color)
    return p


# Figure 1: certified global atlas.
fig, ax = plt.subplots(figsize=(12.2, 8.2))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
box(ax, (0.035,0.61), 0.29,0.29, "DRLM component", [
    "fixed-prime regular sequences",
    "section module <-> shortlex <-> DFAO",
    "rational-mask/Cartier sublocus",
    "periodic recurrence/OGF sublocus",
    "complete core: shortlex record"
], fc="#e7f0f6")
box(ax, (0.355,0.61), 0.29,0.29, "LOC component", [
    "continuous Z_p-valued functions",
    "Mahler coefficients <-> clopen branches",
    "affine branch coordinates",
    "functional-Mahler kept separate",
    "complete core: Mahler sequence"
], fc="#e8f3f4")
box(ax, (0.675,0.61), 0.29,0.29, "FUSS component", [
    "marked U = z + alpha U^q",
    "tree <-> selected algebraic branch",
    "P-recursive coefficient chart",
    "packet support and orbit phase",
    "complete core: (q, alpha)"
], fc="#eaf2ea")
box(ax, (0.195,0.18), 0.29,0.29, "EM component", [
    "integral Euler templates",
    "coefficients <-> exponents <-> ghosts",
    "prime-uniform multiplicative functions",
    "Dirichlet convolution linearized",
    "complete core: exponent sequence"
], fc="#f7eadf")
box(ax, (0.515,0.18), 0.29,0.29, "GAL component", [
    "one finite Galois extension L/K",
    "subgroup <-> fixed field <-> projector",
    "core, normal closure, Mackey packets",
    "Brauer and tensor gates retained",
    "complete core: subgroup H"
], fc="#f1f3f4")
ax.text(0.5,0.965,"Certified finite atlas: five reversible components",ha="center",va="center",fontsize=15,fontweight="bold")
# directional satellites around components
ax.text(0.01,0.77,"integral\nreduction\ntowers",ha="left",va="center",fontsize=8)
arrow(ax,(0.10,0.76),(0.035,0.76),text="directional",style="<|-",dashed=True,color="#9d4b4b")
ax.text(0.99,0.77,"general\nholonomic /\nalgebraic",ha="right",va="center",fontsize=8)
arrow(ax,(0.965,0.76),(0.90,0.76),text="partial",style="<|-",dashed=True,color="#9d4b4b")
ax.text(0.03,0.34,"arbitrary\nproduct\ngrammars",ha="left",va="center",fontsize=8)
arrow(ax,(0.20,0.33),(0.105,0.33),text="partial",style="<|-",dashed=True,color="#9d4b4b")
ax.text(0.97,0.34,"modular / wild /\nnonneutral\nsymmetry",ha="right",va="center",fontsize=8)
arrow(ax,(0.805,0.33),(0.90,0.33),text="obstructed",style="-|>",dashed=True,color="#9d4b4b")
ax.text(0.5,0.07,"The five tags form a disjoint semantic union. No unlisted cross-component equivalence is asserted.",ha="center",va="center",fontsize=9)
save(fig,"global_certified_atlas")

# Figure 2: invariant descent.
fig, ax = plt.subplots(figsize=(11.2, 6.8))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
charts=[("chart A",0.08,0.72),("chart B",0.38,0.72),("chart C",0.68,0.72)]
for name,x,y in charts:
    box(ax,(x,y),0.23,0.16,name,["normalized local object","complete native invariant"],fc="#e7f0f6")
box(ax,(0.32,0.39),0.36,0.16,"invariant descent datum",["comparison isomorphisms on overlaps","triangle and quadruple coherence"],fc="#e7f2f1")
box(ax,(0.32,0.10),0.36,0.16,"global tagged invariant",["component tag + descended native data","reflects isomorphisms on the certified atlas"],fc="#eaf2ea")
for x in (0.195,0.495,0.795):
    arrow(ax,(x,0.72),(0.5,0.55),color="#3d6c8e")
arrow(ax,(0.5,0.39),(0.5,0.26),text="effective isomorphism descent",color="#2f7a78")
ax.text(0.5,0.96,"From local complete invariants to a global complete invariant",ha="center",fontsize=15,fontweight="bold")
ax.text(0.5,0.32,"local completeness + bridge comparison + coherence + effectivity",ha="center",fontsize=9)
ax.text(0.5,0.035,"Directional bridges remain outside the reversible descent core and retain their loss certificates.",ha="center",fontsize=9)
save(fig,"global_invariant_descent")

# Figure 3: Fuss-Catalan triangle.
fig, ax = plt.subplots(figsize=(9.6,7.4))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
box(ax,(0.34,0.72),0.32,0.16,"marked tree chart",[r"$U=z+\alpha U^q$",r"arity $q$ and weight $\alpha$"],fc="#eaf2ea")
box(ax,(0.05,0.17),0.36,0.18,"selected algebraic chart",[r"$P(z,Y)=Y-z-\alpha Y^q$","selected branch U(0)=0"],fc="#f7eadf")
box(ax,(0.59,0.17),0.36,0.18,"holonomic coefficient chart",[r"$C=1+\alpha x C^q$","Fuss-Catalan coefficients","first-order P-recursive ratio"],fc="#e7f0f6")
arrow(ax,(0.41,0.72),(0.23,0.35),text="same marked equation")
arrow(ax,(0.59,0.72),(0.77,0.35),text="Lagrange inversion")
arrow(ax,(0.41,0.26),(0.59,0.26),text="coefficient translation")
arrow(ax,(0.59,0.30),(0.41,0.30),text="selected synthesis",rad=0.18)
ax.add_patch(Circle((0.5,0.48),0.095,facecolor="#f1f3f4",edgecolor="#17324d",linewidth=1.2))
ax.text(0.5,0.5,"complete tag",ha="center",va="center",fontsize=10,fontweight="bold")
ax.text(0.5,0.455,r"$(q,\alpha)$",ha="center",va="center",fontsize=11)
for p in ((0.5,0.72),(0.23,0.35),(0.77,0.35)):
    arrow(ax,p,(0.5,0.57),style="-|>",color="#2f7a78",lw=1.0)
ax.text(0.5,0.96,"A genuine nonlinear-algebraic-holonomic overlap",ha="center",fontsize=15,fontweight="bold")
ax.text(0.5,0.07,"All triangle composites return the same marked parameter pair; the normalized fiber is contractible.",ha="center",fontsize=9)
save(fig,"fuss_catalan_three_stratum")

# Figure 4: normalizer-induced coherence.
fig, ax = plt.subplots(figsize=(10.6,6.5))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
ax.add_patch(Circle((0.5,0.5),0.12,facecolor="#e7f2f1",edgecolor="#17324d",linewidth=1.3))
ax.text(0.5,0.525,"common semantic",ha="center",va="center",fontsize=10,fontweight="bold")
ax.text(0.5,0.475,"normalizer",ha="center",va="center",fontsize=10)
positions=[(0.5,0.88),(0.84,0.65),(0.71,0.18),(0.29,0.18),(0.16,0.65)]
labels=["chart 1","chart 2","chart 3","chart 4","chart 5"]
for (x,y),label in zip(positions,labels):
    ax.add_patch(FancyBboxPatch((x-0.10,y-0.055),0.20,0.11,boxstyle="round,pad=0.02",facecolor="#f1f3f4",edgecolor="#3d6c8e",linewidth=1.1))
    ax.text(x,y,label,ha="center",va="center",fontsize=9,fontweight="bold")
    arrow(ax,(x,y),(0.5,0.5),color="#2f7a78",lw=1.0)
for i in range(len(positions)):
    a=positions[i]; b=positions[(i+1)%len(positions)]
    arrow(ax,a,b,text="bridge",rad=0.12,color="#3d6c8e",lw=1.0)
ax.text(0.5,0.97,"Normalizer-induced higher coherence",ha="center",fontsize=15,fontweight="bold")
ax.text(0.5,0.06,"Every bridge is obtained by normalizing to the same semantic object and re-expanding. All cycle composites are identities.",ha="center",fontsize=9)
save(fig,"normalizer_induced_coherence")

print("BLOCK13_FIGURES=PASS")
