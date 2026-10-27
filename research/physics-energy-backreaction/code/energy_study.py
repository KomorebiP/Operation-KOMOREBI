#!/usr/bin/env python3
"""Energy-budget study for a finite refinement-fiber crossing.

Scope: exact finite-system identities, a conditional Gaussian parameter family,
and numerical finite-cutoff quantum-mode diagnostics. NOT a renormalized FLRW
calculation, a cosmological fit, or a compiler-certified Lean proof.

Run from any working directory: python code/energy_study.py --full
Original code: MIT. See README.md for assumptions and reproduction instructions.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import argparse
from dataclasses import asdict, dataclass
import hashlib, json, math, platform, sys, time
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad, solve_ivp
from numpy.polynomial.legendre import leggauss
import sympy as sp
from inherited_verification import discrete_tower_moments, energy_per_state_dimensionless

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Config:
    epsilon: float = 0.01
    depth: int = 16
    nodes: int = 48
    half_window: float = 10.0
    momentum_cut: float = 3.5
    rtol: float = 2e-10
    atol: float = 2e-13
    force: str = 'full'
    def validate(self) -> None:
        if not 0 < self.epsilon <= 1: raise ValueError('epsilon must be in (0,1]')
        if not 1 <= self.depth <= 22: raise ValueError('depth must be 1..22')
        if not 4 <= self.nodes <= 256: raise ValueError('nodes must be 4..256')
        if self.half_window <= 0 or self.momentum_cut <= 0: raise ValueError('positive cutoffs required')
        if self.force not in ('full','none','occupation_only'): raise ValueError('unknown force')
        if not 0 < self.rtol < 1 or not 0 < self.atol < 1: raise ValueError('invalid tolerance')


def quadrature(c: Config):
    c.validate()
    # Frozen tower, with base mass zero. The finite p-cut is level dependent.
    h = np.arange(1, c.depth + 1)
    masses = 1e-4 * 2.0 ** h
    degeneracy = 2.0 ** (h - 1)
    z, zw = leggauss(c.nodes)
    z, zw = (z + 1) * c.momentum_cut / 2, zw * c.momentum_cut / 2
    y = np.repeat(masses, c.nodes)
    k = (np.sqrt(masses[:, None]) * z).ravel()
    weight = (degeneracy[:,None]*masses[:,None]**1.5 * (z*z*zw)[None,:]/(2*np.pi**2)).ravel()
    raw_energy = discrete_tower_moments(1e-4,2,1.0)['energy']
    inertia = 2*raw_energy/c.epsilon
    return masses, y, k, weight, inertia, raw_energy


def solve_finite(c: Config, samples: int = 1601):
    masses,y,k,w,C,raw = quadrature(c)
    N = len(y)
    initial = np.zeros(2+3*N)
    initial[:2] = [-c.half_window,1.0]
    def rhs(t, state):
        q,p = state[:2]
        f,u,v = state[2:].reshape(3,N)
        omega = np.sqrt(k*k+y*y*(1+q*q))
        W = y*y*q*p/omega**2
        if c.force == 'none': qpp = 0.
        else:
            exchange = f+u/2 if c.force == 'full' else f
            qpp = -q*np.dot(w*y*y/omega,exchange)/C
        return np.concatenate(([p,qpp], W*u/2, W*(1+2*f)-2*omega*v, 2*omega*u))
    start = time.perf_counter()
    sol = solve_ivp(rhs,(0.,2*c.half_window),initial,method='DOP853',
                    rtol=c.rtol,atol=c.atol,max_step=.05,
                    t_eval=np.linspace(0,2*c.half_window,samples))
    if not sol.success: raise RuntimeError(sol.message)
    q,p = sol.y[:2]
    f,u,v = sol.y[2:].reshape(3,N,-1)
    omega = np.sqrt(k[:,None]**2+y[:,None]**2*(1+q[None,:]**2))
    modes = np.sum(w[:,None]*omega*f,axis=0)/(C/2)
    kinetic = p*p
    invariant = (1+2*f)**2-u*u-v*v
    gaussian = np.exp(-np.pi*(y+k*k/y))
    weighted_minimum = w*np.sqrt(k*k+y*y)
    end_extrap = float(np.dot(weighted_minimum,f[:,-1]))
    expected = float(np.dot(weighted_minimum,gaussian))
    result = dict(config=asdict(c),success=True,seconds=time.perf_counter()-start,
                  rhs_calls=sol.nfev,quadrature_modes=N,physical_species=int(2**c.depth-1),
                  energy_residual=float(np.max(abs(kinetic+modes-1))),
                  invariant_residual=float(np.max(abs(invariant-1))),
                  minimum_occupation=float(f.min()),
                  maximum_mode_energy_fraction=float(modes.max()),
                  final_mode_energy_fraction=float(modes[-1]),
                  final_q=float(q[-1]),final_velocity=float(p[-1]),
                  minimum_velocity=float(p.min()),
                  gaussian_energy_fraction_of_full=expected/raw,
                  minimum_mass_extrapolation_over_gaussian=end_extrap/expected,
                  inertia=C,
                  interpretation='Finite-cutoff instantaneous basis; NOT an asymptotic particle yield.')
    arrays = dict(t=sol.t,q=q,velocity=p,modes=modes,kinetic=kinetic,
                  masses=masses,momentum=k,weights=w,gaussian=gaussian,
                  final_occupation=f[:,-1],final_u=u[:,-1],final_v=v[:,-1])
    return result,arrays


def independent_oscillator_check():
    """Compare two separately coded representations of the same finite system."""
    c=Config(depth=14,nodes=12,half_window=6,rtol=1e-10,atol=1e-13)
    first,data=solve_finite(c,samples=401)
    masses,y,k,w,C,raw=quadrature(c); N=len(y)
    omega0=np.sqrt(k*k+y*y*(1+c.half_window**2))
    initial=np.concatenate(([-c.half_window,1.],1/np.sqrt(2*omega0),np.zeros(N),np.zeros(N),-np.sqrt(omega0/2)))
    def rhs(t,s):
        q,p=s[:2]; ar,ai,br,bi=s[2:].reshape(4,N)
        om2=k*k+y*y*(1+q*q); om=np.sqrt(om2)
        force=-q*np.dot(w*y*y,ar*ar+ai*ai-1/(2*om))/C
        return np.concatenate(([p,force],br,bi,-om2*ar,-om2*ai))
    sol=solve_ivp(rhs,(0.,2*c.half_window),initial,method='DOP853',rtol=2e-12,atol=2e-14,
                  t_eval=data['t'],max_step=.02)
    if not sol.success: raise RuntimeError(sol.message)
    q,p=sol.y[:2]; ar,ai,br,bi=sol.y[2:].reshape(4,N,-1)
    om=np.sqrt(k[:,None]**2+y[:,None]**2*(1+q[None,:]**2))
    f=((br*br+bi*bi)+om*om*(ar*ar+ai*ai))/(2*om)-.5
    E=np.sum(w[:,None]*om*f,axis=0)/(C/2)
    return dict(config=asdict(c),max_q_difference=float(np.max(abs(q-data['q']))),
                max_velocity_difference=float(np.max(abs(p-data['velocity']))),
                max_mode_energy_fraction_difference=float(np.max(abs(E-data['modes']))),
                oscillator_energy_residual=float(np.max(abs(p*p+E-1))),
                final_occupation_max_difference=float(np.max(abs(f[:,-1]-data['final_occupation']))))


def symbolic_checks():
    f,u,v,C,p,w,om,omq,Vp=sp.symbols('f u v C p w omega omega_q Vprime',real=True)
    W=omq*p/om
    fd=W*u/2; ud=W*(1+2*f)-2*om*v; vd=2*om*u
    invariant=sp.simplify(4*(1+2*f)*fd-2*u*ud-2*v*vd)
    pdd=-(Vp+w*omq*(f+u/2))/C
    energy=sp.simplify(C*p*pdd+Vp*p+w*(omq*p*f+om*fd))
    missed=sp.simplify(C*p*(-(Vp+w*omq*f)/C)+Vp*p+w*(omq*p*f+om*fd))
    r,eta,e=sp.symbols('r eta e',positive=True)
    # A^4 ∝ lambda * a^4, whereas K ∝ a^2 at fixed rho_V and gamma.
    abundance=sp.simplify(eta*e**2*(r/sp.sqrt(e))**4/(eta*r**4))
    overdraw=sp.simplify((eta*e**2/eta)*(r/sp.sqrt(e))**2/r**2)
    radiative=sp.simplify((eta*e**2)*(r/sp.sqrt(e))**4/(eta*r**4))
    k,m=sp.symbols('k m',positive=True)
    integral=sp.integrate(k**2/(k**2+m**2)**sp.Rational(5,2),(k,0,sp.oo))
    return {'energy_derivative':str(energy),'hyperboloid_derivative':str(invariant),
            'omitted_coherence_energy_derivative':str(missed),'abundance_ratio':str(abundance),
            'gaussian_depletion':str(overdraw),'radiative_proxy_ratio':str(radiative),
            'adiabatic_kinetic_integral':str(integral)}


def parameter_analysis():
    record=json.loads((ROOT/'inputs/frozen_benchmark.json').read_text())
    b=record['calibrated_benchmark']; p=record['parameters']
    a0=b['A_over_mu']; eta=b['capture_normalization']; gamma=p['gamma']; x=p['lambda_over_A']
    energy=discrete_tower_moments(x,2,1.)['energy']
    # An independent adaptive integral, not the inherited Laguerre quadrature.
    independent=0.
    for h in range(1,19):
        y=x*2**h
        value=quad(lambda z:z*z*np.sqrt(y*y+y*z*z)*np.exp(-np.pi*z*z),0,np.inf,epsabs=1e-13,epsrel=2e-12)[0]
        independent+=2**(h-1)*np.exp(-np.pi*y)*y**1.5/(2*np.pi**2)*value
    reconstructed=2*gamma*a0*a0*energy
    omegaV=p['omega_d0']/p['r_dark_today']
    radiation_over_v=p['omega_r0']/omegaV/p['production_scale']**4
    K0_over_rad=b['K_over_rho_V']/radiation_over_v
    table=[]
    for e in (1.,.1,.03,.01,.003,.001):
        lam=eta*e*e; a=a0/np.sqrt(e)
        row=dict(epsilon=e,lambda_value=lam,A_over_mu=a,Lambda_over_mu=x*a,
                 mu_over_original_mu=lam**.25,
                 physical_A_over_original_A=(lam**.25)*a/a0,
                 gaussian_overdraw=2*gamma*lam*a*a*energy,
                 density_over_target=(lam*a**4)/(eta*a0**4),
                 peak_quartic=gamma*lam*(a*record['discrete_tower']['peak_mass_over_A'])**2,
                 required_kinetic_over_old=b['K_over_rho_V']/e/b['K_over_rho_V'],
                 incoming_reservoir_over_radiation=K0_over_rad/e,
                 unused_kinetic_fraction_after_ideal_gaussian=1-e)
        table.append(row)
    rad=[]
    for H in (1,13,14,15,16,17,18):
        hs=np.arange(1,H+1); yy=x*2.**hs;dd=2.**(hs-1)
        S2=float(np.dot(dd,yy**2)); S4=float(np.dot(dd,yy**4))
        R4=gamma*eta*a0**4/(16*np.pi**2)*S4
        Z=S2/(48*np.pi**2)
        produced=sum(2**(h-1)*energy_per_state_dimensionless(x*2**h) for h in range(1,H+1))/energy
        rad.append(dict(depth=H,production_fraction=produced,mass_fourth_moment=S4,
                        curvature_power_counting_proxy=R4,kinetic_correction_large_q=Z,
                        kinetic_correction_ratio_epsilon_001=Z/(2*energy/.01)))
    return dict(eta=eta,raw_energy_over_A4=energy,independent_quad_energy=independent,
                independent_quad_relative_error=abs(independent/energy-1),
                reconstructed_frozen_overdraw=reconstructed,frozen_reconstruction_relative_error=abs(reconstructed*eta-1),
                original_K_over_rhoV=b['K_over_rho_V'],K0_over_radiation=K0_over_rad,
                source_omegaV=omegaV,parameter_family=table,radiative_table=rad,
                caution='Curvature proxy omits subtraction-scale logarithms; not a scheme-independent lower bound.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume',action='store_true',help='reuse complete saved configurations')
    parser.add_argument('--full',action='store_true',help='run cutoff, quadrature, endpoint and negative-control grid')
    parser.add_argument('--output',type=Path,default=ROOT/'results/final')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    analytic=parameter_analysis();symbolic=symbolic_checks()
    (args.output/'parameters.json').write_text(json.dumps(analytic,indent=2))
    (args.output/'symbolic.json').write_text(json.dumps(symbolic,indent=2))
    configs=[Config()]
    if args.full:
        configs += [Config(depth=h) for h in (14,15,17,18)]
        configs += [Config(nodes=n) for n in (32,64)]
        configs += [Config(momentum_cut=z,nodes=64) for z in (2.5,4.5,6.)]
        configs += [Config(half_window=s,nodes=64) for s in (15.,20.)]
        configs += [Config(epsilon=e) for e in (.1,.001)]
        configs += [Config(force=force) for force in ('none','occupation_only')]
        configs += [Config(rtol=2e-8,atol=2e-11)]
    results=[]
    prior = json.loads((args.output/'dynamics.json').read_text()) if args.resume and (args.output/'dynamics.json').exists() else []
    for i,cfg in enumerate(configs):
        if i < len(prior) and prior[i]['config'] == asdict(cfg) and (args.output/f'run_{i:02d}.npz').exists():
            results.append(prior[i]); print('REUSED',i,flush=True); continue
        record,arrays=solve_finite(cfg);record['run_id']=i; results.append(record)
        np.savez_compressed(args.output/f'run_{i:02d}.npz',**arrays)
        (args.output/'dynamics.json').write_text(json.dumps(results,indent=2))
        print(json.dumps(record),flush=True)
    independent=independent_oscillator_check()
    (args.output/'independent_oscillator.json').write_text(json.dumps(independent,indent=2))
    gates=[]
    def gate(name,ok,value,scope): gates.append(dict(name=name,pass_=bool(ok),value=value,scope=scope))
    gate('frozen_reconstruction',analytic['frozen_reconstruction_relative_error']<1e-10,analytic['frozen_reconstruction_relative_error'],'arithmetic')
    gate('independent_momentum_integral',analytic['independent_quad_relative_error']<1e-7,analytic['independent_quad_relative_error'],'quadrature')
    gate('symbolic_energy',symbolic['energy_derivative']=='0',symbolic['energy_derivative'],'finite mathematical identity, not Lean')
    gate('symbolic_invariant',symbolic['hyperboloid_derivative']=='0',symbolic['hyperboloid_derivative'],'finite mathematical identity, not Lean')
    gate('abundance_scaling',max(abs(r['density_over_target']-1) for r in analytic['parameter_family'])<1e-12,analytic['parameter_family'],'conditional Gaussian family')
    gate('independent_oscillator',independent['max_q_difference']<1e-6,independent,'same finite model, alternate variables')
    nominal=results[0]
    gate('nominal_energy',nominal['energy_residual']<1e-8,nominal['energy_residual'],'finite cutoff only')
    gate('nominal_invariant',nominal['invariant_residual']<1e-8,nominal['invariant_residual'],'finite cutoff only')
    good=[r for r in results if r['config']['force']=='full']
    gate('no_finite_energy_overdraw',max(r['maximum_mode_energy_fraction'] for r in good)<1+1e-6,max(r['maximum_mode_energy_fraction'] for r in good),'finite cutoff only')
    if args.full:
        for r in results:
            if r['config']['force']!='full': gate('negative_control_'+r['config']['force'],r['energy_residual']>1e-3,r['energy_residual'],'incorrect closed-system equations rejected')
        # This scientific gate is deliberately not recast as a passing regression.
        depth_rows=[r for r in results if r['config']['depth'] in (14,15,16,17,18) and r['config']['nodes']==48 and r['config']['force']=='full' and r['config']['epsilon']==.01 and r['config']['half_window']==10 and r['config']['rtol']==2e-10]
        spread=max(r['maximum_mode_energy_fraction'] for r in depth_rows)-min(r['maximum_mode_energy_fraction'] for r in depth_rows)
        gate('physical_depth_independence',spread<.01,spread,'FAILED physics validation: increasing depth changes the regulated model')
    summary=dict(date='2026-10-21',scope='Partial research result. Full cosmological energy-budget resolution NOT established.',
                 gates=gates,environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sympy=sp.__version__),
                 source_sha256=hashlib.sha256((ROOT/'inputs/frozen_benchmark.json').read_bytes()).hexdigest())
    (args.output/'verification.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
