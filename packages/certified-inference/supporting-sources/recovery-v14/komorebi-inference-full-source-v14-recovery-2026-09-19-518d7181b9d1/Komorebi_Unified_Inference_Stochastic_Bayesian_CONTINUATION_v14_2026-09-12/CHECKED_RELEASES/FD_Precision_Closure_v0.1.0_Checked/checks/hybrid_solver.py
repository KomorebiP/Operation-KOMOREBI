#!/usr/bin/env python3
"""Exact Richardson solve with slack, then guaranteed outward-rounded certification.

This implements the checked hybridSolve contract, not a rounded gain iteration.
A Python success is provisional: compile the exported Lean module for a proof.
"""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
from typing import Any
from exact_certificate import Model,Matrix,matrix,rational,mlean,vlean,qlean
from solve_richardson import solve
from rounded_certificate import produce
from precision_certificate import sufficient_precision

def hybrid(m:Model,initial:Matrix,eps:Q,max_steps:int=10000,max_bits:int=32768,
           max_precision:int=512,probes:list[int]|None=None)->dict[str,Any]:
    if eps<=0: raise ValueError('The hybrid completion theorem requires positive tolerance.')
    if isinstance(max_precision,bool) or not isinstance(max_precision,int) or not 1<=max_precision<=512:
        raise ValueError('Precision cap must be in 1..512.')
    probes=[] if probes is None else list(probes)
    if len(probes)>16 or any(isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=512 for p in probes):
        raise ValueError('Use at most 16 natural precision probes in 0..512.')
    stage=solve(m,initial,eps/2,max_steps,max_bits)
    if stage['status']!='PASS_EXACT_DIAGNOSTIC':
        return dict(status='RESOURCE_LIMIT',stage='exact_solver',details=stage,
                    posterior_tolerance_certified=False)
    gain=matrix(stage['final_candidate']['gain'],'final gain')
    slack=eps*eps/4
    p,c,parts=sufficient_precision(m,gain,slack)
    predicted=p
    exact_score=rational(stage['final_score'])
    if exact_score>eps*eps/4:
        raise ArithmeticError('The exact solver did not manufacture the required slack.')
    attempts=[]
    for p in probes+[predicted]:
        if p>max_precision:
            return dict(status='RESOURCE_LIMIT',stage='precision',required_precision=p,
                        precision_cap=max_precision,posterior_tolerance_certified=False,
                        iterations=stage['iterations'],precision_attempts=attempts)
        candidate,_=produce(m,gain,p)
        inflation=c/Q(1<<p)
        if candidate.score(m)>exact_score+inflation:
            raise ArithmeticError('Rounded score inflation exceeded the proved bound.')
        passed=candidate.tolerance(m,eps)
        attempts.append(dict(precision=p,score=str(candidate.score(m)),passed=passed))
        if passed:break
    else:
        raise ArithmeticError('The sufficient fallback failed despite the manufactured slack.')
    return dict(status='PASS_HYBRID_PROVISIONAL',iterations=stage['iterations'],
        exact_solver_tolerance=str(eps/2),requested_tolerance=str(eps),
        exact_solver_fuel=stage['conservative_fuel'],exact_score=str(exact_score),
        chosen_precision=p,guaranteed_precision=predicted,precision_probes=probes,
        precision_attempts=attempts,score_slack=str(slack),inflation_coefficient=str(c),
        inflation_upper=str(inflation),predicted_score_upper=str(exact_score+inflation),
        rounded_score=str(candidate.score(m)),final_candidate=candidate.to_dict(),
        coefficient_parts={k:str(v) for k,v in parts.items()},
        limits=dict(max_steps=max_steps,max_bits=max_bits,max_precision=max_precision),
        model_sha256=m.digest(),proof_status='Compile the exported Lean source.',
        non_claims=['Gain iteration is exact rational, not rounded.',
                    'No IEEE-754, uncertain-input, parser, or performance guarantee.'])

def export_lean(m:Model,initial:Matrix,eps:Q,result:dict[str,Any],namespace:str)->str:
    if result['status']!='PASS_HYBRID_PROVISIONAL':raise ValueError('No success export for a capped run.')
    if not namespace.isidentifier() or not namespace.isascii():raise ValueError('Use an ASCII identifier.')
    gain=matrix(result['final_candidate']['gain'],'gain')
    n,k=len(m.H[0]),len(m.H);u,w=len(m.L[0]),len(m.N[0]);a,b=len(m.outputs),len(m.inputs)
    p=result['chosen_precision']
    predicted=result.get('guaranteed_precision',p)
    probes=result.get('precision_probes',[])
    ps='['+', '.join(map(str,probes))+']'
    function=(f'hybridScheduled {ps}' if probes else 'hybridSolve')
    probability_proof=([
      f'  have hc := hybridScheduled_sound {ps} model outputs inputs {qlean(eps)} initial {p} certificate hybrid_return',
      f'  exact checked_tolerance_bounds_posterior model outputs inputs certificate {qlean(eps)} hc.1 hc.2']
      if probes else [f'  exact hybrid_return_bounds_posterior model outputs inputs {qlean(eps)} initial',
                    f'    {p} certificate hybrid_return'])
    return '\n'.join([
      'import Komorebi.HybridPrecisionSchedule','import Komorebi.RationalSolverDecidable',
      'import Mathlib.LinearAlgebra.Matrix.Notation','',
      'set_option autoImplicit false','set_option maxRecDepth 32768','set_option maxHeartbeats 6000000',
      f'namespace Komorebi.RoundedPosterior.{namespace}',
      'open Komorebi.ExactPosterior Komorebi.QuadraticTransport','',
      f'def model : RationalModel (Fin {n}) (Fin {k}) (Fin {u}) (Fin {w}) where',
      f'  observationMatrix := {mlean(m.H)}',f'  priorFactor := {mlean(m.L)}',
      f'  noiseFactor := {mlean(m.N)}',f'  noiseFloor := {qlean(m.sigma)}',
      f'  mean := {vlean(m.mean)}',f'  observation := {vlean(m.observation)}','',
      f'def outputs : Fin {a} → Matrix (Fin {n}) (Fin {n}) ℚ := !['+', '.join(mlean(x) for x in m.outputs)+']',
      f'def inputs : Fin {b} → Matrix (Fin {k}) (Fin {k}) ℚ := !['+', '.join(mlean(x) for x in m.inputs)+']',
      f'def initial : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(initial)}',
      f'def finalGain : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(gain)}',
      f'def certificate := roundedCandidate {p} model outputs inputs finalGain','',
      'theorem precision_computed :',
      f'    sufficientPrecision model outputs inputs finalGain ({qlean(eps)}^2/4) = {predicted} := by',
      '  decide +kernel','',
      'theorem exact_solver_return :',
      f'    solveGain model outputs inputs ({qlean(eps)}/2) initial =',
      '      some (exactCandidate model outputs inputs finalGain) := by',
      '  decide +kernel','',
      f'theorem score_computed : candidateScore model certificate = {qlean(rational(result["rounded_score"]))} := by',
      '  decide +kernel','',
      'theorem hybrid_return :',
      f'    {function} model outputs inputs {qlean(eps)} initial = some ({p},certificate) := by',
      '  decide +kernel','',
      'theorem posterior_tolerance :',
      '    wasserstein2 model.posterior (model.approximation certificate.gain) ≤',
      f'      ENNReal.ofReal (({qlean(eps)} : ℚ) : ℝ) := by',
      *probability_proof,'',
      f'end Komorebi.RoundedPosterior.{namespace}',''])

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--emit-lean',type=Path);ap.add_argument('--namespace',default='GeneratedHybrid')
    ap.add_argument('--max-steps',type=int,default=10000);ap.add_argument('--max-bits',type=int,default=32768)
    ap.add_argument('--max-precision',type=int,default=512)
    ap.add_argument('--try-precisions',type=int,nargs='*',default=[])
    a=ap.parse_args();raw=a.input.read_bytes()
    if len(raw)>1000000:raise ValueError('Input byte cap exceeded.')
    data=json.loads(raw)
    if set(data)!={'model','initial_gain','epsilon'}:raise ValueError('Expected model, initial_gain, epsilon.')
    m=Model.parse(data['model']);initial=matrix(data['initial_gain'],'initial gain');eps=rational(data['epsilon'])
    result=hybrid(m,initial,eps,a.max_steps,a.max_bits,a.max_precision,a.try_precisions)
    result['input_sha256']=hashlib.sha256(raw).hexdigest()
    if a.emit_lean and result['status']=='PASS_HYBRID_PROVISIONAL':
        source=export_lean(m,initial,eps,result,a.namespace)
        a.emit_lean.parent.mkdir(parents=True,exist_ok=True);a.emit_lean.write_text(source)
        result['exported_source_sha256']=hashlib.sha256(source.encode()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='final_candidate'},indent=2))
    return 0 if result['status']=='PASS_HYBRID_PROVISIONAL' else 2

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,KeyError,TypeError,ArithmeticError,OSError) as e:
        raise SystemExit(f'FAILED: {e}')
