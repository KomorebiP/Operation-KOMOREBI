#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import math

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Polygon

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "figures"
RESULTS = ROOT / "results" / "atlas_results.json"
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "pdf.fonttype": 42,
})

COLORS = {
    "restricted": "#355C7D",
    "ambient": "#C06C84",
    "neutral": "#6C757D",
    "accent": "#F8B195",
    "green": "#4E8A6A",
    "gold": "#C49A3A",
    "purple": "#6C5B7B",
    "light": "#F4F6F8",
    "dark": "#263238",
}


def save(fig, name: str) -> None:
    fig.savefig(FIG / name, bbox_inches="tight")
    plt.close(fig)


def rounded(ax, xy, w, h, text, face, edge="#263238", fontsize=10, lw=1.2, radius=0.08):
    box = FancyBboxPatch(xy, w, h, boxstyle=f"round,pad=0.02,rounding_size={radius}",
                         facecolor=face, edgecolor=edge, linewidth=lw)
    ax.add_patch(box)
    ax.text(xy[0] + w/2, xy[1] + h/2, text, ha="center", va="center", fontsize=fontsize)
    return box


def arrow(ax, start, end, text=None, rad=0.0, color=None, lw=1.4):
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                            connectionstyle=f"arc3,rad={rad}", linewidth=lw,
                            color=color or COLORS["dark"])
    ax.add_patch(patch)
    if text:
        mx, my = (start[0]+end[0])/2, (start[1]+end[1])/2
        ax.text(mx, my + (0.08 if rad >= 0 else -0.1), text, ha="center", va="center", fontsize=9,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))


def gate_hierarchy():
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    levels = [
        (0.5, 0.45, 9.0, 5.0, "All unitary or channel realizations", "#FDEDEC"),
        (1.15, 1.05, 7.7, 4.0, "Universal gate sets / full reversible groups", "#F9EBEA"),
        (1.8, 1.65, 6.4, 3.0, "Clifford, parity-preserving, or symmetry-preserving models", "#EBF5FB"),
        (2.45, 2.25, 5.1, 2.0, "Linear, Gaussian, affine, or diagonal submodels", "#E8F8F5"),
        (3.1, 2.85, 3.8, 1.0, "Architecture / flag preserving gates", "#FEF9E7"),
    ]
    for x,y,w,h,t,c in levels:
        rounded(ax,(x,y),w,h,t,c,fontsize=10)
    ax.text(5,5.7,"Nested gate models define a distortion atlas",ha="center",fontsize=14,fontweight="bold")
    ax.text(5,0.15,"Every inclusion H <= G yields intrinsic and ambient costs for targets U in H.",ha="center",fontsize=10)
    save(fig,"gate_hierarchy.pdf")


def catalytic_excursion():
    fig, ax = plt.subplots(figsize=(10,4.8))
    ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
    rounded(ax,(0.4,1.7),1.5,1.1,"restricted\nstate",COLORS["light"])
    rounded(ax,(2.3,3.2),1.4,0.9,"open g", "#FCE4EC")
    rounded(ax,(4.1,3.2),1.8,0.9,"reuse carrier\nh_1,...,h_m", "#FFF3E0")
    rounded(ax,(6.3,3.2),1.4,0.9,"close g^{-1}", "#FCE4EC")
    rounded(ax,(8.1,1.7),1.5,1.1,"target U in H",COLORS["light"])
    arrow(ax,(1.9,2.25),(2.3,3.55),"leave H")
    arrow(ax,(3.7,3.65),(4.1,3.65))
    arrow(ax,(5.9,3.65),(6.3,3.65))
    arrow(ax,(7.7,3.55),(8.1,2.25),"return")
    arrow(ax,(1.9,2.05),(8.1,2.05),"best path constrained to H",rad=-0.12,color=COLORS["restricted"])
    ax.text(5,4.65,"Catalytic escape: a short ambient loop realizes expensive restricted holonomy",ha="center",fontsize=13,fontweight="bold")
    ax.text(5,0.55,r"gain = restricted cost - [2 cost(g) + middle cost]",ha="center",fontsize=11)
    save(fig,"catalytic_excursion_general.pdf")


def pareto_resources():
    fig, ax = plt.subplots(figsize=(7.2,5.5))
    ax.set_xlim(0,8); ax.set_ylim(0,8)
    ax.set_xlabel("two-qubit / nonlocal cost")
    ax.set_ylabel("single-qubit / basis-change cost")
    restricted=[(6.5,1.0),(5.3,2.1),(4.5,3.4),(4.0,4.8)]
    ambient=[(5.3,0.6),(4.2,1.5),(3.0,3.0),(2.6,5.2)]
    ax.plot(*zip(*restricted),marker="o",label="restricted Pareto boundary",linewidth=2,color=COLORS["restricted"])
    ax.plot(*zip(*ambient),marker="o",label="ambient Pareto boundary",linewidth=2,color=COLORS["ambient"])
    for x,y in restricted: ax.fill_between([x,8],[y,y],[8,8],alpha=0.03,color=COLORS["restricted"])
    ax.annotate("cost model selects\na supporting hyperplane",xy=(4.2,1.5),xytext=(5.2,5.9),
                arrowprops=dict(arrowstyle="->"),ha="center")
    ax.grid(alpha=0.25); ax.legend(loc="upper right")
    ax.set_title("Gate-set distortion is resource-vector dependent")
    save(fig,"resource_pareto.pdf")


def draw_circuit(ax, n, gates, title, x0=0.6, x1=9.4, labels=None):
    labels = labels or [f"q_{i}" for i in range(n)]
    ys=[n-i for i in range(n)]
    for i,y in enumerate(ys):
        ax.plot([x0,x1],[y,y],color="#444",lw=1.2)
        ax.text(x0-0.15,y,labels[i],ha="right",va="center",fontsize=9)
    spacing=(x1-x0)/(len(gates)+1)
    for k,g in enumerate(gates,1):
        x=x0+k*spacing
        typ=g[0]
        if typ in ("CX","SUM"):
            c,t=g[1],g[2]
            yc,yt=ys[c],ys[t]
            ax.plot([x,x],[yc,yt],color=COLORS["dark"],lw=1.2)
            ax.add_patch(Circle((x,yc),0.08,facecolor=COLORS["dark"],edgecolor=COLORS["dark"]))
            ax.add_patch(Circle((x,yt),0.15,facecolor="white",edgecolor=COLORS["dark"],lw=1.2))
            ax.plot([x-0.11,x+0.11],[yt,yt],color=COLORS["dark"],lw=1.1)
            ax.plot([x,x],[yt-0.11,yt+0.11],color=COLORS["dark"],lw=1.1)
            if typ=="SUM" and len(g)>3:
                ax.text(x, min(yc,yt)-0.32, str(g[3]), ha="center", fontsize=8)
        elif typ=="CZ":
            a,b=g[1],g[2]; ya,yb=ys[a],ys[b]
            ax.plot([x,x],[ya,yb],color=COLORS["dark"],lw=1.2)
            ax.add_patch(Circle((x,ya),0.08,facecolor=COLORS["dark"],edgecolor=COLORS["dark"]))
            ax.add_patch(Circle((x,yb),0.08,facecolor=COLORS["dark"],edgecolor=COLORS["dark"]))
        elif typ in ("H","S","T","RZ"):
            q=g[1]; y=ys[q]
            ax.add_patch(Rectangle((x-0.18,y-0.18),0.36,0.36,facecolor="white",edgecolor=COLORS["dark"],lw=1.2))
            ax.text(x,y,typ if typ!="RZ" else r"R_z",ha="center",va="center",fontsize=9)
        elif typ=="TOF":
            controls,target=g[1],g[2]
            yvals=[ys[c] for c in controls]+[ys[target]]
            ax.plot([x,x],[min(yvals),max(yvals)],color=COLORS["dark"],lw=1.2)
            for c in controls:
                ax.add_patch(Circle((x,ys[c]),0.08,facecolor=COLORS["dark"],edgecolor=COLORS["dark"]))
            yt=ys[target]
            ax.add_patch(Circle((x,yt),0.15,facecolor="white",edgecolor=COLORS["dark"],lw=1.2))
            ax.plot([x-0.11,x+0.11],[yt,yt],color=COLORS["dark"],lw=1.1)
            ax.plot([x,x],[yt-0.11,yt+0.11],color=COLORS["dark"],lw=1.1)
        elif typ=="MEAS":
            q=g[1]; y=ys[q]
            ax.add_patch(Rectangle((x-0.2,y-0.18),0.4,0.36,facecolor="#FFFDE7",edgecolor=COLORS["dark"],lw=1.2))
            ax.text(x,y,"M",ha="center",va="center",fontsize=9)
    ax.text((x0+x1)/2,n+0.65,title,ha="center",fontsize=11,fontweight="bold")
    ax.set_xlim(x0-0.8,x1+0.3); ax.set_ylim(0.2,n+1.1); ax.axis("off")


def qudit_sum():
    fig, ax = plt.subplots(figsize=(11,5.2))
    gates=[("SUM",2,1,"+1"),("SUM",1,3,"+1"),("SUM",0,1,"+1"),("SUM",1,4,"+1"),("SUM",1,5,"+1"),("SUM",2,1,"-1")]
    draw_circuit(ax,6,gates,"Universal six-qudit catalytic SUM circuit",labels=["x","p","q","t_0","t_1","t_2"])
    ax.text(5.1,0.35,"The first and last gates open and close one reverse-directed dependency.",ha="center",fontsize=9)
    save(fig,"qudit_sum_circuit.pdf")


def clifford_two_qubit():
    fig, axes = plt.subplots(1,2,figsize=(12,3.5))
    restricted=[("CX",0,1),("S",1),("CX",1,0),("CX",0,1)]
    ambient=[("H",1),("CX",1,0),("CX",0,1),("H",0),("S",1),("S",0)]
    draw_circuit(axes[0],2,restricted,"Parabolic realization: 3 entangling gates")
    draw_circuit(axes[1],2,ambient,"Ambient Clifford realization: 2 entangling gates")
    fig.suptitle("Exact two-qubit basis-escape defect when local Clifford gates are free",fontsize=13,fontweight="bold")
    save(fig,"clifford_two_qubit_defect.pdf")


def clifford_three_qubit():
    fig, axes = plt.subplots(2,1,figsize=(12,7.5))
    restricted=[("CX",0,2),("CZ",1,2),("CX",2,0),("CX",0,2),("CX",0,1),("CX",1,0),("CX",0,1)]
    ambient=[("H",1),("CX",1,2),("CX",2,1),("CX",2,0),("CX",0,2),("H",0)]
    draw_circuit(axes[0],3,restricted,"Restricted parabolic word: 7 primitive gates")
    draw_circuit(axes[1],3,ambient,"Ambient symplectic Clifford word: 6 primitive gates")
    fig.suptitle("A computer-certified three-qubit total-gate defect",fontsize=13,fontweight="bold")
    save(fig,"clifford_three_qubit_defect.pdf")


def clifford_census():
    data=json.loads(RESULTS.read_text())
    labels=[]; values=[]; colors=[]
    for entry in data["clifford"]:
        if entry["qubits"] in (2,3) and not entry["include_swap"]:
            labels.append(f"n={entry['qubits']}\n{entry['metric']}")
            values.append(entry["defect_count"])
            colors.append(COLORS["ambient"] if entry["metric"]=="entangling" else COLORS["restricted"])
    fig, ax=plt.subplots(figsize=(8.5,5.2))
    bars=ax.bar(labels,values,color=colors,edgecolor="#333")
    ax.set_yscale("symlog",linthresh=1)
    ax.set_ylabel("number of defective parabolic targets (symlog scale)")
    ax.set_title("Exact Clifford censuses depend strongly on the resource metric")
    for b,v in zip(bars,values): ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.25,str(v),ha="center",va="bottom")
    ax.grid(axis="y",alpha=0.25)
    ax.text(0.98,0.02,"At n=3, adding SWAP as a unit-cost primitive removes all total-count defects.",transform=ax.transAxes,ha="right",fontsize=9)
    save(fig,"clifford_census.pdf")


def affine_toffoli():
    fig, ax=plt.subplots(figsize=(10,4.8))
    ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
    rounded(ax,(0.5,1.45),3.3,2.2,"Affine reversible group\n<X, CNOT>\n1344 elements on 3 bits", "#E8F8F5",fontsize=11)
    rounded(ax,(6.2,1.0),3.3,3.1,"Full 3-bit reversible group\n<X, CNOT, Toffoli>\n40320 elements", "#FDEDEC",fontsize=11)
    arrow(ax,(3.8,2.55),(6.2,2.55),"add temporary nonlinearity")
    ax.text(5,4.55,"Exact three-bit census: no affine target becomes shorter",ha="center",fontsize=13,fontweight="bold")
    ax.text(5,0.45,"This is a rigidity result for n=3, not a proof for n >= 4.",ha="center",fontsize=10)
    save(fig,"affine_toffoli_census.pdf")


def nonlinear_skeleton():
    fig, ax=plt.subplots(figsize=(11,4.5))
    gates=[("TOF",(0,1),2),("CX",2,3),("CX",0,2),("CX",2,4),("TOF",(0,1),2)]
    draw_circuit(ax,5,gates,"Temporary-nonlinearity search template",labels=["a","b","workspace","y_1","y_2"])
    ax.text(5.1,0.33,"Candidate mechanism only: exact affine shortcuts are absent on three bits and open beyond that census.",ha="center",fontsize=8.8)
    save(fig,"temporary_nonlinearity_skeleton.pdf")


def phase_skeleton():
    fig, axes=plt.subplots(1,2,figsize=(12,4))
    draw_circuit(axes[0],3,[("CX",0,2),("CX",1,2),("RZ",2),("CX",1,2),("CX",0,2)],"Diagonal phase-polynomial realization")
    draw_circuit(axes[1],3,[("H",2),("CZ",0,2),("CZ",1,2),("RZ",2),("H",2)],"Basis-escaped phase-gadget template")
    fig.suptitle("Clifford+T and phase-polynomial catalyst templates",fontsize=13,fontweight="bold")
    save(fig,"phase_polynomial_skeleton.pdf")


def gaussian():
    fig, ax=plt.subplots(figsize=(10,5.4))
    ax.set_xlim(-3.5,3.5); ax.set_ylim(-3.0,3.0); ax.axis("off")
    circle=Circle((0,0),2.1,fill=False,edgecolor=COLORS["neutral"],lw=1.5); ax.add_patch(circle)
    ax.arrow(-2.7,0,5.4,0,head_width=0.12,head_length=0.18,length_includes_head=True,color=COLORS["dark"])
    ax.arrow(0,-2.5,0,5.0,head_width=0.12,head_length=0.18,length_includes_head=True,color=COLORS["dark"])
    ax.text(2.9,-0.25,"q",fontsize=11); ax.text(0.15,2.55,"p",fontsize=11)
    poly=Polygon([(-1.4,-1.1),(1.4,-0.5),(1.4,1.1),(-1.4,0.5)],closed=True,facecolor="#EBF5FB",edgecolor=COLORS["restricted"],alpha=0.8)
    ax.add_patch(poly)
    arrow(ax,(-1.0,-1.75),(1.35,1.55),"Fourier / rotation catalyst",rad=0.15,color=COLORS["ambient"])
    ax.text(0,2.85,"Gaussian analogue: shears, rotations, and temporary quadrature mixing",ha="center",fontsize=13,fontweight="bold")
    ax.text(0,-2.75,r"X_A = [[I,A],[0,I]],  Z_B = [[I,0],[B,I]],  F X_A F^{-1} = Z_{-A}",ha="center",fontsize=10)
    save(fig,"gaussian_shear_catalysis.pdf")


def packet_hierarchy():
    fig, ax=plt.subplots(figsize=(10,6))
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis("off")
    items=[
        (0.7,5.5,2.2,0.9,"Spherical packet\neigenvalues, multiplicities","#EAF2F8"),
        (3.3,5.5,2.2,0.9,"Embedded type\nprojectors, incidence","#E8F8F5"),
        (5.9,5.5,2.2,0.9,"Holonomy packet\nordered transitions","#FEF9E7"),
        (3.3,3.5,2.8,1.0,"Restricted realization\ngeodesic, factorization, descent","#FDEDEC"),
        (3.3,1.5,2.8,1.0,"Threshold defect\nmetric or existence","#F5EEF8"),
    ]
    for x,y,w,h,t,c in items: rounded(ax,(x,y),w,h,t,c,fontsize=10)
    arrow(ax,(2.9,5.95),(3.3,5.95),"refine")
    arrow(ax,(5.5,5.95),(5.9,5.95),"retain order")
    arrow(ax,(7.0,5.5),(5.4,4.5),"test")
    arrow(ax,(4.7,3.5),(4.7,2.5),"fails or costs more")
    ax.text(5,6.75,"Projector-resolved hierarchy for combinatorial and quantum thresholds",ha="center",fontsize=13,fontweight="bold")
    ax.text(5,0.65,"Coarse spectra can coincide while realization fibers differ.",ha="center",fontsize=10)
    save(fig,"packet_hierarchy.pdf")


def quantum_latin_gap():
    fig, ax=plt.subplots(figsize=(9.5,4.8))
    ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
    rounded(ax,(0.7,1.5),3.2,2.0,"Non-entangled MOQLS(6)\nrestricted realization\nEMPTY", "#FDEDEC",fontsize=12)
    rounded(ax,(6.1,1.5),3.2,2.0,"Entangled quantum Latin\nrealization / AME(4,6)\nNONEMPTY", "#E8F8F5",fontsize=12)
    arrow(ax,(3.9,2.5),(6.1,2.5),"allow entanglement")
    ax.text(5,4.45,"Existence defect: enlarging the realization category changes feasibility",ha="center",fontsize=13,fontweight="bold")
    ax.text(5,0.65,"Contextual example; it is not the same local packet as the CNOT obstruction.",ha="center",fontsize=9.5)
    save(fig,"quantum_latin_realization_gap.pdf")


def pipeline():
    fig, ax=plt.subplots(figsize=(12,5.2))
    ax.set_xlim(0,12); ax.set_ylim(0,5); ax.axis("off")
    stages=[
        (0.3,"Define\ngate models"),(2.2,"Normalize\ntargets"),(4.1,"Exact search\nor symbolic word"),
        (6.0,"Extract\ncatalytic motif"),(7.9,"Prove restricted\nlower bound"),(9.8,"Amplify and\nregularize")]
    for x,text in stages:
        rounded(ax,(x,2.0),1.55,1.1,text,"#F4F6F8",fontsize=9.5)
    for i in range(len(stages)-1): arrow(ax,(stages[i][0]+1.55,2.55),(stages[i+1][0],2.55))
    rounded(ax,(4.1,0.35),3.45,0.9,"certificate: word, distance, orbit, status", "#FFF3E0",fontsize=9.5)
    arrow(ax,(5.8,2.0),(5.8,1.25))
    ax.text(6,4.45,"Reproducible threshold-discovery pipeline",ha="center",fontsize=13,fontweight="bold")
    save(fig,"computational_pipeline.pdf")


def root_catalysis():
    fig, ax=plt.subplots(figsize=(10,5.2))
    ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis("off")
    points={"alpha":(2,3),"beta":(5,1.4),"a+b":(5,4.6),"b+2a":(8,3)}
    for name,(x,y) in points.items():
        ax.add_patch(Circle((x,y),0.28,facecolor="#EAF2F8",edgecolor=COLORS["dark"],lw=1.2))
        ax.text(x,y,name,ha="center",va="center",fontsize=9)
    arrow(ax,points["alpha"],points["a+b"],"conjugation",rad=0.1)
    arrow(ax,points["beta"],points["a+b"],"root sum",rad=-0.1)
    arrow(ax,points["a+b"],points["b+2a"],"longer string",rad=0.05)
    ax.text(5,5.65,"Root-system catalysis skeleton",ha="center",fontsize=13,fontweight="bold")
    ax.text(5,0.45,r"x_alpha(a) x_beta(b) x_alpha(a)^{-1} = x_beta(b) prod x_{beta+k alpha}(c_k a^k b)",ha="center",fontsize=10)
    save(fig,"root_catalysis.pdf")


def status_map():
    fig, ax=plt.subplots(figsize=(10,6.5))
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis("off")
    rows=[
        (5.9,"Proved analytically","universal SUM atom; snapshot families; algebraic rarity; tensor rules", "#E8F8F5"),
        (4.5,"Exact computation","binary threshold; small Clifford censuses; three-bit affine rigidity", "#EAF2F8"),
        (3.1,"Formal skeleton","Clifford+T; Gaussian; matchgate; charge; measurement-assisted", "#FEF9E7"),
        (1.7,"Conjectural frontier","multi-catalyst ratios; Toffoli threshold; root-system thresholds", "#FDEDEC"),
    ]
    for y,title,desc,c in rows:
        rounded(ax,(0.7,y),2.2,0.8,title,c,fontsize=10)
        rounded(ax,(3.2,y),6.1,0.8,desc,"white",fontsize=9)
    ax.text(5,6.75,"Status separation used throughout the monograph",ha="center",fontsize=13,fontweight="bold")
    ax.text(5,0.55,"A symbolic research program is useful only when proved, computed, and proposed claims remain distinct.",ha="center",fontsize=9.5)
    save(fig,"status_map.pdf")


def tensor_capacity():
    fig, ax=plt.subplots(figsize=(8.5,5.4))
    r=range(1,9)
    restricted=[1.45*x for x in r]
    ambient=[1.0*x+0.25*math.sqrt(x) for x in r]
    ax.plot(list(r),restricted,marker="o",label="normalized restricted tensor cost",color=COLORS["restricted"],lw=2)
    ax.plot(list(r),ambient,marker="o",label="normalized ambient tensor cost",color=COLORS["ambient"],lw=2)
    ax.fill_between(list(r),ambient,restricted,alpha=0.15,color=COLORS["gold"],label="stable catalytic capacity")
    ax.set_xlabel("tensor exponent r")
    ax.set_ylabel(r"cost / m^{r-1}")
    ax.set_title("Regularization can reveal collective tensor activation")
    ax.grid(alpha=0.25); ax.legend()
    save(fig,"tensor_capacity.pdf")


def main():
    gate_hierarchy(); catalytic_excursion(); pareto_resources(); qudit_sum(); clifford_two_qubit(); clifford_three_qubit(); clifford_census(); affine_toffoli(); nonlinear_skeleton(); phase_skeleton(); gaussian(); packet_hierarchy(); quantum_latin_gap(); pipeline(); root_catalysis(); status_map(); tensor_capacity()
    print(f"wrote figures to {FIG}")

if __name__ == "__main__":
    main()
