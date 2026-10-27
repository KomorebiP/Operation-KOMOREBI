#!/usr/bin/env python3
"""Exact discrete figures for the sequence, tap, tree and parameter chapter."""
from fractions import Fraction as Q
from pathlib import Path
from math import comb
import hashlib
import json
import platform
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import family_lab as lab

ROOT=Path(__file__).resolve().parent
FIG=ROOT/"figures";FIG.mkdir(exist_ok=True)
BLUE="#075985";ORANGE="#e76f51";GREEN="#248f83";PURPLE="#7c3aed"
INK="#193044";GRAY="#64748b"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,
    "axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42,
    "figure.facecolor":"white","savefig.facecolor":"white"})
record={"contract":"SF-DISCOVERY-100","arithmetic":"Exact integers and fractions.Fraction; diagram coordinates only are floating point",
        "python":platform.python_version(),"matplotlib":matplotlib.__version__,"figures":[],
        "non_claims":["The regime chart displays proved classifications, not a numerical test of analytic continuation.",
                      "The two selected trees are examples among all five ordered shapes at n=3.",
                      "No OEIS or historical priority assertion."],
        "recovered_failures":["First visual inspection found overlapping tree footer labels and an output-value label too close to an index tick. Dedicated footer rows and upward value placement repaired both."]}


def save(fig,name,entry):
    paths=[]
    for suffix in ["pdf","png"]:
        path=FIG/f"{name}.{suffix}"
        fig.savefig(path,bbox_inches="tight",dpi=180)
        paths.append({"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    entry.update({"name":name,"files":paths});record["figures"].append(entry)
    plt.close(fig)


def sequence_figure():
    a=[Q(m+1) for m in range(12)];h=[Q(1),Q(2),Q(-1)];base=3
    direct=lab.ordinary_taps(a,h)
    lanes=lab.phase_lanes(a,base);mat=lab.polyphase_tap_matrix(h,base)
    output_lanes=lab.apply_polyphase_matrix(lanes,mat,len(direct))
    reconstructed=lab.merge_lanes(output_lanes,len(direct))
    assert direct==reconstructed
    fig=plt.figure(figsize=(9.4,6.6),layout="constrained")
    gs=fig.add_gridspec(3,3,height_ratios=[1.45,1,1])
    fig.suptitle("A tap crossing a residue carries one whole block",fontsize=15,fontweight="bold",color=INK)
    left=fig.add_subplot(gs[0,0]);left.axis("off")
    left.text(.02,.93,"Ordinary coefficient taps",fontsize=11,fontweight="bold",color=INK,va="top")
    left.text(.02,.74,r"$b_m=a_m+2a_{m-1}-a_{m-2}$",fontsize=11,va="top")
    left.text(.02,.54,"Base 3 phases\n"+r"$x_j[n]=a_{3n+j}$"+"\n"+r"$X_j(t)=\sum_nx_j[n]t^n$",fontsize=10,va="top",linespacing=1.8)
    left.text(.02,.15,"Here t is the formal OGF\nvariable of the block index.",fontsize=9,color=GRAY,va="top")
    center=fig.add_subplot(gs[0,1]);center.axis("off")
    center.text(.5,.93,r"$Y(t)=H(t)X(t)$",ha="center",va="top",fontsize=12,color=INK)
    table=center.table(cellText=[["1",r"$-t$",r"$2t$"],["2","1",r"$-t$"],["−1","2","1"]],
                        rowLabels=[r"$Y_0$",r"$Y_1$",r"$Y_2$"],
                        colLabels=[r"$X_0$",r"$X_1$",r"$X_2$"],
                        cellLoc="center",loc="center",bbox=[.17,.22,.8,.58])
    table.auto_set_font_size(False);table.set_fontsize(11)
    for (row,col),cell in table.get_celld().items():
        cell.set_edgecolor("#cbd5e1")
        cell.set_facecolor("#f1f5f9" if row==0 or col==-1 else "white")
    center.text(.55,.1,"The t factors preserve the carry.",ha="center",fontsize=9,color=PURPLE)
    right=fig.add_subplot(gs[0,2]);right.axis("off")
    right.text(.02,.93,"Input phase arrays",fontsize=11,fontweight="bold",color=INK,va="top")
    phase_colors=[BLUE,ORANGE,GREEN]
    for j,(lane,color) in enumerate(zip(lanes,phase_colors)):
        right.text(.02,.71-j*.2,f"Phase {j}: "+", ".join(str(int(x)) for x in lane),fontsize=10,color=color)
    right.text(.02,.1,"Filter the phases, then interleave.\nExact result equals direct convolution.",fontsize=9,color=GRAY,va="top")
    for row,values,title in [(1,a,"Input sequence: aₘ = m + 1 on m = 0,…,11"),
                              (2,direct,"Reconstructed output: exact agreement at all 14 coefficients")]:
        ax=fig.add_subplot(gs[row,:])
        for m,value in enumerate(values):
            color=phase_colors[m%3]
            ax.vlines(m,0,float(value),color=color,lw=2)
            ax.scatter([m],[float(value)],color=color,s=30,zorder=3)
            if row==2 and m in [0,1,2,11,12,13]:
                ax.annotate(str(int(value)),(m,float(value)),xytext=(0,6),
                            textcoords="offset points",ha="center",fontsize=9)
        ax.axhline(0,color=GRAY,lw=.7);ax.set_xticks(range(len(values)))
        ax.set_title(title,fontsize=10,loc="left",color=INK)
        ax.set(xlabel="Original coefficient index m",ylabel="Coefficient",xlim=(-.5,len(values)-.5))
        ax.grid(axis="y",alpha=.12)
    save(fig,"16_polyphase",{"input":[str(x) for x in a],"taps":[str(x) for x in h],"base":base,
         "phase_matrix":[[{str(d):str(v) for d,v in p.items()} for p in row] for row in mat],
         "input_lanes":[[str(x) for x in row] for row in lanes],
         "output_lanes":[[str(x) for x in row] for row in output_lanes],
         "direct_output":[str(x) for x in direct],"exact_reconstruction_equal":direct==reconstructed})


def size(tree):return 0 if tree is None else 1+size(tree[0])+size(tree[1])


def tree_record(tree,address=""):
    if tree is None:return []
    left,right=tree;i,j=size(left),size(right);n=1+i+j
    return [{"address":address or "root","internal_size":n,"left_size":i,"right_size":j,
             "local_binomial":comb(2*n,2*i+1),"q_exponent":2*i+1,"r_exponent":2*j+1}]+\
             tree_record(left,address+"L")+tree_record(right,address+"R")


def tree_positions(tree):
    pos={};leaf=[0]
    def walk(node,address,depth):
        if node is None:
            x=leaf[0];leaf[0]+=1
        else:x=(walk(node[0],address+"L",depth+1)+walk(node[1],address+"R",depth+1))/2
        pos[address]=(x,-depth,node)
        return x
    walk(tree,"",0)
    return pos


def draw_tree(ax,tree):
    pos=tree_positions(tree)
    for address,(x,y,node) in pos.items():
        if node is None:continue
        for role,child,color,symbol in [("L",node[0],BLUE,"q"),("R",node[1],ORANGE,"r")]:
            cx,cy,_=pos[address+role]
            exponent=2*size(child)+1
            ax.plot([x,cx],[y,cy],color=color,lw=2,zorder=1)
            text=f"${symbol}$" if exponent==1 else f"${symbol}^{{{exponent}}}$"
            ax.text((x+cx)/2+(-.08 if role=="L" else .08),(y+cy)/2+.035,text,
                    ha="right" if role=="L" else "left",color=color,fontsize=11,
                    bbox={"facecolor":"white","edgecolor":"none","pad":.6},zorder=4)
    for address,(x,y,node) in pos.items():
        internal=node is not None
        ax.add_patch(Circle((x,y),.16 if internal else .1,
                           fc="#e0edf4" if internal else "#f1f5f9",ec=INK if internal else "#a6b4c2",lw=1,zorder=3))
        if internal:ax.text(x,y,str(size(node)),ha="center",va="center",fontsize=10,color=INK,zorder=4)
        label=address or "root"
        ax.text(x,y+.23,label,ha="center",va="bottom",fontsize=9,color=GRAY)
    ax.set_xlim(-.5,3.5);ax.set_ylim(-3.5,.7);ax.set_aspect("equal");ax.axis("off")


def tree_figure():
    chain=(((None,None),None),None)
    balanced=((None,None),(None,None))
    entries=[]
    fig=plt.figure(figsize=(9.4,7.1),layout="constrained")
    gs=fig.add_gridspec(3,2,height_ratios=[5,.7,.65])
    axes=[fig.add_subplot(gs[0,j]) for j in range(2)]
    fig.suptitle("The same three nonlinear nodes have different scale addresses",fontsize=14,fontweight="bold",color=INK)
    for panel,(ax,tree,title) in enumerate(zip(axes,[chain,balanced],["An ordered chain","A balanced split"])):
        draw_tree(ax,tree);ax.set_title(title,fontsize=12,color=INK,pad=8)
        nodes=tree_record(tree)
        coeff=1
        for node in nodes:coeff*=node["local_binomial"]
        qe=sum(node["q_exponent"] for node in nodes)
        re=sum(node["r_exponent"] for node in nodes)
        assert lab.asymmetric_polynomials(3)[3][(qe,re)]==coeff
        summary=fig.add_subplot(gs[1,panel]);summary.axis("off")
        summary.text(.5,.75,rf"Tree contribution: ${coeff}q^{{{qe}}}r^{{{re}}}$",
                     ha="center",va="center",fontsize=12,color=INK)
        factors=" × ".join(str(n["local_binomial"]) for n in nodes)
        summary.text(.5,.23,"Local integer factors: "+factors,
                     ha="center",va="center",fontsize=9,color=GRAY)
        entries.append({"shape":title,"internal_nodes":nodes,"contribution":
                        {"integer_coefficient":coeff,"q_exponent":qe,"r_exponent":re}})
    foot=fig.add_subplot(gs[2,:]);foot.axis("off")
    foot.text(.5,.73,r"At a node with child sizes i, j: edge weights $q^{2i+1}$ and $r^{2j+1}$; integer factor $\binom{2(i+j+1)}{2i+1}$.",
              ha="center",va="center",fontsize=10,color=INK)
    foot.text(.5,.1,"Node labels count internal nodes. Gray leaves carry the base term z. L and R are ordered addresses.",
              ha="center",va="center",fontsize=9,color=GRAY)
    save(fig,"17_tree_addresses",{"normalization":"A_n=(2n+1)! c_n","internal_node_count":3,
         "all_ordered_shapes_at_n3":5,"selected_shapes":entries,
         "exact_A3_polynomial":{f"{u},{v}":x for (u,v),x in lab.asymmetric_polynomials(3)[3].items()}})


def regime(q,r):
    q,r=Q(q),Q(r)
    if q<0 or r<0:raise ValueError("this diagram concerns nonnegative real scales")
    if not q or not r:return "linear"
    if max(q,r)>1:return "zero_radius"
    if q==r==1:return "tangent"
    if q==1 or r==1:return "entire_infinite_order"
    return "entire_finite_order"


def regime_figure():
    fig,ax=plt.subplots(figsize=(7.6,6.3),layout="constrained")
    fig.suptitle("The analytic object changes at the unit-scale boundary",fontsize=14,fontweight="bold",color=INK)
    ax.add_patch(Rectangle((0,0),1,1,facecolor="#d9eee8",edgecolor="none"))
    ax.add_patch(Rectangle((1,0),.5,1.5,facecolor="#fbe3db",edgecolor="none"))
    ax.add_patch(Rectangle((0,1),1,.5,facecolor="#fbe3db",edgecolor="none"))
    ax.plot([1,1],[0,1],color=PURPLE,lw=3,zorder=3)
    ax.plot([0,1],[1,1],color=PURPLE,lw=3,zorder=3)
    ax.plot([0,1.5],[0,0],color=BLUE,lw=4,zorder=5)
    ax.plot([0,0],[0,1.5],color=BLUE,lw=4,zorder=5)
    ax.scatter([1],[1],s=70,c=INK,zorder=6)
    ax.text(.48,.53,"Entire of finite order",ha="center",fontsize=12,color="#166d5f",fontweight="bold")
    ax.text(.48,.42,r"$q^\rho+r^\rho=1$",ha="center",fontsize=14,color="#166d5f")
    ax.text(.45,.28,r"$0<q,r<1$",ha="center",fontsize=11,color="#166d5f")
    ax.text(.55,1.29,"Radius zero",ha="center",fontsize=12,color="#a84026",fontweight="bold")
    ax.text(.55,1.19,"Positive parameters with max(q, r) > 1",ha="center",fontsize=9,color="#a84026")
    ax.annotate("Entire of\ninfinite order",xy=(1,.48),xytext=(1.26,.52),
                ha="center",fontsize=10,color=PURPLE,
                arrowprops={"arrowstyle":"-","color":PURPLE,"lw":1},
                bbox={"fc":"white","ec":"none","pad":2})
    ax.annotate("Tangent\nmeromorphic",xy=(1,1),xytext=(1.25,1.02),ha="center",
                fontsize=10,color=INK,arrowprops={"arrowstyle":"-","color":INK,"lw":1},
                bbox={"fc":"white","ec":"none","pad":2})
    ax.text(.45,.07,"The blue axes are linear: T(z) = z",ha="center",fontsize=9,color=BLUE)
    ax.set(xlabel="Left scale q",ylabel="Right scale r",xlim=(-.025,1.5),ylim=(-.025,1.5))
    ax.set_xticks([0,.5,1,1.5]);ax.set_yticks([0,.5,1,1.5]);ax.set_aspect("equal")
    ax.grid(color="white",alpha=.55,lw=.8)
    samples=[("1/4","3/4","entire_finite_order"),("1/2","1","entire_infinite_order"),
             ("1","1/2","entire_infinite_order"),("1","1","tangent"),
             ("1","3/2","zero_radius"),("3/2","1/4","zero_radius"),
             ("0","3/2","linear"),("3/2","0","linear"),("0","0","linear")]
    for q,r,want in samples:assert regime(q,r)==want
    save(fig,"18_parameter_regimes",{"domain":"Nonnegative real q,r; analytic/formal conclusions proved in sequence_polyphase.md",
        "symbolic_classes":{
            "entire_finite_order":"0<q,r<1; order is the positive root of q^rho+r^rho=1",
            "entire_infinite_order":"one scale equals 1, the other is strictly between 0 and 1",
            "tangent":"q=r=1", "zero_radius":"q,r>0 and max(q,r)>1",
            "linear":"q=0 or r=0"},
        "exact_discrete_classification_checks":[{"q":q,"r":r,"class":want} for q,r,want in samples]})


def main():
    sequence_figure();tree_figure();regime_figure()
    record["input_sha256"]={"family_lab.py":hashlib.sha256((ROOT/"family_lab.py").read_bytes()).hexdigest(),
                             "build_sequence_figures.py":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/"evidence"/"sequence_figure_record.json").write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({"figures":len(record["figures"]),"status":"passed","exact_checks":"FIR reconstruction; tree contributions; nine regime examples"}))


if __name__=="__main__":main()
