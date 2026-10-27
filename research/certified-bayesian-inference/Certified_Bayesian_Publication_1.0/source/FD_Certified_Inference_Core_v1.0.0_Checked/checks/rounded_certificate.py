#!/usr/bin/env python3
"""Outward-rounded dyadic posterior certificates; Python results need Lean checking.

Fixed exact rational model. Arithmetic centers and error radii are rounded to
p fractional binary bits; signed integer parts have unbounded mathematical range.
This is not an IEEE-754 implementation or a treatment of measurement uncertainty.
"""
from __future__ import annotations
import argparse, json, hashlib
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
from typing import Any
from exact_certificate import Model, Candidate, Matrix, matrix, rational, eye, scale, packet_valid, mlean, vlean, qlean

@dataclass(frozen=True)
class Ball:
    center: Q
    radius: Q
    def encloses(self, x: Q) -> bool:
        return self.radius >= 0 and abs(x-self.center) <= self.radius
    def upper(self) -> Q:
        return (abs(self.center)+self.radius)**2

def down(p: int, x: Q) -> Q:
    d=1<<p
    return Q((x.numerator*d)//x.denominator,d)
def up(p: int, x: Q) -> Q:
    d=1<<p
    return Q(-((-x.numerator*d)//x.denominator),d)
def rounded(p: int, b: Ball) -> Ball:
    c=down(p,b.center)
    return Ball(c,up(p,b.radius+abs(b.center-c)))
def rexact(p: int, x: Q) -> Ball:
    return rounded(p,Ball(x,Q(0)))
def radd(p: int,a: Ball,b: Ball) -> Ball:
    return rounded(p,Ball(a.center+b.center,a.radius+b.radius))
def rsub(p: int,a: Ball,b: Ball) -> Ball:
    return rounded(p,Ball(a.center-b.center,a.radius+b.radius))
def rmul(p: int,a: Ball,b: Ball) -> Ball:
    return rounded(p,Ball(a.center*b.center,abs(a.center)*b.radius+abs(b.center)*a.radius+a.radius*b.radius))
def rsum(p: int,bs) -> Ball:
    bs=tuple(bs)
    return rounded(p,Ball(sum((b.center for b in bs),Q(0)),sum((b.radius for b in bs),Q(0))))
def inp(p: int,x):return tuple(tuple(rexact(p,v) for v in row) for row in x)
def tr(a):return tuple(zip(*a))
def ma(p,a,b):return tuple(tuple(radd(p,x,y) for x,y in zip(ar,br)) for ar,br in zip(a,b))
def ms(p,a,b):return tuple(tuple(rsub(p,x,y) for x,y in zip(ar,br)) for ar,br in zip(a,b))
def mm(p,a,b):
    return tuple(tuple(rsum(p,(rmul(p,a[i][k],b[k][j]) for k in range(len(b))))
                 for j in range(len(b[0]))) for i in range(len(a)))
def mv(p,a,v):return tuple(rsum(p,(rmul(p,x,y) for x,y in zip(row,v))) for row in a)
def eu(a):return sum((x.upper() for row in a for x in row),Q(0))
def serialize_ball_matrix(a):
    return {'center':[[str(x.center) for x in row] for row in a],
            'radius':[[str(x.radius) for x in row] for row in a]}

def produce(m:Model,gain:Matrix,p:int):
    if isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=512:raise ValueError('Precision must be an integer from 0 to 512')
    n,k=len(m.H[0]),len(m.H)
    if max(n,k,len(m.L[0]),len(m.N[0]),len(m.outputs),len(m.inputs))>8:raise ValueError('Producer dimension/packet cap is 8')
    if len(gain)!=n or any(len(row)!=k for row in gain):raise ValueError('Gain dimensions do not match')
    if m.sigma<=0 or not packet_valid(m.outputs,n) or not packet_valid(m.inputs,k):raise ValueError('Invalid noise floor or packet geometry')
    h,l,z,b=inp(p,m.H),inp(p,m.L),inp(p,m.N),inp(p,gain)
    prior=mm(p,l,tr(l))
    noise=ma(p,mm(p,z,tr(z)),inp(p,scale(m.sigma,eye(k))))
    innovation=ma(p,mm(p,mm(p,h,prior),tr(h)),noise)
    residual=ms(p,mm(p,prior,tr(h)),mm(p,b,innovation))
    iv=tuple(rsub(p,x,y) for x,y in zip(tuple(rexact(p,x) for x in m.observation),mv(p,h,tuple(rexact(p,x) for x in m.mean))))
    packets=tuple(tuple(mm(p,mm(p,inp(p,pa),residual),inp(p,pb)) for pb in m.inputs) for pa in m.outputs)
    candidate=Candidate(gain,tuple(tuple(eu(z) for z in row) for row in packets),sum((x.upper() for x in iv),Q(0)))
    trace={'prior':prior,'noise':noise,'innovation':innovation,'residual':residual,'innovation_vector':tuple((x,) for x in iv)}
    for i,row in enumerate(packets):
        for j,z in enumerate(row):trace[f'packet_{i}_{j}']=z
    return candidate,trace

def export_lean(m:Model,gain:Matrix,ps:list[int],eps:Q,results:list[tuple[int,Candidate]],namespace:str)->str:
    if not namespace.isidentifier() or not namespace.isascii():raise ValueError('Namespace must be an ASCII identifier')
    n,k=len(m.H[0]),len(m.H);u,w=len(m.L[0]),len(m.N[0]);a,b=len(m.outputs),len(m.inputs)
    lines=['import Komorebi.RoundedPrecisionSearch','import Mathlib.LinearAlgebra.Matrix.Notation','',
      'set_option autoImplicit false','set_option maxRecDepth 16384','set_option maxHeartbeats 4000000',
      f'namespace Komorebi.RoundedPosterior.{namespace}','open Komorebi.ExactPosterior Komorebi.QuadraticTransport','',
      f'def model : RationalModel (Fin {n}) (Fin {k}) (Fin {u}) (Fin {w}) where',
      f'  observationMatrix := {mlean(m.H)}',f'  priorFactor := {mlean(m.L)}',f'  noiseFactor := {mlean(m.N)}',
      f'  noiseFloor := {qlean(m.sigma)}',f'  mean := {vlean(m.mean)}',f'  observation := {vlean(m.observation)}',
      f'def outputs : Fin {a} → Matrix (Fin {n}) (Fin {n}) ℚ := !['+', '.join(mlean(x) for x in m.outputs)+']',
      f'def inputs : Fin {b} → Matrix (Fin {k}) (Fin {k}) ℚ := !['+', '.join(mlean(x) for x in m.inputs)+']',
      f'def gain : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(gain)}','',
      'theorem setup_valid : checkSetup model outputs inputs = true := by decide +kernel','']
    passing=[]
    for i,(p,c) in enumerate(results):
        lines += [f'def candidate{i} := roundedCandidate {p} model outputs inputs gain',
            f'theorem score{i}_computed : candidateScore model candidate{i} = {qlean(c.score(m))} := by decide +kernel',
            f'theorem tolerance{i}_computed : checkTolerance model candidate{i} {qlean(eps)} = {str(c.tolerance(m,eps)).lower()} := by decide +kernel','']
        if c.tolerance(m,eps):
            passing.append((i,p))
            lines += [f'theorem posterior{i}_bound : wasserstein2 model.posterior (model.approximation gain) ≤ ENNReal.ofReal ({qlean(eps)} : ℝ) := by',
                '  have hs := (checkSetup_eq_true model outputs inputs).mp setup_valid',
                f'  simpa using rounded_tolerance_bounds_posterior {p} model outputs inputs gain {qlean(eps)} hs.1 hs.2.1 hs.2.2 tolerance{i}_computed','']
    if passing:
        i,p=passing[0]
        lines += [f'theorem successful_return : certifyRounded {p} model outputs inputs gain {qlean(eps)} = some candidate{i} := by',
            '  rw [certifyRounded, ite_eq_left setup_valid]',
            f'  change (if checkTolerance model candidate{i} {qlean(eps)} then some candidate{i} else none) = some candidate{i}',
            f'  rw [ite_eq_left tolerance{i}_computed]','']
    lines += [f'end Komorebi.RoundedPosterior.{namespace}','']
    return '\n'.join(lines)

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--emit-lean',type=Path);ap.add_argument('--namespace',default='GeneratedRoundedCase')
    a=ap.parse_args();raw=a.input.read_bytes()
    if len(raw)>1000000:raise ValueError('Input byte cap exceeded')
    d=json.loads(raw)
    if set(d)!={'model','gain','precisions','epsilon'}:raise ValueError('Expected model, gain, precisions, epsilon')
    m=Model.parse(d['model']);gain=matrix(d['gain'],'gain');eps=rational(d['epsilon']);ps=d['precisions']
    if eps<0:raise ValueError('Negative tolerance')
    if not isinstance(ps,list) or not ps or len(ps)>16:raise ValueError('Use 1..16 precision attempts')
    results=[];attempts=[]
    for p in ps:
        c,trace=produce(m,gain,p);results.append((p,c))
        attempts.append({'precision':p,'candidate':c.to_dict(),'score':str(c.score(m)),
           'within_tolerance':c.tolerance(m,eps),'enclosures':{k:serialize_ball_matrix(x) for k,x in trace.items()}})
        if c.tolerance(m,eps):break
    passed=any(x['within_tolerance'] for x in attempts)
    report={'status':'PASS_ROUNDED_PROVISIONAL' if passed else 'NOT_CERTIFIED',
       'input_sha256':hashlib.sha256(raw).hexdigest(),'epsilon':str(eps),'attempts':attempts,
       'lean_status':'Not executed by this producer; compile exported source',
       'arithmetic':'Outward dyadic fixed-point enclosures; exact rational final comparisons',
       'non_claims':['Not IEEE-754 execution','No unknown-input uncertainty guarantee','No precision-search completeness theorem','No hardware resource or speed guarantee']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    if a.emit_lean:
        a.emit_lean.parent.mkdir(parents=True,exist_ok=True)
        a.emit_lean.write_text(export_lean(m,gain,ps,eps,results,a.namespace))
    print(json.dumps({k:report[k] for k in ('status','epsilon','lean_status')}))
    for x in attempts:print('precision',x['precision'],'score',x['score'],'passed',x['within_tolerance'])
    return 0 if passed else 2
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,KeyError,TypeError,ZeroDivisionError) as exc:raise SystemExit(f'INPUT REJECTED: {exc}')
