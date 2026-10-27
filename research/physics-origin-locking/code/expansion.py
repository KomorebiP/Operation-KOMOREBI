"""Finite action-consistent FLRW Gaussian backreaction diagnostic.

Includes scale factor, coherent pressure, and optional metric-dependent finite
kinetic tail. This is NOT fourth-order covariant continuum renormalization.
A finite comoving regulator and an explicitly selected initial state define the
calculation. Original code: MIT.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from dataclasses import dataclass, asdict
from pathlib import Path
import json,time,argparse
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp,quad
from scipy.optimize import brentq
from matching import ROOT,tower, Bcoef,R,J,K,D,S,SE,F,V_origin,dV_origin,BENCH

def gaussian_sum(depth:int)->float:
    y,d=tower(depth)
    return sum(float(dd*yy**2*np.exp(-np.pi*yy)/(2*np.pi**2)*quad(
        lambda z:z*z*np.sqrt(z*z+yy)*np.exp(-np.pi*z*z),0,8,epsabs=1e-15)[0])
        for yy,dd in zip(y,d))

def quadrature(depth,zmax,nodes):
    edges=[0.,1.]
    while edges[-1]<zmax:edges.append(min(2*edges[-1],zmax))
    xx,ww=leggauss(nodes)
    z=np.concatenate([(a+b)/2+(b-a)*xx/2 for a,b in zip(edges[:-1],edges[1:])])
    wz=np.concatenate([(b-a)*ww/2 for a,b in zip(edges[:-1],edges[1:])])
    ys,ds=tower(depth);y=np.repeat(ys,len(z));k=(np.sqrt(ys[:,None])*z).ravel()
    w=(ds[:,None]*ys[:,None]**1.5*(z*z*wz)[None,:]/(2*np.pi**2)).ravel()
    return y,k,w

@dataclass(frozen=True)
class Config:
    depth:int=15
    epsilon:float=.01
    branch:str='origin'
    barrier_fraction:float=.30
    zmax:float=32.
    nodes:int=24
    duration:float=12.
    expansion:str='static'
    initial_hubble:float=.02
    initial_state:str='flat_wkb2'
    tail:bool=True
    control:str='full'
    rtol:float=2e-10
    atol:float=2e-13
    samples:int=1501
    max_step:float=.1
    def validate(self):
        tower(self.depth)
        if self.branch not in ('accessible','origin'):raise ValueError('unknown potential')
        if self.expansion not in ('static','physical','stress'):raise ValueError('unknown expansion')
        if self.initial_state not in ('ground','flat_wkb2'):raise ValueError('unknown state')
        if self.control not in ('full','no_volume_squeeze','no_coherence_pressure','no_tail_pressure','no_coherence_force'):raise ValueError('unknown control')
        if self.zmax<1 or self.nodes<4 or not 0<self.epsilon<=1 or self.duration<=0:raise ValueError('invalid parameters')
        if not 0<self.rtol<1 or not 0<self.atol<1 or self.samples<10:raise ValueError('invalid solver controls')

class Model:
    def __init__(self,c:Config):
        c.validate();self.c=c
        self.y,self.k,self.w=quadrature(c.depth,c.zmax,c.nodes);self.nm=len(self.y)
        self.B=Bcoef(c.depth);self.SE=gaussian_sum(c.depth) if c.branch=='accessible' else SE
        self.C=2*self.SE/c.epsilon;self.E0=self.C/2
        self.fraction=self.SE/SE;self.D=D*self.fraction
        self.barrier=c.barrier_fraction*self.E0
        if c.branch=='accessible' and not self.B*K(S)<self.barrier<self.E0:
            raise ValueError('requested accessible double well violates proven barrier window')
        self.rad0=self.D*BENCH['parameters']['omega_r0']/(1-.049-.261-9e-5)*1e24
        # The numerical constants below are declared conversion inputs, not a refit.
        hb=6.582119569e-16; Mpc=3.085677581491367e22;Mp=2.435e27
        H0=BENCH['parameters']['h0_km_s_mpc']*1000/Mpc*hb
        ov=1-.049-.261-9e-5
        self.A=(3*Mp**2*H0**2*ov/self.D)**.25
        self.M2physical=(Mp/self.A)**2
        self.rho0=self.E0+self.rad0
        self.Hphysical=np.sqrt(self.rho0/(3*self.M2physical))
        self.Href=0. if c.expansion=='static' else (self.Hphysical if c.expansion=='physical' else c.initial_hubble)

    def potential(self,q):
        if self.c.branch=='origin':return V_origin(q,self.c.depth)
        ss=np.asarray(q)**2
        return (self.barrier+self.B*J(S))/S**2*(ss-S)**2+self.B*R(ss)

    def dpotential(self,q):
        if self.c.branch=='origin':return dV_origin(q,self.c.depth)
        ss=np.asarray(q)**2;delta=ss-S;rr=delta/(1+S)
        # dR/ds = 2(1+S)[(1+rr) log(1+rr)-rr].
        poly=np.zeros_like(rr)
        for n in range(20,1,-1):poly=poly*rr+(-1.)**n/(n*(n-1))
        term=np.where(abs(rr)<.05,poly*rr**2,(1+rr)*np.log1p(rr)-rr)
        return 2*q*(2*(self.barrier+self.B*J(S))/S**2*delta+2*self.B*(1+S)*term)

    def inertia(self,q,a):
        if not self.c.tail:return self.C,0.,0.
        y,d=tower(self.c.depth);r=1+q*q;b=y*y;kp2=y*self.c.zmax**2/a**2
        logA=-1.5*np.log1p(b*r/kp2);AA=np.exp(logA);one=-np.expm1(logA)
        coef=d*b/(48*np.pi**2)
        z=np.sum(coef*q*q/r*one)
        zq=np.sum(coef*(2*q/r**2*one+q*q/r*3*q*b*AA/(kp2+b*r)))
        aza=np.sum(coef*3*q*q*b*AA/(kp2+b*r))
        return self.C+float(z),float(zq),float(aza)

    def state_at_rest(self,q):
        om=np.sqrt(self.k*self.k+self.y*self.y*(1+q*q));omq=self.y*self.y*q/om
        Z,_,_=self.inertia(q,1.);force=float(self.dpotential(q));free=-force/Z
        if self.c.initial_state=='ground':
            return np.zeros(self.nm),np.zeros(self.nm),np.zeros(self.nm),free,om
        if free<=0 or q>=0:raise ValueError('initial WKB branch requires inward acceleration on negative outer branch')
        def O(acc):return np.sqrt(om*om-omq*acc/(2*om))
        def equation(acc):
            oo=O(acc);rel=(om*om-oo*oo)/(oo*(om+oo))
            return Z*acc+force+np.dot(self.w*omq,rel/2)
        acc=brentq(equation,0.,free,xtol=1e-14,rtol=1e-14)
        oo=O(acc);r=oo/om
        return (r-1)**2/(4*r),(1/r-r)/2,np.zeros(self.nm),acc,oo

    def initialize(self):
        lo=4. if self.c.branch=='accessible' else 1e-7;hi=max(1.,lo+1)
        while self.potential(hi)<self.E0:hi*=2
        outer=brentq(lambda q:float(self.potential(q)-self.E0),lo,hi,xtol=1e-13)
        def initial_energy(q):
            n,u,v,acc,oo=self.state_at_rest(q)
            om=np.sqrt(self.k*self.k+self.y*self.y*(1+q*q))
            return float(self.potential(q)+np.dot(self.w*om,n))
        q0=-outer
        if self.c.initial_state!='ground':
            inner=-4.-1e-10 if self.c.branch=='accessible' else q0*.01
            q0=brentq(lambda q:initial_energy(q)-self.E0,q0,inner,xtol=1e-13)
        n,u,v,acc,oo=self.state_at_rest(q0)
        # ell=log(a), q, qdot, H/Href, integrated comoving pressure work.
        s=np.concatenate(([0.,q0,0.,1.,0.],n,u,v))
        return s,oo,acc

    def observables(self,s):
        ell,q,p,hh,work=s[:5];a=np.exp(ell);H=self.Href*hh
        n,u,v=s[5:].reshape(3,self.nm)
        k2=self.k*self.k/a**2;om=np.sqrt(k2+self.y*self.y*(1+q*q))
        Z,Zq,aZa=self.inertia(q,a)
        rm=np.dot(self.w*om,n)/a**3
        pm=np.dot(self.w,k2*n/(3*om)-(om/2-k2/(6*om))*u)/a**3
        if self.c.control=='no_coherence_pressure':pm=np.dot(self.w,k2*n/(3*om))/a**3
        rkin=Z*p*p/2;pot=float(self.potential(q));pq=rkin-pot+aZa*p*p/6
        if self.c.control=='no_tail_pressure':pq=rkin-pot
        rad=self.rad0/a**4;rho=rkin+pot+rm+rad;pressure=pq+pm+rad/3
        return dict(a=a,H=H,k2=k2,om=om,Z=Z,Zq=Zq,aZa=aZa,
                    mode_density=rm,mode_pressure=pm,kinetic=rkin,potential=pot,
                    radiation=rad,rho=rho,pressure=pressure)

    def rhs(self,t,s):
        ell,q,p,hh,work=s[:5];n,u,v=s[5:].reshape(3,self.nm);o=self.observables(s)
        a,H,om=o['a'],o['H'],o['om']
        W=(self.y*self.y*q*p-H*o['k2'])/(om*om)
        if self.c.control!='no_volume_squeeze':W=W+3*H
        ex=n if self.c.control=='no_coherence_force' else n+u/2
        force=q*np.dot(self.w*self.y*self.y/om,ex)/a**3
        acc=-(self.dpotential(q)+force+o['Zq']*p*p/2+H*(3*o['Z']+o['aZa'])*p)/o['Z']
        dhh=-(3*self.Href/(2*self.rho0))*(o['rho']+o['pressure'])
        dwork=3*H*a**3*o['pressure']
        return np.concatenate(([H,p,acc,dhh,dwork],W*u/2,W*(1+2*n)-2*om*v,2*om*u))

    def solve(self):
        s0,oo,acc=self.initialize()
        def cross(t,s):return s[1]
        cross.direction=0;cross.terminal=False
        start=time.perf_counter()
        sol=solve_ivp(self.rhs,(0.,self.c.duration),s0,method='DOP853',rtol=self.c.rtol,atol=self.c.atol,
                      t_eval=np.linspace(0,self.c.duration,self.c.samples),events=cross,max_step=self.c.max_step)
        if not sol.success:raise RuntimeError(sol.message)
        observ=[self.observables(ss) for ss in sol.y.T]
        keys=['a','H','mode_density','mode_pressure','kinetic','potential','radiation','rho','pressure']
        arr={k:np.array([o[k] for o in observ]) for k in keys}
        arr.update(t=sol.t,log_scale_factor=sol.y[0],q=sol.y[1],velocity=sol.y[2],hubble_ratio=sol.y[3],pressure_work=sol.y[4],
                   y=self.y,k=self.k,w=self.w,initial_state=s0)
        density=arr['rho'];a=arr['a']
        arr['comoving_balance']=a**3*density+arr['pressure_work']
        arr['friedmann_constraint']=sol.y[3]**2-density/self.rho0 if self.Href else np.zeros_like(sol.t)
        n,u,v=sol.y[5:].reshape(3,self.nm,-1)
        arr['invariant_error']=np.max(np.abs((1+2*n)**2-u*u-v*v-1),axis=0)
        indices=np.unique(np.linspace(0,len(sol.t)-1,min(21,len(sol.t))).astype(int))
        arr.update(audit_t=sol.t[indices],audit_state=sol.y[:,indices],final_n=n[:,-1],final_u=u[:,-1],final_v=v[:,-1])
        cr=[]
        for t,st in zip(sol.t_events[0],sol.y_events[0]):
            ob=self.observables(st)
            cr.append(dict(time=float(t),velocity=float(st[2]),a=ob['a'],mode_density=ob['mode_density'],
                           mode_density_over_initial_budget=ob['mode_density']/self.E0))
        result=dict(config=asdict(self.c),mode_count=self.nm,elapsed_seconds=time.perf_counter()-start,nfev=sol.nfev,
            parameters=dict(C=self.C,E0=self.E0,B=self.B,gaussian_sum=self.SE,retained_gaussian_fraction=self.fraction,
                            D=self.D,barrier=self.barrier if self.c.branch=='accessible' else None,rad0=self.rad0,
                            A_eV=self.A,Hphysical=self.Hphysical,H_used=self.Href,
                            M2physical=self.M2physical,M2_used=(self.rho0/(3*self.Href**2) if self.Href else None),minimum_accessible_barrier=self.B*K(S)),
            initial_q=float(s0[1]),initial_mode_density=float(arr['mode_density'][0]),initial_acceleration=acc,
            energy_work_max_relative_residual=float(np.max(abs(arr['comoving_balance']/self.rho0-1))),
            friedmann_max_scaled_residual=float(np.max(abs(arr['friedmann_constraint']))),
            invariant_max_residual=float(np.max(arr['invariant_error'])),minimum_occupation=float(n.min()),
            final_q=float(arr['q'][-1]),final_velocity=float(arr['velocity'][-1]),final_a=float(a[-1]),
            final_H_ratio=float(sol.y[3,-1]),final_density=float(density[-1]),
            max_q=float(np.max(arr['q'])),min_q=float(np.min(arr['q'])),crossings=cr,
            final_mode_density_over_initial_budget=float(arr['mode_density'][-1]/self.E0),
            scope='Fixed finite comoving regulator; reduced-action FLRW identity. Not covariant fourth-order continuum renormalization, an out-state, or a relic-abundance prediction.')
        return result,arr

def save_run(name,c):
    out=ROOT/'results';out.mkdir(exist_ok=True)
    result,arr=Model(c).solve()
    (out/f'{name}.json').write_text(json.dumps(result,indent=2));np.savez_compressed(out/f'{name}.npz',**arr)
    print(json.dumps(dict(name=name,elapsed=result['elapsed_seconds'],nfev=result['nfev'],
        work_residual=result['energy_work_max_relative_residual'],constraint=result['friedmann_max_scaled_residual'],
        q=result['final_q'],a=result['final_a'],crossings=len(result['crossings']))),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--config',default='{}')
    ar=p.parse_args();save_run(ar.name,Config(**json.loads(ar.config)))
