#!/usr/bin/env python3
"""Twelve bounded scientific illustrations for the gravity atlas.

Run from the edition root: python tools/make_gravity_figures.py
No Lean, Einstein evolution, external data fetch, or random sampling is run.
The particle computation is a finite constrained-mechanics surrogate.
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
from scipy.special import j0, j1
from scipy.optimize import root
import sympy as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"source/gravity_figures"
EVID=ROOT/"evidence/gravity"
DATA=EVID/"inputs/archived_scalar_event_data.json"
OUT.mkdir(parents=True,exist_ok=True)
EVID.mkdir(parents=True,exist_ok=True)
START=time.monotonic()
STAMP=dt.datetime.now(dt.timezone.utc).isoformat()
INPUTS=[Path(__file__).resolve(),DATA]
HASHES={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}
TEAL,GOLD,LILAC="#245D60","#AD7842","#7C738E"
INK,MUTED,PALE="#212B34","#58646B","#EEF3F2"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,
 "axes.labelsize":11,"axes.titlesize":12,"axes.titlepad":13,
 "axes.labelcolor":INK,"text.color":INK,"axes.edgecolor":"#ADBAB9",
 "xtick.color":MUTED,"ytick.color":MUTED,"axes.spines.top":False,
 "axes.spines.right":False,"legend.frameon":False,"legend.fontsize":9,
 "lines.linewidth":2.1,"figure.facecolor":"white","axes.facecolor":"white",
 "savefig.facecolor":"white","pdf.fonttype":42,"ps.fonttype":42,
 "mathtext.fontset":"dejavusans"})
checks,outputs=[],[]
STEMS=["01_local_energy_work","02_conformal_curvature","03_gowdy_mode",
 "04_adm_dispersion","05_nonlinear_defect","06_regular_patch",
 "07_dirac_projection","08_discrete_gradient","09_quasienergy_branch",
 "10_electrovac_horizons","11_scalar_flux","12_trapped_refinement"]

def record(name,passed,detail):
    checks.append({"name":name,"passed":bool(passed),"detail":detail})
    if not passed: raise AssertionError(f"{name}: {detail}")

def save(fig,name):
    for ext in ("pdf","png"):
        buffer=io.BytesIO()
        metadata={"Creator":"Komorebi gravity Python figure generator"}
        if ext=="pdf":metadata.update({"CreationDate":None,"ModDate":None})
        fig.savefig(buffer,format=ext,dpi=190,bbox_inches="tight",pad_inches=.18,metadata=metadata)
        path=OUT/f"{name}.{ext}"
        temporary=path.with_name(path.name+".tmp")
        temporary.write_bytes(buffer.getvalue());temporary.replace(path)
        outputs.append({"path":str(path.relative_to(ROOT)),"kind":"result",
                        "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)

def grid(ax):
    ax.grid(True,color="#DDE5E3",linewidth=.65,alpha=.8);ax.set_axisbelow(True)

def pair():return plt.subplots(1,2,figsize=(9,4.5),layout="constrained")
def centered(f,h):return (np.roll(f,-1)-np.roll(f,1))/(2*h)
def floatvec(v):return np.array(v,dtype=float).ravel()
def canonical(n):return np.block([[np.zeros((n,n)),np.eye(n)],[-np.eye(n),np.zeros((n,n))]])
J6=canonical(3)
LAM=.2
def H(z):return .5*z[3:]@z[3:]+LAM*np.sum(z[:3]**4)/4
def phi(z):return np.array([z[:3]@z[:3]-1,z[:3]@z[3:]])
def dgH(a,b):
    q0,q1=a[:3],b[:3]
    return np.r_[LAM*(q1**3+q1**2*q0+q1*q0**2+q0**3)/4,(a[3:]+b[3:])/2]
def dgPhi(a,b):return np.vstack([np.r_[a[:3]+b[:3],np.zeros(3)],np.r_[(a[3:]+b[3:])/2,(a[:3]+b[:3])/2]])
def jd(a,b):
    G=dgPhi(a,b);C=G@J6@G.T
    return J6-J6@G.T@np.linalg.solve(C,G@J6)
def step_residual(a,b,h):return b-a-h*jd(a,b)@dgH(a,b)

def make_figures():
    # 01. Exact rational local energy/work identity, six periodic cells.
    R=sp.Rational;N=6;h=R(1,2)
    q=list(map(R,[1,2,-1,0,1,-2]));vel=[R(1,3),R(-1,2),R(2,5),R(1,4),R(-1,3),R(1,5)]
    w=[1+R(j,10) for j in range(N)];c=[1+R(j%3,5) for j in range(N)];vp=[R(1,3)]*N
    wd=[R((-1)**j,20) for j in range(N)];cd=[R(j-2,40) for j in range(N)];vd=[R(1,30)]*N
    dq=[q[(j+1)%N]-q[j] for j in range(N)]
    acc=[((c[j]*dq[j]-c[j-1]*dq[j-1])/h**2-vp[j]*q[j]-wd[j]*vel[j])/w[j] for j in range(N)]
    flux=[-c[j]*dq[j]*(vel[j]+vel[(j+1)%N])/(2*h) for j in range(N)]
    source=[-h*wd[j]*vel[j]**2/2+h*vd[j]*q[j]**2/2+(cd[j]*dq[j]**2+cd[j-1]*dq[j-1]**2)/(4*h) for j in range(N)]
    edot=[h*wd[j]*vel[j]**2/2+h*w[j]*vel[j]*acc[j]+h*vd[j]*q[j]**2/2+h*vp[j]*q[j]*vel[j]
      +(cd[j]*dq[j]**2+cd[j-1]*dq[j-1]**2)/(4*h)
      +(c[j]*dq[j]*(vel[(j+1)%N]-vel[j])+c[j-1]*dq[j-1]*(vel[j]-vel[j-1]))/(2*h) for j in range(N)]
    local=[sp.simplify(edot[j]+flux[j]-flux[j-1]-source[j]) for j in range(N)]
    record("exact finite metric local energy/work balance",all(x==0 for x in local),
      {"sites":6,"h":"1/2","q":list(map(str,q)),"velocity":list(map(str,vel)),"w_j":"1+j/10","c_j":"1+(j mod 3)/5","v_j":"1/3","w_dot_j":"(-1)^j/20","c_dot_j":"(j-2)/40","v_dot_j":"1/30","residuals":list(map(str,local))})
    record("exact global geometric work",sp.simplify(sum(edot)-sum(source))==0,{"energy_derivative":str(sum(edot)),"work":str(sum(source)),"periodic_fluxes":"telescope exactly"})
    fig,axs=pair();jj=np.arange(N)
    axs[0].plot(jj,floatvec(flux),"o-",color=TEAL,label="edge flux F")
    axs[0].bar(jj,floatvec(source),color=GOLD,alpha=.65,label="cell geometric work s")
    axs[0].set(xlabel="cell / outgoing edge j",ylabel="dimensionless rate",title="A varying metric does work on the field");axs[0].legend();grid(axs[0])
    incoming=np.array([float(flux[j-1]-flux[j]) for j in range(N)])
    axs[1].plot(jj,floatvec(edot),"o-",color=TEAL,label="direct energy derivative")
    axs[1].plot(jj,incoming+floatvec(source),"x",color=GOLD,ms=9,label="incoming minus outgoing + work")
    axs[1].set(xlabel="cell j",ylabel="dimensionless energy derivative",title="Local balances agree cell by cell");axs[1].legend();grid(axs[1]);save(fig,STEMS[0])

    # 02. Exact conformal Lorentzian curvature, a true 3D scalar-field graph.
    t,x=sp.symbols("t x",real=True);a=R(3,10);ph=a*(t*t-x*x)/2
    f=sp.diff(ph,t,2)-sp.diff(ph,x,2)
    boundary=sp.integrate(-a*(-R(1,2)),(t,0,1))+sp.integrate(a,(x,-R(1,2),R(1,2)))+sp.integrate(-a*R(1,2),(t,1,0))
    area=sp.integrate(f,(t,0,1),(x,-R(1,2),R(1,2)))
    record("exact conformal rectangular holonomy rapidity",sp.simplify(boundary-area)==0 and area==R(3,5),
      {"phi":"3(t^2-x^2)/20","rectangle":"t in [0,1], x in [-1/2,1/2]","orientation":"dt wedge dx positive","signed_edge_convention":"exp(+integral omega); Cartan D=d+omega parallel transport uses the inverse loop","boundary_rapidity":str(boundary),"area_rapidity":str(area),"curvature":"R=6 exp(-2phi)/5"})
    fig=plt.figure(figsize=(9,4.6));ax=fig.add_subplot(121,projection="3d")
    T,X=np.meshgrid(np.linspace(0,1,41),np.linspace(-1,1,51));RR=1.2*np.exp(-.3*(T*T-X*X))
    ax.plot_surface(T,X,RR,cmap="viridis",rstride=1,cstride=1,linewidth=0,alpha=.88)
    ax.set(xlabel="t",ylabel="x",zlabel="scalar curvature R",title="Conformal curvature as a scalar graph")
    ax.view_init(24,-54);ax.set_box_aspect((1,1,.7))
    ax=fig.add_subplot(122);tt=np.linspace(0,1,101)
    ax.plot(tt,.6*tt,color=TEAL,label=r"rapidity $\chi=0.6\,\Delta t$")
    ax.plot(tt,np.sinh(.6*tt),color=GOLD,label=r"boost entry $\sinh\chi$")
    ax.plot(tt,np.cosh(.6*tt)-1,color=LILAC,label=r"boost entry $\cosh\chi-1$")
    ax.set(xlabel="cell height Δt (width = 1)",ylabel="rapidity / boost entry",title="Curvature integrates into a finite boost");ax.legend();grid(ax);fig.subplots_adjust(wspace=.3,left=.01,right=.98,bottom=.15,top=.86);save(fig,STEMS[1])

    # 03. Polarized exact Gowdy mode and a bounded centered residual study.
    A=.3;n=2;tau=.7;xx=n*np.exp(-tau);JJ0,JJ1=j0(xx),j1(xx)
    NN=np.array([32,64,128,256,512]);errs=[]
    for N in NN:
        theta=np.arange(N)*2*np.pi/N;hh=2*np.pi/N
        lt=A*A*xx*xx*(JJ1**2*np.cos(n*theta)**2+JJ0**2*np.sin(n*theta)**2)
        analytic=A*A*n*xx*xx*(JJ0**2-JJ1**2)*np.sin(2*n*theta)
        errs.append(np.max(np.abs(analytic-centered(lt,hh))))
    slope=np.log2(errs[-2]/errs[-1]);record("polarized Gowdy centered compatibility refinement",1.99<slope<2.01,
      {"A":A,"n":n,"tau":tau,"N":NN.tolist(),"residual_max":errs,"last_pair_order":slope,"test":"analytic tau derivative of lambda_theta minus centered theta derivative of lambda_tau"})
    th=np.linspace(0,2*np.pi,401);mom=-A*A*n*xx*JJ0*JJ1*np.sin(2*n*th)
    record("polarized periodic momentum benchmark",abs(np.trapezoid(mom,th))<1e-15,{"401_sample_trapezoid":float(np.trapezoid(mom,th)),"exact_reason":"integral of sin(2n theta) is zero for integer n","tolerance":1e-15})
    fig,axs=pair();TH,TAU=np.meshgrid(np.linspace(0,2*np.pi,201),np.linspace(0,2.5,101));P=A*j0(n*np.exp(-TAU))*np.cos(n*TH)
    im=axs[0].pcolormesh(TH,TAU,P,cmap="RdBu_r",shading="auto",vmin=-A,vmax=A);fig.colorbar(im,ax=axs[0],label="P(τ, θ)",shrink=.8)
    axs[0].set(xlabel="θ",ylabel="τ",title="An exact polarized gravitational mode")
    hh=2*np.pi/NN;axs[1].loglog(hh,errs,"o-",color=TEAL,label="compatibility residual")
    axs[1].loglog(hh,errs[-1]*(hh/hh[-1])**2,"--",color=GOLD,label="second-order reference")
    axs[1].set(xlabel="angular spacing h",ylabel="maximum residual",title="Finite differences approach integrability");axs[1].legend();grid(axs[1]);save(fig,STEMS[2])

    # 04. Centered ADM dispersion and checkerboard null modes.
    kh=np.linspace(0,np.pi,401);sym=np.sin(kh)
    record("centered derivative Nyquist null benchmark",abs(sym[-1])<2e-15 and abs(sym[0])<2e-15,{"dimensionless_symbol":"sin(kh)","kh_samples":401,"Nyquist":"kh=pi","tolerance":2e-15})
    k=np.array([1.,2.,.5]);hhs=2.**-np.arange(2,11);E=np.linalg.norm(k);wh=np.linalg.norm(np.sin(hhs[:,None]*k)/hhs[:,None],axis=1);error=E-wh
    s=np.log2(error[-2]/error[-1]);record("ADM fixed-mode dispersion refinement",1.999<s<2.001,{"k":k.tolist(),"h":hhs.tolist(),"omega_h":wh.tolist(),"last_pair_order":s})
    fig,axs=pair();axs[0].plot(kh,sym,color=TEAL,label="centered |sin(kh)|")
    axs[0].plot(kh,kh,"--",color=GOLD,label="continuum |kh|");axs[0].plot([np.pi],[0],"o",color=LILAC,ms=8)
    axs[0].set(xlabel="dimensionless wave number kh",ylabel="dimensionless frequency hω",title="Nyquist can be a zero of a centered derivative",xticks=[0,np.pi/2,np.pi],xticklabels=["0","π/2","π"]);axs[0].legend(loc="upper left");grid(axs[0])
    axs[1].loglog(hhs,error,"o-",color=TEAL,label="E − ωh")
    ref=hhs**2*np.sum(k**4)/(6*E);axs[1].loglog(hhs,ref,"--",color=GOLD,label="leading h² term")
    axs[1].set(xlabel="spacing h",ylabel="frequency error",title="A fixed resolved mode has second-order error");axs[1].legend();grid(axs[1]);save(fig,STEMS[3])

    # 05. Exact bracket counterexample and smooth centered product-rule defect.
    N=5;D=sp.zeros(N)
    for j in range(N):D[j,(j+1)%N]=R(1,2);D[j,(j-1)%N]=-R(1,2)
    basis=[sp.eye(N)[:,j] for j in range(N)];q,p,xi,eta=basis[0],basis[1],basis[1],basis[2]
    mul=lambda f,g:sp.Matrix([f[j]*g[j] for j in range(N)])
    actual=sum(p[j]*(xi[j]*(D*mul(eta,D*q))[j]-eta[j]*(D*mul(xi,D*q))[j]) for j in range(N))
    closure=sum(p[j]*(xi[j]*(D*eta)[j]-eta[j]*(D*xi)[j])*(D*q)[j] for j in range(N))
    record("exact finite pointwise nonlinear bracket failure",actual==0 and closure==-R(1,4),{"N":5,"h":1,"q":"e0","p=xi":"e1","eta":"e2","actual_bracket":str(actual),"naive_closed_rhs":str(closure),"defect":str(actual-closure),"arithmetic":"rationals"})
    Ns=2**np.arange(5,11);le=[]
    for N in Ns:
        hh=2*np.pi/N;xx=np.arange(N)*hh;f=np.sin(xx);g=np.cos(2*xx)
        le.append(np.max(np.abs(centered(f*g,hh)-centered(f,hh)*g-f*centered(g,hh))))
    s=np.log2(le[-2]/le[-1]);record("smooth centered Leibniz defect refinement",1.99<s<2.01,{"f":"sin x","g":"cos 2x","N":Ns.tolist(),"max_defect":le,"last_pair_order":s})
    K=sp.Matrix([[1,R(1,3)],[R(1,3),-2]]);X=sp.Matrix([[1,2],[0,-1]]);Y=sp.Matrix([[0,1],[3,2]])
    deriv=lambda Z:sp.I*(K*Z-Z*K)
    record("exact inner-derivation product rule",deriv(X*Y)-deriv(X)*Y-X*deriv(Y)==sp.zeros(2),{"K":"[[1,1/3],[1/3,-2]]","X":"[[1,2],[0,-1]]","Y":"[[0,1],[3,2]]","arithmetic":"Gaussian rationals"})
    fig,axs=pair();axs[0].bar([0,1,2],[float(actual),float(closure),float(actual-closure)],color=[TEAL,GOLD,LILAC]);axs[0].axhline(0,color=INK,lw=.7)
    axs[0].set(xticks=[0,1,2],xticklabels=["actual bracket","naive RHS","defect"],ylabel="exact finite value",title="A five-site counterexample exposes the defect");grid(axs[0])
    hh=2*np.pi/Ns;axs[1].loglog(hh,le,"o-",color=TEAL,label="centered Leibniz defect");axs[1].loglog(hh,le[-1]*(hh/hh[-1])**2,"--",color=GOLD,label="second-order reference")
    axs[1].set(xlabel="spacing h",ylabel="maximum defect",title="Small smooth-data errors do not give closure");axs[1].legend();grid(axs[1]);save(fig,STEMS[4])

    # 06. Two separate regularity boundaries; no identification of the models.
    rho=np.geomspace(.03,1,301);G=sp.Matrix([[2,0,0,0,0,0],[0,1,0,1,0,0]])
    rr=sp.symbols("rho",positive=True);GG=sp.Matrix([[2*rr,0,0,0,0,0],[0,1,0,rr,0,0]])
    JJ=sp.Matrix(canonical(3).astype(int));CC=GG*JJ*GG.T
    record("exact particle regularity matrix",CC==sp.Matrix([[0,2*rr**2],[-2*rr**2,0]]),{"q":"(rho,0,0)","p":"(0,1,0)","constraints":"q.q-1 and q.p","smallest_singular_value":"2 rho^2","scope":"off-surface rank diagnostic; rho=1 is the unit constraint surface"})
    fig,axs=pair();axs[0].loglog(rho,rho,color=TEAL,label=r"fermionic primary magnitude $e$");axs[0].loglog(rho,1/rho,color=GOLD,label=r"inverse magnitude $1/e$")
    axs[0].set(xlabel="positive triad determinant e",ylabel="scaled magnitude",title="The physical reduction excludes e = 0");axs[0].legend();grid(axs[0])
    axs[1].loglog(rho,2*rho**2,color=TEAL,label=r"particle $\sigma_{\min}(\Delta)$")
    axs[1].loglog(rho,1/(2*rho**2),color=GOLD,label=r"particle $\|\Delta^{-1}\|_2$")
    axs[1].set(xlabel="particle configuration radius ρ",ylabel="matrix scale",title="A separate toy inverse also becomes singular");axs[1].legend();grid(axs[1]);save(fig,STEMS[5])

    # 07. Exact rational Dirac tensor and genuine tangent geometry.
    q=sp.Matrix([R(3,5),R(4,5),0]);p=sp.Matrix([-R(4,5),R(3,5),R(1,2)])
    G=sp.Matrix.vstack(sp.Matrix([list(2*q)+[0,0,0]]),sp.Matrix([list(p)+list(q)]))
    CC=G*JJ*G.T;JD=sp.simplify(JJ-JJ*G.T*CC.inv()*G*JJ)
    record("exact rational Dirac skewness, annihilation and rank",JD.T==-JD and G*JD==sp.zeros(2,6) and JD.rank()==4,
      {"q":[str(x) for x in q],"p":[str(x) for x in p],"q_squared":str((q.T*q)[0]),"q_dot_p":str((q.T*p)[0]),"rank":JD.rank(),"arithmetic":"rationals"})
    fig=plt.figure(figsize=(9,4.6));ax=fig.add_subplot(121,projection="3d")
    phis,thetas=np.meshgrid(np.linspace(0,2*np.pi,45),np.linspace(0,np.pi,25));SX=np.sin(thetas)*np.cos(phis);SY=np.sin(thetas)*np.sin(phis);SZ=np.cos(thetas)
    ax.plot_surface(SX,SY,SZ,color=TEAL,alpha=.14,linewidth=.25,edgecolor="#C0D0CE")
    qq=floatvec(q);pp=floatvec(p);ax.scatter(*qq,color=GOLD,s=45);ax.quiver(*qq,*(.55*pp),color=GOLD,linewidth=2,arrow_length_ratio=.18)
    ax.quiver(*qq,*(.4*qq),color=LILAC,linewidth=2,arrow_length_ratio=.18)
    ax.set(xlabel="q₁",ylabel="q₂",zlabel="q₃",title="Tangent momentum satisfies q · p = 0",xlim=(-1.1,1.2),ylim=(-1.1,1.5),zlim=(-1.1,1.1));ax.view_init(22,-64);ax.set_box_aspect((1,1,1))
    ax=fig.add_subplot(122);im=ax.imshow(np.array(JD,float),cmap="RdBu_r",vmin=-1,vmax=1);fig.colorbar(im,ax=ax,label="Dirac tensor entry",shrink=.75)
    ax.set(xticks=np.arange(6),yticks=np.arange(6),xticklabels=["q₁","q₂","q₃","p₁","p₂","p₃"],yticklabels=["q₁","q₂","q₃","p₁","p₂","p₃"],title="Two constraint gradients are annihilated")
    fig.subplots_adjust(left=.01,right=.98,bottom=.12,top=.87,wspace=.30);save(fig,STEMS[6])

    # 08. Fresh bounded constrained particle run, with a one-Newton-step control.
    z0=np.array([1.,0,0,0,.7,.2]);z=z0.copy();zc=z0.copy();hh=.1;steps=1000
    EH=[];EC=[];IH=[];IC=[];RES=[];CRES=[];MIN=[];NF=[]
    for step in range(steps):
        predictor=z+hh*jd(z,z)@dgH(z,z)
        sol=root(lambda b:step_residual(z,b,hh),predictor,method="hybr",tol=1e-11)
        res=float(np.linalg.norm(step_residual(z,sol.x,hh)))
        if not sol.success or res>1e-9:raise RuntimeError(f"particle implicit solve at step {step}: {sol.message}; residual {res}")
        G=dgPhi(z,sol.x);MIN.append(float(np.linalg.svd(G@J6@G.T,compute_uv=False)[-1]));z=sol.x
        EH.append(abs(H(z)-H(z0)));EC.append(float(np.max(abs(phi(z)))));RES.append(res);NF.append(sol.nfev)
        guess=zc+hh*jd(zc,zc)@dgH(zc,zc);eps=1e-6
        jac=np.column_stack([(step_residual(zc,guess+eps*np.eye(6)[j],hh)-step_residual(zc,guess-eps*np.eye(6)[j],hh))/(2*eps) for j in range(6)])
        guess=guess-np.linalg.solve(jac,step_residual(zc,guess,hh));CRES.append(float(np.linalg.norm(step_residual(zc,guess,hh))));zc=guess
        IH.append(abs(H(zc)-H(z0)));IC.append(float(np.max(abs(phi(zc)))))
    record("bounded particle discrete-gradient solve",max(EH)<1e-10 and max(EC)<1e-10 and max(RES)<1e-9 and min(MIN)>1,
      {"z0":z0.tolist(),"lambda":LAM,"dt":hh,"steps":steps,"H0":float(H(z0)),"max_energy_error":max(EH),"max_constraint_error":max(EC),"max_step_residual":max(RES),"min_endpoint_Dirac_singular_value":min(MIN),"max_function_evaluations":max(map(int,NF)),"tolerances":{"energy":1e-10,"constraint":1e-10,"solve":1e-9},"scope":"finite quartic particle surrogate, not gravity evolution"})
    record("one-Newton-step preservation negative control",max(IH)>100*max(EH) and max(IC)>100*max(EC) and max(CRES)>100*max(RES),
      {"max_energy_error":max(IH),"max_constraint_error":max(IC),"max_step_residual":max(CRES),"one_iteration":"central finite-difference Newton Jacobian epsilon 1e-6; no exact solve claimed"})
    record("exact quartic AVF chain rule",all(sp.expand((b**4-a**4)-(a**3+a*a*b+a*b*b+b**3)*(b-a))==0 for a,b in [(sp.Symbol("a"),sp.Symbol("b"))]),"Polynomial difference identity, independent of the implicit numerical solve.")
    fig,axs=pair();times=hh*np.arange(1,steps+1)
    axs[0].semilogy(times,np.maximum(EH,1e-17),color=TEAL,label="resolved energy error");axs[0].semilogy(times,np.maximum(EC,1e-17),color=LILAC,label="resolved constraint error")
    axs[0].semilogy(times,np.maximum(IH,1e-17),color=GOLD,label="one-Newton energy error");axs[0].semilogy(times,np.maximum(IC,1e-17),color=GOLD,ls="--",label="one-Newton constraint error")
    axs[0].set(xlabel="particle time",ylabel="absolute invariant error",title="Solving the implicit equation matters");axs[0].legend(fontsize=8);grid(axs[0])
    axs[1].semilogy(times,np.maximum(RES,1e-17),color=TEAL,label="resolved step residual");axs[1].semilogy(times,np.maximum(CRES,1e-17),color=GOLD,label="one-Newton step residual")
    axs[1].set(xlabel="particle time",ylabel="Euclidean residual norm",title="The conservation proof uses a zero residual");axs[1].legend();grid(axs[1]);save(fig,STEMS[7])

    # 09. A principal branch of the source's product-cosine model.
    d=.4;xx=np.linspace(-.99*np.pi/(2*d),.99*np.pi/(2*d),501)
    KK=np.sign(xx)*np.sqrt(-2*np.log(np.cos(d*xx)))/d
    back=np.sign(KK)*np.arccos(np.exp(-d*d*KK*KK/2))/d
    record("principal phase coordinate finite inverse",np.max(abs(back-xx))<2e-12 and np.all(np.diff(KK)>0),{"Delta":d,"501_inputs_interval":[float(xx[0]),float(xx[-1])],"max_inverse_residual":float(np.max(abs(back-xx))),"tolerance":2e-12,"exclusions":"cosine zeros and all other branches"})
    momenta=np.linspace(0,2,401);m=.7;kx=momenta;ky=.4;kz=.2
    energy=np.sqrt(m*m+kx*kx+ky*ky+kz*kz);omega=np.arccos(np.cos(d*m)*np.cos(d*kx)*np.cos(d*ky)*np.cos(d*kz))/d
    K=lambda x:np.sqrt(-2*np.log(np.cos(d*x)))/d
    residual=K(omega)**2-K(kx)**2-K(ky)**2-K(kz)**2-K(m)**2
    record("product-cosine model principal shell finite check",np.max(abs(residual))<5e-14 and np.all(omega<=energy+1e-14),{"m":m,"ky":ky,"kz":kz,"kx_range":[0,2],"samples":401,"Delta":d,"max_shell_residual":float(np.max(abs(residual))),"tolerance":5e-14,"model_status":"free product-cosine ansatz; no gravitational or empirical identification"})
    fig,axs=pair();axs[0].plot(xx,KK,color=TEAL,label="KΔ(x)");axs[0].plot(xx,xx,"--",color=GOLD,label="identity")
    for side in [-1,1]:axs[0].axvline(side*np.pi/(2*d),color=LILAC,lw=1,ls=":")
    axs[0].set(xlabel="phase coordinate x",ylabel="principal transformed coordinate",title="The map approaches a branch boundary");axs[0].legend();grid(axs[0])
    axs[1].plot(momenta,energy,"--",color=GOLD,label="continuum E");axs[1].plot(momenta,omega,color=TEAL,label="model quasienergy ωΔ")
    axs[1].set(xlabel="kx",ylabel="positive frequency",title="An exact shell can still be a model choice");axs[1].legend();grid(axs[1]);save(fig,STEMS[8])

    # 10. RN horizons and PG reality boundary in units M=1.
    RR=np.linspace(.25,4,601);charges=[.8,1.,1.1]
    rplus=1+np.sqrt(1-.8**2);rminus=1-np.sqrt(1-.8**2)
    F=lambda r,q:1-2/r+q*q/r**2
    record("RN horizon polynomial benchmarks",abs(F(rplus,.8))<1e-14 and abs(F(rminus,.8))<1e-14 and F(1,1)==0 and 1-1.1**2<0,
      {"M":1,"charges":charges,"subextremal_horizons":[rminus,rplus],"extremal_horizon":1,"superextremal_discriminant":1-1.1**2,"PG_reality_bound":"R>=Q^2/(2M)","tolerance":1e-14})
    fig,axs=pair()
    for Q,col,label in zip(charges,[TEAL,GOLD,LILAC],["Q/M = 0.8","Q/M = 1.0","Q/M = 1.1"]):axs[0].plot(RR,F(RR,Q),color=col,label=label)
    axs[0].axhline(0,color=INK,lw=.8);axs[0].plot([rminus,rplus],[0,0],"o",color=TEAL)
    axs[0].set(xlabel="areal radius R / M",ylabel="F = 1 − 2M/R + Q²/R²",ylim=(-1.6,2),title="Horizons are roots of the invariant F");axs[0].legend();grid(axs[0])
    rp=np.linspace(.8**2/2,4,601);v=np.sqrt(np.maximum(2/rp-.8**2/rp**2,0))
    axs[1].plot(rp,1-v,color=TEAL,label="outgoing speed 1 − v");axs[1].plot(rp,-1-v,color=GOLD,label="ingoing speed −1 − v")
    axs[1].axvspan(0,.8**2/2,color=LILAC,alpha=.13,label="PG radicand < 0");axs[1].axhline(0,color=INK,lw=.8)
    for r in [rminus,rplus]:axs[1].axvline(r,color=MUTED,lw=.8,ls=":")
    axs[1].set(xlabel="R / M",ylabel="radial coordinate speed",xlim=(0,4),title="The horizons are regular in the PG chart");axs[1].legend(fontsize=8);grid(axs[1]);save(fig,STEMS[9])

    # 11. Exact scalar energy/flux diagonalization into null channels.
    Pi,Phi,v,sig=sp.symbols("Pi Phi v sigma",real=True);wp=Pi+Phi;wm=Pi-Phi
    ee=(Pi**2+Phi**2)/2+v*Pi*Phi;jj=sig*(Pi+v*Phi)*(Phi+v*Pi)
    en=(1+v)*wp**2/4+(1-v)*wm**2/4;jn=sig*((1+v)**2*wp**2-(1-v)**2*wm**2)/4
    record("exact scalar null-channel energy and flux",sp.expand(ee-en)==0 and sp.expand(jj-jn)==0,
      {"energy":"E=(1+v) w_plus^2/4+(1-v) w_minus^2/4","flux":"J=sigma[(1+v)^2 w_plus^2-(1-v)^2 w_minus^2]/4","normalization":"G=c=1, varphi=sqrt(4pi) phi_phys","scope":"pointwise identities, no evolved scalar field"})
    vv=np.linspace(0,1.5,301);fig,axs=pair();axs[0].plot(vv,(1+vv)/4,color=TEAL,label="w+ channel coefficient");axs[0].plot(vv,(1-vv)/4,color=GOLD,label="w− channel coefficient")
    axs[0].axvline(1,color=MUTED,lw=1,ls=":");axs[0].axhline(0,color=INK,lw=.7);axs[0].set(xlabel="PG flow v",ylabel="coefficient in mass-density E",title="The mass-density form loses positivity at v = 1");axs[0].legend();grid(axs[0])
    axs[1].plot(vv,(1+vv)**2/4,color=TEAL,label="unit w+ channel");axs[1].plot(vv,-(1-vv)**2/4,color=GOLD,label="unit w− channel")
    axs[1].axvline(1,color=MUTED,lw=1,ls=":");axs[1].axhline(0,color=INK,lw=.7);axs[1].set(xlabel="PG flow v (σ = 1)",ylabel="signed mass flux J",title="Flux signs follow the chosen mass convention");axs[1].legend();grid(axs[1]);save(fig,STEMS[10])

    # 12. Archived event table, never relabeled as a new collapse run.
    data=json.loads(DATA.read_text());events=data["convergence"]
    hs=np.array([e["h"] for e in events]);ts=np.array([e["horizon_time"] for e in events]);rs=np.array([e["horizon_radius"] for e in events])
    record("archived scalar horizon table internal identities",len(events)==7 and all(abs(e["horizon_mass"]-e["horizon_radius"]/2)<1e-14 for e in events)
      and all(abs((e["event_adm_mass"]-e["initial_adm_mass"])/e["initial_adm_mass"]-e["mass_change_fraction"])<1e-14 for e in events),
      {"source":"archived_scalar_event_data.json","event_count":len(events),"node_counts":[e["node_count"] for e in events],"identities":"m_H=r_H/2; mass-change fraction recomputed from stored outer masses","tolerance":1e-14,"not_done":"No collapse code or event extraction is rerun."})
    finest=events[-1];record("archived event interpolation distinct from final stored time",finest["horizon_time"]<finest["final_time"],
      {"interpolated_horizon_time":finest["horizon_time"],"last_step_time":finest["final_time"],"meaning":"event interpolation precedes the stored next-step time"})
    fig,axs=pair();axs[0].plot(hs,ts,"o-",color=TEAL,label="archived horizon time");ax2=axs[0].twinx();ax2.plot(hs,rs,"s-",color=GOLD,label="archived horizon radius")
    fit=data["event_fits"];hh=np.linspace(0,.04,101)
    for ax,key,col in [(axs[0],"horizon_time",TEAL),(ax2,"horizon_radius",GOLD)]:
        f=fit[key];ax.plot(hh,f["limit"]+f["coefficient"]*hh**f["order"],"--",color=col,alpha=.7)
    axs[0].set(xlabel="radial spacing h",ylabel="horizon time tH",title="Archived first-horizon refinement table");ax2.set_ylabel("horizon radius rH",color=GOLD);axs[0].tick_params(axis="y",colors=TEAL);ax2.tick_params(axis="y",colors=GOLD);grid(axs[0])
    axs[0].text(.03,.05,"Dashed: inherited six-finest fits",transform=axs[0].transAxes,fontsize=8,color=MUTED)
    vv=np.linspace(0,1.5,301);axs[1].plot(vv,1-vv,color=TEAL,label="rθ+ / 2 = 1 − v");axs[1].plot(vv,-1-vv,color=GOLD,label="rθ− / 2 = −1 − v")
    axs[1].axvline(1,color=MUTED,ls=":",lw=1);axs[1].axhline(0,color=INK,lw=.7);axs[1].axvspan(1,1.5,color=PALE,label="both expansions negative")
    axs[1].set(xlabel="PG flow v",ylabel="scaled null expansion",title="A marginal outer trapped sphere has v = 1");axs[1].legend(fontsize=8);grid(axs[1]);save(fig,STEMS[11])
    record("complete plate inventory",len(outputs)==24,"Twelve PDF plates and twelve PNG previews, every family deterministic.")

def write_manifest(status,exit_status,error=None):
    artifacts=[{"path":str(p.relative_to(ROOT)),"sha256":HASHES[str(p.relative_to(ROOT))],"sha256_after":hashlib.sha256(p.read_bytes()).hexdigest()} for p in INPUTS]
    manifest={"schema_version":2,"claim_id":"physics-gravity-atlas-bounded-examples-v0.4.0",
      "repository":{"commit":"not applicable: recovered publication staging directory","dirty":True},
      "command":[sys.executable,"tools/make_gravity_figures.py"],
      "environment":{"software":[{"name":"Python","version":platform.python_version()},{"name":"NumPy","version":np.__version__},{"name":"SciPy","version":scipy.__version__},{"name":"SymPy","version":sp.__version__},{"name":"Matplotlib","version":matplotlib.__version__}],"hardware":platform.machine()},
      "mathematics":{"assertion_tested":"The explicitly displayed finite energy balances, exact matrix and polynomial identities, sampled analytic families and bounded particle solve meet the checks below; archived event data have the tested internal identities.",
        "coefficient_domain":"Exact rational and symbolic-polynomial SymPy expressions; IEEE float64 numerical samples and implicit particle solves; inherited scalar data at their recorded precision.",
        "conventions":"Positive dt wedge dx curvature orientation; conformal signed plus-edge exp(+integral omega), inverse to Cartan D=d+omega parallel transport; periodic centered D; canonical J=[0 I;-I 0]; gravity units stated per figure; PG ingoing v>=0; column vectors.",
        "inputs":[{"path":k,"sha256":v} for k,v in HASHES.items()],
        "bounds":{"periodic_metric_cells":6,"exact_counterexample_sites":5,"Gowdy_N":[32,64,128,256,512],"Leibniz_N":"32 through 1024 doubling","particle_steps":1000,"particle_dt":.1,"particle_dimension":6,"branch_samples":501,"shell_samples":401,"RN_samples":601,"archived_scalar_event_count":7,"resource_policy":"Small fixed arrays; no network, no random sampling, no Lean, no Einstein simulation. No OS memory/CPU caps requested; runtime is recorded."},
        "non_claims":["Finite examples do not establish universal gravity, constraint closure or convergence theorems.","The particle is a constrained-mechanics surrogate, not an Einstein-matter solver.","Numerical invariants remain tolerance results; exact preservation requires an exactly solved implicit equation.","The archived scalar event data are replotted and internally checked, not freshly reproduced evolution.","The quasienergy shell is a free model choice, not an observed law or a gravity theorem.","A scalar-field 3D graph is not an embedding of Lorentzian spacetime.","No new Lean kernel check, global horizon identification, critical-collapse or cosmic-censorship result is supplied."]},
      "randomness":{"used":False,"generator":"none","seed":None},
      "run":{"started_at":STAMP,"runtime_seconds":time.monotonic()-START,"exit_status":exit_status,"status":status,"resource_limits":{"memory_bytes":None,"cpu_seconds":None,"max_cores":None,"max_threads":None}},
      "input_artifacts":artifacts,"execution_artifacts":[str(p.relative_to(ROOT)) for p in INPUTS],
      "declared_results":[f"source/gravity_figures/{stem}.{ext}" for stem in STEMS for ext in ("pdf","png")],
      "outputs":outputs,"checks":checks,"result":"Implementation and finite assertions verified in the stated ranges, conditional on the declared floating tolerances." if status=="completed" else f"Run failed: {error}",
      "residual_risks":["Floating special functions, implicit solvers and norms are not interval certified.","Exact symbolic checks rely on SymPy and are not proof-assistant receipts.","Archived numerical data do not authenticate their original execution environment or full source evolution."]}
    name="figure_checks.json" if status=="completed" else "figure_failed_"+STAMP.replace(":","-")+".json"
    temporary=(EVID/name).with_suffix(".json.tmp");temporary.write_text(json.dumps(manifest,indent=2)+"\n");temporary.replace(EVID/name)
    with (EVID/"figure_run_history.jsonl").open("a") as stream:stream.write(json.dumps({"started_at":STAMP,"status":status,"exit_status":exit_status,"inputs":HASHES,"manifest":name,"error":error})+"\n")
    return manifest

if __name__=="__main__":
    try:make_figures()
    except Exception as exc:write_manifest("failed",1,str(exc));traceback.print_exc();sys.exit(1)
    m=write_manifest("completed",0)
    print(json.dumps({"figures":12,"checks":len(checks),"all_passed":True,"runtime_seconds":m["run"]["runtime_seconds"]},indent=2))
