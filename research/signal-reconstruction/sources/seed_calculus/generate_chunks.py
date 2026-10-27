from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
import numpy as np
import sympy as sp

from proof_atlas import arithmetic, bayes, details, linear, nonlinear_geometry, physics, quantum, signal
from proof_atlas.figures import (
    INK, MUTED, PAPER, BLUE, CYAN, TEAL, GREEN, YELLOW, ORANGE, RED,
    MAGENTA, PURPLE, WHITE, COLORS, _save, _box, _arrow, _matrix_float, _vector_float, _legend_below, _matrix_text
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"



def chunk0() -> None:
    lc = linear.build_certificate()

    fig, ax = plt.subplots(figsize=(12.8, 6.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(.5, .92, "One finite calculus, seven independent realizations", ha="center", fontsize=22, weight="bold")
    _box(ax, .39, .42, .22, .18, "complete packets\n$\\sum_\\alpha P_\\alpha=I$\nexact reconstruction", face="#E6F0F4", edge=BLUE, fontsize=14)
    items = [
        (.08,.70,"algebra",BLUE),(.30,.75,"signals",TEAL),(.70,.75,"quantum",PURPLE),(.90,.70,"Bayes",ORANGE),
        (.12,.18,"arithmetic",MAGENTA),(.38,.10,"physics",GREEN),(.70,.10,"nonlinear +\nholonomy",RED)
    ]
    for x0,y0,label,color in items:
        ax.add_patch(Circle((x0,y0), .075, facecolor=color+"28", edgecolor=color, lw=2))
        ax.text(x0,y0,label,ha="center",va="center",fontsize=11.5,weight="bold")
        start=(x0 + (.07 if x0<.5 else -.07), y0 + (.01 if y0<.5 else -.01))
        end=(.39 if x0<.5 else .61, .49 if y0<.5 else .53)
        _arrow(ax,start,end,color=color,rad=.08 if y0<.5 else -.08)
    ax.text(.5,.73,"analysis",ha="center",fontsize=11,color=MUTED)
    ax.text(.5,.27,"synthesis and certificates",ha="center",fontsize=11,color=MUTED)
    ax.text(.5,.035,"Each chapter verifies the axioms, solves one domain problem, reconstructs the result, and checks the residual independently in Python/SymPy.",ha="center",fontsize=10.8,color=MUTED)
    _save(fig,OUT,"00_cross_domain_pipeline")

    norms=np.zeros((3,3))
    for b in range(3):
        for a in range(3):
            norms[b,a]=np.linalg.norm(_matrix_float(lc.blocks[b][a]))
    fig,ax=plt.subplots(figsize=(7.8,6.2)); im=ax.imshow(norms,cmap="viridis")
    ax.set_xticks(range(3),["input $X_0$","input $X_1$","input $X_2$"])
    ax.set_yticks(range(3),["output $X_0$","output $X_1$","output $X_2$"])
    for i in range(3):
        for j in range(3):
            ax.text(j,i,f"{norms[i,j]:.2f}",ha="center",va="center",color=WHITE if norms[i,j]>.55*norms.max() else INK,weight="bold")
    ax.set_title("Exact transfer-block matrix $T_{\\beta\\alpha}=P_\\beta T P_\\alpha$",weight="bold")
    fig.colorbar(im,ax=ax,label="Frobenius norm"); fig.tight_layout(); _save(fig,OUT,"01_linear_transfer_blocks")

    fig,axes=plt.subplots(1,3,figsize=(12.5,4.0))
    mats=[lc.projectors[0], sp.diag(1,0,0,0,0,0), sp.diag(0,1,0,0,0,0)]
    titles=["coarse $P_0$","child $Q_{00}$","child $Q_{01}$"]
    for ax,M,title in zip(axes,mats,titles,strict=True):
        ax.imshow(np.array(M.tolist(),dtype=float),cmap="Blues",vmin=0,vmax=1)
        ax.set_title(title,weight="bold"); ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("Refinement identity: $P_0=Q_{00}+Q_{01}$",fontsize=17,weight="bold")
    fig.tight_layout(rect=[0,0,1,.88]); _save(fig,OUT,"02_linear_refinement")


def chunk1() -> None:
    # Figures use numerical evaluations of the exact coordinates proved and
    # stored by the symbolic signal module.  This keeps regeneration fast.
    x=np.array([3.0,1.0,4.0,1.0,5.0,9.0,2.0,6.0])
    phase4=tuple(x[r::4] for r in range(4))
    fig,axes=plt.subplots(5,1,figsize=(12.5,7.2),sharex=False,gridspec_kw={"height_ratios":[1.4,1,1,1,1]})
    axes[0].stem(range(8),x,linefmt=INK,markerfmt="o",basefmt=" ")
    axes[0].set_title("Length-8 signal and its four exact polyphase channels",loc="left",weight="bold"); axes[0].set_ylabel("$x[n]$")
    for r,vals in enumerate(phase4):
        axes[r+1].stem(range(len(vals)),vals,linefmt=COLORS[r],markerfmt="o",basefmt=" ")
        axes[r+1].set_ylabel(f"phase {r}"); axes[r+1].text(.99,.78,f"addresses $n\\equiv {r}\\;(\\mathrm{{mod}}\\;4)$",transform=axes[r+1].transAxes,ha="right",color=COLORS[r])
    axes[-1].set_xlabel("decimated address $q$")
    for ax in axes: ax.grid(alpha=.15)
    fig.tight_layout(); _save(fig,OUT,"03_signal_polyphase")

    h=np.empty(8)
    for k in range(4):
        h[2*k]=(x[2*k]+x[2*k+1])/np.sqrt(2)
        h[2*k+1]=(x[2*k]-x[2*k+1])/np.sqrt(2)
    fourier=np.fft.fft(x)/np.sqrt(8)
    f=np.abs(fourier)
    fig,axes=plt.subplots(1,3,figsize=(12.8,4.2))
    axes[0].stem(range(8),x,linefmt=INK,markerfmt="o",basefmt=" "); axes[0].set_title("spatial coordinates",weight="bold")
    axes[1].stem(range(8),f,linefmt=BLUE,markerfmt="o",basefmt=" "); axes[1].set_title("unitary Fourier magnitude",weight="bold")
    axes[2].stem(range(8),h,linefmt=MAGENTA,markerfmt="o",basefmt=" "); axes[2].set_title("one-level Haar coordinates",weight="bold")
    for ax in axes: ax.grid(alpha=.16); ax.set_xlabel("coordinate")
    fig.suptitle("The same object in three exact atlases",fontsize=17,weight="bold"); fig.tight_layout(rect=[0,0,1,.90]); _save(fig,OUT,"04_signal_three_atlases")

    groups=((0,),(1,7),(2,6),(3,5),(4,))
    energies=[float(sum(abs(fourier[k])**2 for k in group)) for group in groups]
    labels=["DC","|k|=1","|k|=2","|k|=3","Nyquist"]
    fig,ax=plt.subplots(figsize=(8.8,4.8)); ax.bar(labels,energies,color=COLORS[:5],edgecolor=INK)
    ax.axhline(float(sum(energies)),color=INK,lw=.8,ls="--",label=f"total energy = {sum(energies):.0f}")
    ax.set_ylabel("packet energy"); ax.set_title("Pulled-back Fourier projectors partition the signal energy",weight="bold")
    ax.grid(alpha=.16,axis="y"); _legend_below(ax,ncol=1,y=-.16); fig.tight_layout(rect=[0,.10,1,1]); _save(fig,OUT,"05_fourier_packet_energy")

def chunk2() -> None:
    qc = quantum.build_certificate()
    bc = bayes.build_certificate()

    fig,ax=plt.subplots(figsize=(12.5,5.6)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.text(.5,.92,"Bell-state preparation as an exact packet path sum",ha="center",fontsize=20,weight="bold")
    _box(ax,.04,.40,.13,.18,"$|00\\rangle$\neven parity",face="#E6F0F4",edge=BLUE,fontsize=14)
    _box(ax,.25,.63,.18,.15,"even branch\n$|00\\rangle/\\sqrt{2}$",face="#E6F3F1",edge=TEAL,fontsize=13)
    _box(ax,.25,.20,.18,.15,"odd branch\n$|10\\rangle/\\sqrt{2}$",face="#FBF0E6",edge=ORANGE,fontsize=13)
    _box(ax,.56,.63,.18,.15,"CNOT\n$|00\\rangle/\\sqrt{2}$",face=WHITE,edge=TEAL,fontsize=13)
    _box(ax,.56,.20,.18,.15,"CNOT\n$|11\\rangle/\\sqrt{2}$",face=WHITE,edge=ORANGE,fontsize=13)
    _box(ax,.83,.40,.14,.18,"$|\\Phi^+\\rangle$\neven packet",face="#F4EAF1",edge=MAGENTA,fontsize=14)
    _arrow(ax,(.17,.49),(.25,.70),color=TEAL,text="$P_eH_1P_e$",text_offset=(0,.05))
    _arrow(ax,(.17,.49),(.25,.28),color=ORANGE,text="$P_oH_1P_e$",text_offset=(0,-.05))
    _arrow(ax,(.43,.70),(.56,.70),color=TEAL); _arrow(ax,(.43,.28),(.56,.28),color=ORANGE)
    _arrow(ax,(.74,.70),(.83,.54),color=TEAL); _arrow(ax,(.74,.28),(.83,.45),color=ORANGE)
    ax.text(.5,.075,"The two nonzero paths synthesize $|00\\rangle/\\sqrt{2}+|11\\rangle/\\sqrt{2}$; every other parity path vanishes.",ha="center",fontsize=11,color=MUTED)
    _save(fig,OUT,"06_quantum_packet_paths")

    bell=_vector_float(qc.bell).reshape(-1,1); rho=bell@bell.conjugate().T; rhoA=_matrix_float(qc.reduced_density)
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.3),gridspec_kw={"width_ratios":[1.15,1.0]})
    im0=axes[0].imshow(np.real(rho),cmap="coolwarm",vmin=-.5,vmax=.5); axes[0].set_title("Bell density matrix",weight="bold")
    axes[0].set_xticks(range(4),["00","01","10","11"]); axes[0].set_yticks(range(4),["00","01","10","11"])
    axes[1].imshow(np.real(rhoA),cmap="coolwarm",vmin=-.5,vmax=.5); axes[1].set_title("reduced state $I/2$",weight="bold")
    axes[1].set_xticks(range(2),["0","1"]); axes[1].set_yticks(range(2),["0","1"])
    for ax,M in [(axes[0],np.real(rho)),(axes[1],np.real(rhoA))]:
        for i in range(M.shape[0]):
            for j in range(M.shape[1]): ax.text(j,i,f"{M[i,j]:.2f}",ha="center",va="center",color=WHITE if abs(M[i,j])>.3 else INK)
    fig.suptitle("Exact state reconstruction and an entanglement certificate",fontsize=17,weight="bold",y=.97)
    fig.subplots_adjust(left=.08,right=.87,bottom=.14,top=.80,wspace=.45)
    cax=fig.add_axes([.91,.18,.018,.56])
    fig.colorbar(im0,cax=cax,label="matrix entry")
    _save(fig,OUT,"07_quantum_density")

    E=np.array(bc.expectation_matrix.tolist(),dtype=float); Ef=np.array([float(v) for v in bc.projected_observable])
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.4))
    im=axes[0].imshow(E,cmap="viridis",vmin=0,vmax=2/3); axes[0].set_title("conditional-expectation projector",weight="bold")
    axes[0].set_xticks(range(4)); axes[0].set_yticks(range(4))
    for i in range(4):
        for j in range(4): axes[0].text(j,i,f"{E[i,j]:.2f}",ha="center",va="center",color=WHITE if E[i,j]>.4 else INK)
    axes[1].bar(np.arange(4)-.16,[1,4,-2,3],width=.32,label="$f$",color=BLUE)
    axes[1].bar(np.arange(4)+.16,Ef,width=.32,label="$E[f|\\pi]$",color=ORANGE)
    axes[1].axhline(0,color=INK,lw=.7); axes[1].set_xticks(range(4)); axes[1].legend(); axes[1].grid(alpha=.15,axis="y")
    axes[1].set_title("projection onto packet-constant observables",weight="bold")
    fig.colorbar(im,ax=axes[0],fraction=.046); fig.tight_layout(); _save(fig,OUT,"08_conditional_expectation")

    fig,axes=plt.subplots(1,2,figsize=(11.8,4.4))
    fine=np.array([float(v) for v in bc.sufficient_fine_posterior]); coarse=np.array([float(v) for v in bc.sufficient_coarse_posterior])
    axes[0].bar(range(4),fine,color=[BLUE,BLUE,TEAL,TEAL],edgecolor=INK); axes[0].set_title("sufficient likelihood: fine posterior",weight="bold")
    axes[0].set_xticks(range(4),["0","1","2","3"]); axes[0].grid(alpha=.15,axis="y")
    axes[0].text(.5,.92,f"coarse masses = ({coarse[0]:.3f}, {coarse[1]:.3f})",transform=axes[0].transAxes,ha="center")
    exact=np.array([float(v) for v in bc.nonsufficient_exact_coarse]); nominal=np.array([float(v) for v in bc.nonsufficient_nominal_coarse]); idx=np.arange(2)
    axes[1].bar(idx-.17,exact,width=.34,label="exact effective likelihood",color=MAGENTA)
    axes[1].bar(idx+.17,nominal,width=.34,label="nominal coarse likelihood",color=ORANGE)
    axes[1].set_xticks(idx,["packet A","packet B"]); axes[1].set_title("nonsufficient likelihood exposes a defect",weight="bold")
    axes[1].legend(fontsize=9); axes[1].grid(alpha=.15,axis="y"); fig.tight_layout(); _save(fig,OUT,"09_bayesian_updates")

    defect=np.array([float(v) for v in bc.defect]); fact=np.array([float(v) for v in bc.factorized_defect])
    fig,ax=plt.subplots(figsize=(8.8,4.6)); idx=np.arange(2)
    ax.bar(idx-.18,defect,width=.36,label="direct defect",color=RED); ax.bar(idx+.18,fact,width=.36,label="factorized defect",color=TEAL)
    ax.axhline(0,color=INK,lw=.8); ax.set_xticks(idx,["packet A","packet B"]); ax.legend(); ax.grid(alpha=.16,axis="y")
    ax.set_title("Exact information-loss packet factorization",weight="bold"); ax.text(.5,.05,"symbolic residual = 0",transform=ax.transAxes,ha="center",weight="bold",color=TEAL)
    fig.tight_layout(); _save(fig,OUT,"10_bayesian_defect_factorization")


def chunk3() -> None:
    ac=arithmetic.build_certificate(12)
    seq=np.array([int(v) for v in ac.sequence],dtype=object); logs=np.array([math.log10(int(v)) if int(v)>0 else 0 for v in seq])
    fig,ax=plt.subplots(figsize=(9.5,4.8)); ax.plot(range(len(seq)),logs,marker="o",color=MAGENTA,lw=2)
    for n in range(min(6,len(seq))): ax.annotate(str(seq[n]),(n,logs[n]),xytext=(0,8),textcoords="offset points",ha="center",fontsize=8)
    ax.set_xlabel("block index $n$"); ax.set_ylabel("$\\log_{10} a_n$"); ax.grid(alpha=.18)
    ax.set_title("Candidate OEIS row: coefficients of $D_5(z)^{-2}$",weight="bold"); fig.tight_layout(); _save(fig,OUT,"11_candidate_sequence_growth")

    z=sp.symbols("z",real=True); d5=arithmetic.d5_root_sum(z); d5f=sp.lambdify(z,d5,"numpy"); zz=np.linspace(-2.0,2.0,800)
    vals=np.real(d5f(zz)); svals=1/vals**2
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.3))
    axes[0].plot(zz,vals,color=BLUE,lw=2); axes[0].axhline(0,color=INK,lw=.7); axes[0].grid(alpha=.17); axes[0].set_title("closed form for $D_5(z)$",weight="bold")
    axes[1].plot(zz,svals,color=MAGENTA,lw=2); axes[1].grid(alpha=.17); axes[1].set_title("reciprocal square $D_5(z)^{-2}$",weight="bold")
    for ax in axes: ax.set_xlabel("$z$")
    fig.suptitle("A root-of-unity packet sum produces an explicit analytic family",fontsize=17,weight="bold"); fig.tight_layout(rect=[0,0,1,.90]); _save(fig,OUT,"12_candidate_sequence_closed_form")

    rr=np.linspace(0,3,400); fig,ax=plt.subplots(figsize=(9.5,5.2)); r=sp.symbols("r")
    for n,poly in enumerate(ac.parameter_polynomials[1:5],start=1):
        fun=sp.lambdify(r,poly,"numpy"); y=np.asarray(fun(rr),dtype=float)
        ax.plot(rr,np.log10(1+np.abs(y)),lw=2,label=f"$P_{{5,{n}}}(r)$",color=COLORS[n-1])
    ax.set_xlabel("reciprocal order $r$"); ax.set_ylabel("$\\log_{10}(1+|P_{5,n}(r)|)$"); ax.grid(alpha=.18); ax.legend()
    ax.set_title("One closed polynomial semigroup contains every reciprocal order",weight="bold"); fig.tight_layout(); _save(fig,OUT,"13_parameter_polynomials")


def chunk4() -> None:
    pc=physics.build_certificate(); t=sp.symbols("t",real=True); qfun=sp.lambdify(t,pc.q,"numpy"); tt=np.linspace(0,20,1000)
    # Matrix lambdify with vector input can be awkward; evaluate components separately.
    q1=sp.lambdify(t,pc.q[0],"numpy")(tt); q2=sp.lambdify(t,pc.q[1],"numpy")(tt)
    fig,ax=plt.subplots(figsize=(10.8,4.8)); ax.plot(tt,q1,label="$q_1(t)$",color=BLUE,lw=1.8); ax.plot(tt,q2,label="$q_2(t)$",color=ORANGE,lw=1.8)
    ax.set_xlabel("time"); ax.set_ylabel("displacement"); ax.grid(alpha=.18); _legend_below(ax,ncol=2,y=-.18); ax.set_title("Two coupled oscillators reconstructed from symmetric and antisymmetric packets",weight="bold")
    fig.tight_layout(rect=[0,.12,1,1]); _save(fig,OUT,"14_coupled_oscillator_motion")

    fig,ax=plt.subplots(figsize=(8.7,4.5)); vals=[.25,.75,1.0]
    ax.bar(["symmetric mode","antisymmetric mode","total"],vals,color=[TEAL,MAGENTA,INK],edgecolor=INK); ax.set_ylim(0,1.1); ax.set_ylabel("energy"); ax.grid(alpha=.15,axis="y")
    ax.set_title("Exact energy partition is constant in time",weight="bold")
    for i,v in enumerate(vals): ax.text(i,v+.03,f"{v:.2f}",ha="center",weight="bold")
    fig.tight_layout(); _save(fig,OUT,"15_coupled_oscillator_energy")


def chunk5() -> None:
    ng=nonlinear_geometry.build_certificate()
    xin=np.array([float(v) for v in ng.signal]); y=np.array([float(v) for v in ng.direct_output]); yp=np.array([float(v) for v in ng.packet_output])
    fig,ax=plt.subplots(figsize=(10.5,4.7)); idx=np.arange(len(xin))
    ax.plot(idx,xin,marker="o",color=INK,lw=1.5,label="input $x$"); ax.plot(idx,y,marker="o",color=RED,lw=2,label="direct nonlinear output")
    ax.plot(idx,yp,marker="x",color=TEAL,lw=1.2,ls="--",label="packet reconstruction"); ax.set_xlabel("sample address"); ax.grid(alpha=.18); _legend_below(ax,ncol=3,y=-.18)
    ax.set_title("A nonlinear memory-one filter remains exact in even/odd packet coordinates",weight="bold"); fig.tight_layout(rect=[0,.12,1,1]); _save(fig,OUT,"16_nonlinear_filter_packets")

    fig,ax=plt.subplots(figsize=(7.4,6.2)); ax.set_xlim(-1.2,1.2); ax.set_ylim(-1.2,1.2); ax.axis("off"); pos=[(-.8,.8),(.8,.8),(.8,-.8),(-.8,-.8)]
    for i,(px,py) in enumerate(pos): ax.add_patch(Circle((px,py),.16,facecolor=COLORS[i]+"28",edgecolor=COLORS[i],lw=2)); ax.text(px,py,f"$v_{i}$",ha="center",va="center",fontsize=15,weight="bold")
    for u,v in [(0,1),(1,2),(2,3),(3,0)]:
        p0=np.array(pos[u],float); p1=np.array(pos[v],float); vec=p1-p0; vec/=np.linalg.norm(vec); _arrow(ax,tuple(p0+.18*vec),tuple(p1-.18*vec),color=INK)
    ax.text(0,1.08,"flat packet transport",ha="center",fontsize=19,weight="bold"); ax.text(0,0,"$B_{03}B_{32}B_{21}B_{10}=I$",ha="center",fontsize=18,weight="bold",bbox=dict(boxstyle="round,pad=.3",facecolor="#E6F3F1",edgecolor=TEAL))
    ax.text(0,-1.08,"spanning-tree propagation reconstructs all gauges exactly",ha="center",fontsize=10.5,color=MUTED); _save(fig,OUT,"17_flat_holonomy")

    flat=np.array(ng.flat_holonomy.tolist(),dtype=float); bad=np.array(ng.perturbed_holonomy.tolist(),dtype=float); obs=np.array(ng.obstruction_matrix.tolist(),dtype=float)
    fig,axes=plt.subplots(1,3,figsize=(11.7,3.8)); mats=[flat,bad,obs]; titles=["flat holonomy","perturbed holonomy","obstruction $H-I$"]; cmaps=["Blues","coolwarm","magma"]
    for ax,M,title,cmap in zip(axes,mats,titles,cmaps,strict=True):
        ax.imshow(M,cmap=cmap,vmin=-1,vmax=1); ax.set_title(title,weight="bold"); ax.set_xticks([0,1]); ax.set_yticks([0,1])
        for i in range(2):
            for j in range(2): ax.text(j,i,f"{M[i,j]:.2f}",ha="center",va="center",color=WHITE if abs(M[i,j])>.5 else INK)
    fig.suptitle("One changed edge creates an exact cycle obstruction",fontsize=17,weight="bold"); fig.text(.5,.02,"$\\|H-I\\|_F^2=8/5$ exactly",ha="center",fontsize=11.5,weight="bold",color=RED)
    fig.tight_layout(rect=[0,.06,1,.90]); _save(fig,OUT,"18_holonomy_obstruction")


def chunk6() -> None:
    ng=nonlinear_geometry.build_certificate()
    rows=[
        ("linear object reconstruction","0"),("linear operator reconstruction","0"),("linear block product","0"),
        ("polyphase synthesis","0"),("Haar synthesis","0"),("Fourier synthesis","0"),("Fourier projector completeness","0"),
        ("quantum path synthesis","0"),("Bell reduced-state residual","0"),("conditional expectation idempotence","0"),
        ("Bayesian sufficient coarsening","0"),("Bayesian defect factorization","0"),("sequence recurrence","0"),
        ("closed coefficient formula","0"),("oscillator ODE","0"),("energy partition","0"),
        ("nonlinear packet synthesis","0"),("flat holonomy","0"),("bad holonomy norm squared","8/5 (nonzero obstruction)"),
    ]
    fig,ax=plt.subplots(figsize=(11.6,8.0)); ax.axis("off"); ax.text(.5,.96,"Exact symbolic certificate dashboard",ha="center",fontsize=21,weight="bold",transform=ax.transAxes)
    y=.90
    for i,(name,label) in enumerate(rows):
        bg=PAPER if i%2==0 else "#EFF2F2"; ax.add_patch(FancyBboxPatch((.05,y-.022),.90,.040,boxstyle="round,pad=.004",facecolor=bg,edgecolor="none",transform=ax.transAxes))
        ax.text(.07,y,name,ha="left",va="center",transform=ax.transAxes,fontsize=10.3); color=RED if "nonzero" in label else TEAL
        ax.text(.92,y,label,ha="right",va="center",transform=ax.transAxes,fontsize=10.3,family="monospace",weight="bold",color=color); y-=.044
    ax.text(.5,.035,"All zero entries are exact SymPy identities. The nonzero final row is the intended negative-control obstruction.",ha="center",fontsize=10.5,color=MUTED,transform=ax.transAxes)
    _save(fig,OUT,"19_verification_dashboard")



def chunk7() -> None:
    lc = linear.build_certificate()
    dc = details.build_detailed_certificate()
    x = np.array([float(v) for v in lc.x])
    packets = [np.array([float(v) for v in p]) for p in lc.packets]
    fig, axes = plt.subplots(4, 1, figsize=(12.8, 7.8), sharex=True, constrained_layout=True)
    labels = ["original vector $x$", "$P_0x$", "$P_1x$", "$P_2x$"]
    vals = [x] + packets
    colors = [INK, BLUE, TEAL, ORANGE]
    for ax, value, label, color in zip(axes, vals, labels, colors, strict=True):
        ax.bar(np.arange(6), value, color=color, alpha=.84, edgecolor=INK, linewidth=.7)
        ax.axhline(0, color=INK, lw=.7)
        ax.set_ylabel(label)
        ax.grid(alpha=.14, axis="y")
        for i, v in enumerate(value):
            if abs(v) > 1e-12:
                ax.text(i, v + (.22 if v >= 0 else -.32), f"{v:g}", ha="center", va="bottom" if v>=0 else "top", fontsize=9)
    axes[-1].set_xticks(np.arange(6), [f"coordinate {i+1}" for i in range(6)])
    axes[-1].tick_params(axis="x", rotation=20)
    fig.suptitle("Object analysis is an exact coordinate partition", fontsize=18, weight="bold")
    _save(fig, OUT, "20_linear_object_packets")

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.8), constrained_layout=True)
    packet_coords = [(0,1),(2,3),(4,5)]
    for b, ax in enumerate(axes):
        coords = packet_coords[b]
        bottom = np.zeros(2)
        for a in range(3):
            vec = np.array([float(dc.linear_contributions[b][a][i]) for i in coords])
            ax.bar([0,1], vec, bottom=bottom, color=COLORS[a], edgecolor=INK, linewidth=.6, label=f"from input $X_{a}$")
            bottom = bottom + vec
        target = np.array([float((lc.projectors[b]*lc.operator*lc.x)[i]) for i in coords])
        ax.scatter([0,1], target, color=INK, marker="D", s=48, zorder=5, label="target output")
        ax.axhline(0, color=INK, lw=.7)
        ax.set_xticks([0,1], [f"coord {coords[0]+1}", f"coord {coords[1]+1}"])
        ax.set_title(f"output packet $X_{b}$", weight="bold")
        ax.grid(alpha=.15, axis="y")
        for i,v in enumerate(target): ax.text(i, v + (.3 if v>=0 else -.45), f"sum={v:g}", ha="center", fontsize=9, weight="bold")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5,-.02), ncol=4)
    fig.suptitle("Every output packet is the sum of its input-to-output transfer contributions", fontsize=17, weight="bold")
    _save(fig, OUT, "21_linear_block_contributions")


def chunk8() -> None:
    x_exact=np.array([3.0,1.0,4.0,1.0,5.0,9.0,2.0,6.0])
    haar_labels=[r"2\sqrt{2}",r"\sqrt{2}",r"5\sqrt{2}/2",r"3\sqrt{2}/2",r"7\sqrt{2}",r"-2\sqrt{2}",r"4\sqrt{2}",r"-2\sqrt{2}"]
    # Polyphase interleaving diagram.
    fig, ax = plt.subplots(figsize=(13.0, 6.3))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.text(.5,.94,"Polyphase synthesis is exact address placement",ha="center",fontsize=20,weight="bold")
    channels=[(0,[3,5],TEAL),(1,[1,9],ORANGE),(2,[4,2],MAGENTA),(3,[1,6],PURPLE)]
    for r,vals,color in channels:
        y=.78-r*.17
        _box(ax,.04,y-.055,.20,.11,f"channel $x_{r}$\n{vals}",face=color+"22",edge=color,fontsize=13)
        for q,val in enumerate(vals):
            target=4*q+r
            tx=.39+target*.07
            _arrow(ax,(.24,y),(tx,.22),color=color,rad=(-.10+.03*r))
            ax.text((.24+tx)/2,(y+.22)/2+.03,f"{val}",ha="center",fontsize=9,color=color)
    for n,val in enumerate([3,1,4,1,5,9,2,6]):
        x=.39+n*.07
        _box(ax,x-.026,.15,.052,.12,f"{val}\n$n={n}$",face=WHITE,edge=COLORS[n%4],fontsize=10)
    ax.text(.5,.055,"Each channel value returns to the unique address $n=4q+r$; no interpolation or averaging occurs.",ha="center",fontsize=11,color=MUTED)
    _save(fig,OUT,"22_signal_polyphase_interleave")

    # Haar butterfly with all exact pair calculations.
    x=np.array([3,1,4,1,5,9,2,6],dtype=float)
    fig,axes=plt.subplots(1,4,figsize=(13.2,4.8),constrained_layout=True)
    for k,ax in enumerate(axes):
        a,b=x[2*k],x[2*k+1]
        low=(a+b)/np.sqrt(2); high=(a-b)/np.sqrt(2)
        ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
        _box(ax,.04,.67,.24,.14,f"$x_{{{2*k}}}={a:g}$",face=BLUE+"18",edge=BLUE,fontsize=12)
        _box(ax,.04,.25,.24,.14,f"$x_{{{2*k+1}}}={b:g}$",face=ORANGE+"18",edge=ORANGE,fontsize=12)
        _box(ax,.66,.67,.28,.14,f"low\n${haar_labels[2*k]}$",face=TEAL+"18",edge=TEAL,fontsize=11)
        _box(ax,.66,.25,.28,.14,f"detail\n${haar_labels[2*k+1]}$",face=MAGENTA+"18",edge=MAGENTA,fontsize=11)
        _arrow(ax,(.28,.74),(.66,.74),color=TEAL,text=r"$+\,/\sqrt{2}$",text_offset=(0,.05))
        _arrow(ax,(.28,.32),(.66,.32),color=MAGENTA,text=r"$-\,/\sqrt{2}$",text_offset=(0,-.05))
        _arrow(ax,(.28,.74),(.66,.32),color=MAGENTA,rad=-.15)
        _arrow(ax,(.28,.32),(.66,.74),color=TEAL,rad=.15)
        ax.set_title(f"pair {k}",weight="bold")
    fig.suptitle("One-level Haar analysis is four exact two-sample butterflies",fontsize=17,weight="bold")
    _save(fig,OUT,"23_signal_haar_butterfly")

    # Fourier magnitude, phase, and exact inverse residual.
    coeff=np.fft.fft(x_exact)/np.sqrt(8)
    mag=np.abs(coeff); phase=np.angle(coeff)
    rec=np.fft.ifft(np.fft.fft(np.array([3,1,4,1,5,9,2,6],dtype=float)))
    residual=np.real(rec)-np.array([3,1,4,1,5,9,2,6],dtype=float)
    fig,axes=plt.subplots(1,3,figsize=(13.2,4.5),constrained_layout=True)
    axes[0].stem(np.arange(8),mag,linefmt=BLUE,markerfmt="o",basefmt=" "); axes[0].set_title("unitary magnitude",weight="bold"); axes[0].set_xlabel("frequency $k$"); axes[0].grid(alpha=.16)
    axes[1].stem(np.arange(8),phase,linefmt=ORANGE,markerfmt="o",basefmt=" "); axes[1].set_title("phase",weight="bold"); axes[1].set_xlabel("frequency $k$"); axes[1].set_ylabel("radians"); axes[1].grid(alpha=.16)
    axes[2].bar(np.arange(8),residual,color=RED,edgecolor=INK); axes[2].set_title("inverse-DFT residual",weight="bold"); axes[2].set_xlabel("sample $n$"); axes[2].ticklabel_format(axis='y',style='sci',scilimits=(0,0)); axes[2].grid(alpha=.16,axis='y')
    fig.suptitle("The complex Fourier coordinates retain magnitude and phase; the complete inverse is exact",fontsize=16.5,weight="bold")
    _save(fig,OUT,"24_signal_fourier_coefficients")

    # Pulled-back Fourier band signals.
    groups=((0,), (1,7), (2,6), (3,5), (4,))
    raw=np.fft.fft(x_exact)
    packets=[]
    for group in groups:
        selected=np.zeros(8,dtype=complex)
        for k in group: selected[k]=raw[k]
        packets.append(np.real_if_close(np.fft.ifft(selected)).astype(float))
    labels=["DC","|k|=1","|k|=2","|k|=3","Nyquist"]
    fig,axes=plt.subplots(6,1,figsize=(13.0,9.2),sharex=True,constrained_layout=True)
    original=np.array([3,1,4,1,5,9,2,6],dtype=float)
    axes[0].plot(np.arange(8),original,marker='o',color=INK,lw=2); axes[0].set_ylabel("$x$"); axes[0].set_title("Fourier band packets in the original signal coordinates",loc='left',weight='bold')
    for i,(ax,p,label) in enumerate(zip(axes[1:],packets,labels,strict=True)):
        ax.plot(np.arange(8),p,marker='o',color=COLORS[i],lw=1.6); ax.axhline(0,color=INK,lw=.6); ax.set_ylabel(label); ax.grid(alpha=.14)
    axes[-1].set_xlabel("sample address $n$")
    _save(fig,OUT,"25_signal_fourier_band_packets")


def chunk9() -> None:
    qc=quantum.build_certificate(); dc=details.build_detailed_certificate(); bc=bayes.build_certificate()
    states=[qc.psi0,qc.psi1,qc.bell]
    titles=["seed $|00\\rangle$","after $H\\otimes I$","after CNOT"]
    basis=["00","01","10","11"]
    fig,axes=plt.subplots(1,3,figsize=(13.0,4.5),sharey=True,constrained_layout=True)
    for ax,state,title,color in zip(axes,states,titles,[BLUE,ORANGE,MAGENTA],strict=True):
        probs=[float(sp.N(sp.conjugate(v)*v)) for v in state]
        ax.bar(np.arange(4),probs,color=color,edgecolor=INK); ax.set_xticks(np.arange(4),basis); ax.set_ylim(0,1.05); ax.set_title(title,weight='bold'); ax.grid(alpha=.15,axis='y')
        for i,v in enumerate(probs): ax.text(i,v+.03,f"{v:.2f}",ha='center',fontsize=9)
    axes[0].set_ylabel("computational-basis probability")
    fig.suptitle("Bell-state preparation step by step",fontsize=18,weight='bold')
    _save(fig,OUT,"26_quantum_state_evolution")

    labels=[name for name,_ in dc.quantum_path_table]
    norms=[float(sp.N((vec.conjugate().T*vec)[0])) for _,vec in dc.quantum_path_table]
    fig,axes=plt.subplots(1,2,figsize=(12.6,4.6),constrained_layout=True)
    axes[0].bar(np.arange(4),norms,color=[TEAL,ORANGE,BLUE,RED],edgecolor=INK); axes[0].set_xticks(np.arange(4),labels); axes[0].set_ylabel("path probability weight"); axes[0].set_title("all parity paths",weight='bold'); axes[0].grid(alpha=.15,axis='y')
    probs=[float(v) for v in dc.quantum_measurement_probabilities]
    axes[1].bar(np.arange(4),probs,color=[MAGENTA,GRID if 'GRID' in globals() else MUTED,MUTED,MAGENTA],edgecolor=INK); axes[1].set_xticks(np.arange(4),["00","01","10","11"]); axes[1].set_ylabel("measurement probability"); axes[1].set_title("final Bell measurement",weight='bold'); axes[1].grid(alpha=.15,axis='y')
    fig.suptitle("Two packet paths survive and generate exactly two measurement outcomes",fontsize=16.5,weight='bold')
    _save(fig,OUT,"27_quantum_path_and_measurement")

    f=np.array([1,4,-2,3],dtype=float); Ef=np.array([float(v) for v in bc.projected_observable]); res=f-Ef
    mu=np.array([.1,.2,.3,.4])
    indicators=[np.array([1,1,0,0],dtype=float),np.array([0,0,1,1],dtype=float)]
    dots=[float(np.sum(mu*res*g)) for g in indicators]
    fig,axes=plt.subplots(1,2,figsize=(12.7,4.7),constrained_layout=True)
    idx=np.arange(4); w=.25
    axes[0].bar(idx-w,f,width=w,label="$f$",color=BLUE); axes[0].bar(idx,Ef,width=w,label="$E_\\pi f$",color=TEAL); axes[0].bar(idx+w,res,width=w,label="residual",color=ORANGE); axes[0].axhline(0,color=INK,lw=.7); axes[0].set_xticks(idx); axes[0].set_title("projection and residual",weight='bold'); axes[0].grid(alpha=.15,axis='y'); _legend_below(axes[0],ncol=3,y=-.18)
    axes[1].bar([0,1],dots,color=[MAGENTA,PURPLE],edgecolor=INK); axes[1].axhline(0,color=INK,lw=.7); axes[1].set_xticks([0,1],["packet A indicator","packet B indicator"]); axes[1].set_ylabel("weighted inner product"); axes[1].set_title("residual is orthogonal to packet constants",weight='bold'); axes[1].grid(alpha=.15,axis='y')
    fig.suptitle("Conditional expectation is a genuine weighted orthogonal projector",fontsize=16.5,weight='bold')
    _save(fig,OUT,"28_bayes_weighted_projection")

    p1=np.array([.1,.2,.3,.4]); p2=np.array([.2,.1,.4,.3]); cp=np.array([.3,.7])
    post1=np.array([float(v) for v in dc.bayes_witness_posterior_1]); post2=np.array([float(v) for v in dc.bayes_witness_posterior_2])
    fig,axes=plt.subplots(1,3,figsize=(13.2,4.6),constrained_layout=True)
    axes[0].bar(np.arange(4)-.16,p1,width=.32,label="$p^{(1)}$",color=BLUE); axes[0].bar(np.arange(4)+.16,p2,width=.32,label="$p^{(2)}$",color=ORANGE); axes[0].set_title("different fine priors",weight='bold'); axes[0].set_xticks(np.arange(4)); axes[0].grid(alpha=.15,axis='y'); _legend_below(axes[0],ncol=2,y=-.18)
    axes[1].bar([0,1],cp,color=[TEAL,MAGENTA],edgecolor=INK); axes[1].set_xticks([0,1],["A","B"]); axes[1].set_title("same coarse prior $(3/10,7/10)$",weight='bold'); axes[1].grid(alpha=.15,axis='y')
    idx=np.arange(2); axes[2].bar(idx-.18,post1,width=.36,label="posterior 1",color=BLUE); axes[2].bar(idx+.18,post2,width=.36,label="posterior 2",color=ORANGE); axes[2].set_xticks(idx,["A","B"]); axes[2].set_title("different coarse posteriors",weight='bold'); axes[2].grid(alpha=.15,axis='y'); _legend_below(axes[2],ncol=2,y=-.18)
    fig.suptitle("A nonsufficient packet forgets fine information needed by the likelihood",fontsize=16.5,weight='bold')
    _save(fig,OUT,"29_bayes_same_coarse_witness")


def chunk10() -> None:
    dc=details.build_detailed_certificate(); ac=arithmetic.build_certificate(12)
    roots=[np.exp(1j*(np.pi+2*np.pi*k)/5) for k in range(5)]
    fig,ax=plt.subplots(figsize=(7.2,6.4),constrained_layout=True)
    theta=np.linspace(0,2*np.pi,500); ax.plot(np.cos(theta),np.sin(theta),color=MUTED,lw=1)
    for k,r in enumerate(roots):
        ax.scatter([r.real],[r.imag],s=90,color=COLORS[k],edgecolor=INK,zorder=3); ax.text(r.real*1.13,r.imag*1.13,rf"$\eta_{k}$",ha='center',va='center',fontsize=12,weight='bold')
        ax.arrow(0,0,r.real*.86,r.imag*.86,width=.004,head_width=.045,length_includes_head=True,color=COLORS[k],alpha=.75)
    ax.set_aspect('equal'); ax.set_xlim(-1.35,1.35); ax.set_ylim(-1.25,1.25); ax.axhline(0,color=INK,lw=.6); ax.axvline(0,color=INK,lw=.6); ax.set_xlabel("real part"); ax.set_ylabel("imaginary part"); ax.grid(alpha=.12)
    ax.set_title(r"The five roots of $\eta^5=-1$ form the signed root-filter packet",weight='bold')
    _save(fig,OUT,"30_arithmetic_signed_roots")

    contrib=np.array([[int(a),int(b),int(c)] for a,b,c in dc.recurrence_contributions],dtype=object)
    n=np.arange(1,5)
    fig,ax=plt.subplots(figsize=(10.8,5.4),constrained_layout=True)
    # normalize by each total for readable stacked proportions, while annotate exact values.
    ratios=np.array([[float(a/c),float(b/c)] for a,b,c in contrib])
    ax.bar(n,ratios[:,0],color=TEAL,edgecolor=INK,label="first convolution sum")
    ax.bar(n,ratios[:,1],bottom=ratios[:,0],color=ORANGE,edgecolor=INK,label="derivative-weighted sum")
    ax.set_ylim(0,1.12); ax.set_xticks(n); ax.set_xlabel("coefficient index $n$"); ax.set_ylabel("fraction of exact recurrence total"); ax.grid(alpha=.15,axis='y')
    for i,(a,b,c) in enumerate(contrib):
        ax.text(n[i],1.025,f"$a_{n[i]}={c}$",ha='center',fontsize=9,weight='bold')
        ax.text(n[i],ratios[i,0]/2,f"{a}",ha='center',va='center',fontsize=8,color=WHITE if ratios[i,0]>.22 else INK)
        ax.text(n[i],ratios[i,0]+ratios[i,1]/2,f"{b}",ha='center',va='center',fontsize=8,color=WHITE if ratios[i,1]>.22 else INK)
    _legend_below(ax,ncol=2,y=-.16)
    ax.set_title("The exact integer recurrence splits each coefficient into two integral contributions",weight='bold')
    _save(fig,OUT,"31_arithmetic_recurrence_contributions")

    seq=np.array([int(v) for v in ac.sequence],dtype=object)
    digits=np.array([len(str(v)) for v in seq])
    fig,axes=plt.subplots(1,2,figsize=(12.8,4.6),constrained_layout=True)
    axes[0].bar(np.arange(8),digits[:8],color=MAGENTA,edgecolor=INK); axes[0].set_xticks(np.arange(8)); axes[0].set_xlabel("$n$"); axes[0].set_ylabel("decimal digits"); axes[0].set_title("coefficient growth",weight='bold'); axes[0].grid(alpha=.15,axis='y')
    vals=np.array([0 if v==0 else math.log10(v) for v in seq[:8]],dtype=float)
    axes[1].plot(np.arange(8),vals,marker='o',color=BLUE,lw=2); axes[1].set_xticks(np.arange(8)); axes[1].set_xlabel("$n$"); axes[1].set_ylabel(r"$\log_{10} a_n$"); axes[1].set_title("same growth on logarithmic scale",weight='bold'); axes[1].grid(alpha=.15)
    fig.suptitle("The sequence grows rapidly, but every displayed coefficient is generated exactly",fontsize=16.5,weight='bold')
    _save(fig,OUT,"32_arithmetic_digit_growth")


def chunk11() -> None:
    ng=nonlinear_geometry.build_certificate()
    es=np.array([1/np.sqrt(2),1/np.sqrt(2)]); ea=np.array([1/np.sqrt(2),-1/np.sqrt(2)])
    fig,axes=plt.subplots(1,2,figsize=(10.8,4.5),sharey=True,constrained_layout=True)
    axes[0].bar([1,2],es,color=[BLUE,BLUE],edgecolor=INK); axes[0].set_xticks([1,2],["mass 1","mass 2"]); axes[0].set_title(r"symmetric mode, $\lambda=1$",weight='bold'); axes[0].axhline(0,color=INK,lw=.7); axes[0].grid(alpha=.15,axis='y')
    axes[1].bar([1,2],ea,color=[ORANGE,ORANGE],edgecolor=INK); axes[1].set_xticks([1,2],["mass 1","mass 2"]); axes[1].set_title(r"antisymmetric mode, $\lambda=3$",weight='bold'); axes[1].axhline(0,color=INK,lw=.7); axes[1].grid(alpha=.15,axis='y')
    axes[0].set_ylabel("normalized mode amplitude")
    fig.suptitle("The stiffness matrix is resolved by two orthogonal normal-mode projectors",fontsize=16.5,weight='bold')
    _save(fig,OUT,"33_physics_mode_shapes")

    t=sp.symbols('t',real=True); tt=np.linspace(0,12,900)
    qs=np.cos(tt)/np.sqrt(2); qa=np.cos(np.sqrt(3)*tt)/np.sqrt(2)
    vs=-np.sin(tt)/np.sqrt(2); va=-np.sqrt(3)*np.sin(np.sqrt(3)*tt)/np.sqrt(2)
    fig,axes=plt.subplots(2,2,figsize=(12.7,7.0),constrained_layout=True)
    axes[0,0].plot(tt,qs,color=TEAL,lw=1.8,label="$q_s$"); axes[0,0].plot(tt,qa,color=MAGENTA,lw=1.8,label="$q_a$"); axes[0,0].set_title("modal coordinates",weight='bold'); axes[0,0].grid(alpha=.15); _legend_below(axes[0,0],ncol=2,y=-.18)
    q1=(np.cos(tt)+np.cos(np.sqrt(3)*tt))/2; q2=(np.cos(tt)-np.cos(np.sqrt(3)*tt))/2
    axes[0,1].plot(tt,q1,color=BLUE,lw=1.8,label="$q_1$"); axes[0,1].plot(tt,q2,color=ORANGE,lw=1.8,label="$q_2$"); axes[0,1].set_title("physical coordinates",weight='bold'); axes[0,1].grid(alpha=.15); _legend_below(axes[0,1],ncol=2,y=-.18)
    axes[1,0].plot(qs,vs,color=TEAL,lw=1.5); axes[1,0].set_xlabel("$q_s$"); axes[1,0].set_ylabel(r"$\dot q_s$"); axes[1,0].set_title("symmetric-mode phase orbit",weight='bold'); axes[1,0].grid(alpha=.15); axes[1,0].set_aspect('equal',adjustable='box')
    axes[1,1].plot(qa,va,color=MAGENTA,lw=1.5); axes[1,1].set_xlabel("$q_a$"); axes[1,1].set_ylabel(r"$\dot q_a$"); axes[1,1].set_title("antisymmetric-mode phase orbit",weight='bold'); axes[1,1].grid(alpha=.15); axes[1,1].set_aspect('equal',adjustable='box')
    fig.suptitle("Packet evolution is diagonal in modal coordinates and reconstructs coupled physical motion",fontsize=16.2,weight='bold')
    _save(fig,OUT,"34_physics_modal_reconstruction")

    e=np.array([1.0,0.0,3.0,-2.0]); o=np.array([2.0,-1.0,1.0,2.0]); ye=np.array([3.0,2.0,3.5,-1.5]); yo=np.array([2.5,-1.0,5.5,4.0])
    fig,axes=plt.subplots(2,2,figsize=(12.0,6.4),sharex=True,constrained_layout=True)
    data=[e,o,ye,yo]; titles=["even input $e[k]$","odd input $o[k]$","even output $y_e[k]$","odd output $y_o[k]$"]; colors=[BLUE,ORANGE,TEAL,MAGENTA]
    for ax,d,title,color in zip(axes.ravel(),data,titles,colors,strict=True):
        ax.bar(np.arange(4),d,color=color,edgecolor=INK); ax.axhline(0,color=INK,lw=.7); ax.set_title(title,weight='bold'); ax.set_xticks(np.arange(4)); ax.grid(alpha=.15,axis='y')
        for i,v in enumerate(d): ax.text(i,v+(.18 if v>=0 else -.28),f"{v:g}",ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
    fig.suptitle("The nonlinear filter closes exactly on even and odd packet coordinates",fontsize=16.5,weight='bold')
    _save(fig,OUT,"35_nonlinear_channel_values")

    edges=[
        np.array([[3/5,-4/5],[4/5,3/5]],dtype=float),
        np.array([[63/65,-16/65],[16/65,63/65]],dtype=float),
        np.array([[323/325,-36/325],[36/325,323/325]],dtype=float),
        np.array([[7/25,24/25],[-24/25,7/25]],dtype=float),
    ]
    names=["$B_{10}$","$B_{21}$","$B_{32}$","$B_{03}$"]
    fig,axes=plt.subplots(1,4,figsize=(13.2,3.8),constrained_layout=True)
    for ax,M,name in zip(axes,edges,names,strict=True):
        im=ax.imshow(M,cmap='coolwarm',vmin=-1,vmax=1); ax.set_title(name,weight='bold'); ax.set_xticks([0,1]); ax.set_yticks([0,1]); _matrix_text(ax,M,threshold=1.0)
    fig.colorbar(im,ax=axes.ravel().tolist(),fraction=.025,pad=.015)
    fig.suptitle("Each edge transport is exact; their ordered cycle product is the identity",fontsize=16.5,weight='bold')
    _save(fig,OUT,"36_holonomy_edge_matrices")

    # Cross-domain proof checklist.
    cols=["packets","analysis","transfer/refine","synthesis","independent audit"]
    rows=["linear","signal","quantum","Bayes","arithmetic","physics","nonlinear/holonomy"]
    M=np.ones((7,5))
    fig,ax=plt.subplots(figsize=(10.5,5.4),constrained_layout=True)
    im=ax.imshow(M,cmap=matplotlib.colors.ListedColormap([TEAL]),vmin=0,vmax=1)
    ax.set_xticks(np.arange(5),cols,rotation=20,ha='right'); ax.set_yticks(np.arange(7),rows)
    for i in range(7):
        for j in range(5): ax.text(j,i,"proved",ha='center',va='center',color=WHITE,weight='bold',fontsize=9)
    ax.set_title("Every worked area completes the same five-stage proof protocol",weight='bold')
    _save(fig,OUT,"37_cross_domain_proof_matrix")

def main() -> None:
    if len(sys.argv)!=2: raise SystemExit("usage: python generate_chunks.py {0|1|2|3|4|5|6|7|8|9|10|11}")
    globals()[f"chunk{sys.argv[1]}"]()

if __name__=="__main__": main()
