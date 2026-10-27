#!/usr/bin/env python3
"""Exact rational Richardson gain iteration with posterior-error certificates.

A PASS is an exact Python diagnostic. Compile the exported Lean module to obtain
an instance proof. The mathematical input certified there is its explicit data,
not an unspecified rounded or uncertain real measurement.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
from typing import Any
from exact_certificate import (Model, Candidate, Matrix, matrix, rational, shape,
    eye, add, sub, scale, mul, trans, energy, packet_valid, encode, mlean, vlean, qlean)


def ceilq(x: Q) -> int:
    return max(0, -((-x.numerator) // x.denominator))


def solve(m: Model, initial: Matrix, epsilon: Q, max_steps: int = 10000,
          max_bits: int = 32768) -> dict[str, Any]:
    """Run the exact checked recurrence, returning no certification on a resource cap."""
    n, k = len(m.P), len(m.H)
    if shape(initial) != (n, k):
        raise ValueError('Initial gain dimensions do not match the model.')
    if m.sigma <= 0 or epsilon <= 0:
        raise ValueError('Noise floor and requested tolerance must be strictly positive.')
    if not packet_valid(m.outputs, n) or not packet_valid(m.inputs, k):
        raise ValueError('Complete symmetric orthogonal packet families are required.')
    if not 0 <= max_steps <= 100000 or not 128 <= max_bits <= 1000000:
        raise ValueError('Resource limits are outside supported ranges.')
    S = m.S
    cap = m.sigma + sum((S[j][j] for j in range(k)), Q(0))
    tau = 1/cap
    rho = 1-m.sigma/cap
    rate = rho*rho
    if not (cap > 0 and 0 <= rho < 1):
        raise ArithmeticError('The represented model failed the derived spectral-cap invariant.')
    initial_score = m.exact(initial).score(m)
    fuel = ceilq(initial_score/(epsilon*epsilon*(1-rate)))
    transition = sub(eye(k), scale(tau, S))
    B = initial
    history: list[dict[str, Any]] = []
    previous_score: Q | None = None
    for iteration in range(min(fuel, max_steps)+1):
        F = m.residual(B)
        c = m.exact(B)
        if not c.valid(m):
            raise ArithmeticError('The exact candidate producer failed its own checker.')
        score = c.score(m)
        envelope = rate**iteration*initial_score
        if score > envelope or (previous_score is not None and score > rate*previous_score):
            raise ArithmeticError('Exact geometric contraction invariant failed.')
        gain_hash = hashlib.sha256(json.dumps(encode(B),separators=(',',':')).encode()).hexdigest()
        history.append(dict(iteration=iteration, residual_energy=str(energy(F)),
            score=str(score), geometric_upper=str(envelope), gain_sha256=gain_hash))
        if c.tolerance(m, epsilon):
            return dict(status='PASS_EXACT_DIAGNOSTIC', iterations=iteration,
                sigma=str(m.sigma), spectral_cap=str(cap), step=str(tau), rho=str(rho),
                energy_rate=str(rate), conservative_fuel=fuel,
                requested_tolerance=str(epsilon), initial_score=str(initial_score),
                final_score=str(score), final_candidate=c.to_dict(), history=history,
                model_sha256=m.digest(), max_steps=max_steps, max_bits=max_bits,
                proof_status='Compile the exported Lean source for an instance proof.')
        if iteration == min(fuel,max_steps):
            break
        nextB = add(B, scale(tau, F))
        if m.residual(nextB) != mul(F, transition):
            raise ArithmeticError('Exact residual recurrence failed.')
        if any(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) > max_bits
               for row in nextB for x in row):
            return dict(status='RESOURCE_LIMIT', reason='Rational bit-size cap',
                iterations=iteration, conservative_fuel=fuel, history=history,
                posterior_tolerance_certified=False)
        previous_score = score
        B = nextB
    if max_steps >= fuel:
        raise ArithmeticError('The mathematical fuel bound was exhausted without success.')
    return dict(status='RESOURCE_LIMIT', reason='Iteration cap below proved fuel',
        iterations=min(fuel,max_steps), conservative_fuel=fuel, history=history,
        posterior_tolerance_certified=False)


def export_lean(m: Model, initial: Matrix, epsilon: Q, result: dict[str,Any],
                namespace: str) -> str:
    if result['status'] != 'PASS_EXACT_DIAGNOSTIC':
        raise ValueError('Cannot export a success theorem for a capped run.')
    if not namespace.isidentifier() or not namespace.isascii():
        raise ValueError('Use a simple ASCII Lean namespace.')
    B = matrix(result['final_candidate']['gain'], 'final gain')
    n,k=len(m.P),len(m.H);u,w=len(m.L[0]),len(m.N[0]);a,b=len(m.outputs),len(m.inputs)
    return '\n'.join([
        'import Komorebi.RationalSolverPosterior',
        'import Komorebi.RationalSolverDecidable',
        'import Mathlib.LinearAlgebra.Matrix.Notation', '',
        'set_option autoImplicit false', 'set_option maxRecDepth 16384',
        'set_option maxHeartbeats 1200000',
        f'namespace Komorebi.ExactPosterior.{namespace}',
        'open Komorebi.ExactPosterior Komorebi.QuadraticTransport', '',
        f'def model : RationalModel (Fin {n}) (Fin {k}) (Fin {u}) (Fin {w}) where',
        f'  observationMatrix := {mlean(m.H)}', f'  priorFactor := {mlean(m.L)}',
        f'  noiseFactor := {mlean(m.N)}', f'  noiseFloor := {qlean(m.sigma)}',
        f'  mean := {vlean(m.mean)}', f'  observation := {vlean(m.observation)}', '',
        f'def outputs : Fin {a} → Matrix (Fin {n}) (Fin {n}) ℚ := !['+
        ', '.join(mlean(x) for x in m.outputs)+']',
        f'def inputs : Fin {b} → Matrix (Fin {k}) (Fin {k}) ℚ := !['+
        ', '.join(mlean(x) for x in m.inputs)+']',
        f'def initial : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(initial)}',
        f'def finalGain : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(B)}',
        'def certificate := exactCandidate model outputs inputs finalGain', '',
        'theorem returned_by_solver :',
        f'    solveGain model outputs inputs {qlean(epsilon)} initial = some certificate := by',
        '  decide +kernel', '',
        f'theorem iterate_matches : model.solverGain initial {result["iterations"]} = finalGain := by',
        '  decide +kernel', '',
        'theorem posterior_tolerance :',
        '    wasserstein2 model.posterior (model.approximation certificate.gain) ≤',
        f'      ENNReal.ofReal (({qlean(epsilon)} : ℚ) : ℝ) := by',
        f'  exact solver_return_bounds_posterior model outputs inputs {qlean(epsilon)} initial',
        '    certificate returned_by_solver', '',
        f'end Komorebi.ExactPosterior.{namespace}', ''])


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--emit-lean',type=Path)
    ap.add_argument('--namespace',default='GeneratedRichardson')
    ap.add_argument('--max-steps',type=int,default=10000)
    ap.add_argument('--max-bits',type=int,default=32768)
    args=ap.parse_args()
    data=json.loads(args.input.read_text())
    if set(data) != {'model','initial_gain','epsilon'}:
        raise ValueError('Expected exactly model, initial_gain and epsilon fields.')
    m=Model.parse(data['model']);B=matrix(data['initial_gain'],'initial gain');eps=rational(data['epsilon'])
    result=solve(m,B,eps,args.max_steps,args.max_bits)
    result['input_sha256']=hashlib.sha256(args.input.read_bytes()).hexdigest()
    if args.emit_lean and result['status']=='PASS_EXACT_DIAGNOSTIC':
        source=export_lean(m,B,eps,result,args.namespace)
        args.emit_lean.parent.mkdir(parents=True,exist_ok=True);args.emit_lean.write_text(source)
        result['exported_source_sha256']=hashlib.sha256(source.encode()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'history','final_candidate'}},indent=2))
    return 0 if result['status']=='PASS_EXACT_DIAGNOSTIC' else 2

if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, ArithmeticError, OSError) as error:
        raise SystemExit(f'FAILED: {error}')
