"""Exact, restricted operator-only ellipsoidal certificate discovery and replay.

No template or hidden generator is imported. Discovery uses a one-dimensional
invariant-form space from an operator ratio and a rational rank-one image to
propose scale. Every candidate must pass the independent polynomial verifier.
Failure means a withheld certificate in this restricted search, not invalidity.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import permutations
from typing import Any
import sympy as sp
from continuous_reference import U, rational, matrix, encode, polynomial, coeffs, zero, integral, psd


def scalar_coeffs(p: sp.Expr) -> list[str]:
    p=sp.Poly(sp.cancel(p),U,domain=sp.QQ)
    return [str(p.nth(k)) for k in range(max(0,int(p.degree()))+1)] if p else ['0']


def scalar_poly(data: Any) -> sp.Expr:
    if not isinstance(data,list) or not 1<=len(data)<=33:
        raise ValueError('Invalid bounded scalar coefficient list.')
    return sum((rational(x)*U**k for k,x in enumerate(data)),sp.Integer(0))


def sos_value(items: Any) -> sp.Expr:
    if not isinstance(items,list) or len(items)>64:
        raise ValueError('Invalid scalar SOS list.')
    ans=sp.Integer(0)
    for term in items:
        w=rational(term['weight'])
        if w<0: raise ValueError('Negative SOS weight.')
        g=term.get('multiplier','one')
        if g not in ('one','one_minus_u_squared'): raise ValueError('Invalid SOS multiplier.')
        ans+=w*(1 if g=='one' else 1-U**2)*scalar_poly(term['coefficients'])**2
    return sp.expand(ans)


def global_sos(p: sp.Expr) -> list[dict]:
    """Factor-based sufficient rational SOS construction, not a general SDP."""
    p=sp.Poly(sp.cancel(p),U,domain=sp.QQ)
    if p.is_zero: return []
    c,factors=sp.factor_list(p.as_expr(),U)
    if c<=0: raise ValueError('Factor-based SOS proposal withheld.')
    terms=[(c,sp.Integer(1))]
    for fac,power in factors:
        square=fac**(power//2)
        terms=[(w,sp.expand(q*square)) for w,q in terms]
        if power%2:
            f=sp.Poly(fac,U,domain=sp.QQ)
            if f.degree()!=2: raise ValueError('Unresolved odd factor in scalar SOS proposal.')
            a,b,d=f.all_coeffs(); margin=d-b*b/(4*a)
            if a<=0 or margin<0: raise ValueError('Quadratic factor is not globally nonnegative.')
            pieces=[(a,U+b/(2*a))]
            if margin>0: pieces.append((margin,sp.Integer(1)))
            terms=[(w*v,sp.expand(q*r)) for w,q in terms for v,r in pieces]
    out=[{'weight':str(w),'coefficients':scalar_coeffs(q)} for w,q in terms]
    if sp.expand(sos_value(out)-p.as_expr())!=0: raise ArithmeticError('SOS construction identity failed.')
    return out


def centered_form(center: sp.Matrix, H: sp.Matrix) -> tuple[sp.Matrix,sp.Matrix]:
    d=H.rows
    if H.shape!=(d,d) or center.shape!=(d,1): raise ValueError('Geometry shape mismatch.')
    S=sp.eye(d+1);S[1:,0]=-center
    return S.T*sp.diag(1,-H)*S,S


def residual_sos(items: Any,r: int) -> sp.Matrix:
    if not isinstance(items,list) or len(items)>64: raise ValueError('Invalid matrix SOS list.')
    out=sp.zeros(r)
    for term in items:
        w=rational(term['weight'])
        if w<0: raise ValueError('Negative matrix SOS weight.')
        g=term.get('multiplier','one')
        if g not in ('one','one_minus_u_squared'): raise ValueError('Invalid matrix SOS multiplier.')
        vec=polynomial([matrix(m) for m in term['vector_coefficients']])
        if vec.shape!=(r,1): raise ValueError('Wrong matrix SOS vector size.')
        out+=w*(1 if g=='one' else 1-U**2)*vec*vec.T
    return out.applyfunc(sp.expand)


@dataclass
class VerifiedQuadratic:
    center: sp.Matrix
    metric: sp.Matrix
    form: sp.Matrix
    initial: sp.Matrix
    operators: dict[str,sp.Matrix]
    report: dict

    def contains(self,z: sp.Matrix) -> bool:
        return z.shape==self.initial.shape and bool(z[0]>=0) and bool((z.T*self.form*z)[0]>=0)

    def condition_at(self,action: str,u: Any,z: sp.Matrix|None=None):
        val=rational(u)
        if not -1<=val<=1: raise ValueError('Observation outside support.')
        z=self.initial if z is None else sp.Matrix(z)
        if not self.contains(z) or z[0]!=1: raise ValueError('Input is not a normalized domain state.')
        v=self.operators[action].subs(U,val)*z
        if v[0]<=0: raise ValueError('Zero-density branch has no posterior.')
        out=v/v[0]
        if not self.contains(out): raise ArithmeticError('Verified update left its cone.')
        return v[0],out


def verify_quadratic(data: dict) -> VerifiedQuadratic:
    if data.get('schema')!='komorebi.ellipsoidal-polynomial-certificate.v1': raise ValueError('Unknown schema.')
    if data.get('reference_measure')!={'support':['-1','1'],'density_wrt_lebesgue':'1/2'}: raise ValueError('Wrong reference measure.')
    c=matrix(data['center']);H=matrix(data['metric']);z0=matrix(data['initial'])
    if H.rows>4 or not psd(H,strict=True) or c.shape!=(H.rows,1): raise ValueError('Metric must be positive definite in dimension at most four.')
    Q,_=centered_form(c,H);r=H.rows+1;lam=sp.zeros(1,r);lam[0]=1
    if matrix(data['mass'])!=lam or z0.shape!=(r,1) or z0[0]!=1 or (z0.T*Q*z0)[0]<0: raise ValueError('Invalid mass or initial state.')
    if not isinstance(data.get('actions'),dict) or not data['actions']: raise ValueError('No action family.')
    ops={}; identities=[]
    for action,d in data['actions'].items():
        B=polynomial([matrix(M) for M in d['operator_coefficients']])
        if B.shape!=(r,r): raise ValueError('Wrong operator size.')
        tau=sos_value(d['tau_sos']);R=residual_sos(d['residual_sos'],r)
        if not zero(B.T*Q*B-tau*Q-R): raise ValueError(f'Quadratic invariance identity failed: {action}')
        row=lam*B;v=row[:,1:];beta=sp.expand(row[0]+(v*c)[0]);dual=sp.expand(beta**2-(v*H.inv()*v.T)[0])
        if sp.expand(beta-sos_value(d['mass_orientation_sos']))!=0: raise ValueError(f'Mass orientation failed: {action}')
        if sp.expand(dual-sos_value(d['dual_margin_sos']))!=0: raise ValueError(f'Dual-cone margin failed: {action}')
        if not zero(lam*integral(B)-lam): raise ValueError(f'Integrated mass failed: {action}')
        ops[action]=B;identities.append({'action':action,'tau':scalar_coeffs(tau),'orientation':scalar_coeffs(beta),'dual_margin':scalar_coeffs(dual),'quadratic_residual_zero':zero(R)})
    report={'passed':True,'schema':data['schema'],'dimension':r,'action_count':len(ops),'identities':identities,
            'scope':'Supplied model, all u in [-1,1] and all finite horizons. No data or true-model coverage claim.',
            'template_used_by_replay':False,'lean_kernel_run':False}
    return VerifiedQuadratic(c,H,Q,z0,ops,report)


def propose_conformal_certificate(fitted: dict,c: sp.Matrix,H: sp.Matrix,provenance: dict) -> dict:
    Q,_=centered_form(c,H);r=Q.rows;lam=fitted['mass']
    ij=next((i,j) for i in range(r) for j in range(r) if Q[i,j]!=0)
    actions={}
    for name,items in fitted['operators'].items():
        B=polynomial(items);J=B.T*Q*B;tau=sp.cancel(J[ij[0],ij[1]]/Q[ij[0],ij[1]])
        if not zero(J-tau*Q): raise ValueError('Candidate does not meet conformal search restriction.')
        row=lam*B;v=row[:,1:];beta=sp.expand(row[0]+(v*c)[0]);dual=sp.expand(beta**2-(v*H.inv()*v.T)[0])
        actions[name]={'operator_coefficients':[encode(m) for m in items],'tau_sos':global_sos(tau),
                       'residual_sos':[],'mass_orientation_sos':global_sos(beta),'dual_margin_sos':global_sos(dual)}
    data={'schema':'komorebi.ellipsoidal-polynomial-certificate.v1',
          'reference_measure':{'support':['-1','1'],'density_wrt_lebesgue':'1/2'},
          'center':encode(c),'metric':encode(H),'initial':encode(fitted['initial']),'mass':encode(lam),
          'actions':actions,'provenance':provenance}
    verify_quadratic(data)
    return data


def discover_quadratic(fitted: dict) -> dict:
    """Restricted exact synthesis from operators, with no structural template.

    Requires a two-dimensional spatial section, a suitable ratio at a rational
    anchor, a one-dimensional invariant-metric space, and a rational rank-one
    branch image. Search anchors are explicit. Independent verification is final.
    """
    if fitted['mass']!=sp.Matrix([[1,0,0]]): raise ValueError('Search requires three mass-first coordinates.')
    ops={a:polynomial(x) for a,x in fitted['operators'].items()}
    h0,h1,h2=sp.symbols('h0:3');Hsym=sp.Matrix([[h0,h1],[h1,h2]])
    tries=[]
    for num,den in permutations(sorted(ops),2):
        for anchor in [sp.Integer(0),sp.Integer(-1),sp.Integer(1),sp.Rational(1,2),sp.Rational(-1,2)]:
            if ops[den].subs(U,anchor).det()==0: continue
            F=ops[num].subs(U,anchor)*ops[den].subs(U,anchor).inv()
            if F[0,:]!=sp.Matrix([[1,0,0]]): continue
            A=F[1:,1:];b=F[1:,0]
            if (sp.eye(2)-A).det()==0: continue
            c=(sp.eye(2)-A).inv()*b
            eq=list(A.T*Hsym*A-Hsym)
            coeff,_=sp.linear_eq_to_matrix(eq,(h0,h1,h2));ns=coeff.nullspace()
            if len(ns)!=1: continue
            h=ns[0];H=sp.Matrix([[h[0],h[1]],[h[1],h[2]]])
            if psd(-H,strict=True):H=-H
            if not psd(H,strict=True): continue
            for action,B in ops.items():
                det=sp.Poly(sp.expand(B.det()),U,domain=sp.QQ)
                if det.is_zero: continue
                for root in sorted(sp.polys.polytools.ground_roots(det).keys()):
                    if not -1<=root<=1:continue
                    C=B.subs(U,root)
                    if C.rank()!=1:continue
                    j=next((j for j in range(3) if C[0,j]!=0),None)
                    if j is None:continue
                    v=C[:,j]/C[0,j];d=v[1:,0]-c;scale=(d.T*H*d)[0]
                    if scale<=0:continue
                    Hn=H/scale
                    prov={'method':'Operator-ratio invariant-form synthesis with rank-one scale proposal.',
                          'template_supplied':False,'hidden_generator_supplied':False,
                          'population_values_not_sampled_estimates':True,
                          'true_rank_degree_or_distribution_coverage_verified':False,
                          'general_domain_synthesis':False,'ratio_actions':[num,den],'anchor':str(anchor),
                          'scale_action':action,'scale_observation':str(root),'invariant_form_dimension':1,
                          'earlier_withheld_candidates':tries}
                    try:return propose_conformal_certificate(fitted,c,Hn,prov)
                    except ValueError as exc:tries.append(str(exc))
    raise ValueError('No certificate in this restricted operator-ratio search; model validity is undecided.')
