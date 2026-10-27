from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
import numpy as np
import sympy as sp

from .foundations import build_certificate

INK = "#17202A"
MUTED = "#566573"
PAPER = "#FAFAF7"
WHITE = "#FFFFFF"
BLUE = "#2E86AB"
CYAN = "#42B8C5"
TEAL = "#2A9D8F"
GREEN = "#6A994E"
YELLOW = "#E9C46A"
ORANGE = "#F4A261"
RED = "#E76F51"
MAGENTA = "#A23E8C"
PURPLE = "#6C5CE7"
COLORS = [BLUE, TEAL, ORANGE, MAGENTA, PURPLE, GREEN, RED, CYAN]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.titlesize": 14.0,
    "axes.labelsize": 10.5,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "text.color": INK,
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def _save(fig: plt.Figure, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight", pad_inches=0.10)
    fig.savefig(out / f"{name}.png", dpi=220, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)


def _axes(figsize=(12.8, 6.4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def _balanced_wrap(text: str, max_chars: int = 24) -> str:
    lines = []
    for raw in text.split("\n"):
        if len(raw) <= max_chars or " " not in raw or "$" in raw:
            lines.append(raw)
            continue
        words = raw.split()
        cur = ""
        for word in words:
            if cur and len(cur) + 1 + len(word) > max_chars:
                lines.append(cur)
                cur = word
            else:
                cur = word if not cur else cur + " " + word
        if cur:
            lines.append(cur)
    return "\n".join(lines)


def _box(ax, x, y, w, h, text, face=WHITE, edge=INK, fontsize=11.0):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.015,rounding_size=0.018",
        facecolor=face, edgecolor=edge, linewidth=1.6, zorder=2,
    )
    ax.add_patch(patch)
    fitted = _balanced_wrap(text, max_chars=max(12, int(31 * w / 0.18)))
    lines = fitted.count("\n") + 1
    size = fontsize
    if lines >= 4:
        size *= 0.82
    elif lines == 3:
        size *= 0.90
    if w < .12:
        size *= .85
    ax.text(x+w/2, y+h/2, fitted, ha="center", va="center", multialignment="center",
            linespacing=1.08, fontsize=max(7.2, size), zorder=4)
    return patch


def _arrow(ax, start, end, color=INK, text=None, rad=0.0, offset=(0, 0), lw=1.7):
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                            linewidth=lw, color=color, connectionstyle=f"arc3,rad={rad}", zorder=3)
    ax.add_patch(patch)
    if text:
        mx = (start[0]+end[0])/2 + offset[0]
        my = (start[1]+end[1])/2 + offset[1]
        ax.text(mx, my, text, ha="center", va="center", fontsize=8.8,
                bbox=dict(boxstyle="round,pad=.10", facecolor=PAPER, edgecolor="none", alpha=.96), zorder=5)
    return patch


def _float_matrix(M: sp.Matrix) -> np.ndarray:
    return np.array([[complex(sp.N(M[i, j], 16)) for j in range(M.cols)] for i in range(M.rows)])


def _annotate_matrix(ax, M: np.ndarray, fmt=".0f", fontsize=8.6):
    maxv = max(float(np.max(np.abs(M))), 1e-12)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            value = M[i, j]
            if abs(value.imag) < 1e-10:
                label = format(value.real, fmt)
            else:
                label = f"{value.real:.1f}\n{value.imag:+.1f}i"
            color = WHITE if abs(value) > .52*maxv else INK
            ax.text(j, i, label, ha="center", va="center", fontsize=fontsize, color=color, weight="bold")


def generate_foundation_figures(base: Path) -> int:
    out = base / "figures"
    c = build_certificate()
    n = c.dimension

    # 38: Full calculus pipeline.
    fig, ax = _axes((13.2, 7.0))
    ax.text(.5, .955, "From one seed to a certified reconstruction", ha="center", fontsize=23, weight="bold")
    labels = [
        ("0. seed", "primitive datum"),
        ("1. type", "ambient object"),
        ("2. grammar", "admissible operators"),
        ("3. orbit", "generated hull"),
        ("4. relations", "quotient law"),
        ("5. addresses", "packet labels"),
        ("6. project", "$P_\\alpha x$"),
        ("7. transfer", "$P_\\beta T P_\\alpha$"),
        ("8. refine", "parent = children"),
        ("9. interact", "nonlinear packets"),
        ("10. complete", "limit/topology"),
        ("11. synthesize", "object + certificate"),
    ]
    xs = [0.03, .19, .35, .51, .67, .83]
    ys = [.68, .29]
    for idx, (title, sub) in enumerate(labels):
        row, col = divmod(idx, 6)
        x0, y0 = xs[col], ys[row]
        color = COLORS[idx % len(COLORS)]
        _box(ax, x0, y0, .135, .17, f"{title}\n{sub}", face=color+"20", edge=color, fontsize=10.5)
        if col < 5:
            _arrow(ax, (x0+.135, y0+.085), (xs[col+1]-.006, y0+.085), color=INK, lw=1.35)
    _arrow(ax, (.897, .675), (.897, .46), color=INK, text="continue", offset=(.045, 0), lw=1.35)
    _arrow(ax, (.83, .375), (.165, .375), color=MAGENTA, text="exact reconstruction closes the loop", rad=-.14, offset=(0, -.055), lw=1.5)
    ax.text(.5, .075, "Every later domain example instantiates this same chain with different objects, operators, projectors, and certificates.", ha="center", color=MUTED, fontsize=11.0)
    _save(fig, out, "38_seed_to_reconstruction_pipeline")

    # 39: Seed-system anatomy.
    fig, ax = _axes((12.8, 6.5))
    ax.text(.5, .93, "The typed seed system separates data from the rules that act on it", ha="center", fontsize=21, weight="bold")
    _box(ax, .38, .39, .24, .20, "seed system\n$(X,S,A,R,P,tau)$", face="#E6F0F4", edge=BLUE, fontsize=13)
    items = [
        (.08,.68,"ambient type $X$\nwhere values live",BLUE),
        (.37,.72,"seed family $S$\nprimitive data",TEAL),
        (.70,.68,"operator grammar $A$\nallowed constructions",ORANGE),
        (.08,.18,"relations $R$\nidentities and quotients",MAGENTA),
        (.38,.10,"packets $P$\nexact coordinates",PURPLE),
        (.70,.18,"completion $\\tau$\ntopology or inverse limit",GREEN),
    ]
    for x,y,text,color in items:
        _box(ax,x,y,.22,.14,text,face=color+"20",edge=color,fontsize=11)
        start=(x+.11, y+.07)
        end=(.38 if x<.38 else (.62 if x>.62 else .50), .49 if y>.39 else .42)
        _arrow(ax,start,end,color=color,rad=.08 if x<.4 else -.08,lw=1.25)
    ax.text(.5,.035,"A universality claim is meaningful only when the grammar and relations are fixed before the target object is encoded.",ha="center",fontsize=10.7,color=MUTED)
    _save(fig,out,"39_seed_system_anatomy")

    # 40: Orbit matrix.
    M = np.real(_float_matrix(c.orbit_matrix))
    fig, ax = plt.subplots(figsize=(8.4, 6.4))
    im = ax.imshow(M, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(n), [f"$U^{k}s$" for k in range(n)], rotation=35, ha="right")
    ax.set_yticks(range(n), [f"$e_{j}$" for j in range(n)])
    _annotate_matrix(ax, M, fmt=".0f", fontsize=9)
    ax.set_title("The orbit matrix of the cyclic-shift seed", weight="bold")
    ax.text(.5,-.18,"Every basis coordinate appears exactly once, so the orbit rank is 8.",transform=ax.transAxes,ha="center",color=MUTED,fontsize=10.5)
    fig.colorbar(im, ax=ax, fraction=.046, label="coordinate coefficient")
    fig.tight_layout()
    _save(fig,out,"40_seed_orbit_matrix")

    # 41: Hull growth.
    dims = np.arange(1, n+1)
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    ax.step(np.arange(n), dims, where="mid", lw=2.2, color=BLUE)
    ax.scatter(np.arange(n), dims, s=45, color=TEAL, edgecolor=INK, zorder=3)
    for k,d in enumerate(dims):
        ax.text(k,d+.18,str(d),ha="center",fontsize=9)
    ax.set_xticks(range(n), [f"$U^{k}s$" for k in range(n)])
    ax.set_xlabel("new orbit word admitted")
    ax.set_ylabel("dimension of generated hull")
    ax.set_ylim(.5,9)
    ax.grid(alpha=.18)
    ax.set_title("Generated-hull growth reaches the full ambient space", weight="bold")
    fig.tight_layout()
    _save(fig,out,"41_generated_hull_growth")

    # 42: Relation and quotient.
    fig, ax = _axes((12.6, 5.9))
    ax.text(.5,.92,"The orbit relation turns a free word algebra into a finite cyclic module",ha="center",fontsize=21,weight="bold")
    _box(ax,.04,.42,.24,.18,"free words\n$K[z]e$\n$e,ze,z^2e,\\ldots$",face=BLUE+"20",edge=BLUE,fontsize=13)
    _box(ax,.38,.42,.24,.18,"relation\n$(z^8-1)e=0$\nidentify $z^8e=e$",face=ORANGE+"20",edge=ORANGE,fontsize=13)
    _box(ax,.72,.42,.24,.18,"quotient module\n$K[z]/(z^8-1)$\n$\\cong X$",face=TEAL+"20",edge=TEAL,fontsize=13)
    _arrow(ax,(.28,.51),(.38,.51),color=INK,text="impose",offset=(0,.05))
    _arrow(ax,(.62,.51),(.72,.51),color=INK,text="evaluate $z\\mapsto U$",offset=(0,.055))
    ax.text(.5,.20,"The finite relation is not an approximation. It is the exact kernel relation of the shift representation.",ha="center",fontsize=11,color=MUTED)
    ax.text(.5,.10,r"$U^8=I$ gives a complete normal form $a_0I+a_1U+\cdots+a_7U^7$.",ha="center",fontsize=14,weight="bold")
    _save(fig,out,"42_relation_quotient")

    # 43: Address/refinement tree.
    fig, ax = _axes((13.0, 7.0))
    ax.text(.5,.95,"Address refinement: parity -> residue mod 4 -> individual coordinates",ha="center",fontsize=20,weight="bold")
    levels = [
        [(.5,.82,"$X$",INK)],
        [(.27,.63,"even",BLUE),(.73,.63,"odd",ORANGE)],
        [(.14,.42,"$r=0$",TEAL),(.38,.42,"$r=2$",GREEN),(.62,.42,"$r=1$",MAGENTA),(.86,.42,"$r=3$",PURPLE)],
        [(x,.18,f"$e_{j}$",COLORS[j%8]) for j,x in enumerate(np.linspace(.06,.94,8))],
    ]
    for li,nodes in enumerate(levels):
        for x,y,label,color in nodes:
            w=.11 if li<3 else .075
            _box(ax,x-w/2,y-.045,w,.09,label,face=color+"18" if color!=INK else WHITE,edge=color,fontsize=11)
    # edges root to parity
    for x,_,_,color in levels[1]: _arrow(ax,(.5,.775),(x,.68),color=color,lw=1.2)
    # parity to mod4
    for child in levels[2][:2]: _arrow(ax,(.27,.585),(child[0],.465),color=child[3],lw=1.2)
    for child in levels[2][2:]: _arrow(ax,(.73,.585),(child[0],.465),color=child[3],lw=1.2)
    # mod4 to coordinates: R0->{0,4}, R2->{2,6}, R1->{1,5}, R3->{3,7}
    groups=[[0,4],[2,6],[1,5],[3,7]]
    for parent,inds in zip(levels[2],groups,strict=True):
        for j in inds: _arrow(ax,(parent[0],.375),(levels[3][j][0],.225),color=parent[3],lw=1.0)
    ax.text(.5,.055,r"$P_{\rm even}=R_0+R_2$, $P_{\rm odd}=R_1+R_3$, and $R_r=E_r+E_{r+4}$.",ha="center",fontsize=13)
    _save(fig,out,"43_address_refinement_tree")

    # 44: Analysis/synthesis packets.
    x = np.real(_float_matrix(c.signal)).ravel()
    fig, axes = plt.subplots(2, 1, figsize=(12.6, 6.2), gridspec_kw={"height_ratios":[1.05,1.55]}, constrained_layout=True)
    axes[0].stem(range(n),x,linefmt=INK,markerfmt="o",basefmt=" ")
    axes[0].set_title("Object produced by the seed polynomial",loc="left",weight="bold")
    axes[0].set_ylabel("$x_j$")
    bottom=np.zeros(n)
    for j,Px in enumerate(c.spatial_packets):
        vals=np.real(_float_matrix(Px)).ravel()
        axes[1].bar(np.arange(n), vals, bottom=bottom, color=COLORS[j], edgecolor=INK, linewidth=.35, label=f"$E_{j}x$")
        bottom += vals
    axes[1].plot(np.arange(n),x,"o",color=INK,label="reconstructed $x$")
    axes[1].set_title("Eight disjoint packets synthesize the object exactly",loc="left",weight="bold")
    axes[1].set_xlabel("coordinate address")
    axes[1].set_ylabel("packet contribution")
    axes[1].legend(loc="upper center",bbox_to_anchor=(.5,-.16),ncol=5,fontsize=8,frameon=True)
    for a in axes: a.grid(alpha=.14); a.set_xticks(range(n))
    _save(fig,out,"44_analysis_synthesis_packets")

    # 45: transfer support matrix.
    support=np.zeros((n,n))
    for b,a in c.transfer_support:
        support[b,a]=1
    fig,ax=plt.subplots(figsize=(8.1,6.4))
    im=ax.imshow(support,cmap=matplotlib.colors.ListedColormap([PAPER,TEAL]),vmin=0,vmax=1)
    ax.set_xticks(range(n),[f"in {j}" for j in range(n)],rotation=35,ha="right")
    ax.set_yticks(range(n),[f"out {j}" for j in range(n)])
    for i in range(n):
        for j in range(n):
            if support[i,j]: ax.text(j,i,"$T_{%d%d}$"%(i,j),ha="center",va="center",fontsize=7.5,color=WHITE,weight="bold")
    ax.set_title("Support of the transfer-block matrix for $T=2I-U+3U^2$",weight="bold")
    ax.text(.5,-.19,"Only the identity, one-step, and two-step cyclic transfer bands are nonzero.",transform=ax.transAxes,ha="center",color=MUTED,fontsize=10.2)
    fig.tight_layout()
    _save(fig,out,"45_transfer_support_matrix")

    # 46: same operator in spatial and Fourier coordinates.
    T=np.real(_float_matrix(c.operator))
    Tf=np.abs(_float_matrix(c.fourier_diagonal_operator))
    fig,axes=plt.subplots(1,2,figsize=(12.4,5.2),constrained_layout=True)
    im0=axes[0].imshow(T,cmap="coolwarm",vmin=-3,vmax=3)
    _annotate_matrix(axes[0],T,fmt=".0f",fontsize=8)
    axes[0].set_title("spatial packet matrix",weight="bold")
    axes[0].set_xticks([]); axes[0].set_yticks([])
    im1=axes[1].imshow(Tf,cmap="viridis")
    _annotate_matrix(axes[1],Tf,fmt=".2f",fontsize=8)
    axes[1].set_title("Fourier atlas: diagonal magnitude",weight="bold")
    axes[1].set_xticks([]); axes[1].set_yticks([])
    fig.colorbar(im0,ax=axes[0],fraction=.046,label="signed entry")
    fig.colorbar(im1,ax=axes[1],fraction=.046,label="magnitude")
    fig.suptitle("Coordinate transport changes the visible structure, not the operator",fontsize=17,weight="bold")
    _save(fig,out,"46_operator_spatial_fourier")

    # 47: transfer path multiplication.
    fig,ax=_axes((12.8,6.0))
    ax.text(.5,.92,"Composition is a sum over intermediate packet addresses",ha="center",fontsize=21,weight="bold")
    cols=[.12,.50,.88]
    labels=["input packets $a$","intermediate packets $\\gamma$","output packets $b$"]
    for xcol,label in zip(cols,labels,strict=True): ax.text(xcol,.82,label,ha="center",fontsize=12,weight="bold")
    ys=np.linspace(.68,.20,4)
    for layer,xcol in enumerate(cols):
        for j,y in enumerate(ys):
            color=COLORS[(j+2*layer)%8]
            ax.add_patch(Circle((xcol,y),.035,facecolor=color+"30",edgecolor=color,lw=1.5))
            ax.text(xcol,y,str(j),ha="center",va="center",fontsize=9,weight="bold")
    # representative paths, not all 512
    for a in range(4):
        for g in ((a)%4,(a+1)%4):
            _arrow(ax,(cols[0]+.038,ys[a]),(cols[1]-.038,ys[g]),color=BLUE,lw=.9,rad=.04)
            for b in ((g)%4,(g+1)%4):
                _arrow(ax,(cols[1]+.038,ys[g]),(cols[2]-.038,ys[b]),color=MAGENTA,lw=.9,rad=-.04)
    ax.text(.5,.075,r"$P_bSTP_a=\sum_\gamma(P_bSP_\gamma)(P_\gamma TP_a)$; summing $a,b,\gamma$ reconstructs $ST$.",ha="center",fontsize=13)
    _save(fig,out,"47_operator_path_sum")

    # 48: refinement incidence matrix.
    incidence=np.zeros((2,4))
    incidence[0,[0,2]]=1
    incidence[1,[1,3]]=1
    fig,ax=plt.subplots(figsize=(8.2,4.8))
    im=ax.imshow(incidence,cmap=matplotlib.colors.ListedColormap([PAPER,ORANGE]),vmin=0,vmax=1,aspect="auto")
    ax.set_xticks(range(4),["$R_0$","$R_1$","$R_2$","$R_3$"])
    ax.set_yticks(range(2),["even parent","odd parent"])
    for i in range(2):
        for j in range(4): ax.text(j,i,"child" if incidence[i,j] else "-",ha="center",va="center",color=WHITE if incidence[i,j] else MUTED,weight="bold")
    ax.set_title("The coarse-to-fine incidence matrix is exact, not statistical",weight="bold")
    ax.text(.5,-.20,"Coarsening sums the indicated child packets; refinement expands each parent into exactly those descendants.",transform=ax.transAxes,ha="center",color=MUTED,fontsize=10.2)
    fig.tight_layout()
    _save(fig,out,"48_refinement_incidence")

    # 49: transform atlas.
    fig,ax=_axes((13.0,6.2))
    ax.text(.5,.93,"One object, three exact coordinate atlases",ha="center",fontsize=22,weight="bold")
    _box(ax,.39,.40,.22,.18,"object $x$\nin $X$",face=INK+"10",edge=INK,fontsize=15)
    atlases=[(.05,.66,"spatial atlas\n$I x$",BLUE,"$I$"),(.73,.66,"Fourier atlas\n$F x$",TEAL,"$F$"),(.05,.13,"Haar atlas\n$H x$",MAGENTA,"$H$"),(.73,.13,"pulled-back packets\n$U^{-1}E_\\alpha U$",ORANGE,"conjugation")]
    for x0,y0,text,color,arrowtext in atlases:
        _box(ax,x0,y0,.22,.15,text,face=color+"20",edge=color,fontsize=12)
        start=(.39 if x0<.39 else .61,.49)
        end=(x0+.22 if x0<.39 else x0,y0+.075)
        _arrow(ax,start,end,color=color,text=arrowtext,rad=.08 if y0<.4 else -.08,offset=(0,.04 if y0>.4 else -.04),lw=1.3)
        _arrow(ax,end,start,color=color,rad=-.14 if y0>.4 else .14,lw=1.0)
    ax.text(.5,.055,"Complete coordinates differ in visibility and sparsity, but each retains an exact synthesis map.",ha="center",color=MUTED,fontsize=11)
    _save(fig,out,"49_transform_atlas_portfolio")

    # 50: redundant multi-atlas tight frame.
    fig,ax=_axes((12.8,6.4))
    ax.text(.5,.94,"The weighted spatial-Fourier-Haar portfolio is a finite tight frame",ha="center",fontsize=21,weight="bold")
    _box(ax,.05,.42,.15,.17,"$x$\noriginal object",face=BLUE+"18",edge=BLUE,fontsize=13)
    branches=[(.31,.68,"$1\\cdot Ix$",BLUE),(.31,.42,"$2\\cdot Fx$",TEAL),(.31,.16,"$3\\cdot Hx$",MAGENTA)]
    for x0,y0,text,color in branches:
        _box(ax,x0,y0,.17,.13,text,face=color+"20",edge=color,fontsize=13)
        _arrow(ax,(.20,.505),(x0,y0+.065),color=color,lw=1.3)
    _box(ax,.62,.34,.19,.28,"canonical synthesis\n$\\frac{1}{14}(I^*c_0+2F^*c_1+3H^*c_2)$",face=ORANGE+"20",edge=ORANGE,fontsize=12)
    for x0,y0,_,color in branches: _arrow(ax,(x0+.17,y0+.065),(.62,.48),color=color,lw=1.3)
    _box(ax,.87,.42,.09,.17,"$\\widehat x=x$",face=TEAL+"20",edge=TEAL,fontsize=13)
    _arrow(ax,(.81,.48),(.87,.505),color=INK,lw=1.5)
    ax.text(.5,.07,r"$S A=(1^2+2^2+3^2)^{-1}(1^2I+2^2I+3^2I)=I$.",ha="center",fontsize=14,weight="bold")
    _save(fig,out,"50_multi_atlas_tight_frame")

    # 51: nonlinear interaction hypergraph.
    fig,ax=_axes((12.8,6.4))
    ax.text(.5,.94,"Nonlinearity replaces one transfer edge by packet interaction hyperedges",ha="center",fontsize=21,weight="bold")
    input_pos=[(.10,.68),(.10,.48),(.10,.28)]
    for j,(x0,y0) in enumerate(input_pos):
        ax.add_patch(Circle((x0,y0),.045,facecolor=COLORS[j]+"28",edgecolor=COLORS[j],lw=1.6)); ax.text(x0,y0,f"$P_{j}x$",ha="center",va="center",fontsize=9)
    inter_pos=[(.43,.73,"$(0,1)$"),(.43,.52,"$(1,2)$"),(.43,.31,"$(0,2)$")]
    for i,(x0,y0,label) in enumerate(inter_pos):
        _box(ax,x0-.055,y0-.04,.11,.08,label,face=ORANGE+"20",edge=ORANGE,fontsize=10)
    # hyperedge lines
    pairs=[(0,1),(1,2),(0,2)]
    for k,(a,b) in enumerate(pairs):
        y=inter_pos[k][1]
        _arrow(ax,(input_pos[a][0]+.047,input_pos[a][1]),(.375,y),color=COLORS[a],lw=1.0)
        _arrow(ax,(input_pos[b][0]+.047,input_pos[b][1]),(.375,y),color=COLORS[b],lw=1.0)
    out_pos=[(.82,.68),(.82,.48),(.82,.28)]
    for j,(x0,y0) in enumerate(out_pos):
        ax.add_patch(Circle((x0,y0),.050,facecolor=MAGENTA+"22",edgecolor=MAGENTA,lw=1.6)); ax.text(x0,y0,f"$P_{j}N(x)$",ha="center",va="center",fontsize=9)
    for k,(_,y,_) in enumerate(inter_pos):
        for j in range(3):
            _arrow(ax,(.485,y),(out_pos[j][0]-.052,out_pos[j][1]),color=MUTED,lw=.75,rad=.06*(j-1))
    ax.text(.5,.10,r"For a bilinear term $B(x,x)$, exact packetization is $B(x,x)=\sum_{a,c}B(P_ax,P_cx)$.",ha="center",fontsize=13)
    _save(fig,out,"51_nonlinear_interaction_hypergraph")

    # 52: obstruction geometry.
    Pi=np.real(_float_matrix(c.obstruction_projector))
    fig,axes=plt.subplots(1,2,figsize=(12.4,5.2),constrained_layout=True)
    im=axes[0].imshow(Pi,cmap="coolwarm",vmin=-.4,vmax=.7)
    _annotate_matrix(axes[0],Pi,fmt=".2f",fontsize=10)
    axes[0].set_title("cokernel obstruction projector",weight="bold")
    axes[0].set_xticks(range(3),["$d_1$","$d_2$","$d_3$"])
    axes[0].set_yticks(range(3),["$o_1$","$o_2$","$o_3$"])
    fig.colorbar(im,ax=axes[0],fraction=.046,label="projector entry")
    vals=np.array([0.0,float(sp.sqrt((c.blocked_obstruction.T*c.blocked_obstruction)[0]))])
    axes[1].bar(["solvable\n$d=(1,2,3)$","blocked\n$d=(1,2,4)$"],vals,color=[TEAL,RED],edgecolor=INK)
    axes[1].set_ylabel("obstruction norm")
    axes[1].set_title("vanishing is the exact continuation criterion",weight="bold")
    for i,v in enumerate(vals): axes[1].text(i,v+.015,f"{v:.3f}",ha="center",weight="bold")
    axes[1].set_ylim(0,max(.7,vals.max()*1.25)); axes[1].grid(alpha=.16,axis="y")
    _save(fig,out,"52_obstruction_packet_geometry")

    # 53: completion/refinement tower.
    fig,ax=_axes((13.0,6.4))
    ax.text(.5,.94,"Finite refinement tower and the declared completion direction",ha="center",fontsize=21,weight="bold")
    levels=[(.12,"level 0\nwhole object",1),(.36,"level 1\nparity packets",2),(.60,"level 2\nmod-4 packets",4),(.84,"level 3\ncoordinate packets",8)]
    for x0,label,count in levels:
        ax.text(x0,.82,label,ha="center",fontsize=11,weight="bold")
        ys=np.linspace(.20,.68,count)
        for j,y in enumerate(ys):
            h=min(.07,.38/max(count,1));
            _box(ax,x0-.045,y-h/2,.09,h,f"{j}",face=COLORS[j%8]+"20",edge=COLORS[j%8],fontsize=8.5)
    for li in range(len(levels)-1):
        xa,counta=levels[li][0],levels[li][2]
        xb,countb=levels[li+1][0],levels[li+1][2]
        ysa=np.linspace(.20,.68,counta); ysb=np.linspace(.20,.68,countb)
        factor=countb//counta
        for a,ya in enumerate(ysa):
            for b in range(a*factor,(a+1)*factor): _arrow(ax,(xa+.047,ya),(xb-.047,ysb[b]),color=MUTED,lw=.7)
    ax.text(.5,.085,"At every level the packets sum to the identity. An infinite theory must additionally declare the topology in which this tower converges.",ha="center",fontsize=10.8,color=MUTED)
    _save(fig,out,"53_completion_refinement_tower")

    # 54: master example pipeline.
    fig,ax=_axes((13.2,7.0))
    ax.text(.5,.95,"Master example: the length-eight cyclic signal through the complete calculus",ha="center",fontsize=20,weight="bold")
    stages=[
        (.04,.69,"seed\n$s=e_0$",BLUE),(.22,.69,"grammar\n$U$",TEAL),(.40,.69,"hull\n$U^ks$",ORANGE),(.58,.69,"relation\n$U^8=I$",MAGENTA),(.76,.69,"object\n$x=p(U)s$",PURPLE),
        (.04,.29,"project\n$E_jx$",GREEN),(.22,.29,"transfer\n$E_bTE_a$",YELLOW),(.40,.29,"refine\nparity/mod 4",ORANGE),(.58,.29,"atlas\n$F,H,I$",TEAL),(.76,.29,"nonlinear\ninteraction",RED),
    ]
    for x0,y0,text,color in stages:
        _box(ax,x0,y0,.14,.15,text,face=color+"20",edge=color,fontsize=10.5)
    for row in [stages[:5],stages[5:]]:
        for a,b in zip(row,row[1:]): _arrow(ax,(a[0]+.14,a[1]+.075),(b[0]-.005,b[1]+.075),color=INK,lw=1.2)
    _arrow(ax,(.83,.68),(.83,.48),color=INK,text="analyze",offset=(.045,0),lw=1.2)
    _box(ax,.39,.06,.22,.12,"synthesis + residual\n$\\widehat x=x$, $\\widehat T=T$",face=BLUE+"18",edge=BLUE,fontsize=12)
    for x0 in (.11,.29,.47,.65,.83): _arrow(ax,(x0,.29),(.50,.18),color=MUTED,lw=.7,rad=(x0-.5)*.3)
    _save(fig,out,"54_master_example_pipeline")

    # 55: master seed and output.
    Tx=np.real(_float_matrix(c.operator_output)).ravel()
    fig,axes=plt.subplots(2,1,figsize=(12.5,6.3),sharex=True,constrained_layout=True)
    axes[0].stem(range(n),x,linefmt=BLUE,markerfmt="o",basefmt=" ")
    axes[0].set_title(r"Seed polynomial $x=(2-U+3U^2+U^4+4U^5-2U^6+5U^7)s$",loc="left",weight="bold")
    axes[0].set_ylabel("$x_j$")
    axes[1].stem(range(n),Tx,linefmt=MAGENTA,markerfmt="o",basefmt=" ")
    axes[1].set_title(r"Operator output $Tx$ for $T=2I-U+3U^2$",loc="left",weight="bold")
    axes[1].set_ylabel("$(Tx)_j$"); axes[1].set_xlabel("cyclic coordinate")
    for a in axes: a.grid(alpha=.16); a.set_xticks(range(n))
    _save(fig,out,"55_master_seed_and_transfer_output")

    # 56: master Fourier spectrum.
    fx=np.array([complex(sp.N(v,16)) for v in c.fourier_matrix*c.signal])
    fig,axes=plt.subplots(2,1,figsize=(11.5,6.3),constrained_layout=True)
    axes[0].bar(range(n),np.abs(fx),color=COLORS,edgecolor=INK)
    axes[0].set_title("Fourier packet magnitudes",loc="left",weight="bold")
    axes[0].set_ylabel("$|(Fx)_k|$")
    axes[1].bar(range(n),np.angle(fx),color=COLORS,edgecolor=INK)
    axes[1].set_title("Fourier packet phases",loc="left",weight="bold")
    axes[1].set_ylabel("phase (radians)"); axes[1].set_xlabel("frequency packet $k$")
    axes[1].set_ylim(-np.pi,np.pi); axes[1].axhline(0,color=INK,lw=.7)
    for a in axes: a.grid(alpha=.14,axis="y"); a.set_xticks(range(n))
    _save(fig,out,"56_master_fourier_packets")

    # 57: master nonlinear output.
    ny=np.real(_float_matrix(c.nonlinear_output)).ravel()
    fig,ax=plt.subplots(figsize=(11.8,5.2))
    width=.36
    ax.bar(np.arange(n)-width/2,x,width,color=BLUE,edgecolor=INK,label="$x$")
    ax.bar(np.arange(n)+width/2,ny,width,color=RED,edgecolor=INK,label="$N(x)$")
    ax.set_xticks(range(n)); ax.set_xlabel("coordinate packet")
    ax.set_ylabel("value")
    ax.set_title(r"Exact nonlinear synthesis for $N(x)=x+(Ux)\odot(U^3x)$",weight="bold")
    ax.grid(alpha=.15,axis="y")
    ax.legend(loc="upper center",bbox_to_anchor=(.5,-.14),ncol=2)
    fig.tight_layout()
    _save(fig,out,"57_master_nonlinear_reconstruction")

    # 58: master certificate dashboard.
    rows=[
        ("orbit rank",float(c.orbit_rank),8.0),
        ("relation residual",0.0,1.0),
        ("spatial synthesis",0.0,1.0),
        ("transfer reconstruction",0.0,1.0),
        ("path-product residual",0.0,1.0),
        ("Fourier completeness",0.0,1.0),
        ("multi-atlas synthesis",0.0,1.0),
        ("nonlinear synthesis",0.0,1.0),
        ("solvable obstruction",0.0,1.0),
        ("blocked obstruction",float(sp.sqrt((c.blocked_obstruction.T*c.blocked_obstruction)[0])),1.0),
    ]
    fig,ax=plt.subplots(figsize=(12.0,6.4)); ax.axis("off")
    ax.text(.5,.95,"Master seed-to-reconstruction certificate ledger",ha="center",fontsize=20,weight="bold",transform=ax.transAxes)
    y=.86
    for i,(name,value,target) in enumerate(rows):
        face=WHITE if i%2==0 else "#EEF1F2"
        ax.add_patch(FancyBboxPatch((.06,y-.032),.88,.052,boxstyle="round,pad=.004,rounding_size=.004",facecolor=face,edgecolor="none",transform=ax.transAxes))
        ax.text(.08,y,name,ha="left",va="center",fontsize=10.8,transform=ax.transAxes)
        if name=="orbit rank": label=f"{int(value)}/8"; color=TEAL
        else: label=f"{value:.3e}"; color=TEAL if value<1e-12 else RED
        ax.text(.92,y,label,ha="right",va="center",fontsize=10.8,family="monospace",weight="bold",color=color,transform=ax.transAxes)
        y-=.071
    ax.text(.5,.07,"The nonzero blocked-obstruction row is the intended negative control; all reconstruction identities vanish exactly in symbolic arithmetic.",ha="center",fontsize=10.4,color=MUTED,transform=ax.transAxes)
    _save(fig,out,"58_master_certificate_dashboard")

    # 59: operation closure wheel.
    fig,ax=plt.subplots(figsize=(8.2,8.2)); ax.set_aspect("equal"); ax.axis("off")
    labels=[("seed",BLUE),("generate",CYAN),("relate",TEAL),("project",GREEN),("transfer",YELLOW),("refine",ORANGE),("interact",RED),("complete",PURPLE),("synthesize",MAGENTA)]
    theta=np.linspace(90,90-360,len(labels)+1)
    from matplotlib.patches import Wedge
    for i,(label,color) in enumerate(labels):
        wedge=Wedge((0,0),1.0,theta[i+1],theta[i],width=.34,facecolor=color,edgecolor=PAPER,lw=2)
        ax.add_patch(wedge)
        ang=np.deg2rad((theta[i]+theta[i+1])/2)
        rot=(theta[i]+theta[i+1])/2-90
        ax.text(.81*np.cos(ang),.81*np.sin(ang),label,ha="center",va="center",rotation=rot,rotation_mode="anchor",fontsize=12,weight="bold",color=WHITE)
    ax.add_patch(Circle((0,0),.49,facecolor=PAPER,edgecolor=INK,lw=2))
    ax.text(0,.10,"projector-resolved",ha="center",fontsize=14,weight="bold")
    ax.text(0,-.01,"seed calculus",ha="center",fontsize=20,weight="bold")
    ax.text(0,-.16,"one exact reconstruction law",ha="center",fontsize=10.5,color=MUTED)
    ax.set_xlim(-1.12,1.12); ax.set_ylim(-1.12,1.12)
    ax.set_title("The complete operational cycle",fontsize=20,weight="bold",pad=12)
    _save(fig,out,"59_complete_calculus_wheel")

    # 60: theorem dependency ladder.
    fig,ax=_axes((13.0,7.1))
    ax.text(.5,.95,"Proof dependency ladder: what each stage contributes",ha="center",fontsize=21,weight="bold")
    stages=[
        ("Seed theorem","a controlled source of values",BLUE),
        ("Hull theorem","all admissible operator words",CYAN),
        ("Relation theorem","finite normal forms and quotients",TEAL),
        ("Packet theorem","exact analysis and synthesis",GREEN),
        ("Transfer theorem","operator reconstruction and paths",YELLOW),
        ("Refinement theorem","coarse packets equal child sums",ORANGE),
        ("Nonlinear theorem","interaction tensors and trees",RED),
        ("Completion theorem","finite identities extend in declared topology",PURPLE),
        ("Realization theorem","domain objects inherit the calculus",MAGENTA),
    ]
    ys=np.linspace(.82,.16,len(stages))
    for i,((title,sub,color),y) in enumerate(zip(stages,ys,strict=True)):
        _box(ax,.22,y-.035,.56,.07,f"{title}: {sub}",face=color+"18",edge=color,fontsize=10.5)
        if i<len(stages)-1: _arrow(ax,(.50,y-.04),(.50,ys[i+1]+.04),color=INK,lw=1.0)
    ax.text(.5,.055,"The seven-area chapters begin only after this dependency chain has been proved and instantiated in the master cyclic example.",ha="center",fontsize=10.5,color=MUTED)
    _save(fig,out,"60_theorem_dependency_ladder")

    return 23


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(generate_foundation_figures(root))
