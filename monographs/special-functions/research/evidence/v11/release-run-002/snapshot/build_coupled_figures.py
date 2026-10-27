#!/usr/bin/env python3
"""Six reproducible Matplotlib plates for the coupled feedback family.

Exact Fraction data are retained where available. Large-radius curves use
floating log coefficients with an explicit two-truncation comparison.
"""
from fractions import Fraction as Q
from math import exp, factorial, isfinite, log, log10
from pathlib import Path
import hashlib
import json
import platform
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import coupled_lab as lab

ROOT=Path(__file__).resolve().parent
FIG=ROOT/"figures_v11";FIG.mkdir(exist_ok=True)
EVIDENCE=ROOT/"evidence/v11";EVIDENCE.mkdir(parents=True,exist_ok=True)
BLUE="#075985";ORANGE="#cc5d3c";GREEN="#258b80";PURPLE="#7658aa"
INK="#193044";GRAY="#617182";LIGHT="#eaf1f5"
P=tuple(map(Q,("1/5","2/5","3/5","7/10")))
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,
    "axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42,
    "figure.facecolor":"white","savefig.facecolor":"white"})
record={"checkpoint":"SF-DISCOVERY-110","python":platform.python_version(),
        "numpy":np.__version__,"matplotlib":matplotlib.__version__,"figures":[],
        "source_sha256":{},
        "scope":"Exact certificates are labelled separately from double-precision illustrations. Numerical plots do not prove growth laws or historical novelty."}


def save(fig,name,data):
    outputs=[]
    for suffix in ("pdf","png"):
        path=FIG/(name+"."+suffix)
        fig.savefig(path,dpi=180,bbox_inches="tight")
        outputs.append({"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    record["figures"].append({"name":name,"files":outputs,**data})
    plt.close(fig)


def logsum(values):
    top=max(values)
    return top+log(sum(exp(x-top) for x in values))


def numerical_log_coefficients(p,last):
    lq,lr,la,lb=map(lambda x:log(float(x)),p)
    u=v=None
    u=[0.0];v=[0.0]
    for n in range(1,last+1):
        u.append(logsum([u[i]+v[n-1-i]+(2*i+1)*lq+(2*(n-1-i)+1)*lr for i in range(n)])-log(2*n+1))
        v.append(logsum([u[i]+v[n-1-i]+(2*i+1)*la+(2*(n-1-i)+1)*lb for i in range(n)])-log(2*n+1))
    return u,v


def log_value(coefficients,x):
    return logsum([c+(2*n+1)*log(x) for n,c in enumerate(coefficients)])


def matrix_plate():
    fig=plt.figure(figsize=(10,5.5),layout="constrained")
    grid=fig.add_gridspec(2,2,height_ratios=[1,.16])
    ax=fig.add_subplot(grid[0,0]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    fig.suptitle("Two functions share feedback through four contraction scales",fontsize=16,color=INK,fontweight="bold")
    for x,label,color in [(.22,"U",BLUE),(.78,"V",ORANGE)]:
        ax.add_patch(FancyBboxPatch((x-.115,.37),.23,.25,boxstyle="round,pad=.015",fc=LIGHT,ec=color,lw=2))
        ax.text(x,.50,label,ha="center",va="center",fontsize=23,color=color,fontweight="bold")
    ax.add_patch(FancyArrowPatch((.35,.56),(.65,.56),connectionstyle="arc3,rad=-.45",arrowstyle="-|>",mutation_scale=15,color=BLUE,lw=2))
    ax.add_patch(FancyArrowPatch((.65,.43),(.35,.43),connectionstyle="arc3,rad=-.45",arrowstyle="-|>",mutation_scale=15,color=ORANGE,lw=2))
    ax.text(.5,.77,"U feeds V at a = 3/5",ha="center",fontsize=11,color=BLUE)
    ax.text(.5,.20,"V feeds U at r = 2/5",ha="center",fontsize=11,color=ORANGE)
    ax.text(.22,.05,"U also uses q = 1/5",ha="center",fontsize=10,color=GRAY)
    ax.text(.78,.05,"V also uses b = 7/10",ha="center",fontsize=10,color=GRAY)
    ax.text(.5,.96,r"$U'=1+U(qz)V(rz)$"+"\n"+r"$V'=1+U(az)V(bz)$",ha="center",va="top",fontsize=12,linespacing=1.5)
    ax=fig.add_subplot(grid[0,1]);ax.axis("off")
    ax.text(.5,.94,"The growth matrix at exponent ρ",ha="center",va="top",fontsize=12,color=INK)
    table=ax.table(cellText=[[r"$q^\rho$",r"$r^\rho$"],[r"$a^\rho$",r"$b^\rho$"]],
                   rowLabels=["U equation","V equation"],colLabels=["U input","V input"],
                   cellLoc="center",bbox=[.36,.56,.58,.28])
    table.auto_set_font_size(False);table.set_fontsize(13)
    for (_, _),cell in table.get_celld().items():cell.set_edgecolor("#cbd5e1")
    ax.text(.5,.43,"At ρ = 1, both identities hold exactly",ha="center",fontsize=11,color=INK)
    ax.text(.5,.32,r"$\frac{1}{5}\!\cdot\!\frac{1}{2}+\frac{2}{5}=\frac{1}{2}$",ha="center",fontsize=16,color=BLUE)
    ax.text(.5,.16,r"$\frac{3}{5}\!\cdot\!\frac{1}{2}+\frac{7}{10}=1$",ha="center",fontsize=16,color=ORANGE)
    footer=fig.add_subplot(grid[1,:]);footer.axis("off")
    footer.text(.5,.5,"The positive eigenvector is (1/2, 1). Row sums alone are 3/5 and 13/10, so a single row cannot determine the coupled order.",
                ha="center",va="center",fontsize=10,color=GRAY,wrap=True)
    save(fig,"coupled_01_matrix",{"arithmetic":"Exact rational matrix/eigenvector labels",
        "parameters":[str(x) for x in P],"rho_exact":"1","right_eigenvector":["1/2","1"]})


def function_plate():
    generic=tuple(map(Q,("1/3","2/3","1/2","3/4")))
    coeff=numerical_log_coefficients(generic,240)
    coeff_small=[x[:121] for x in coeff]
    radii=np.linspace(.001,8,301)
    values=np.array([[exp(log_value(c,float(x))) for x in radii] for c in coeff])
    differences=[abs(log_value(c,8)-log_value(s,8)) for c,s in zip(coeff,coeff_small)]
    fig,axes=plt.subplots(1,2,figsize=(10,4.8),layout="constrained")
    fig.suptitle("The same normalization develops into different coupled functions",fontsize=15,fontweight="bold",color=INK)
    for arr,label,color in zip(values,["U(x)","V(x)"],[BLUE,ORANGE]):
        axes[0].plot(radii,arr,label=label,color=color,lw=2.4)
        axes[1].semilogy(radii,arr/radii,label=label+" / x",color=color,lw=2.4)
    axes[0].set(xlabel="Positive real argument x",ylabel="Function value",xlim=(0,8))
    axes[1].set(xlabel="Positive real argument x",ylabel="Amplification above the initial slope",xlim=(0,8))
    for ax in axes:ax.grid(alpha=.15);ax.legend(frameon=False)
    axes[0].set_title("q = 1/3, r = 2/3, a = 1/2, b = 3/4",fontsize=11,loc="left")
    axes[1].set_title("U′(0) = V′(0) = 1",fontsize=11,loc="left")
    save(fig,"coupled_02_functions",{"arithmetic":"Double log-sum recurrence, last odd index 240",
        "parameters":[str(x) for x in generic],"radii":radii.tolist(),"U":values[0].tolist(),"V":values[1].tolist(),
        "log_value_difference_120_vs_240_at_x8":differences,
        "certification":"Truncation agreement is a numerical diagnostic, not a rigorous tail bound."})


def growth_plate():
    coeff=numerical_log_coefficients(P,800)
    radii=np.geomspace(3,160,140)
    logs=np.array([[log_value(c,float(x)) for x in radii] for c in coeff])
    slopes=np.array([np.gradient(np.log(y),np.log(radii)) for y in logs])
    differences=[abs(log_value(c,160)-log_value(c[:401],160)) for c in coeff]
    fig,axes=plt.subplots(1,2,figsize=(10,4.9),layout="constrained")
    fig.suptitle("Different amplitudes can share one growth order",fontsize=15,fontweight="bold",color=INK)
    for y,s,label,color in zip(logs,slopes,["U","V"],[BLUE,ORANGE]):
        axes[0].loglog(radii,y,label=r"$\log "+label+r"(R)$",color=color,lw=2.3)
        axes[1].semilogx(radii[1:-1],s[1:-1],label=label,color=color,lw=2.3)
    axes[1].axhline(1,color=GREEN,linestyle="--",label="PF root ρ = 1")
    axes[0].set(xlabel="Observation radius R",ylabel="Logarithm of function value")
    axes[1].set(xlabel="Observation radius R",ylabel="Local slope of log log F(R)",ylim=(.5,1.8))
    for ax in axes:ax.grid(alpha=.15);ax.legend(frameon=False)
    axes[0].set_title("q = 1/5, r = 2/5, a = 3/5, b = 7/10",fontsize=10.5,loc="left")
    axes[1].set_title("Finite-radius slopes near the PF root",fontsize=10.5,loc="left")
    save(fig,"coupled_03_growth",{"arithmetic":"Double log-sum recurrence, last odd index 800",
        "parameters":[str(x) for x in P],"radii":radii.tolist(),"log_U":logs[0].tolist(),"log_V":logs[1].tolist(),
        "local_slopes_U":slopes[0].tolist(),"local_slopes_V":slopes[1].tolist(),
        "log_value_difference_400_vs_800_at_R160":differences,
        "certification":"Finite-radius illustration. The exact order comes from the separate proof, not this fit."})


def landscape_plate():
    axis=np.linspace(.1,.9,65)
    orders=np.array([[lab.pf_order(float(q),.4,.6,float(b))["rho"] for q in axis] for b in axis])
    fig,ax=plt.subplots(figsize=(8.3,6.0),layout="constrained")
    img=ax.imshow(orders,origin="lower",extent=(.1,.9,.1,.9),aspect="equal",cmap="viridis",interpolation="nearest")
    lines=ax.contour(axis,axis,orders,levels=[.6,.8,1,1.4,2],colors="white",linewidths=.8,alpha=.9)
    ax.clabel(lines,inline=True,fontsize=10,fmt="ρ = %.1f")
    ax.scatter([.2],[.7],color=ORANGE,s=65,ec="white",lw=1.3,zorder=5)
    ax.annotate("Exact anchor: ρ = 1",(.2,.7),xytext=(.30,.79),color="white",fontsize=11,
                arrowprops={"arrowstyle":"-","color":"white"})
    ax.set(xlabel="Self-contraction q in the U equation",ylabel="Self-contraction b in the V equation",
           title="Coupled growth landscape with r = 2/5 and a = 3/5")
    fig.colorbar(img,ax=ax,label="Numerical root of spectral radius = 1",shrink=.88)
    save(fig,"coupled_04_landscape",{"arithmetic":"Double precision PF bisection, tolerance 1e-12",
        "q_grid":axis.tolist(),"b_grid":axis.tolist(),"r":"2/5","a":"3/5","rho_grid":orders.tolist(),
        "certification":"Colors and contours are numerical. Marked order-one anchor is verified exactly."})


def certificate_plate():
    indices=list(range(4,61,2));radii=[Q(1,2),Q(1),Q(3,2),Q(2)]
    fig,ax=plt.subplots(figsize=(9.2,5.5),layout="constrained")
    fig.suptitle("A finite coefficient list can carry a rigorous error certificate",fontsize=15,fontweight="bold",color=INK)
    rows=[]
    for x,color in zip(radii,[BLUE,GREEN,ORANGE,PURPLE]):
        outer=x+1;bound=lab.disk_majorant(*P,outer)
        exact=[bound*(x/outer)**(2*n+3) for n in indices]
        values=[log10(value.numerator)-log10(value.denominator) for value in exact]
        ax.plot(indices,values,label=f"Disk radius R = {x}",color=color,lw=2.2)
        rows.append({"R":str(x),"outer_radius":str(outer),"majorant":str(bound),"errors":[str(e) for e in exact]})
    ax.axhline(-10,color=GRAY,lw=1,ls="--");ax.text(5,-8.5,"10⁻¹⁰ absolute error",color=GRAY,fontsize=10)
    ax.set(xlabel="Last odd coefficient index N  (degree 2N + 1)",ylabel="log₁₀ of the certified uniform tail bound",xlim=(4,60))
    ax.legend(frameon=False,loc="upper right");ax.grid(alpha=.15)
    ax.set_title(r"$\|F-F_N\|_{|z|\leq R}\;\leq\;B(S)(R/S)^{2N+3},\qquad S=R+1$",fontsize=12,pad=12)
    save(fig,"coupled_05_certification",{"arithmetic":"Exact rational tail bounds; plotted base-10 logs are double precision",
        "parameters":[str(x) for x in P],"last_indices":indices,"certificates":rows,
        "certification":"The displayed upper bounds are rigorous for both components on each complex disk."})


def phase_plate():
    _,v=lab.coupled_odd_derivatives(*P,last=8)
    inputs=lab.full_egf_coefficients(v);taps=[Q(1),Q(-2),Q(1)];base=3
    direct=lab.ordinary_taps(inputs,taps)
    lanes=lab.phase_lanes(inputs,base);matrix=lab.polyphase_tap_matrix(taps,base)
    recovered=lab.merge_lanes(lab.apply_polyphase_matrix(lanes,matrix,len(direct)),len(direct))
    if recovered!=direct:raise AssertionError("coupled polyphase reconstruction failed")
    fig,axes=plt.subplots(2,1,figsize=(10,6.3),sharex=True,layout="constrained")
    fig.suptitle("Coupled coefficients pass through the existing phase and tap calculus",fontsize=14.5,color=INK,fontweight="bold")
    for ax,arr,title in zip(axes,[inputs,direct],["Input: derivatives V⁽ᵐ⁾(0), with zero even coefficients","Output: aₘ − 2aₘ₋₁ + aₘ₋₂, including the phase carry"]):
        for residue,color in enumerate([BLUE,ORANGE,GREEN]):
            indexes=list(range(residue,len(arr),base));values=[float(arr[m]) for m in indexes]
            ax.vlines(indexes,0,values,color=color,lw=1.8)
            ax.scatter(indexes,values,color=color,s=30,label=f"Residue {residue}")
        ax.axhline(0,color=GRAY,lw=.8);ax.set_title(title,fontsize=11,loc="left")
        ax.set_ylabel("Derivative array value");ax.grid(axis="y",alpha=.15)
    axes[0].legend(frameon=False,ncol=3)
    axes[1].set(xlabel="Original derivative index m",xticks=range(0,len(direct),2),xlim=(-.6,len(direct)-.4))
    save(fig,"coupled_06_polyphase",{"arithmetic":"Exact rational derivatives and FIR/polyphase reconstruction",
        "parameters":[str(x) for x in P],"base":base,"taps":[str(x) for x in taps],
        "input":[str(x) for x in inputs],"output":[str(x) for x in direct],"reconstruction_equal":recovered==direct,
        "phase_matrix":[[{str(k):str(x) for k,x in cell.items()} for cell in row] for row in matrix],
        "convention":"Ordinary FIR on derivative arrays corresponds to zero-constant integration shifts of their EGF, not EGF multiplication."})


def main():
    matrix_plate();function_plate();growth_plate();landscape_plate();certificate_plate();phase_plate()
    for name in ("coupled_lab.py","family_lab.py","build_coupled_figures.py"):
        record["source_sha256"][name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    (EVIDENCE/"coupled_figures.json").write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({"figures":len(record["figures"]),"output_dir":str(FIG)}))


if __name__=="__main__":main()
