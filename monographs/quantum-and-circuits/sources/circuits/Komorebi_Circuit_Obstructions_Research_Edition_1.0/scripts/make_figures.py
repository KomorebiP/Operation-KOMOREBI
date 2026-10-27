#!/usr/bin/env python3
"""Generate exact vector figures and fixture provenance for the visual guide.

No data are sampled or inferred from drawings. Source checkers are imported
read-only; their main functions are not invoked. Finite examples are asserted
separately from the all-size formulas proved in THEORY.md.
"""
from pathlib import Path
from itertools import product
from collections import Counter
import hashlib
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/komorebi-circuit-obstructions-v1.2.0"
sys.path.insert(0, str(SOURCE / "checks"))
import reversible as rv
import truth_tables as tt
import verify_projection as vp
import verify_fingerprint as vf
import verify_completeness as vc

FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
TEAL, GOLD, INK, RED, PALE = "#176F72", "#A56F26", "#173238", "#AF493D", "#F1F5F3"
plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 11,
                    "axes.spines.top": False, "axes.spines.right": False,
                    "axes.labelcolor": INK, "text.color": INK,
                    "axes.edgecolor": INK, "pdf.fonttype": 42,
                    "savefig.facecolor": "white"})
DATA = {"status": "PASS", "arithmetic": "exact Boolean/F2 and GF16",
        "source_release": "v1.2.0", "figures": {}, "fixtures": {},
        "scope": "new exact finite fixtures plus plots of proved all-size formulas"}


def save(fig, name, description):
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.12, dpi=180)
    plt.close(fig)
    DATA["figures"][name] = description


def canvas(size=(7.2, 3.8)):
    fig, ax = plt.subplots(figsize=size)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, color=TEAL, fontsize=12):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
                           facecolor=PALE, edgecolor=color, linewidth=1.5)
    ax.add_patch(patch)
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fontsize, color=color)


def arrow(ax, start, end, color=INK):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                               linewidth=1.3, color=color))


def table_figure(columns, rows, rowlabels=None, size=(7.2, 3.2), fontsize=11):
    fig, ax = canvas(size)
    t = ax.table(cellText=rows, colLabels=columns, rowLabels=rowlabels,
                 cellLoc="center", loc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(fontsize)
    t.scale(1, 1.85)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#CCD6DA")
        cell.set_text_props(color=INK)
        if r == 0:
            cell.set_facecolor(TEAL)
            cell.set_text_props(color="white")
        else:
            cell.set_facecolor(PALE if r % 2 else "white")
    return fig, ax


# 1. The arbitrary-cut diagram, with exact named objects from C01.
fig, ax = canvas((7.2, 3.3)); ax.set_xlim(0, 8); ax.set_ylim(0, 3.2)
box(ax, .15, 2.15, 1.65, .65, r"$(x,0^a,0)$")
box(ax, 2.55, 2.15, 1.35, .65, r"$P$")
box(ax, 4.65, 2.15, 2.55, .65, r"$A=P(x,0)$")
arrow(ax, (1.85, 2.48), (2.5, 2.48)); arrow(ax, (3.95, 2.48), (4.6, 2.48))
box(ax, .15, .85, 1.65, .65, r"$(x,0^a,0)$", GOLD)
box(ax, 2.55, .85, 1.35, .65, r"$Q^{-1}$", GOLD)
box(ax, 4.65, .85, 2.55, .65, r"$B=P(x,f(x))$", GOLD)
arrow(ax, (1.85, 1.18), (2.5, 1.18), GOLD); arrow(ax, (3.95, 1.18), (4.6, 1.18), GOLD)
ax.text(4.1, .2, r"$H=A+B=f(x)D(x),\qquad D=P(x,1)+P(x,0)\ne0$", ha="center", fontsize=13)
save(fig, "cut_transport", "C01 exact forward/inverse-suffix comparison; schematic, no numerical data")

# 2. The exact four-wire dirty-workspace fixture from Lean Examples.
ops = [("T", 0, 1, 2), ("C", 2, 3), ("T", 0, 1, 2)]
rv.validate(ops, 4)
traces = [rv.trace(ops, [1, 1, 0, y], 1) for y in (0, 1)]
for y, states in enumerate(traces): assert states[-1] == [1, 1, 0, y ^ 1]
DATA["fixtures"]["dirty_and"] = {"wire_order": ["a", "b", "scratch", "target"],
 "gates": ops, "initial_targets": [0, 1], "traces": traces, "Toffolis": 2,
 "note": "legal Lean witness, not the optimal AND2 oracle"}
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.3), constrained_layout=True)
from matplotlib.colors import ListedColormap
for y, ax in enumerate(axs):
    values = np.array(traces[y]).T
    ax.imshow(values, cmap=ListedColormap([PALE, TEAL]), vmin=0, vmax=1, aspect="auto")
    for i in range(4):
        for j in range(4):
            ax.text(j, i, str(values[i,j]), ha="center", va="center", color="white" if values[i,j] else INK, fontsize=14)
    ax.set_xticks(range(4), ["start", "compute", "copy", "restore"], fontsize=9)
    ax.set_yticks(range(4), ["a", "b", "scratch", "target"])
    ax.set_title(f"a=b=1; initial target {y}", fontsize=11)
    for spine in ax.spines.values(): spine.set_visible(False)
save(fig, "dirty_and_trace", "Exact four-wire AND compute/copy/uncompute traces for both target values")

# 3. All 32 assignments of unbalanced OR F3 on a,b,z1,z2,z3.
n=5; vs=rv.variables(n); f=(vs[0]&vs[1]) | (vs[2]&vs[3]&vs[4]); g=f^vs[0]
alpha,beta=tt.profile(f,n); assert (alpha,beta)==(2,3)
masks=tt.affine_masks(n); orbit=[tt.profile(f^l,n) for l in masks]
assert (max(a for a,b in orbit), max(b for a,b in orbit))==(3,4)
DATA["fixtures"]["unbalanced_or"]={"n":n,"k":3,"truth_table":f,"shifted_truth_table":g,
 "alpha":alpha,"beta":beta,"affine_masks_checked":len(masks),"alphaStar":3,"betaStar":4,
 "positive_count":f.bit_count(),"complete_Toffoli_lower_bound":5,"combined_degree_one_packet_lower_bound":4}
fig,ax=plt.subplots(figsize=(7.2,3.5));
for ab in range(4):
    for z in range(8):
        x=ab|(z<<2); positive=(f>>x)&1
        color=TEAL if ab==3 else GOLD if z==7 else "#D7DEDC"
        ax.scatter(z,ab,s=200,color=color,edgecolor="white")
        if positive:ax.text(z,ab,"1",ha="center",va="center",color="white",fontsize=10)
ax.set_yticks(range(4), ["ab=00","ab=10","ab=01","ab=11"])
ax.set_xticks(range(8),[format(z,"03b")[::-1] for z in range(8)])
ax.set_xlabel(r"$(z_1,z_2,z_3)$");ax.set_xlim(-.5,7.5);ax.set_ylim(-.6,3.6)
ax.text(.03,1.05,"Teal: packet ab (degree 2)     Gold: additional positives hit by z₁z₂z₃",transform=ax.transAxes,fontsize=10)
save(fig,"packet_coverage","Exact 32-point F3 accepting set, complete safe cover ab and z1z2z3")

# 4. Singleton AND2's degree-one evaluation dependence.
points=[(0,0),(1,0),(0,1),(1,1)]
evaluation=[[1,*x] for x in points]
assert [evaluation[0][i]^evaluation[1][i]^evaluation[2][i] for i in range(3)]==evaluation[3]
fig,ax=table_figure(["point (a,b)","1","a","b","AND(a,b)"],
 [[str(x),*row,int(x==(1,1))] for x,row in zip(points,evaluation)],size=(7.2,3.0))
ax.text(.5,.03,r"$v_1(11)=v_1(00)+v_1(10)+v_1(01)$",transform=ax.transAxes,ha="center",fontsize=14)
save(fig,"evaluation_dual","Exact three-negative degree-one certificate for AND2's positive point")
DATA["fixtures"]["evaluation_dual"]={"n":2,"d":1,"positive":[1,1],"negatives":points[:3],"rows":evaluation,"beta":2}

# 5. Shared computation and degrees from complete truth tables on four bits.
ops=[("T",0,1,4),("T",2,3,5),("T",4,5,6)]; rv.validate(ops,7)
states=rv.trace(ops,rv.variables(4)+[0,0,0],rv.one(4))
maxdeg=[max(rv.degree(s,4) for s in st) for st in states]
assert maxdeg==[1,2,2,4]
productdeg=rv.degree(states[2][4]&states[2][5],4);assert productdeg==4
fig,ax=plt.subplots(figsize=(7.2,3.6));t=np.arange(4)
ax.plot(t,t+1,"--",color=GOLD,linewidth=2,label="coordinate bound t+1")
ax.plot(t,maxdeg,"o-",color=TEAL,linewidth=2,label="actual maximum coordinate degree")
ax.scatter([2],[4],s=110,marker="s",color=RED,label="product of two registers at t=2")
ax.set_xticks(t,["initial","q₁=x₁x₂","q₂=x₃x₄","q₃=q₁q₂"]);ax.set_yticks(range(1,6))
ax.set_ylabel("exact Boolean degree");ax.set_ylim(.7,5.1)
ax.legend(loc="upper left",frameon=False,fontsize=9)
save(fig,"sharing_degree","Exact four-input shared register degrees; product degree 4 after two ANDs")
DATA["fixtures"]["sharing_degree"]={"n":4,"gates":ops,"max_coordinate_degree":maxdeg,"product_degree_after_two":4,"product_list_length":2}

# 6. Reconstruct every small restored oracle, verify both target branches.
small=[];counts=Counter(); scalar=0
for n in range(1,4):
    c=Counter()
    for f in range(1<<(1<<n)):
        ops,w,y,T=vc.optimal_small(f,n);rv.validate(ops,w)
        for target in (0,1):
            initial=rv.variables(n)+[0]*(w-n);initial[y]=rv.one(n) if target else 0
            expected=initial[:];expected[y]^=f
            assert rv.trace(ops,initial,rv.one(n))[-1]==expected
            scalar+=1<<n
        assert sum(op[0]=="T" for op in ops)==T
        c[T]+=1;counts[T]+=1
    small.append({"n":n,"functions":sum(c.values()),"counts":dict(c)})
assert dict(counts)=={0:28,1:120,3:128}
DATA["fixtures"]["small_oracles"]={"by_n":small,"totals":dict(counts),"target_input_cases":scalar,"functions":276}
fig,ax=plt.subplots(figsize=(7.2,3.5)); bottom=np.zeros(3)
for T,color in [(0,TEAL),(1,GOLD),(3,RED)]:
    heights=np.array([r["counts"].get(T,0) for r in small]);ax.bar([1,2,3],heights,bottom=bottom,width=.55,color=color,label=f"T={T}")
    for i,h in enumerate(heights):
        if h >= 24:ax.text(i+1,bottom[i]+h/2,str(h),ha="center",va="center",color="white",fontsize=12)
    bottom+=heights
ax.set_xticks([1,2,3],["1 input\n4 functions","2 inputs\n16 functions","3 inputs\n256 functions"])
ax.set_ylabel("number of Boolean functions");ax.legend(frameon=False,loc="upper left")
ax.text(.04,.52,"n=1: 4 affine\nn=2: 8 affine + 8 quadratic",transform=ax.transAxes,fontsize=10,linespacing=1.5)
save(fig,"small_oracle_counts","All 276 functions through three inputs: matching explicit restored constructions")

# 7,8. Source-derived construction counts and theorem cost formulas.
projection=[]
for m in range(2,11):
    labels=list(range(1,(1<<m)-1));n=len(labels)
    ops,w,y=vp.full_oracle(m,labels);qops,qw,qy=vp.q_oracle(labels,(1<<m)-1)
    T=sum(op[0]=="T" for op in ops);C=sum(op[0]=="C" for op in ops)
    assert T==2*m-3 and C==2*m*((1<<(m-1))-1) and len(qops)==n//2
    projection.append({"m":m,"n":n,"P_Toffolis":T,"P_CNOTs":C,"P_total":len(ops),"Q_Toffolis":len(qops),"full_truth_table_enumerated_here":False})
DATA["fixtures"]["projection_costs"]={"rows":projection,"cost_optimality_status":"all-size written proof; gate counts asserted against source constructors"}
fig,ax=plt.subplots(figsize=(7.2,3.6));ns=[r["n"] for r in projection]
ax.plot(ns,[r["P_Toffolis"] for r in projection],"o-",color=TEAL,label=r"full $P_m$: $2m-3$")
ax.plot(ns,[r["Q_Toffolis"] for r in projection],"s-",color=RED,label=r"quadratic $Q_m$: $n/2$")
ax.set_xscale("log",base=2);ax.set_yscale("log",base=2)
ax.set_xlabel("actual input length n = 2ᵐ − 2");ax.set_ylabel("optimal restored Toffoli count")
ax.set_xticks([2,14,62,254,1022],["2","14","62","254","1,022"])
ax.set_yticks([1,4,16,64,256,512],["1","4","16","64","256","512"])
ax.legend(frameon=False,loc="upper left");ax.grid(alpha=.12)
save(fig,"projection_costs","Plots of proved exact formulas against actual n; no synthesis search")
r=projection[-1];fig,axs=plt.subplots(1,2,figsize=(7.2,3.7),constrained_layout=True)
for ax,vals,title in [(axs[0],[r["P_Toffolis"],r["Q_Toffolis"]],"Toffoli gates"),(axs[1],[r["P_total"],r["Q_Toffolis"]],"total gates of these constructions")]:
    bars=ax.bar(["full P₁₀","quadratic Q₁₀"],vals,color=[TEAL,RED],width=.6)
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+max(vals)*.035,f"{v:,}",ha="center",fontsize=12)
    ax.set_ylim(0,max(vals)*1.18);ax.set_title(title,fontsize=11)
save(fig,"projection_m10","m=10 n=1022: exact T 17 vs511; constructed total 10237 vs511")

# 9. Recompute all m=3 projection values, and the first unsafe assignment.
m=3;a=7;labels=list(range(1,a));n=6;vs=rv.variables(n)
forms=[]
for j in range(m):
    h=0
    for i,v in enumerate(labels):
        if v>>j&1:h^=vs[i]
    forms.append(h)
P=rv.one(n)
for h in forms:P&=h
pairs=[(i,j) for i in range(n) for j in range(i+1,n) if labels[i]^labels[j]==a]
Q=0
for i,j in pairs:Q^=vs[i]&vs[j]
bad=Q & (rv.one(n)^P);first=(bad&-bad).bit_length()-1
assert first==13 and bad.bit_count()==24
x=[(first>>i)&1 for i in range(n)];L=[(h>>first)&1 for h in forms]
assert x==[1,0,1,1,0,0] and L==[0,1,1]
DATA["fixtures"]["unsafe_projection"]={"m":3,"n":6,"labels":labels,"assignment_integer":first,"input_bits_little_endian":x,"linear_forms":L,"P":0,"Q":1,"false_positives":24,"all_inputs_checked":64,"pairs_one_based":[[i+1,j+1] for i,j in pairs]}
fig,ax=table_figure(["input","x₁","x₂","x₃","x₄","x₅","x₆"],
 [["label v",*labels],["x (13)",*x]],size=(7.2,3.0),fontsize=11)
ax.text(.5,.11,r"$L=(0,1,1)\Rightarrow P_3=0;\quad Q_3=x_1x_6+x_2x_5+x_3x_4=1$",transform=ax.transAxes,ha="center",fontsize=12)
save(fig,"unsafe_projection","Exact m3 unsafe assignment13, source label ordering1..6")

# 10. Orthogonal idempotents for all four witnesses at m=2.
matrix=np.eye(4,dtype=int);fig,ax=plt.subplots(figsize=(5.5,3.8))
ax.imshow(matrix,cmap=ListedColormap([PALE,TEAL]),vmin=0,vmax=1)
diagonal_labels=["δ₀₀","δ₁₀","δ₀₁","δ₁₁"]
for i in range(4):
    for j in range(4):ax.text(j,i,diagonal_labels[i] if i==j else "0",ha="center",va="center",color="white" if i==j else INK,fontsize=14)
ax.set_xticks(range(4),["δ₀₀","δ₁₀","δ₀₁","δ₁₁"]);ax.set_yticks(range(4),["δ₀₀","δ₁₀","δ₀₁","δ₁₁"])
ax.set_xlabel("right factor");ax.set_ylabel("left factor");
for spine in ax.spines.values():spine.set_visible(False)
save(fig,"orthogonal_gluing","Point-indicator multiplication table for the four-witness product algebra")
DATA["fixtures"]["orthogonal_gluing"]={"m":2,"witness_points":4,"independent_idempotents":4,"matrix":matrix.tolist(),"theorem_hypotheses":"field K; linear multiplicative map; all point images nonzero"}

# 11. Nonzero witness polynomial even though parity of accepts is zero.
accepted=[1,2,5,6];R=sum(1<<s for s in accepted);assert R.bit_count()%2==0
rows=[]
for s in range(8):
    bits=tuple((s>>i)&1 for i in range(3)); mon="1" if s==0 else "".join(f"z{ i+1 }" for i in range(3) if s>>i&1)
    rows.append(["".join(map(str,bits)),int(s in accepted),mon if s in accepted else "—"])
fig,ax=table_figure(["witness (w₁,w₂,w₃)","R(w)","retained monomial"],rows,size=(7.2,4.8),fontsize=10)
save(fig,"witness_fingerprint","Exact m3 verifier accepting1,2,5,6; four distinct monomials survive ordinary parity cancellation")
DATA["fixtures"]["fingerprint"]={"m":3,"truth_table":R,"accepting_witness_integers":accepted,"parity":0,"polynomial_support":accepted,"polynomial":"z1+z2+z1*z3+z2*z3"}

# 12. Exact GF16 overlap controls from the same field routines as the source.
z=2;trace_w=vf.evaluate(2,vf.weights([z]));trace_notw=vf.evaluate(1,vf.weights([z]))
intersection=vf.evaluate(0,vf.weights([z]));square_trace=vf.evaluate(2,vf.weights([z]));product=vf.M[trace_w][trace_notw];squared=vf.M[trace_w][trace_w]
assert (trace_w,trace_notw,intersection,square_trace,product,squared)==(2,1,0,2,2,4)
fig,ax=table_figure(["expression","trace after product","product of traces"],
 [["w(1+w)","0","θ"],["w² = w","θ","θ²"]],size=(7.2,3.3),fontsize=12)
ax.text(.5,.1,"GF(16) = F₂[θ]/(θ⁴+θ+1); θ = integer 2, θ² = integer 4",transform=ax.transAxes,ha="center",fontsize=10)
save(fig,"overlap_gf16","Exact GF16 mismatch at z=theta=2: intersection0 vs2 and idempotence2 vs4")
DATA["fixtures"]["overlap_gf16"]={"modulus":19,"field_size":16,"z":z,"trace_w":trace_w,"trace_notw":trace_notw,"trace_intersection":intersection,"product_traces":product,"trace_boolean_square":square_trace,"square_trace":squared}

DATA["source_sha256"]={str(p.relative_to(SOURCE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/"docs/THEORY.md",SOURCE/"checks/reversible.py",SOURCE/"checks/truth_tables.py",SOURCE/"checks/verify_projection.py",SOURCE/"checks/verify_fingerprint.py",SOURCE/"checks/verify_completeness.py"]}
(ROOT/"reviews/visual_examples.json").write_text(json.dumps(DATA,indent=2)+"\n")
print(f"PASS: {len(DATA['figures'])} PDF/PNG figure pairs; exact fixtures saved")
