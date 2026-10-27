"""Origin locking, vacuum fate, and explicitly conditional transport diagnostics.

This script does not freeze a physical production trajectory. Its transport
columns answer the counterfactual: what would follow if a saved instantaneous
occupation were an incoherent conserved comoving distribution? Remaining
background kinetic energy is never discarded or converted to particles.
Original code: MIT.
"""
from __future__ import annotations
from pathlib import Path
import json,hashlib
import numpy as np
import mpmath as mp
from scipy.optimize import brentq
from matching import ROOT,Bcoef,D,S,SE,BENCH

def vacuum_minimum(depth=15):
    mp.mp.dps=70;dd=mp.mpf(str(D));BB=mp.mpf(str(Bcoef(depth)));ss=mp.mpf(str(S))
    def FF(x):return (1+x)**2*mp.log1p(x)-x-mp.mpf('1.5')*x*x
    def V(x):return dd*(1-x/ss)**2+BB*FF(x)
    def dv(x):return -2*dd/ss*(1-x/ss)+2*BB*((1+x)*mp.log1p(x)-x)
    x0=mp.sqrt(2*dd/(BB*ss))
    r=mp.findroot(dv,(x0*mp.mpf('.9'),x0*mp.mpf('1.1')),solver='secant')
    return dict(depth=depth,q_min=str(mp.sqrt(r)),s_min=str(r),V_min_over_D=str(V(r)/dd),
                fractional_vacuum_drop=str(1-V(r)/dd),stationarity_residual=str(dv(r)),
                scope='Empty receiving sector, origin-matched Gaussian potential; not the old tree vacuum.')

def moments(a,y,k,w,n):
    E=np.sqrt(k*k/a**2+y*y)
    rho=np.dot(w,E*n)/a**3
    pressure=np.dot(w,k*k*n/(3*a*a*E))/a**3
    trace=np.dot(w,y*y*n/E)/a**3
    return rho,pressure,trace

def conditional_transport(npzfile:Path,jsonfile:Path):
    source=np.load(npzfile);r=json.loads(jsonfile.read_text())
    y,k,w=source['y'],source['k'],source['w'];N=len(y)
    events=source['event_state'];times=source['event_times']
    threshold=4*D/S
    rows=[];curves={}
    for ei in [0,len(events)//2,len(events)-1]:
        st=events[ei];n,u,v=st[2:].reshape(3,N)
        rho,p,tr=moments(1.,y,k,w,n)
        coh=np.dot(w*y*y/(2*np.sqrt(k*k+y*y)),u)
        cold=float(np.dot(w*y,n))
        today=moments(1e6,y,k,w,n)
        loga=brentq(lambda la:np.log(moments(np.exp(la),y,k,w,n)[2]/threshold),0,30,xtol=1e-13)
        rows.append(dict(crossing=int(ei+1),time=float(times[ei]),velocity=float(st[1]),
             instantaneous_energy=rho,instantaneous_energy_over_E0=rho/r['initial_energy'],
             unresolved_background_kinetic=r['C']*st[1]**2/2,
             trace_if_dephased=tr,coherent_curvature_correction=float(coh),
             instantaneous_frozen_curvature=tr+coh-threshold,
             cold_comoving_mass=cold,conditional_today_density_over_D=today[0]/D,
             conditional_today_trace_over_D=today[2]/D,
             conditional_release_cosmic_scale=float(1e-6*np.exp(loga)),
             conditional_cold_release_cosmic_scale=float(1e-6*(cold/threshold)**(1/3))))
        scales=np.geomspace(1,2e7,401)
        vals=np.array([moments(aa,y,k,w,n) for aa in scales])
        curves[str(ei+1)]=dict(a=scales,rho=vals[:,0],pressure=vals[:,1],trace=vals[:,2])
    identity_residuals=[]
    for a in [1,3,100,1e6]:
      for st in events[::7]:
        n=st[2:2+N];rr,pp,tt=moments(a,y,k,w,n)
        identity_residuals.append(abs(rr-3*pp-tt)/max(abs(rr),1e-300))
    out=dict(scope='Conditional collisionless continuation of instantaneous snapshots, NOT a derived out-state or cosmological prediction.',
       source_npz_sha256=hashlib.sha256(npzfile.read_bytes()).hexdigest(),source_json_sha256=hashlib.sha256(jsonfile.read_bytes()).hexdigest(),
       threshold=threshold,rows=rows,max_scaled_trace_identity_error=max(identity_residuals),
       original_conditional_release=BENCH['calibrated_benchmark']['release_scale'],
       origin_vacuum=vacuum_minimum(),
       remaining_reservoir='Background kinetic energy in each row is retained as an unresolved reservoir. No occupation rescaling is applied.')
    (ROOT/'results/origin_locking_audit.json').write_text(json.dumps(out,indent=2))
    store={}
    for name,d in curves.items():
      for key,val in d.items():store[f'crossing_{name}_{key}']=val
    np.savez_compressed(ROOT/'results/conditional_transport_curves.npz',**store)
    # Include just the three exact states and quadrature that the new diagnostic uses.
    idx=[0,len(events)//2,len(events)-1]
    np.savez_compressed(ROOT/'inputs/inherited_origin_snapshots.npz',y=y,k=k,w=w,
                        state=events[idx],time=times[idx],crossing=np.array(idx)+1,C=r['C'],E0=r['initial_energy'])
    return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--npz',required=True);p.add_argument('--json',required=True)
    a=p.parse_args();print(json.dumps(conditional_transport(Path(a.npz),Path(a.json)),indent=2))
