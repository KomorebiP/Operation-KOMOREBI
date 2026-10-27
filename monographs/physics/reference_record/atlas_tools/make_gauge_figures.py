#!/usr/bin/env python3
"""Reproduce the twelve gauge atlas plates and their bounded evidence record.

Run: python tools/make_gauge_figures.py
Exact checks use Gaussian rational matrices. Numerical checks concern only the
declared examples and ranges. This script never invokes Lean.
"""
from pathlib import Path
import datetime as dt
import hashlib
import io
import json
import platform
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.linalg import expm, logm
import sympy as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source" / "gauge_figures"
EVID = ROOT / "evidence" / "gauge"
OUT.mkdir(parents=True, exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)
START = time.monotonic()
STAMP = dt.datetime.now(dt.timezone.utc).isoformat()
INPUT_HASH = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
TEAL, GOLD, LILAC = "#245D60", "#AD7842", "#7C738E"
INK, MUTED, PALE = "#212B34", "#58646B", "#EEF3F2"
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":11,
    "axes.labelsize":11,"axes.titlesize":12.5,"axes.titlepad":13,
    "axes.labelcolor":INK,"text.color":INK,"axes.edgecolor":"#ADBAB9",
    "xtick.color":MUTED,"ytick.color":MUTED,"axes.spines.top":False,
    "axes.spines.right":False,"legend.frameon":False,"legend.fontsize":10,
    "lines.linewidth":2.2,"figure.facecolor":"white","axes.facecolor":"white",
    "savefig.facecolor":"white","pdf.fonttype":42,"ps.fonttype":42,
    "mathtext.fontset":"dejavusans"})
checks, outputs = [], []
sx = np.array([[0,1],[1,0]], complex)
sy = np.array([[0,-1j],[1j,0]], complex)
sz = np.diag([1.,-1.]).astype(complex)
pauli = [sx,sy,sz]
SP = [sp.Matrix([[0,1],[1,0]]),sp.Matrix([[0,-sp.I],[sp.I,0]]),sp.diag(1,-1)]

def record(name, passed, detail):
    item = {"name":name,"passed":bool(passed),"detail":detail}
    checks.append(item)
    if not passed:
        raise AssertionError(f"{name}: {detail}")

def save(fig, name):
    for ext in ("pdf","png"):
        path = OUT / f"{name}.{ext}"
        metadata = {"Creator":"Komorebi gauge figure generator"}
        if ext == "pdf": metadata.update({"CreationDate":None,"ModDate":None})
        buffer=io.BytesIO()
        fig.savefig(buffer,format=ext,dpi=190,bbox_inches="tight",pad_inches=.15,metadata=metadata)
        data=buffer.getvalue()
        temporary=path.with_name(path.name+".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
        outputs.append({"path":str(path.relative_to(ROOT)),"kind":"result",
                        "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)

def grid(ax):
    ax.grid(True,color="#DDE5E3",linewidth=.65,alpha=.8)
    ax.set_axisbelow(True)

def arrow(ax,start,end,col=TEAL,lw=2,style="->"):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle=style,mutation_scale=14,
                               color=col,lw=lw,shrinkA=2,shrinkB=2))

def rational_su2(t,axis):
    return ((1-t*t)*sp.eye(2)+2*sp.I*t*SP[axis])/(1+t*t)

def asarray(matrix): return np.array(matrix,dtype=complex)

def product(values):
    out = np.eye(2,dtype=complex)
    for val in values: out=out@val
    return out

def make_figures():
    # 01: endpoint covariance, exact Gaussian rational benchmark.
    U=sp.Rational(3,5)+sp.I*sp.Rational(4,5)
    gx=sp.Rational(5,13)+sp.I*sp.Rational(12,13)
    gy=sp.Rational(8,17)-sp.I*sp.Rational(15,17)
    a=1+sp.I/2; b=-sp.Rational(1,3)+sp.I
    D=sp.expand(U*b-a); Up=sp.expand(gx*U*sp.conjugate(gy))
    Dp=sp.expand(Up*gy*b-gx*a)
    record("exact scalar endpoint covariance",sp.simplify(Dp-gx*D)==0
           and sp.simplify(sp.conjugate(Up)*Up)==1,
           "U=(3+4i)/5; gx=(5+12i)/13; gy=(8-15i)/17; psi_x=1+i/2; psi_y=-1/3+i; h=1.")
    fig,axs=plt.subplots(1,2,figsize=(9,4.4),layout="constrained")
    ax=axs[0];ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    for x,label in [(.18,r"$x$"),(.82,r"$y$")]:
        ax.add_patch(Circle((x,.53),.075,facecolor=PALE,edgecolor=TEAL,lw=1.5))
        ax.text(x,.53,label,ha="center",va="center",fontsize=13)
    arrow(ax,(.71,.65),(.29,.65));arrow(ax,(.29,.40),(.71,.40),GOLD)
    ax.text(.5,.75,r"backward $U: H_y\to H_x$",ha="center",color=TEAL)
    ax.text(.5,.28,r"forward $u=U^{-1}:H_x\to H_y$",ha="center",color=GOLD)
    ax.text(.82,.87,r"$y=x+\hat\mu$",ha="center",fontsize=11)
    ax.text(.5,.10,r"$U'=g_xUg_y^{-1}$     $u'=g_yug_x^{-1}$",ha="center",fontsize=12)
    ax.set_title("Transport direction fixes the endpoint factors")
    ax=axs[1];ax.set_aspect("equal")
    for z,col,label in [(complex(D),TEAL,r"$D$"),(complex(Dp),GOLD,r"$D'=g_xD$")]:
        arrow(ax,(0,0),(z.real,z.imag),col)
        ax.text(z.real*1.12,z.imag*1.12,label,color=col,ha="center",fontsize=12)
    rr=abs(complex(D));theta=np.linspace(0,2*np.pi,301)
    ax.plot(rr*np.cos(theta),rr*np.sin(theta),color=MUTED,lw=1,ls=":")
    ax.axhline(0,color=MUTED,lw=.6);ax.axvline(0,color=MUTED,lw=.6)
    ax.set(xlim=(-2.75,2.75),ylim=(-2.75,2.75),xlabel="real part",ylabel="imaginary part",
           title="A gauge change rotates the covariant difference")
    save(fig,"01_link_covariance")

    # 02: signed phase cancellation on an oriented Abelian plaquette.
    th=sp.Matrix([sp.Rational(3,10),-sp.Rational(1,5),sp.Rational(2,5),sp.Rational(1,10)])
    chi=[sp.Rational(1,10),-sp.Rational(2,5),sp.Rational(4,5),sp.Rational(3,10)]
    transformed=th+sp.Matrix([chi[0]-chi[1],chi[1]-chi[2],chi[3]-chi[2],chi[0]-chi[3]])
    signs=sp.diag(1,1,-1,-1)
    record("exact plaquette signed phase cancellation",sum(signs*th)==sum(signs*transformed)==-sp.Rational(2,5),
           {"edge_phases":[str(v) for v in th],"gauge_angles":[str(v) for v in chi],"signed_flux":"-2/5 radians; no branch crossing is involved"})
    fig,axs=plt.subplots(1,2,figsize=(9,4.4),layout="constrained")
    ax=axs[0];ax.set_aspect("equal");ax.set(xlim=(-.35,1.4),ylim=(-.30,1.30));ax.axis("off")
    vertices=[(0,0),(1,0),(1,1),(0,1)]
    ax.add_patch(Rectangle((0,0),1,1,facecolor=PALE,edgecolor="none"))
    for s,e in [(1,0),(2,1),(3,2),(0,3)]:arrow(ax,vertices[s],vertices[e])
    for label,pos in [(r"$U_b$",(.5,-.14)),(r"$U_r$",(1.17,.5)),(r"$U_t^{-1}$",(.5,1.12)),(r"$U_l^{-1}$",(-.2,.5))]:ax.text(*pos,label,ha="center",va="center",fontsize=13)
    ax.plot(0,0,"o",color=GOLD,ms=8);ax.text(.5,.55,r"$W=e^{-0.4i}$",ha="center",fontsize=16)
    ax.text(.5,.37,"composition acts right to left",ha="center",fontsize=9,color=MUTED)
    ax.set_title("The oriented loop closes at its basepoint")
    x=np.arange(4);axs[1].bar(x-.17,np.array(signs*th,float).ravel(),.34,color=TEAL,label="before gauge change")
    axs[1].bar(x+.17,np.array(signs*transformed,float).ravel(),.34,color=GOLD,label="after gauge change")
    axs[1].axhline(0,color=MUTED,lw=.7);axs[1].set(xticks=x,xticklabels=["bottom","right","− top","− left"],
        ylabel="signed edge phase (radians)",ylim=(-1.55,.98),title="Individual edge phases change; their sum does not")
    axs[1].legend(loc="upper right",fontsize=9);grid(axs[1]);save(fig,"02_abelian_plaquette")

    # 03: exact SU(2) noncommutativity and conjugation invariance.
    A=rational_su2(sp.Rational(1,3),0);B=rational_su2(sp.Rational(2,5),1)
    G=rational_su2(sp.Rational(3,7),2);W=A*B*A.H*B.H
    record("exact SU2 order and conjugation",all(sp.simplify(Q.H*Q)==sp.eye(2) and sp.simplify(Q.det())==1 for Q in (A,B,G)) and A*B!=B*A
           and sp.simplify(sp.trace(G*W*G.H)-sp.trace(W))==0,
           "Cayley rational rotations t=1/3 about x, t=2/5 about y, gauge t=3/7 about z.")
    tt=np.linspace(0,np.pi,301);norms=[];wil=[];wilg=[]
    Gf=asarray(G);bf=expm(.7j*sy)
    for t in tt:
        af=expm(1j*t*sx);wf=af@bf@af.conj().T@bf.conj().T
        norms.append(np.linalg.norm(af@bf-bf@af,"fro"))
        wil.append(1-np.trace(wf).real/2);wilg.append(1-np.trace(Gf@wf@Gf.conj().T).real/2)
    analytic=2*np.sqrt(2)*np.abs(np.sin(tt)*np.sin(.7))
    record("SU2 plotted norm independent formula",np.max(abs(np.array(norms)-analytic))<2e-14
           and np.max(abs(np.array(wil)-wilg))<2e-14,
           {"angles":[0,float(np.pi)],"samples":301,"fixed_y_angle":.7,"tolerance":2e-14})
    fig,axs=plt.subplots(1,2,figsize=(9,4.25),layout="constrained")
    axs[0].plot(tt,norms,color=TEAL);axs[0].set(xlabel="x rotation angle t",ylabel=r"$\|AB-BA\|_F$",title="Changing the order changes the transporter")
    axs[1].plot(tt,wil,color=TEAL,label="W");axs[1].plot(tt,wilg,color=GOLD,ls="--",label=r"$GWG^{-1}$")
    axs[1].set(xlabel="x rotation angle t",ylabel=r"$1-\frac{1}{2}\mathrm{Re}\,\mathrm{Tr}\,W$",title="The Wilson scalar survives conjugation")
    axs[1].legend();
    for ax in axs:grid(ax)
    save(fig,"03_nonabelian_order")

    # 04: exact ordered 2-by-2 rational SU(2) refinement.
    X={(i,j):rational_su2(sp.Rational(1+i+2*j,10),(i+j)%3) for i in range(2) for j in range(3)}
    Y={(i,j):rational_su2(sp.Rational(2+2*i+j,13),(i+2*j+1)%3) for i in range(3) for j in range(2)}
    plaquettes={(i,j):X[i,j]*Y[i+1,j]*X[i,j+1].H*Y[i,j].H for i in range(2) for j in range(2)}
    row={j:X[0,j]*plaquettes[1,j]*X[0,j].H*plaquettes[0,j] for j in range(2)}
    coarse=X[0,0]*X[1,0]*Y[2,0]*Y[2,1]*X[1,2].H*X[0,2].H*Y[0,1].H*Y[0,0].H
    reconstructed=row[0]*Y[0,0]*row[1]*Y[0,0].H
    naive=plaquettes[0,0]*plaquettes[1,0]*plaquettes[0,1]*plaquettes[1,1]
    correct=all(sp.simplify(z)==0 for z in coarse-reconstructed)
    wrong=float(np.linalg.norm(asarray(coarse-naive),"fro"))
    record("exact non-Abelian 2x2 boundary identity",correct and naive!=coarse,
           {"arithmetic":"Gaussian rationals","X_Cayley_t":"(1+i+2j)/10; axis (i+j) mod 3",
            "Y_Cayley_t":"(2+2i+j)/13; axis (i+2j+1) mod 3",
            "matrix_identity_residual":"exact zero","naive_product_Frobenius_error":wrong})
    fig,axs=plt.subplots(1,2,figsize=(9,4.5),layout="constrained")
    ax=axs[0];ax.set_aspect("equal");ax.axis("off");ax.set(xlim=(-.30,2.3),ylim=(-.3,2.4))
    for i in range(2):
        for j in range(2):
            ax.add_patch(Rectangle((i,j),1,1,facecolor=[PALE,"#F8F0E6"][(i+j)%2],edgecolor=MUTED,lw=1))
            ax.text(i+.5,j+.53,f"W{i}{j}",ha="center",fontsize=15,color=TEAL)
    for j in range(3):
        for i in range(2): arrow(ax,(i+.88,j),(i+.12,j),TEAL,1.6)
    for i in range(3):
        for j in range(2): arrow(ax,(i,j+.88),(i,j+.12),GOLD,1.6)
    ax.plot(0,0,"o",color=INK,ms=7);ax.text(.14,-.20,"common basepoint",fontsize=9)
    ax.set_title("Every interior edge cancels in the right order")
    ax=axs[1];ax.axis("off");ax.set(xlim=(0,1),ylim=(0,1))
    ax.text(.5,.84,r"$R_j=(X_{0j}W_{1j}X_{0j}^{-1})W_{0j}$",ha="center",fontsize=14)
    ax.text(.5,.65,r"$W_{\rm boundary}=R_0Y_{00}R_1Y_{00}^{-1}$",ha="center",fontsize=14)
    ax.text(.5,.47,"Ordered reconstruction",ha="center",fontsize=11,color=TEAL)
    ax.text(.5,.36,"exact residual: 0",ha="center",fontsize=20,color=TEAL)
    ax.text(.5,.17,"Naive product of four based plaquettes",ha="center",fontsize=10,color=MUTED)
    ax.text(.5,.065,f"Frobenius error: {wrong:.4f}",ha="center",fontsize=15,color=GOLD)
    ax.set_title("Transport to a common basepoint comes first")
    save(fig,"04_ordered_refinement")

    # 05: BCH curvature; stable finite principal-log branch, not a proof by slope.
    AA=1j*sx;BB=1j*sy;comm=AA@BB-BB@AA
    hs=2.**-np.arange(2,10);raw=[];rich=[];branches=[]
    def F(h):
        ww=expm(h*AA)@expm(h*BB)@expm(-h*AA)@expm(-h*BB)
        branches.append(float(np.max(np.abs(np.angle(np.linalg.eigvals(ww))))))
        return logm(ww)/(h*h)
    for h in hs:
        fh=F(h);ff=F(h/2);raw.append(np.linalg.norm(fh-comm,"fro"))
        rich.append(np.linalg.norm(2*ff-fh-comm,"fro"))
    raw=np.array(raw);rich=np.array(rich)
    slopes=[float(np.log(raw[-2]/raw[-1])/np.log(2)),float(np.log(rich[-2]/rich[-1])/np.log(2))]
    record("finite BCH and Richardson slopes",.98<slopes[0]<1.02 and 1.95<slopes[1]<2.05
           and max(branches)<.2,
           {"A":"i sigma_x","B":"i sigma_y","h_values":hs.tolist(),"slope_last_pair":slopes,
            "max_principal_eigenangle":max(branches),"norm":"Frobenius","branch_scope":"finite displayed matrices only"})
    fig,ax=plt.subplots(figsize=(8.8,4.45),layout="constrained")
    ax.loglog(hs,raw,"o-",color=TEAL,label=r"$F_h=h^{-2}\log W_h$")
    ax.loglog(hs,rich,"s-",color=GOLD,label=r"$2F_{h/2}-F_h$")
    ax.loglog(hs,raw[0]*(hs/hs[0]),color=TEAL,ls=":",lw=1,label="slope 1 reference")
    ax.loglog(hs,rich[0]*(hs/hs[0])**2,color=GOLD,ls=":",lw=1,label="slope 2 reference")
    ax.set(xlabel="spacing h",ylabel=r"error against $[A,B]$ in Frobenius norm",
        title="A fixed SU(2) example displays first-order cancellation")
    ax.legend(loc="upper left",fontsize=10);grid(ax);save(fig,"05_curvature_richardson")

    # 06: finite periodic coined walk, fully specified post-coin amplitudes.
    ep=np.array([1,2j,-1,1+1j,-2j,2],complex)/np.sqrt(24)
    em=np.array([1j,1,-1j,2,-1,0],complex)/np.sqrt(24)
    n=6;phases=np.array([.2,-.3,.4,-.1,.6,-.2]);links=np.exp(1j*phases)
    xp=np.roll(ep,1)/np.roll(links,1);xm=links*np.roll(em,-1)
    rho=np.abs(ep)**2+np.abs(em)**2;rho1=np.abs(xp)**2+np.abs(xm)**2
    cur=np.abs(ep)**2-np.abs(np.roll(em,-1))**2
    residual=rho1-rho-(np.roll(cur,1)-cur)
    record("periodic walk continuity and norm",np.max(np.abs(residual))<2e-15
           and abs(sum(rho)-1)<2e-15 and abs(sum(rho1)-1)<2e-15,
           {"sites":n,"eta_plus":"(1,2i,-1,1+i,-2i,2)/sqrt24","eta_minus":"(i,1,-i,2,-1,0)/sqrt24",
            "U_phases":phases.tolist(),"continuity_max_residual":float(np.max(np.abs(residual))),"tolerance":2e-15})
    fig,axs=plt.subplots(2,1,figsize=(8.8,5.2),sharex=True,layout="constrained");xx=np.arange(n)
    axs[0].bar(xx-.17,rho,.34,color=TEAL,label="before linked shift");axs[0].bar(xx+.17,rho1,.34,color=GOLD,label="after linked shift")
    axs[0].set(ylabel="site population",ylim=(0,.44),title="Unit-modulus links change phases without losing population")
    axs[0].legend(loc="upper right",ncol=2,fontsize=9)
    axs[1].plot(xx,rho1-rho,"o-",color=TEAL,label=r"$\rho'_j-\rho_j$")
    axs[1].plot(xx,np.roll(cur,1)-cur,"x--",color=GOLD,label=r"$J_{j-1/2}-J_{j+1/2}$")
    axs[1].axhline(0,color=MUTED,lw=.7);axs[1].set(xticks=xx,xlabel="periodic site j (six sites)",ylabel="population change",ylim=(-.30,.36))
    axs[1].legend(loc="upper right",ncol=2,fontsize=9)
    for ax in axs:grid(ax)
    save(fig,"06_walk_continuity")

    # 07: integrals compose, arbitrary point samples need not.
    a=.2;b=.7;c=1.2
    integral=lambda x,y: np.cos(x)-np.cos(y)
    u1=np.exp(1j*integral(a,b));u2=np.exp(1j*integral(b,c));uc=np.exp(1j*integral(a,c))
    exactres=abs(u2*u1-uc)
    sampled=np.exp(1j*(c-a)*np.sin(a));sampled_fine=np.exp(1j*((b-a)*np.sin(a)+(c-b)*np.sin(b)))
    record("integrated Abelian subdivision",exactres<2e-15 and abs(sampled_fine-sampled)>.1,
           {"connection":"a(s)=sin(s)","endpoints":[a,b,c],"forward_phase":"exp(i integral a ds)",
            "integral_product_residual":float(exactres),"left_sample_mismatch":float(abs(sampled_fine-sampled)),"tolerance":2e-15})
    fig,axs=plt.subplots(1,2,figsize=(9,4.4),layout="constrained")
    tt=np.linspace(a,c,301);axs[0].plot(tt,np.sin(tt),color=TEAL)
    axs[0].fill_between(tt,np.sin(tt),where=tt<=b,color=TEAL,alpha=.18)
    axs[0].fill_between(tt,np.sin(tt),where=tt>=b,color=GOLD,alpha=.22)
    axs[0].axvline(b,color=MUTED,lw=1,ls="--");axs[0].set(xlabel="edge coordinate s",ylabel="connection coefficient a(s)",title="The two edge integrals add exactly")
    axs[0].text(.43,.31,r"$\int_a^b a(s)\,ds$",ha="center",fontsize=12,color=TEAL)
    axs[0].text(.95,.32,r"$\int_b^c a(s)\,ds$",ha="center",fontsize=12,color=GOLD);grid(axs[0])
    ax=axs[1];ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    for x,lab in [(.1,"a"),(.5,"b"),(.9,"c")]:ax.plot(x,.58,"o",color=INK);ax.text(x,.45,lab,ha="center")
    arrow(ax,(.12,.58),(.48,.58),TEAL);arrow(ax,(.52,.58),(.88,.58),GOLD)
    ax.text(.30,.69,r"$u_1$",ha="center",color=TEAL,fontsize=15);ax.text(.70,.69,r"$u_2$",ha="center",color=GOLD,fontsize=15)
    ax.text(.5,.85,r"$u_{ac}=u_2u_1$",ha="center",fontsize=18)
    ax.text(.5,.28,"Integrated links: exact composition",ha="center",color=TEAL,fontsize=12)
    ax.text(.5,.10,f"Left-point mismatch here: {abs(sampled_fine-sampled):.4f}",ha="center",color=GOLD,fontsize=12)
    ax.set_title("Forward composition is second times first")
    save(fig,"07_edge_subdivision")

    # 08: the five face terms selected by the fixed cubical comparison.
    fig=plt.figure(figsize=(9,4.65));fig.subplots_adjust(left=.02,right=.98,bottom=.06,top=.89,wspace=.15);ax=fig.add_subplot(121,projection="3d")
    faces=[[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,0),(1,1,0),(1,1,1),(0,1,1)],
           [(0,0,0),(0,1,0),(0,1,1),(0,0,1)],[(1,0,0),(1,1,0),(1,1,1),(1,0,1)],
           [(0,0,0),(1,0,0),(1,0,1),(0,0,1)]]
    ax.add_collection3d(Poly3DCollection(faces,facecolors=[TEAL,GOLD,LILAC,TEAL,GOLD],alpha=.20,edgecolor=MUTED,linewidth=1))
    top=np.array([(0,0,1),(1,0,1),(1,1,1),(0,1,1),(0,0,1)])
    ax.plot(*top.T,color=INK,ls="--",lw=1.6)
    ax.set(xlim=(0,1),ylim=(0,1),zlim=(0,1),xlabel="x",ylabel="y",zlabel="z",xticks=[0,1],yticks=[0,1],zticks=[0,1])
    ax.view_init(23,-57);ax.set_box_aspect((1,1,1));ax.set_title("Five faces enter this path comparison")
    ax=fig.add_subplot(122);ax.axis("off");ax.set(xlim=(0,1),ylim=(0,1))
    labels=[r"$|\Omega_{xy}(0)-1|$",r"$|\Omega_{xz}(1)-1|$",r"$|\Omega_{yz}(0)-1|$",r"$|\Omega_{yz}(1)-1|$",r"$|\Omega_{xz}(0)-1|$"]
    for i,(lab,col) in enumerate(zip(labels,[TEAL,GOLD,LILAC,TEAL,GOLD])):
        y=.87-.14*i;ax.add_patch(Rectangle((.08,y-.03),.045,.045,facecolor=col,edgecolor="none"));ax.text(.17,y,lab,va="center",fontsize=14)
    ax.text(.08,.05,r"Top face $\Omega_{xy}(1)$ is absent from this sum.",fontsize=10,color=MUTED)
    ax.set_title(r"The selected sum is $\kappa$, not all six faces")
    record("five-face diagram inventory",len(faces)==5,{"selected_faces":["xy(0)","xz(1)","yz(0)","yz(1)","xz(0)"],"omitted":"xy(1)","scope":"Combinatorial face inventory; no operator theorem is tested by this drawing."})
    save(fig,"08_five_face_budget")

    # 09: common-space 2x2 unitary surrogate with repeated factors.
    eps=2.**-np.arange(2,11);actual=[];bound=[];maxunit=0.
    base=[expm(.31j*sx),expm(-.23j*sy),expm(.19j*sz)]
    M=expm(.12j*(sx+sz)/np.sqrt(2))
    for e in eps:
        fine=[expm(1j*e*c*pauli[(j+1)%3])@base[j] for j,c in enumerate([1,.7,.4])]
        delta=[float(np.linalg.norm(fine[j]-base[j],2)) for j in range(3)]
        w0=product([M,base[0],base[1],base[2],base[1],base[0],M])
        w1=product([M,fine[0],fine[1],fine[2],fine[1],fine[0],M])
        actual.append(float(np.linalg.norm(w1-w0,2)));bound.append(2*delta[0]+2*delta[1]+delta[2])
        maxunit=max(maxunit,float(np.linalg.norm(w1.conj().T@w1-np.eye(2),2)))
    record("common-space repeated-factor telescoping example",np.all(np.array(actual)<=np.array(bound)+2e-14) and maxunit<2e-14,
           {"epsilon_values":eps.tolist(),"dimension":2,"norm":"spectral operator norm","delta":"actual factor operator differences, not a lattice edge ratio",
            "maximum_unitarity_residual":maxunit,"max_defect_to_budget_ratio":float(max(np.array(actual)/bound)),"tolerance":2e-14})
    fig,ax=plt.subplots(figsize=(8.8,4.45),layout="constrained")
    ax.loglog(eps,actual,"o-",color=TEAL,label="actual seven-factor matrix difference")
    ax.loglog(eps,bound,"s--",color=GOLD,label=r"$2\delta_x+2\delta_y+\delta_z$")
    ax.set(xlabel="perturbation parameter ε",ylabel="operator norm / scalar budget",title="The two repeated directions each contribute twice")
    ax.legend(loc="upper left");grid(ax);save(fig,"09_full_walk_defect")

    # 10: exact line integral for A_y=sin x, all other coefficients zero.
    hh=2.**-np.arange(0,10);xx=np.linspace(-np.pi,np.pi,401)
    vals=np.abs(np.expm1(1j*hh[:,None]*(np.sin(xx[None,:]+hh[:,None])-np.sin(xx[None,:]))))
    maxgrid=vals.max(axis=1)
    exactmax=2*np.sin(hh*np.sin(hh/2))
    record("regular sinusoidal connection curvature envelope",np.all(vals<=hh[:,None]**2+2e-15)
           and np.all(maxgrid<=exactmax+2e-15),
           {"A":"A_y(x)=sin x, A_x=A_z=0","h_values":hh.tolist(),"x_samples":401,"x_interval":[-float(np.pi),float(np.pi)],
            "Omega":"exp(i h(sin(x+h)-sin x))","analytic_sup":"2 sin(h sin(h/2)) for 0<h<=1","tolerance":2e-15})
    fig,axs=plt.subplots(1,2,figsize=(9,4.4),layout="constrained")
    for k,col in zip([0,1,2],[TEAL,GOLD,LILAC]):axs[0].plot(xx,vals[k]/hh[k]**2,color=col,label=f"h = {hh[k]:g}")
    axs[0].axhline(1,color=INK,lw=1,ls=":");axs[0].set(xlabel="basepoint x",ylabel=r"$|\Omega_{xy}-1|/h^2$",ylim=(-.03,1.15),title="The bound is uniform in the basepoint")
    axs[0].legend(loc="upper center",bbox_to_anchor=(.5,1.02),ncol=3,fontsize=9)
    axs[1].loglog(hh,exactmax,"o-",color=TEAL,label="analytic supremum")
    axs[1].loglog(hh,hh**2,color=GOLD,ls="--",label=r"derivative bound $h^2$")
    axs[1].set(xlabel="spacing h",ylabel="face defect",title="Regularity supplies a quadratic envelope")
    axs[1].legend(loc="upper left",fontsize=9)
    for ax in axs:grid(ax)
    save(fig,"10_regular_connection")

    # 11: exact rational finite sums plus stated geometric-series tail.
    C=sp.Rational(3,2);N=9
    for n in range(N):
        finite=sum(C*sp.Rational(1,4)**k for k in range(n,N))
        tail=C*sp.Rational(4,3)*sp.Rational(1,4)**N
        record(f"dyadic tail decomposition n={n}",finite+tail==C*sp.Rational(4,3)*sp.Rational(1,4)**n,
               {"last_finite_level":N-1,"arithmetic":"exact rationals","scope":"Checks a finite decomposition of the supplied geometric-series formula."})
    nn=np.arange(9);budget=1.5*4.**-nn;tails=2.*4.**-nn
    fig,axs=plt.subplots(1,2,figsize=(9,4.4),layout="constrained")
    axs[0].semilogy(nn,budget,"o-",color=TEAL,label=r"one step: $C4^{-n}$")
    axs[0].semilogy(nn,tails,"s--",color=GOLD,label=r"remaining budget: $(4/3)C4^{-n}$")
    axs[0].set(xlabel="dyadic level n",ylabel="scalar budget",xticks=nn,title="Halving spacing quarters a quadratic bound")
    axs[0].legend(loc="upper right",fontsize=9);grid(axs[0])
    k=np.arange(5);heights=.75*4.**-k;axs[1].bar(k,heights,color=[TEAL,GOLD,LILAC,TEAL,GOLD],width=.65)
    axs[1].set(xticks=k,xticklabels=["n","n+1","n+2","n+3","n+4"],ylim=(0,.88),ylabel="fraction of the entire remaining budget",title="The first term accounts for three quarters")
    for j,h in enumerate(heights):axs[1].text(j,h+.025,f"{100*h:.2g}%",ha="center",fontsize=10)
    grid(axs[1]);save(fig,"11_dyadic_budget")

    # 12: parent-to-eight-child weighted normalization, exact arithmetic.
    coarse=sp.Matrix([2,-1+sp.I]);weights=sp.ones(8,1)/8
    mass_before=sp.simplify((coarse.H*coarse)[0])
    mass_after=sp.simplify(sum(weights[i]*(coarse.H*coarse)[0] for i in range(8)))
    unweighted_after=sp.simplify(sum(((coarse/sp.sqrt(8)).H*(coarse/sp.sqrt(8)))[0] for _ in range(8)))
    record("eight-child weighted isometry",mass_before==mass_after==unweighted_after==6,
           {"parent_volume":1,"child_volumes":["1/8"]*8,"parent_vector":"(2,-1+i)","weighted_child_value":"same vector on every child","unweighted_child_coordinate":"parent/sqrt8","arithmetic":"exact radicals"})
    fig=plt.figure(figsize=(9,4.65));fig.subplots_adjust(left=.02,right=.98,bottom=.06,top=.89,wspace=.15);ax=fig.add_subplot(121,projection="3d")
    occupied=np.ones((2,2,2),bool);colors=np.empty((2,2,2),dtype=object)
    for i in range(2):
        for j in range(2):
            for k in range(2):colors[i,j,k]=[TEAL,GOLD,LILAC][(i+j+k)%3]
    ax.voxels(occupied,facecolors=colors,edgecolor="white",alpha=.50,linewidth=1.2)
    ax.set(xlim=(0,2),ylim=(0,2),zlim=(0,2),xticks=[0,1,2],yticks=[0,1,2],zticks=[0,1,2],
           xticklabels=["0","½","1"],yticklabels=["0","½","1"],zticklabels=["0","½","1"],xlabel="x",ylabel="y",zlabel="z")
    ax.view_init(23,-57);ax.set_box_aspect((1,1,1));ax.set_title("Eight child cubes fill one parent cube")
    ax=fig.add_subplot(122);ax.axis("off");ax.set(xlim=(0,1),ylim=(0,1))
    for y,title,formula,col in [(.81,"Volume-weighted cell values",r"$\sum_{j=1}^{8}\frac{1}{8}\|v\|^2=\|v\|^2$",TEAL),(.42,"Unweighted coefficient coordinates",r"$\sum_{j=1}^{8}\|v/\sqrt{8}\|^2=\|v\|^2$",GOLD)]:
        ax.text(.5,y,title,ha="center",color=col,fontsize=12);ax.text(.5,y-.15,formula,ha="center",fontsize=17)
    ax.text(.5,.055,"The normalization belongs to the chosen representation.",ha="center",fontsize=10,color=MUTED)
    ax.set_title("Cell volume and amplitude normalization agree")
    save(fig,"12_weighted_cells")
    record("complete plate inventory",len(outputs)==24,"Twelve PDF plates and twelve PNG previews; all input families deterministic.")

def write_manifest(status,exit_status,error=None):
    code=Path(__file__).resolve();codepath=str(code.relative_to(ROOT));after=hashlib.sha256(code.read_bytes()).hexdigest()
    manifest={"schema_version":2,"claim_id":"physics-gauge-atlas-bounded-examples-v0.3.0",
      "repository":{"commit":"not applicable: standalone recovered publication staging directory","dirty":True},
      "command":[sys.executable,"tools/make_gauge_figures.py"],
      "environment":{"software":[{"name":"Python","version":platform.python_version()},
        {"name":"NumPy","version":np.__version__},{"name":"SciPy","version":scipy.__version__},
        {"name":"SymPy","version":sp.__version__},{"name":"Matplotlib","version":matplotlib.__version__}],"hardware":platform.machine()},
      "mathematics":{"assertion_tested":"The explicitly displayed finite link, matrix, walk, phase and volume examples satisfy the exact identities and tolerance checks stated in this record.",
        "coefficient_domain":"Exact rational and Gaussian rational SymPy matrices; exact radicals for weighted normalization; IEEE double/complex128 for numerical plots.",
        "conventions":"Column states; backward U_xy:H_y to H_x, U'=g_x U g_y^-1; forward u=U^-1, u'=g_y u g_x^-1; operator composition acts right to left; Frobenius norm only where labeled, spectral norm in the full-walk surrogate.",
        "inputs":[{"path":codepath,"sha256":INPUT_HASH}],
        "bounds":{"finite_matrix_dimension":2,"plaquette_grid_cells":[2,2],"periodic_walk_sites":6,
          "BCH_h":"2^-2 through 2^-9, with half-spacing values for Richardson","regular_h":"2^0 through 2^-9",
          "regular_basepoint_samples":401,"full_walk_epsilon":"2^-2 through 2^-10","dyadic_display_levels":[0,8],
          "resource_policy":"No external network, no random sampling, no Lean invocation; small fixed arrays. Wall time recorded; no OS memory or CPU caps requested."},
        "non_claims":["Finite computations do not prove the universal covariance or refinement theorems.",
          "The two-dimensional full-walk matrices are a common-space telescoping surrogate, not the formal Clifford lattice implementation.",
          "The five-face diagram tests its face inventory only; it is not a numerical operator proof.",
          "A plotted slope does not establish the BCH expansion or select a universal logarithm branch.",
          "The weighted-cell example is finite and does not identify an arbitrary transported Euclidean subspace with ordinary dyadic-box functions.",
          "No new Lean build, coupled gauge evolution, or empirical prediction is produced."]},
      "randomness":{"used":False,"generator":"none","seed":None},
      "run":{"started_at":STAMP,"runtime_seconds":time.monotonic()-START,"exit_status":exit_status,"status":status,
             "resource_limits":{"memory_bytes":None,"cpu_seconds":None,"max_cores":None,"max_threads":None}},
      "input_artifacts":[{"path":codepath,"sha256":INPUT_HASH,"sha256_after":after}],"execution_artifacts":[codepath],
      "declared_results":[f"source/gauge_figures/{stem}.{ext}" for stem in ["01_link_covariance","02_abelian_plaquette","03_nonabelian_order","04_ordered_refinement","05_curvature_richardson","06_walk_continuity","07_edge_subdivision","08_five_face_budget","09_full_walk_defect","10_regular_connection","11_dyadic_budget","12_weighted_cells"] for ext in ["pdf","png"]],
      "outputs":outputs,"checks":checks,
      "result":"Implementation and finite assertions verified in the stated ranges, conditional on the declared floating tolerances." if status=="completed" else f"Run failed: {error}",
      "residual_risks":["Floating matrix exponentials, logarithms, norms and trigonometric values are not interval-certified.","Exact symbolic identities rely on SymPy; they are not proof-assistant receipts.","The script and this run record are reviewed publication support, not independent reimplementations of every formal theorem."]}
    name="figure_checks.json" if status=="completed" else "figure_failed_"+STAMP.replace(":","-")+".json"
    (EVID/name).write_text(json.dumps(manifest,indent=2)+"\n")
    history=EVID/"figure_run_history.jsonl"
    with history.open("a") as f:f.write(json.dumps({"started_at":STAMP,"status":status,"exit_status":exit_status,"input_sha256":INPUT_HASH,"manifest":name,"error":error})+"\n")
    return manifest

if __name__=="__main__":
    try:
        make_figures()
    except Exception as exc:
        write_manifest("failed",1,str(exc));traceback.print_exc();sys.exit(1)
    manifest=write_manifest("completed",0)
    print(json.dumps({"figures":12,"checks":len(checks),"all_passed":True,"runtime_seconds":manifest["run"]["runtime_seconds"]},indent=2))
