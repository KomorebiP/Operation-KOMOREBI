"""Exact reference tools for finite polynomial continuous-observation instruments.

Rational input only. This is a theory reference, not a production learner.
A certificate proves the supplied model's internal validity, not truth or
statistical coverage. Polynomial coefficients use ascending powers on [-1,1]
with reference measure du/2. No arbitrary expression evaluation is used.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path
import re
from typing import Any
import sympy as sp

U = sp.Symbol('u', real=True)
MAX_DIM = 12


def rational(value: Any) -> sp.Rational:
    if isinstance(value, bool):
        raise ValueError('Boolean is not a rational coefficient.')
    if isinstance(value, (int, sp.Integer, sp.Rational)):
        return sp.Rational(value)
    if not isinstance(value, str) or len(value) > 500 or not re.fullmatch(r'-?\d+(?:/[1-9]\d*)?', value):
        raise ValueError('Expected an integer or an exact rational string.')
    return sp.Rational(value)


def matrix(rows: Any) -> sp.Matrix:
    if not isinstance(rows, list) or not rows or len(rows) > MAX_DIM:
        raise ValueError('Expected a nonempty bounded matrix.')
    if not all(isinstance(row, list) and 0 < len(row) <= MAX_DIM for row in rows):
        raise ValueError('Expected nonempty matrix rows.')
    if len({len(row) for row in rows}) != 1:
        raise ValueError('Ragged matrix.')
    return sp.Matrix([[rational(x) for x in row] for row in rows])


def encode(M: sp.Matrix) -> list[list[str]]:
    return [[str(sp.cancel(M[i,j])) for j in range(M.cols)] for i in range(M.rows)]


def coeffs(M: sp.Matrix, degree: int | None = None) -> list[sp.Matrix]:
    if degree is None:
        degree = max([sp.Poly(x,U).degree() for x in M if x != 0] or [0])
    return [M.applyfunc(lambda x: sp.expand(x).coeff(U,k)) for k in range(int(degree)+1)]


def polynomial(matrices: list[sp.Matrix]) -> sp.Matrix:
    if not matrices or len(matrices)>17:
        raise ValueError('Polynomial needs 1 to 17 coefficient matrices.')
    shape=matrices[0].shape
    if any(M.shape != shape for M in matrices):
        raise ValueError('Coefficient shapes differ.')
    return sum((M*U**k for k,M in enumerate(matrices)),sp.zeros(*shape))


def zero(M: sp.Matrix) -> bool:
    return all(sp.cancel(x)==0 for x in M)


def moment(k: int) -> sp.Rational:
    if isinstance(k,bool) or not isinstance(k,(int,sp.Integer)) or k<0:
        raise ValueError('Moment index must be a nonnegative integer.')
    return sp.Rational(0) if k%2 else sp.Rational(1,k+1)


def integral(M: sp.Matrix, lo: Any=-1, hi: Any=1) -> sp.Matrix:
    lo,hi=rational(lo),rational(hi)
    if lo < -1 or hi > 1 or lo>=hi:
        raise ValueError('Integration interval must lie in [-1,1] and have positive width.')
    return M.applyfunc(lambda x: sp.integrate(x,(U,lo,hi))/2)


def psd(M: sp.Matrix, *, strict: bool=False) -> bool:
    """Exact Sylvester/principal-minor test. Deliberately limited to small matrices."""
    if M.rows != M.cols or M.rows>6 or M != M.T:
        return False
    if strict:
        return all(M[:k,:k].det()>0 for k in range(1,M.rows+1))
    for k in range(1,M.rows+1):
        for I in combinations(range(M.rows),k):
            if M.extract(I,I).det()<0:
                return False
    return True


def embedding(pencil: list[sp.Matrix], z: sp.Matrix) -> sp.Matrix:
    if z.shape != (len(pencil),1):
        raise ValueError('State does not match the embedding dimension.')
    return sum((z[i]*P for i,P in enumerate(pencil)),sp.zeros(*pencil[0].shape))


def apply_congruences(terms: list[dict], X: sp.Matrix) -> sp.Matrix:
    result=sp.zeros(X.rows)
    for term in terms:
        w=rational(term['weight'])
        if w<0:
            raise ValueError('Negative certificate weight.')
        mul=term.get('multiplier','one')
        if mul not in ['one','one_minus_u_squared']:
            raise ValueError('Unsupported nonnegative multiplier.')
        f=sp.Integer(1) if mul=='one' else 1-U**2
        K=polynomial([matrix(m) for m in term['coefficients']])
        if K.shape != X.shape:
            raise ValueError('Congruence matrix has the wrong shape.')
        result += w*f*K*X*K.T
    return sp.expand(result)


@dataclass
class VerifiedInstrument:
    pencil: list[sp.Matrix]
    mass: sp.Matrix
    initial: sp.Matrix
    operators: dict[str,sp.Matrix]
    verification: dict

    def condition_at(self, action: str, observation: Any, state: sp.Matrix | None=None) -> tuple[sp.Rational,sp.Matrix]:
        y=rational(observation)
        if y < -1 or y > 1:
            raise ValueError('Observation outside the declared support.')
        z=self.initial if state is None else sp.Matrix(state)
        if z.shape != self.initial.shape or not zero(self.mass*z-sp.ones(1,1)) or not psd(embedding(self.pencil,z)):
            raise ValueError('Input state is not in the normalized certified domain.')
        v=self.operators[action].subs(U,y)*z
        density=sp.cancel((self.mass*v)[0])
        if density<=0:
            raise ValueError('Zero-density branch has no specified conditional state.')
        return density,v.applyfunc(lambda x:sp.cancel(x/density))


def verify_certificate(data: dict) -> VerifiedInstrument:
    if data.get('schema')!='komorebi.polynomial-psd-certificate.v1':
        raise ValueError('Unsupported certificate schema.')
    if data.get('reference_measure')!={'support':['-1','1'],'density_wrt_lebesgue':'1/2'}:
        raise ValueError('Unsupported reference measure.')
    pencil=[matrix(M) for M in data['embedding']]
    if not pencil or any(M.shape!=pencil[0].shape or M!=M.T for M in pencil):
        raise ValueError('Embedding pencil must have equally sized symmetric coefficients.')
    d=pencil[0].rows
    if d!=pencil[0].cols or d>6:
        raise ValueError('Embedding size outside the reference checker scope.')
    flat=sp.Matrix.hstack(*(sp.Matrix(list(M)) for M in pencil))
    r=len(pencil)
    if flat.rank()!=r:
        raise ValueError('Embedding is not injective.')
    lam=matrix(data['mass']); z0=matrix(data['initial']); interior=matrix(data['interior'])
    if lam.shape!=(1,r) or z0.shape!=(r,1) or interior.shape!=(r,1):
        raise ValueError('State and mass dimensions do not agree.')
    if lam!=sp.Matrix([[sp.trace(M) for M in pencil]]):
        raise ValueError('Mass is not the embedding trace.')
    if not psd(embedding(pencil,interior),strict=True):
        raise ValueError('No strictly positive interior witness.')
    if not zero(lam*z0-sp.ones(1,1)) or not psd(embedding(pencil,z0)):
        raise ValueError('Invalid initial state.')
    if not data.get('actions'):
        raise ValueError('At least one action is required.')
    ops={}; tested=0
    for action,body in data['actions'].items():
        B=polynomial([matrix(M) for M in body['operator_coefficients']])
        if B.shape!=(r,r):
            raise ValueError('Operator dimension mismatch.')
        if not zero(lam*integral(B)-lam):
            raise ValueError(f'Mass conservation fails for {action}.')
        for j in range(r):
            left=embedding(pencil,B[:,j])
            right=apply_congruences(body['positive_terms'],pencil[j])
            if not zero(left-right):
                raise ValueError(f'Intertwining fails for {action}, basis {j}.')
            tested+=1
        ops[action]=B
    return VerifiedInstrument(pencil,lam,z0,ops,{
        'status':'PASS','dimension':r,'matrix_size':d,'actions':len(ops),
        'exact_polynomial_intertwining_identities':tested,
        'domain':'embedding(state) positive semidefinite',
        'scope':'All observations in [-1,1] and all finite horizons for this supplied model.',
        'truth_or_rank_coverage_verified':False,
    })


def fit_population_moments(data: dict) -> dict:
    """Recover the declared finite polynomial model from exact population tables.

    The caller supplies degree and rank coverage assumptions. This routine does
    not infer them from a finite matrix and does not see a hidden generator.
    """
    if data.get('reference_measure')!={'support':['-1','1'],'density_wrt_lebesgue':'1/2'}:
        raise ValueError('Unsupported observation measure.')
    D=data['degree']
    if isinstance(D,bool) or not isinstance(D,int) or not 0<=D<=8:
        raise ValueError('Degree must be an integer between zero and eight.')
    H=matrix(data['core']);z0=matrix(data['initial_tests']);lam=matrix(data['mass'])
    if H.rows!=H.cols or H.det()==0 or z0.shape!=(H.rows,1) or lam.shape!=(1,H.rows):
        raise ValueError('Malformed or singular core.')
    W=sp.Matrix(D+1,D+1,lambda j,k:moment(j+k));Winv=W.inv();Hinv=H.inv()
    operators={}
    for action,items in data['shifted_moment_tables'].items():
        if len(items)!=D+1:
            raise ValueError('Missing moment table.')
        G=[matrix(g) for g in items]
        if any(g.shape!=H.shape for g in G):
            raise ValueError('Moment table shape mismatch.')
        M=[g*Hinv for g in G]
        operators[action]=[sum((Winv[k,j]*M[j] for j in range(D+1)),sp.zeros(H.rows)) for k in range(D+1)]
    return {'mass':lam,'initial':z0,'operators':operators,'core_determinant':H.det(),
            'moment_gram_determinant':W.det(),'degree_assumed':D,
            'global_rank_coverage_assumed':True,'population_values_not_sampled_estimates':True}


def recognize_template(fitted: dict, template: dict) -> sp.Matrix:
    """Find the unique invertible mass-preserving linear match to a fixed template."""
    n=fitted['mass'].cols
    if fitted['mass'].shape!=(1,n) or set(fitted['operators'])!=set(template['actions']):
        raise ValueError('Template action or dimension mismatch.')
    unknowns=sp.symbols(f't0:{n*n}')
    T=sp.Matrix(n,n,unknowns);equations=[]
    for a,items in fitted['operators'].items():
        other=[matrix(x) for x in template['actions'][a]['operator_coefficients']]
        if len(other)!=len(items):
            raise ValueError('Template degree mismatch.')
        for Bh,B in zip(items,other):
            equations.extend(list(Bh*T-T*B))
    equations.extend(list(fitted['mass']*T-matrix(template['mass'])))
    solutions=sp.linsolve(equations,unknowns)
    if solutions is sp.EmptySet or len(solutions)!=1:
        raise ValueError('No unique template solution.')
    values=next(iter(solutions))
    if any(v.free_symbols for v in values):
        raise ValueError('Template match is underdetermined.')
    T=sp.Matrix(n,n,values)
    if T.det()==0:
        raise ValueError('Template match is singular.')
    return T


def certificate_from_template(fitted: dict,template: dict,T: sp.Matrix) -> dict:
    inv=T.inv();old=[matrix(x) for x in template['embedding']]
    pencil=[embedding(old,inv[:,j]) for j in range(T.rows)]
    actions={a:{'operator_coefficients':[encode(M) for M in fitted['operators'][a]],
                'positive_terms':v['positive_terms']} for a,v in template['actions'].items()}
    certificate={
        'schema':'komorebi.polynomial-psd-certificate.v1',
        'reference_measure':template['reference_measure'],
        'embedding':[encode(M) for M in pencil],
        'mass':encode(fitted['mass']),'initial':encode(fitted['initial']),
        'interior':encode(T*matrix(template['interior'])),'actions':actions,
        'provenance':{'construction':'Exact population moments followed by fixed-template recognition.',
                      'template_supplied':True,'general_domain_discovery':False,
                      'global_rank_and_degree_assumptions_verified':False,
                      'exact_alignment':encode(T)},
    }
    verify_certificate(certificate)
    return certificate


def load_json(path: Path) -> dict:
    if path.stat().st_size>2_000_000:
        raise ValueError('Reference JSON exceeds size limit.')
    result=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(result,dict):
        raise ValueError('Expected a JSON object.')
    return result
