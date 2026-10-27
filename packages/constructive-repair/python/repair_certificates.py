#!/usr/bin/env python3
"""Exact rational constructive repair and an untrusted Lean witness exporter.

Python 3.10+, standard library only. Input D and R are fixed independently of
certificate data. Exact Fraction arithmetic, zero-dimensional matrices, strict
canonical rational decoding, and bounded inputs are supported. This search is
not proved correct in Lean; each exported answer is checked by Lean instead.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math
import re
from typing import Any

MAX_DIM = 32
MAX_BYTES = 4 * 1024 * 1024
MAX_DIGITS = 512
MAX_JSON_NESTING = 128
SCHEMA = 'komorebi.repair.rational.v0.3.0'

class InvalidData(ValueError):
    """Malformed input or invalid certificate. This never means no repair."""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidData(message)

def _integer(value: Any, *, nonnegative: bool = False) -> int:
    require(type(value) is int, 'Expected an integer, not a float or boolean')
    require(not nonnegative or value >= 0, 'Expected a nonnegative integer')
    return value

def rational_pair(value: Any) -> F:
    require(type(value) is list and len(value) == 2, 'Rational must be two decimal strings')
    a, b = value
    require(all(type(x) is str and len(x) <= MAX_DIGITS for x in value), 'Invalid rational digits')
    require(re.fullmatch(r'0|-?[1-9][0-9]*', a) is not None, 'Noncanonical numerator')
    require(re.fullmatch(r'[1-9][0-9]*', b) is not None, 'Denominator must be positive')
    n, d = int(a), int(b)
    require(math.gcd(n, d) == 1, 'Rational pair must be reduced')
    return F(n, d)

@dataclass(frozen=True)
class Mat:
    rows: int
    cols: int
    data: tuple[tuple[F, ...], ...]

    def __post_init__(self) -> None:
        require(type(self.rows) is int and type(self.cols) is int and self.rows >= 0 and self.cols >= 0,
                'Invalid matrix dimensions')
        require(type(self.data) is tuple and all(type(row) is tuple for row in self.data),
                'Matrix storage must be immutable tuples')
        require(len(self.data) == self.rows and all(len(r) == self.cols for r in self.data), 'Matrix shape mismatch')
        require(all(type(x) is F for r in self.data for x in r), 'Matrix entries must be exact Fraction values')

    @staticmethod
    def of(rows: list[list[int | F]], cols: int | None = None) -> Mat:
        if cols is not None:
            require(type(cols) is int and cols >= 0, 'Explicit column count must be a nonnegative integer')
        c = len(rows[0]) if rows else (0 if cols is None else cols)
        require(cols is None or c == cols, 'Explicit column count conflicts with data')
        require(all(type(x) in (int, F) for row in rows for x in row), 'Exact values only')
        return Mat(len(rows), c, tuple(tuple(F(x) for x in row) for row in rows))

    @staticmethod
    def zero(r: int, c: int) -> Mat:
        return Mat(r, c, tuple(tuple(F(0) for _ in range(c)) for _ in range(r)))

    @staticmethod
    def eye(n: int) -> Mat:
        return Mat(n, n, tuple(tuple(F(i == j) for j in range(n)) for i in range(n)))

    def __matmul__(self, b: Mat) -> Mat:
        require(self.cols == b.rows, 'Matrix product shape mismatch')
        return Mat(self.rows, b.cols, tuple(tuple(sum((self.data[i][k]*b.data[k][j]
            for k in range(self.cols)), F(0)) for j in range(b.cols)) for i in range(self.rows)))

    def __add__(self, b: Mat) -> Mat:
        require((self.rows,self.cols)==(b.rows,b.cols), 'Matrix sum shape mismatch')
        return Mat(self.rows,self.cols,tuple(tuple(a+x for a,x in zip(r,s)) for r,s in zip(self.data,b.data)))

    def __neg__(self) -> Mat:
        return Mat(self.rows,self.cols,tuple(tuple(-x for x in r) for r in self.data))

    @property
    def T(self) -> Mat:
        return Mat(self.cols,self.rows,tuple(tuple(self.data[i][j] for i in range(self.rows)) for j in range(self.cols)))

    def columns(self, indices: list[int]) -> Mat:
        require(all(type(j) is int and 0 <= j < self.cols for j in indices), 'Column index out of range')
        return Mat(self.rows,len(indices),tuple(tuple(r[j] for j in indices) for r in self.data))

    def select_rows(self, indices: list[int]) -> Mat:
        require(all(type(i) is int and 0 <= i < self.rows for i in indices), 'Row index out of range')
        return Mat(len(indices),self.cols,tuple(self.data[i] for i in indices))

    def join(self, b: Mat) -> Mat:
        require(self.rows==b.rows,'Column join shape mismatch')
        return Mat(self.rows,self.cols+b.cols,tuple(x+y for x,y in zip(self.data,b.data)))

    def to_wire(self) -> dict[str, Any]:
        return {'rows':self.rows,'cols':self.cols,
                'entries':[[[str(x.numerator),str(x.denominator)] for x in row] for row in self.data]}

    @staticmethod
    def from_wire(value: Any) -> Mat:
        require(type(value) is dict and set(value)=={'rows','cols','entries'}, 'Invalid matrix record keys')
        r,c=_integer(value['rows'],nonnegative=True),_integer(value['cols'],nonnegative=True)
        require(r<=MAX_DIM and c<=MAX_DIM,'Matrix dimension resource limit')
        data=value['entries']
        require(type(data) is list and len(data)==r,'Wrong number of rows')
        require(all(type(row) is list and len(row)==c for row in data),'Wrong number of columns')
        return Mat(r,c,tuple(tuple(rational_pair(x) for x in row) for row in data))

    def display(self) -> str:
        return f'{self.rows} x {self.cols}: ' + repr([[str(x) for x in row] for row in self.data])


def rref(a: Mat) -> tuple[Mat, list[int]]:
    """Deterministic exact row reduction; no external linear algebra is trusted."""
    x=[list(row) for row in a.data]; pivots=[]; r=0
    for j in range(a.cols):
        if r == a.rows: break
        pivot=next((i for i in range(r,a.rows) if x[i][j]),None)
        if pivot is None: continue
        x[r],x[pivot]=x[pivot],x[r]
        v=x[r][j];x[r]=[z/v for z in x[r]]
        for i in range(a.rows):
            if i != r:
                v=x[i][j]
                if v: x[i]=[u-v*z for u,z in zip(x[i],x[r])]
        pivots.append(j);r+=1
    return Mat.of(x,a.cols),pivots

def inverse(a: Mat) -> Mat:
    require(a.rows==a.cols,'Inverse requires a square matrix')
    red,piv=rref(a.join(Mat.eye(a.rows)))
    require(piv[:a.cols]==list(range(a.cols)),'Singular matrix')
    require(red.columns(list(range(a.cols)))==Mat.eye(a.rows),'Inverse construction failed')
    return red.columns(list(range(a.cols,2*a.cols)))

def canonical(value: Any) -> bytes:
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out={}
    for k,v in items:
        require(k not in out,'Duplicate JSON key: '+k)
        out[k]=v
    return out

def read_json(path: Path) -> Any:
    # Bound the bytes actually read, not an earlier, potentially stale stat.
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, 'JSON size resource limit')
    # Do not rely on the interpreter's configurable recursion limit.
    depth = 0
    quoted = escaped = False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            require(depth <= MAX_JSON_NESTING, 'JSON nesting resource limit')
        elif byte in (93, 125):
            depth -= 1

    def reject_number(x):
        raise InvalidData('Floating-point or nonfinite JSON is forbidden: ' + x)
    def bounded_integer(x):
        require(len(x.lstrip('-')) <= MAX_DIGITS, 'JSON integer digit resource limit')
        return int(x)
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                          parse_float=reject_number, parse_constant=reject_number,
                          parse_int=bounded_integer)
    except (UnicodeError, RecursionError, json.JSONDecodeError) as exc:
        raise InvalidData('Malformed or excessively nested JSON') from exc

def problem(D: Mat, R: Mat) -> dict[str,Any]:
    require(D.rows==R.rows,'Residual target mismatch')
    return {'schema':SCHEMA,'kind':'free_linear','D':D.to_wire(),'R':R.to_wire()}

def parse_problem(p: Any) -> tuple[Mat,Mat]:
    require(type(p) is dict and set(p)=={'schema','kind','D','R'},'Invalid problem keys')
    require(p['schema']==SCHEMA and p['kind']=='free_linear','Wrong problem schema')
    D,R=Mat.from_wire(p['D']),Mat.from_wire(p['R'])
    require(D.rows==R.rows,'Residual target mismatch')
    return D,R

def construct(p: dict[str, Any], trace: list[str] | None=None) -> dict[str,Any]:
    """Construct P,K,L,F,G,J,Q and the attaining E,U,W for fixed D,R."""
    D,R=parse_problem(p);m,n,s=D.rows,D.cols,R.cols
    _,piv=rref(D); k=len(piv); d=m-k
    B=D.columns(piv); complement=[]
    for i in range(m):
        trial=B.join(Mat.eye(m).columns([i]))
        if len(rref(trial)[1])>B.cols:
            B=trial;complement.append(i)
    require(B.cols==m,'Failed to complete a target basis')
    BInv=inverse(B)
    data=[[F(0) for _ in range(m)] for _ in range(n)]
    for j,col in enumerate(piv): data[col]=list(BInv.data[j])
    P=Mat.of(data,m);K=Mat.eye(m).columns(complement);L=BInv.select_rows(list(range(k,m)))
    C=L@R;_,rpiv=rref(C);t=len(rpiv)
    FF=C.columns(rpiv);Q=Mat.eye(s).columns(rpiv)
    _,independent_rows=rref(FF.T)
    select=Mat.eye(d).select_rows(independent_rows)
    J=inverse(FF.select_rows(independent_rows))@select
    G=J@C
    E=K@FF;U=-(P@R);W=-G;H=J@L
    matrices={'P':P,'K':K,'L':L,'F':FF,'G':G,'J':J,'Q':Q,'E':E,'U':U,'W':W,'H':H}
    cert={'schema':SCHEMA,'kind':'optimal_free_repair','problem_sha256':digest(p),'d':d,'t':t,
          'matrices':{key:value.to_wire() for key,value in matrices.items()}}
    check_certificate(p,cert)
    if trace is not None:
        trace.extend([f'rank(D)={k}; image column indices={piv}; complement axes={complement}',
                      f'Obstruction coordinates C=LR: {C.display()}',
                      f'Independent residual columns={rpiv}; t={t}',
                      *[key+' = '+a.display() for key,a in matrices.items()],
                      'LD=0 PASS; DP+KL=I PASS; LR=FG PASS; JLRQ=I_t PASS',
                      'DU+EW=-R PASS; E=KF PASS; U=-PR PASS; W=-G PASS',
                      'HD=0 PASS; HRQ=I_t PASS'])
    return cert

MATRIX_KEYS={'P','K','L','F','G','J','Q','E','U','W','H'}
def decode_certificate(p: dict[str,Any],c: Any) -> dict[str,Mat]:
    require(len(canonical(c)) <= MAX_BYTES, 'Certificate size resource limit')
    D,R=parse_problem(p)
    require(type(c) is dict and set(c)=={'schema','kind','problem_sha256','d','t','matrices'},'Invalid certificate keys')
    require(c['schema']==SCHEMA and c['kind']=='optimal_free_repair','Wrong certificate schema')
    require(c['problem_sha256']==digest(p),'Certificate is bound to a different original problem')
    d,t=_integer(c['d'],nonnegative=True),_integer(c['t'],nonnegative=True)
    require(d<=MAX_DIM and t<=MAX_DIM,'Certificate dimension limit')
    require(type(c['matrices']) is dict and set(c['matrices'])==MATRIX_KEYS,'Missing/extra certificate matrices')
    ms={k:Mat.from_wire(v) for k,v in c['matrices'].items()}
    m,n,s=D.rows,D.cols,R.cols
    shapes={'P':(n,m),'K':(m,d),'L':(d,m),'F':(d,t),'G':(t,s),'J':(t,d),
            'Q':(s,t),'E':(m,t),'U':(n,s),'W':(t,s),'H':(t,m)}
    for k,a in ms.items():require((a.rows,a.cols)==shapes[k],f'Wrong shape for {k}')
    return ms

def check_certificate(p: dict[str,Any],c: Any) -> dict[str,bool]:
    D,R=parse_problem(p); a=decode_certificate(p,c);d,t=c['d'],c['t'];m,n,s=D.rows,D.cols,R.cols
    P,K,L,FF,G,J,Q=(a[k] for k in ['P','K','L','F','G','J','Q'])
    checks={
        'detector_annihilation': L@D==Mat.zero(d,n),
        'complete_split': D@P+K@L==Mat.eye(m),
        'residual_factorization': L@R==FF@G,
        'rank_lower_witness': J@L@R@Q==Mat.eye(t),
        'returned_E': a['E']==K@FF,
        'returned_U': a['U']==-(P@R),
        'returned_W': a['W']==-G,
        'original_equations': D@a['U']+a['E']@a['W']==-R,
        'returned_H': a['H']==J@L,
        'dimension_annihilation': a['H']@D==Mat.zero(t,n),
        'dimension_lower_witness': a['H']@R@Q==Mat.eye(t)}
    for label,passed in checks.items():require(passed,'Failed certificate identity: '+label)
    return checks

def lean_matrix(a: Mat) -> str:
    """Only numeric tokens generated from exact integers enter Lean source."""
    if a.rows==0: return '(Matrix.of fun i => Fin.elim0 i)'
    if a.cols==0: return '(Matrix.of fun _ j => Fin.elim0 j)'
    def rat(x: F) -> str:
        if x.denominator==1:return f'({x.numerator} : ℚ)'
        return f'(({x.numerator} : ℚ) / {x.denominator})'
    return '(Matrix.of !['+', '.join('!['+', '.join(rat(x) for x in row)+']' for row in a.data)+'])'

def lean_wire(a: Mat) -> str:
    if a.rows==0: return '(Matrix.of fun i => Fin.elim0 i)'
    if a.cols==0: return '(Matrix.of fun _ j => Fin.elim0 j)'
    return '(Matrix.of !['+', '.join('!['+', '.join(
        f'({x.numerator}, {x.denominator})' for x in row)+']' for row in a.data)+'])'

def emit_matrix(name: str,a: Mat) -> list[str]:
    return [f'def wire{name} : WireMatrix {a.rows} {a.cols} := {lean_wire(a)}',
            f'def {name} : Mat {a.rows} {a.cols} := decodeWireMatrix wire{name}']

def emit_input(p: dict[str,Any],namespace: str) -> str:
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',namespace) is not None,'Unsafe namespace')
    D,R=parse_problem(p)
    return '\n'.join(['import KomorebiRepair.Wire',
      '-- Fixed original problem, emitted independently of certificate contents.',
      f'-- Canonical problem SHA256: {digest(p)}',
      'set_option autoImplicit false', 'set_option maxRecDepth 100000',
      'open KomorebiRepair.RationalCertificates', f'namespace {namespace}',
      *emit_matrix('D',D),*emit_matrix('R',R),
      'theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel',
      f'end {namespace}'])+'\n'

def emit_certificate(p: dict[str,Any],c: dict[str,Any],namespace: str,input_module: str,
                     *,check: bool=True) -> str:
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]*',input_module) is not None,'Unsafe import')
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',namespace) is not None,'Unsafe namespace')
    D,R=parse_problem(p);a=decode_certificate(p,c)
    if check:check_certificate(p,c)
    lines=[f'import {input_module}', '-- Untrusted certificate data; original D and R are fixed imports.',
           'set_option autoImplicit false','set_option maxRecDepth 100000',
           'set_option maxHeartbeats 3000000','open KomorebiRepair.RationalCertificates',
           f'namespace {namespace}']
    keys=['P','K','L','F','G','J','Q','E','U','W','H']
    for name in keys:lines+=emit_matrix(name,a[name])
    lines += ['theorem certificate_encoding_valid : '+' ∧ '.join('WireMatrixValid wire'+k for k in keys)+' := by decide +kernel',
              'theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel',
              'theorem original_equations_checked : D * U + E * W = -R := by decide +kernel',
              'theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel',
              f'theorem optimal : D * U + E * W = -R ∧\n'
              f'    ∀ (w : ℕ) (Eprime : Mat {D.rows} w) (Uprime : Mat {D.cols} {R.cols}) (Wprime : Mat w {R.cols}),\n'
              f'    D * Uprime + Eprime * Wprime = -R → {c["t"]} ≤ w := by\n'
              '  exact ⟨original_equations_checked,\n'
              '    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩',
              'end '+namespace]
    return '\n'.join(lines)+'\n'


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    a=sub.add_parser('solve');a.add_argument('input',type=Path);a.add_argument('output',type=Path);a.add_argument('--trace',type=Path)
    a=sub.add_parser('check');a.add_argument('input',type=Path);a.add_argument('certificate',type=Path)
    a=sub.add_parser('export');a.add_argument('input',type=Path);a.add_argument('certificate',type=Path);a.add_argument('output_dir',type=Path);a.add_argument('--namespace',default='ExportedRepair')
    args=ap.parse_args()
    try:
        p=read_json(args.input)
        if args.command=='solve':
            trace=[];c=construct(p,trace);args.output.write_bytes(canonical(c))
            if args.trace:args.trace.write_text('\n'.join(trace)+'\n', encoding="utf-8")
            print(json.dumps({'status':'PYTHON_CERTIFICATE_VALID','minimum_added_dimension':c['t'],'problem_sha256':digest(p)}))
        else:
            c=read_json(args.certificate);checks=check_certificate(p,c)
            if args.command=='check': print(json.dumps({'status':'PYTHON_CERTIFICATE_VALID','checks':checks}))
            else:
                args.output_dir.mkdir(parents=True,exist_ok=True)
                (args.output_dir/'Input.lean').write_text(emit_input(p,args.namespace), encoding="utf-8")
                (args.output_dir/'Certificate.lean').write_text(emit_certificate(p,c,args.namespace,'Input'), encoding="utf-8")
                print('Exported Input.lean and Certificate.lean. Compile both with the provided Lean package; Python acceptance is not kernel acceptance.')
        return 0
    except (InvalidData,ValueError,OSError,KeyError) as e:
        print(json.dumps({'status':'UNRESOLVED_INVALID_DATA','error':str(e)}));return 2

if __name__=='__main__':raise SystemExit(main())
