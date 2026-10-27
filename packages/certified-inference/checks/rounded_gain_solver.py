#!/usr/bin/env python3
"""Adaptive-precision rounded Richardson updates with rounded posterior verification.

All arithmetic is exact Fraction-based emulation of the declared dyadic ball
operations. This is not IEEE-754. A passing Python run is provisional until the
exported explicit Lean instance compiles under the pinned environment.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from fractions import Fraction as Q
from typing import Any
from exact_certificate import Model, Matrix, matrix, rational, energy, vec_energy, shape, mlean, vlean, qlean, encode, scale as mscale, eye
import rounded_certificate as rb
import precision_certificate as pb

class ResourceLimit(RuntimeError):
    pass

def parameters(m: Model, initial: Matrix, eps: Q) -> dict[str, Any]:
    if eps <= 0:
        raise ValueError('Positive tolerance is required.')
    if m.sigma <= 0:
        raise ValueError('Noise floor must be positive.')
    n,k=shape(initial)
    if (n,k)!=(len(m.H[0]),len(m.H)):
        raise ValueError('Initial gain dimensions do not match.')
    # Also validates the declared packet geometry and dimensions.
    pb.graph(m,initial)
    s=m.S
    cap=m.sigma+sum((s[i][i] for i in range(k)),Q(0))
    tau=1/cap
    q=(1-m.sigma/cap)**2
    if not (0<=q<1):
        raise ArithmeticError('Contractive trace-step invariant failed.')
    weight=(m.sigma+vec_energy(m.innovation))/(m.sigma*m.sigma)
    coeff=12*n*k*energy(s)*weight/(1-q)**2
    accuracy=pb.precision_for(coeff,eps*eps/8)
    initial_score=energy(m.residual(initial))*weight
    nf=initial_score/((eps/4)**2*(1-q))
    fuel=max(0,-((-nf.numerator)//nf.denominator))
    return dict(cap=cap,step=tau,rate=q,weight=weight,coefficient=coeff,
                update_accuracy=accuracy,fuel=fuel,initial_score=initial_score)

def rounded_update(m: Model,gain: Matrix,accuracy: int,max_precision: int=512):
    if isinstance(accuracy,bool) or not isinstance(accuracy,int) or not 0<=accuracy<=max_precision:
        raise ResourceLimit('Local accuracy is outside the precision cap.')
    nodes=pb.graph(m,gain)
    cap=m.sigma+sum((m.S[i][i] for i in range(len(m.S))),Q(0))
    tau=1/cap
    budgets=tuple(tuple(pb.plus(pb.source(x),pb.times(pb.source(tau),b))
                        for x,b in zip(row,br)) for row,br in zip(gain,nodes['residual']))
    coefficient=sum((b.coeff for row in budgets for b in row),Q(0))
    p=pb.precision_for(coefficient,Q(1,1<<accuracy))
    if p>max_precision:
        raise ResourceLimit(f'Update requires {p} fractional bits; cap is {max_precision}.')
    h,l,z,b=rb.inp(p,m.H),rb.inp(p,m.L),rb.inp(p,m.N),rb.inp(p,gain)
    prior=rb.mm(p,l,rb.tr(l))
    noise=rb.ma(p,rb.mm(p,z,rb.tr(z)),rb.inp(p,mscale(m.sigma,eye(len(m.H)))))
    innovation=rb.ma(p,rb.mm(p,rb.mm(p,h,prior),rb.tr(h)),noise)
    residual=rb.ms(p,rb.mm(p,prior,rb.tr(h)),rb.mm(p,b,innovation))
    step=tuple(tuple(rb.radd(p,rb.rexact(p,x),rb.rmul(p,rb.rexact(p,tau),r))
                    for x,r in zip(row,rr)) for row,rr in zip(gain,residual))
    if any(b.radius>Q(1,1<<accuracy) for row in step for b in row):
        raise ArithmeticError('Quantified update enclosure invariant failed.')
    result=tuple(tuple(x.center for x in row) for row in step)
    return result, dict(precision=p,coefficient=str(coefficient),
                       maximum_radius=str(max((x.radius for row in step for x in row),default=Q(0)))),step

def solve(m: Model,initial: Matrix,eps: Q,probes: list[int]|None=None,
          max_steps: int=10000,max_precision: int=512,max_bits: int=32768):
    probes=[] if probes is None else list(probes)
    if len(probes)>16 or any(isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=512 for p in probes):
        raise ValueError('Use at most 16 natural precision probes in 0..512.')
    if isinstance(max_steps,bool) or max_steps<0 or max_steps>100000:
        raise ValueError('Update cap must be in 0..100000.')
    if not 1<=max_precision<=512 or not 64<=max_bits<=1000000:
        raise ValueError('Invalid precision/bit cap.')
    pars=parameters(m,initial,eps);gain=initial;trace=[];updates=[]
    try:
        for n in range(min(pars['fuel'],max_steps)+1):
            for x in (x for row in gain for x in row):
                if max(abs(x.numerator).bit_length(),x.denominator.bit_length())>max_bits:
                    raise ResourceLimit('State rational bit-size cap reached.')
            pstar,_,_=pb.sufficient_precision(m,gain,eps*eps/4)
            attempts=[]
            for p in probes+[pstar]:
                if p>max_precision:
                    raise ResourceLimit(f'Certificate requires {p} bits; cap is {max_precision}.')
                candidate,_=rb.produce(m,gain,p)
                passed=candidate.tolerance(m,eps)
                attempts.append(dict(precision=p,score=str(candidate.score(m)),passed=passed))
                if passed:
                    trace.append(dict(iteration=n,certificates=attempts))
                    return dict(status='PASS_ROUNDED_SOLVER_PROVISIONAL',iterations=n,
                        parameters=encode(pars),chosen_precision=p,precision_probes=probes,
                        final_candidate=candidate.to_dict(),rounded_score=str(candidate.score(m)),
                        iteration_trace=trace,updates=updates,requested_tolerance=str(eps),
                        model_sha256=m.digest(),proof_status='Compile the exported Lean instance.',
                        non_claims=['No IEEE-754/BLAS or bounded-word guarantee.',
                                    'Exact model, exact rational preprocessing and budget arithmetic.',
                                    'No parser-fidelity, speedup or model-changing adaptation theorem.'])
            trace.append(dict(iteration=n,certificates=attempts))
            if n==pars['fuel']:
                raise ArithmeticError('Proved iteration horizon reached without certificate.')
            if n==max_steps:
                raise ResourceLimit('Update count cap reached before certification.')
            gain,ur,_=rounded_update(m,gain,pars['update_accuracy'],max_precision)
            updates.append(dict(iteration=n+1,**ur))
    except ResourceLimit as e:
        return dict(status='RESOURCE_LIMIT',reason=str(e),parameters=encode(pars),
                    iteration_trace=trace,updates=updates,posterior_tolerance_certified=False)
    raise ArithmeticError('Unreachable solver state.')

def export_lean(m: Model,initial: Matrix,eps: Q,result: dict[str,Any],namespace: str)->str:
    if result.get('status')!='PASS_ROUNDED_SOLVER_PROVISIONAL':
        raise ValueError('A failed or capped run cannot export a success proof.')
    if not namespace.isidentifier() or not namespace.isascii():raise ValueError('Use an ASCII identifier.')
    gain=matrix(result['final_candidate']['gain'],'gain')
    n,k=shape(gain);u,w=len(m.L[0]),len(m.N[0]);a,b=len(m.outputs),len(m.inputs)
    t=result['parameters']['update_accuracy'];fuel=result['parameters']['fuel'];it=result['iterations'];p=result['chosen_precision']
    ps='['+', '.join(map(str,result['precision_probes']))+']'
    return '\n'.join([
      'import Komorebi.RoundedSolverPosterior','import Komorebi.RationalSolverDecidable',
      'import Mathlib.LinearAlgebra.Matrix.Notation','',
      'set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 8000000',
      f'namespace Komorebi.RoundoffSolver.{namespace}',
      'open Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.QuadraticTransport','',
      f'def model : RationalModel (Fin {n}) (Fin {k}) (Fin {u}) (Fin {w}) where',
      f'  observationMatrix := {mlean(m.H)}',f'  priorFactor := {mlean(m.L)}',
      f'  noiseFactor := {mlean(m.N)}',f'  noiseFloor := {qlean(m.sigma)}',
      f'  mean := {vlean(m.mean)}',f'  observation := {vlean(m.observation)}','',
      f'def outputs : Fin {a} → Matrix (Fin {n}) (Fin {n}) ℚ := !['+', '.join(mlean(x) for x in m.outputs)+']',
      f'def inputs : Fin {b} → Matrix (Fin {k}) (Fin {k}) ℚ := !['+', '.join(mlean(x) for x in m.inputs)+']',
      f'def initial : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(initial)}',
      f'def finalGain : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(gain)}',
      f'def certificate := roundedCandidate {p} model outputs inputs finalGain','',
      f'theorem accuracy_computed : updateAccuracy model {qlean(eps)} = {t} := by decide +kernel',
      f'theorem fuel_computed : roundedFuel model initial {qlean(eps)} = {fuel} := by decide +kernel',
      f'theorem rounded_iterate_computed : roundedGain model {t} initial {it} = finalGain := by decide +kernel',
      f'theorem score_computed : candidateScore model certificate = {qlean(rational(result["rounded_score"]))} := by decide +kernel','',
      'theorem rounded_return :',
      f'    solveRounded model outputs inputs {qlean(eps)} {ps} initial = some ({p},certificate) := by',
      '  decide +kernel','',
      'theorem posterior_tolerance :',
      '    wasserstein2 model.posterior (model.approximation certificate.gain) ≤',
      f'      ENNReal.ofReal (({qlean(eps)} : ℚ) : ℝ) := by',
      f'  exact rounded_solver_return_bounds_posterior model outputs inputs {qlean(eps)} {ps} initial',
      f'    {p} certificate rounded_return','',f'end Komorebi.RoundoffSolver.{namespace}',''])

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--emit-lean',type=Path);ap.add_argument('--namespace',default='GeneratedRoundedSolver')
    ap.add_argument('--max-steps',type=int,default=10000);ap.add_argument('--max-precision',type=int,default=512)
    ap.add_argument('--max-bits',type=int,default=32768);ap.add_argument('--try-precisions',nargs='*',type=int,default=[])
    a=ap.parse_args();raw=a.input.read_bytes()
    if len(raw)>1000000:raise ValueError('Input byte cap exceeded.')
    data=json.loads(raw);m=Model.parse(data['model']);initial=matrix(data['initial_gain'],'initial_gain');eps=rational(data['epsilon'])
    r=solve(m,initial,eps,a.try_precisions,a.max_steps,a.max_precision,a.max_bits)
    r['input_sha256']=hashlib.sha256(raw).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n')
    if a.emit_lean:
        source=export_lean(m,initial,eps,r,a.namespace)
        a.emit_lean.parent.mkdir(parents=True,exist_ok=True);a.emit_lean.write_text(source)
    print(r['status'], 'updates',r.get('iterations'), 'precision',r.get('chosen_precision'))
    return 0 if r['status']=='PASS_ROUNDED_SOLVER_PROVISIONAL' else 2

if __name__=='__main__':
    raise SystemExit(main())
