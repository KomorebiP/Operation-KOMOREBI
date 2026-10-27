#!/usr/bin/env python3
"""Exact-rational posterior certificates and Lean proof-instance export.

JSON integers, decimal strings, and p/q strings mean exact rational numbers.
JSON floating-point numbers are rejected. A Python PASS is NOT a Lean proof:
compile the emitted .lean file with the pinned runtime to certify that instance.
"""
from __future__ import annotations
import argparse, hashlib, json
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
from typing import Any

Matrix = tuple[tuple[Q, ...], ...]
Vector = tuple[Q, ...]

def rational(x: Any) -> Q:
    if isinstance(x, bool) or not isinstance(x, (int, str, Q)):
        raise ValueError('Use an integer or an exact decimal/fraction string; floats are not enclosures.')
    if isinstance(x, str) and len(x) > 4096:
        raise ValueError('Rational literal exceeds the input cap.')
    try:
        return Q(x)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f'Invalid rational literal {x!r}') from exc

def matrix(x: Any, name: str) -> Matrix:
    if not isinstance(x, list) or not x or len(x) > 64:
        raise ValueError(f'{name}: expected 1..64 rows')
    if any(not isinstance(row, list) for row in x) or not x[0] or len(x[0]) > 64:
        raise ValueError(f'{name}: expected 1..64 columns')
    w = len(x[0])
    if any(len(row) != w for row in x):
        raise ValueError(f'{name}: ragged matrix')
    return tuple(tuple(rational(a) for a in row) for row in x)

def shape(a: Matrix) -> tuple[int, int]:
    return len(a), len(a[0])

def zero(n: int, m: int) -> Matrix:
    return tuple(tuple(Q(0) for _ in range(m)) for _ in range(n))

def eye(n: int) -> Matrix:
    return tuple(tuple(Q(int(i == j)) for j in range(n)) for i in range(n))

def trans(a: Matrix) -> Matrix:
    return tuple(zip(*a))

def add(a: Matrix, b: Matrix) -> Matrix:
    if shape(a) != shape(b): raise ValueError('Addition dimension mismatch')
    return tuple(tuple(x+y for x,y in zip(ar,br)) for ar,br in zip(a,b))

def scale(c: Q, a: Matrix) -> Matrix:
    return tuple(tuple(c*x for x in row) for row in a)

def sub(a: Matrix,b: Matrix) -> Matrix:
    return add(a,scale(Q(-1),b))

def mul(a: Matrix,b: Matrix) -> Matrix:
    n,k=shape(a);k0,m=shape(b)
    if k!=k0: raise ValueError('Multiplication dimension mismatch')
    return tuple(tuple(sum((a[i][l]*b[l][j] for l in range(k)),Q(0)) for j in range(m)) for i in range(n))

def mv(a: Matrix,v: Vector) -> Vector:
    if shape(a)[1]!=len(v):raise ValueError('Vector dimension mismatch')
    return tuple(sum((x*y for x,y in zip(row,v)),Q(0)) for row in a)

def energy(a: Matrix) -> Q:
    return sum((x*x for row in a for x in row),Q(0))

def vec_energy(v: Vector) -> Q:
    return sum((x*x for x in v),Q(0))

def packet_valid(ps: tuple[Matrix,...],n: int) -> bool:
    if not ps or any(shape(p)!=(n,n) for p in ps):return False
    total=zero(n,n)
    for i,p in enumerate(ps):
        if trans(p)!=p or mul(p,p)!=p:return False
        if any(mul(p,q)!=zero(n,n) for j,q in enumerate(ps) if i!=j):return False
        total=add(total,p)
    return total==eye(n)

def encode(x: Any) -> Any:
    if isinstance(x,Q):return str(x)
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x

@dataclass(frozen=True)
class Model:
    H: Matrix
    L: Matrix
    N: Matrix
    sigma: Q
    mean: Vector
    observation: Vector
    outputs: tuple[Matrix,...]
    inputs: tuple[Matrix,...]

    @staticmethod
    def parse(d: dict[str,Any]) -> 'Model':
        required={'H','L','N','sigma','mean','observation','output_packets','input_packets'}
        if set(d)!=required:raise ValueError(f'Model fields must be exactly {sorted(required)}')
        H=matrix(d['H'],'H');L=matrix(d['L'],'L');N=matrix(d['N'],'N');k,n=shape(H)
        m=tuple(map(rational,d['mean']));y=tuple(map(rational,d['observation']))
        if len(m)!=n or len(y)!=k or len(L)!=n or len(N)!=k:raise ValueError('Model dimensions do not match')
        out=tuple(matrix(a,'output packet') for a in d['output_packets'])
        ins=tuple(matrix(a,'input packet') for a in d['input_packets'])
        if not out or not ins or len(out)>64 or len(ins)>64:raise ValueError('Invalid packet counts')
        if any(shape(a)!=(n,n) for a in out) or any(shape(a)!=(k,k) for a in ins):raise ValueError('Packet dimensions do not match')
        return Model(H,L,N,rational(d['sigma']),m,y,out,ins)

    @property
    def P(self)->Matrix:return mul(self.L,trans(self.L))
    @property
    def R(self)->Matrix:return add(mul(self.N,trans(self.N)),scale(self.sigma,eye(len(self.H))))
    @property
    def S(self)->Matrix:return add(mul(mul(self.H,self.P),trans(self.H)),self.R)
    @property
    def innovation(self)->Vector:return tuple(a-b for a,b in zip(self.observation,mv(self.H,self.mean)))
    def residual(self,gain:Matrix)->Matrix:return sub(mul(self.P,trans(self.H)),mul(gain,self.S))
    def input_dict(self)->dict[str,Any]:
        return encode(dict(H=self.H,L=self.L,N=self.N,sigma=self.sigma,mean=self.mean,observation=self.observation,output_packets=self.outputs,input_packets=self.inputs))
    def digest(self)->str:
        return hashlib.sha256(json.dumps(self.input_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def exact(self,gain:Matrix,padding:Q=Q(0))->'Candidate':
        f=self.residual(gain)
        b=tuple(tuple(energy(mul(mul(p,f),q))+padding for q in self.inputs) for p in self.outputs)
        return Candidate(gain,b,vec_energy(self.innovation))

@dataclass(frozen=True)
class Candidate:
    gain: Matrix
    upper: Matrix
    innovation_upper: Q
    def valid(self,m:Model)->bool:
        n,k=shape(m.P)[0],len(m.H)
        if shape(self.gain)!=(n,k) or shape(self.upper)!=(len(m.outputs),len(m.inputs)):return False
        if m.sigma<=0 or not packet_valid(m.outputs,n) or not packet_valid(m.inputs,k):return False
        f=m.residual(self.gain)
        return (all(energy(mul(mul(p,f),q))<=self.upper[i][j] for i,p in enumerate(m.outputs) for j,q in enumerate(m.inputs))
                and vec_energy(m.innovation)<=self.innovation_upper)
    def total(self)->Q:return sum((x for row in self.upper for x in row),Q(0))
    def score(self,m:Model)->Q:
        if m.sigma==0:raise ValueError('Zero noise floor has no accepted certificate')
        return self.total()*(m.sigma+self.innovation_upper)/(m.sigma*m.sigma)
    def tolerance(self,m:Model,eps:Q)->bool:
        return eps>=0 and self.total()*(m.sigma+self.innovation_upper)<=eps*eps*m.sigma*m.sigma
    def to_dict(self)->dict[str,Any]:return encode(dict(gain=self.gain,packet_upper=self.upper,innovation_upper=self.innovation_upper))
    @staticmethod
    def parse(d:dict[str,Any],m:Model)->'Candidate':
        b=matrix(d['gain'],'gain')
        if shape(b)!=(len(m.P),len(m.H)):raise ValueError('Gain dimensions do not match')
        if set(d)=={'gain'}:return m.exact(b)
        if set(d)!={'gain','packet_upper','innovation_upper'}:raise ValueError('Candidate has unexpected fields')
        upper=matrix(d['packet_upper'],'packet_upper')
        if shape(upper)!=(len(m.outputs),len(m.inputs)):raise ValueError('Upper-bound dimensions do not match')
        return Candidate(b,upper,rational(d['innovation_upper']))

def select(m:Model,inc:Candidate,proposals:list[Candidate])->tuple[Candidate,list[dict[str,Any]]]:
    if not inc.valid(m):raise ValueError('The incumbent must have a valid certificate')
    decisions=[]
    for i,c in enumerate(proposals):
        valid=c.valid(m)
        accepted=valid and c.score(m)<=inc.score(m)
        decisions.append(dict(index=i,valid=valid,accepted=accepted,
            score=str(c.score(m)) if m.sigma!=0 else None))
        if accepted:inc=c
    return inc,decisions

def qlean(q:Q)->str:
    return str(q.numerator) if q.denominator==1 else f'({q.numerator}/{q.denominator})'

def mlean(a:Matrix)->str:
    return '!!['+'; '.join(', '.join(qlean(x) for x in row) for row in a)+']'

def vlean(v:Vector)->str:return '!['+', '.join(qlean(x) for x in v)+']'

def export_lean(m:Model,cs:list[Candidate],eps:Q,namespace:str)->str:
    if not namespace.isidentifier() or not namespace.isascii():raise ValueError('Use an ASCII identifier for the namespace')
    n,k=len(m.P),len(m.H);u,w=len(m.L[0]),len(m.N[0]);a,b=len(m.outputs),len(m.inputs)
    lines=['import Komorebi.RationalPosteriorCertificate','import Mathlib.LinearAlgebra.Matrix.Notation','',
           'set_option autoImplicit false','set_option maxRecDepth 8192','set_option maxHeartbeats 800000',
           f'namespace Komorebi.ExactPosterior.{namespace}','open Komorebi.ExactPosterior Komorebi.QuadraticTransport','',
           f'def model : RationalModel (Fin {n}) (Fin {k}) (Fin {u}) (Fin {w}) where',
           f'  observationMatrix := {mlean(m.H)}',f'  priorFactor := {mlean(m.L)}',f'  noiseFactor := {mlean(m.N)}',
           f'  noiseFloor := {qlean(m.sigma)}',f'  mean := {vlean(m.mean)}',f'  observation := {vlean(m.observation)}','',
           f'def outputs : Fin {a} → Matrix (Fin {n}) (Fin {n}) ℚ := !['+', '.join(mlean(x) for x in m.outputs)+']',
           f'def inputs : Fin {b} → Matrix (Fin {k}) (Fin {k}) ℚ := !['+', '.join(mlean(x) for x in m.inputs)+']','']
    valid=[]
    for i,c in enumerate(cs):
        lines += [f'def candidate{i} : RationalCandidate (Fin {n}) (Fin {k}) (Fin {a}) (Fin {b}) where',
                  f'  gain := {mlean(c.gain)}',f'  packetUpper := {mlean(c.upper)}',f'  innovationUpper := {qlean(c.innovation_upper)}','']
        ok=c.valid(m);valid.append(ok)
        lines += [f'theorem candidate{i}_checked : checkCandidate model outputs inputs candidate{i} = {str(ok).lower()}  := by decide +kernel','']
        if ok and c.tolerance(m,eps):
            lines += [f'theorem candidate{i}_tolerance : checkTolerance model candidate{i} {qlean(eps)} = true  := by decide +kernel',
                      f'theorem candidate{i}_posterior_bound :',
                      f'    wasserstein2 model.posterior (model.approximation candidate{i}.gain) ≤ ENNReal.ofReal ({qlean(eps)} : ℝ) := by',
                      f'  simpa using checked_tolerance_bounds_posterior model outputs inputs candidate{i} {qlean(eps)} candidate{i}_checked candidate{i}_tolerance','']
    if valid and valid[0]:
        proposal='['+', '.join(f'candidate{i}' for i in range(1,len(cs)))+']'
        lines += [f'def selected := selectCandidates model outputs inputs candidate0 {proposal}',
                  'theorem selected_checked : checkCandidate model outputs inputs selected = true  := by decide +kernel',
                  'theorem selected_score_nonincrease : candidateScore model selected ≤ candidateScore model candidate0 := by',
                  f'  exact selectCandidates_score_le model outputs inputs candidate0 {proposal}','']
        selected,_=select(m,cs[0],cs[1:])
        if selected.tolerance(m,eps):
            lines += [f'theorem selected_tolerance : checkTolerance model selected {qlean(eps)} = true  := by decide +kernel',
                      'theorem selected_posterior_bound :',
                      f'    wasserstein2 model.posterior (model.approximation selected.gain) ≤ ENNReal.ofReal ({qlean(eps)} : ℝ) := by',
                      f'  simpa using checked_tolerance_bounds_posterior model outputs inputs selected {qlean(eps)} selected_checked selected_tolerance','']
    lines += [f'end Komorebi.ExactPosterior.{namespace}','']
    return '\n'.join(lines)

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--emit-lean',type=Path);ap.add_argument('--namespace',default='GeneratedExactCase')
    a=ap.parse_args();d=json.loads(a.input.read_text());m=Model.parse(d['model']);eps=rational(d['tolerance'])
    cs=[Candidate.parse(c,m) for c in d['candidates']]
    selected,decisions=select(m,cs[0],cs[1:])
    result=dict(schema_version=1,arithmetic='exact rational',input_sha256=m.digest(),
                candidate_checks=[c.valid(m) for c in cs],decisions=decisions,
                selected=selected.to_dict(),selected_score=str(selected.score(m)),
                tolerance=str(eps),within_tolerance=selected.tolerance(m,eps),
                lean_status='not checked by this Python program',
                non_claims=['No floating-point enclosure','No claim of iterative termination or global optimality'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    if a.emit_lean:
        a.emit_lean.parent.mkdir(parents=True,exist_ok=True)
        a.emit_lean.write_text(export_lean(m,cs,eps,a.namespace))
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError) as exc:raise SystemExit(f'INPUT REJECTED: {exc}')
