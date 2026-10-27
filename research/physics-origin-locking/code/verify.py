"""Audit the delivered finite study. Original software: MIT."""
from __future__ import annotations
import json,hashlib,platform
from pathlib import Path
import numpy as np, scipy, sympy, mpmath
from expansion import Model,Config,ROOT
from matching import D,S,Bcoef,K,SE

def verify(replay=False):
    out=ROOT/'results';gates=[]
    def gate(name,ok,value,scope='computational'):
        gates.append(dict(name=name,pass_=bool(ok),value=value,scope=scope))
    ma=json.loads((out/'matching_audit.json').read_text());lo=json.loads((out/'origin_locking_audit.json').read_text());ia=json.loads((out/'independent_audit.json').read_text())
    gate('matching_symbolic',all(v=='0' for v in ma['symbolic'].values()),ma['symbolic'],'symbolic algebra, not Lean')
    gate('matching_independent_integrals',max(x['error'] for x in ma['independent_remainder_integrals'])<1e-10,max(x['error'] for x in ma['independent_remainder_integrals']))
    gate('quartic_polynomial_invariance',ma['max_scaled_matching_residual']<1e-12,ma['max_scaled_matching_residual'])
    gate('trace_moment_identity',lo['max_scaled_trace_identity_error']<1e-13,lo['max_scaled_trace_identity_error'],'conditional collisionless moments')
    gate('flrw_symbolic_exchange',all(v=='0' for v in ia['symbolic'].values()),ia['symbolic'],'finite action identities, not covariant renormalization')
    cx=ia['complex'];gate('independent_complex_variables',cx['max_q_difference']<1e-9 and cx['max_mode_energy_difference_over_E0']<1e-8,cx)
    recs=[];saved_audit=[]
    for p in sorted(out.glob('*.json')):
        r=json.loads(p.read_text())
        if 'parameters' not in r or 'config' not in r:continue
        ar=np.load(p.with_suffix('.npz'));m=Model(Config(**r['config']));good=r['config']['control']=='full'
        local=0.
        for jj,st in enumerate(ar['audit_state'].T):
            ob=m.observables(st);a=ob['a'];balance=(a**3*ob['rho']+st[4])/m.rho0
            # Audit snapshots independently of saved aggregate rho arrays.
            ix=int(np.argmin(abs(ar['t']-ar['audit_t'][jj])))
            local=max(local,abs(ob['rho']-ar['rho'][ix])/m.rho0,
                      abs(balance-ar['comoving_balance'][ix]/m.rho0))
        saved_audit.append(local)
        recs.append((p.stem,r,good))
    gate('saved_state_audit',max(saved_audit)<1e-12,dict(configurations=len(recs),maximum_scaled_discrepancy=max(saved_audit)))
    good=[r for _,r,g in recs if g]
    gate('correct_finite_energy_work',max(r['energy_work_max_relative_residual'] for r in good)<1e-8,max(r['energy_work_max_relative_residual'] for r in good),'sampled finite-model residual')
    gate('friedmann_constraint',max(r['friedmann_max_scaled_residual'] for r in good)<1e-8,max(r['friedmann_max_scaled_residual'] for r in good),'constraint evolved, not reset algebraically')
    gate('positive_occupations',min(r['minimum_occupation'] for r in good)>-1e-8,min(r['minimum_occupation'] for r in good))
    gate('mode_hyperboloid',max(r['invariant_max_residual'] for r in good)<1e-5,max(r['invariant_max_residual'] for r in good))
    for name,r,g in recs:
        if not g:gate(name+'_rejected',r['energy_work_max_relative_residual']>1e-5,r['energy_work_max_relative_residual'],'intentional wrong-model control')
    def read(n):return json.loads((out/f'{n}.json').read_text())
    stat=read('origin_static_refined');phys=read('origin_physical_refined')
    ast=np.load(out/'origin_static_refined.npz');aph=np.load(out/'origin_physical_refined.npz')
    gate('short_physical_scale_comparison',float(np.max(abs(ast['q']-aph['q'])))<1e-10,
         dict(max_q_difference=float(np.max(abs(ast['q']-aph['q']))),H_over_A=phys['parameters']['Hphysical'],final_log_a=float(aph['log_scale_factor'][-1])),
         'short microscopic interval only; no late-time inference')
    pre=json.loads((ROOT/'provenance/inherited_short_reference.json').read_text())
    err=abs(stat['crossings'][0]['mode_density']-pre['crossings'][0]['mode_energy'])/stat['parameters']['E0']
    gate('flat_limit_reference',err<1e-8,err,'new code replay against inherited first-crossing reference')
    q1=read('origin_stress64');q2=read('origin_stress128');q3=read('origin_stress128_cut32')
    dq=max(abs(x['mode_density_over_initial_budget']-y['mode_density_over_initial_budget']) for x,y in zip(q1['crossings'],q2['crossings']))
    gate('fixed_cutoff_quadrature',dq<1e-6,dq,'stress-test interval 0<=tau<=4, 64 to 128 nodes')
    uv=abs(q3['crossings'][0]['mode_density']-q2['crossings'][0]['mode_density'])/abs(q2['crossings'][0]['mode_density'])
    gate('expanding_momentum_cutoff_acceptance',uv<1e-3,
         dict(first_crossing_relative_shift=uv,z16_mode_fraction=q2['crossings'][0]['mode_density_over_initial_budget'],z32_mode_fraction=q3['crossings'][0]['mode_density_over_initial_budget']),
         'FAILED scientific gate: state and curvature subtractions not completed')
    # Matching-window test is a classification, not acceptance of a physical tower endpoint.
    from expansion import gaussian_sum
    win=[]
    for h in range(10,16):
        e=gaussian_sum(h)/.01
        win.append(dict(depth=h,gaussian_fraction=gaussian_sum(h)/SE,threshold_over_budget=Bcoef(h)*K(S)/e))
    gate('modified_model_matching_window',win[2]['threshold_over_budget']<.3 and win[3]['threshold_over_budget']>1,win,'counterfactual model classification, not a selected cosmology')
    fresh=[]
    if replay:
      for name in ['origin_stress64','origin_static_refined','candidate_static','control_no_tail_pressure']:
        ref=read(name);now,arr=Model(Config(**ref['config'])).solve()
        delta=abs(now['final_q']-ref['final_q'])
        fresh.append(dict(name=name,final_q_difference=delta,work_residual_difference=abs(now['energy_work_max_relative_residual']-ref['energy_work_max_relative_residual'])))
      gate('fresh_replay',max(x['final_q_difference'] for x in fresh)<1e-9,fresh)
    result=dict(scope='Finite action and conditional moment checks. No repaired original cosmology or new Lean certificate.',
        configurations=len(recs),correct_configurations=len(good),negative_control_configurations=len(recs)-len(good),
        gates=gates,pass_count=sum(g['pass_'] for g in gates),fail_count=sum(not g['pass_'] for g in gates),
        unestablished=['covariant fourth-order renormalized stress tensor','physical incoming state','late-time capture and out-state','intended abundance','physical ultraviolet endpoint','old post-release vacuum-energy relaxation'],
        correction='The inherited density-locked branch is q=0. q=4 is an empty-sector tree vacuum, not the original locking point.',
        frozen_input_sha256=hashlib.sha256((ROOT/'inputs/frozen_benchmark.json').read_bytes()).hexdigest(),
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sympy=sympy.__version__,mpmath=mpmath.__version__))
    (out/'verification.json').write_text(json.dumps(result,indent=2))
    return result
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');p.add_argument('--strict',action='store_true',help='Exit 3 if any gate fails. This study deliberately retains two failures.');a=p.parse_args()
    r=verify(a.replay);print(json.dumps(r,indent=2))
    if a.strict and r['fail_count']:
        raise SystemExit(3)
