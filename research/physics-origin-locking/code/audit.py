"""Symbolic and independent numerical checks. Original code: MIT."""
from __future__ import annotations
import json,sys
from dataclasses import asdict
import numpy as np
from scipy.integrate import solve_ivp
import sympy as sp
from expansion import Config,Model,ROOT

def symbolic():
    a,H,q,p,om,y,k2,w,n,u,v=sp.symbols('a H q p om y k2 w n u v',nonzero=True, real=True)
    W=3*H+(y*y*q*p-H*k2)/(om*om)
    nd=W*u/2;ud=W*(1+2*n)-2*om*v;vd=2*om*u
    omdot=(y*y*q*p-H*k2)/om
    rho=w*om*n/a**3
    pressure=w/a**3*(k2*n/(3*om)-(om/2-k2/(6*om))*u)
    rhodot=w/a**3*(omdot*n+om*nd-3*H*om*n)
    force=w*y*y*q/(a**3*om)*(n+u/2)
    mode=sp.simplify(rhodot+3*H*(rho+pressure)-p*force)
    inv=sp.simplify(4*(1+2*n)*nd-2*u*ud-2*v*vd)
    Z,Zq,aZa,Up,FF,pdot=sp.symbols('Z Zq aZa Up FF pdot',real=True)
    pdot=-(Up+FF+Zq*p*p/2+H*(3*Z+aZa)*p)/Z
    qrhodot=Z*p*pdot+(Zq*p+aZa*H)*p*p/2+Up*p
    scalar=sp.simplify(qrhodot+3*H*(Z*p*p+aZa*p*p/6)+p*FF)
    # Check the pressure from scale-factor variation of a^3 Z qdot^2/2.
    a0=sp.symbols('a0',positive=True);z=sp.Function('Z')(a0)
    pressure_from_action=sp.diff(a0**3*z*p*p/2,a0)/(3*a0*a0)
    ps=sp.simplify(pressure_from_action-z*p*p/2-a0*sp.diff(z,a0)*p*p/6)
    rr,pp,M2=sp.symbols('rr pp M2',positive=True)
    friedmann=sp.simplify(2*H*(-(rr+pp)/(2*M2))-(-3*H*(rr+pp))/(3*M2))
    result=dict(mode_exchange=str(mode),hyperboloid=str(inv),background_exchange=str(scalar),
                metric_pressure=str(ps),friedmann_constraint=str(friedmann))
    assert all(v=='0' for v in result.values()),result
    return result

def independent_complex():
    c=Config(branch='origin',depth=14,nodes=8,zmax=8,duration=6,expansion='stress',initial_hubble=.02,samples=401,rtol=1e-13,atol=1e-16)
    m=Model(c);reference,ra=m.solve();s0,O,_=m.initialize();N=m.nm
    f0=1/np.sqrt(2*O);g0=-1j*O*f0
    init=np.concatenate((s0[:5],f0,np.zeros(N),g0.real,g0.imag))
    def obs(s):
        ell,q,p,hh,work=s[:5];a=np.exp(ell);H=m.Href*hh
        fr,fi,gr,gi=s[5:].reshape(4,N);f2=fr*fr+fi*fi;g2=gr*gr+gi*gi
        kp2=m.k*m.k/a**2;mass=m.y*m.y*(1+q*q);om=np.sqrt(kp2+mass)
        Z,Zq,aZa=m.inertia(q,a);pot=float(m.potential(q))
        rho_mode=np.dot(m.w,(g2+om*om*f2)/2-om/(2*a**3))
        p_mode=np.dot(m.w,(g2-(mass+kp2/3)*f2)/2-kp2/(6*a**3*om))
        rho=Z*p*p/2+pot+rho_mode+m.rad0/a**4
        pressure=Z*p*p/2-pot+aZa*p*p/6+p_mode+m.rad0/(3*a**4)
        force=q*np.dot(m.w*m.y*m.y,f2-1/(2*a**3*om))
        return a,H,om,Z,Zq,aZa,rho,pressure,force,rho_mode
    def rhs(t,s):
        a,H,om,Z,Zq,aZa,rho,pressure,force,rm=obs(s);ell,q,p,hh,work=s[:5]
        fr,fi,gr,gi=s[5:].reshape(4,N)
        acc=-(m.dpotential(q)+force+Zq*p*p/2+H*(3*Z+aZa)*p)/Z
        dhh=-3*m.Href*(rho+pressure)/(2*m.rho0)
        return np.concatenate(([H,p,acc,dhh,3*H*a**3*pressure],gr,gi,-3*H*gr-om*om*fr,-3*H*gi-om*om*fi))
    sol=solve_ivp(rhs,(0,c.duration),init,method='DOP853',rtol=c.rtol,atol=c.atol,max_step=.1,t_eval=ra['t'])
    assert sol.success
    oo=np.array([obs(s) for s in []]) if False else [obs(s) for s in sol.y.T]
    rm=np.array([o[-1] for o in oo]);rho=np.array([o[6] for o in oo]);a=np.exp(sol.y[0])
    fr,fi,gr,gi=sol.y[5:].reshape(4,N,-1)
    # a^3(f g* - f* g)/i = 2 a^3 (fi*gr-fr*gi).
    wr=2*a[None,:]**3*(fi*gr-fr*gi)
    result=dict(config=asdict(c),max_q_difference=float(np.max(abs(sol.y[1]-ra['q']))),
       max_velocity_difference=float(np.max(abs(sol.y[2]-ra['velocity']))),
       max_mode_energy_difference_over_E0=float(np.max(abs(rm-ra['mode_density']))/m.E0),
       max_work_balance_residual=float(np.max(abs((a**3*rho+sol.y[4])/m.rho0-1))),
       max_wronskian_residual=float(np.max(abs(wr-1))))
    np.savez_compressed(ROOT/'results/independent_complex.npz',t=sol.t,q=sol.y[1],reference_q=ra['q'],mode_density=rm,
                        reference_mode_density=ra['mode_density'],rho=rho,a=a,pressure_work=sol.y[4],wronskian_max_error=np.max(abs(wr-1),axis=0))
    return result

if __name__=='__main__':
    r=dict(symbolic=symbolic(),complex=independent_complex())
    (ROOT/'results/independent_audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
