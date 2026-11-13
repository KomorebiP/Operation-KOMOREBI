"""Exact lossless parity duals and support for the written one-R bound.
Author: Komorebi P. Finite computations do not replace the universal graph proof.
"""
from fractions import Fraction as F
from itertools import combinations
import json
from exact_phasor import C,solve,response as reference
from natural_graph_polynomials import determinant,pair,value
from pure_type_margins import SAMPLES,gamma
from regular_balanced import CORES,endpoint
def inverse(A):
    n=len(A);cols=[solve(A,[F(int(i==j)) for i in range(n)]) for j in range(n)]
    out=[list(row) for row in zip(*cols)]
    assert all(sum(A[i][k]*out[k][j] for k in range(n))==int(i==j) for i in range(n) for j in range(n))
    return out

def parity_certificate(p_parity):
    columns=[('P',k) for k in range(5) if k%2==p_parity]+[('Q',k) for k in range(5) if k%2!=p_parity]
    rows=[[(1-gamma(s))*s**k if which=='P' else -(1+gamma(s))*s**k for which,k in columns] for s in SAMPLES]
    candidates=[]
    for ids in combinations(range(7),5):
        A=[rows[j] for j in ids];det=determinant(A)
        if not det:continue
        weights=solve([list(row) for row in zip(*A)],[F(1)]*5)
        assert all(sum(w*A[j][k] for j,w in enumerate(weights))==1 for k in range(5))
        norm=sum(abs(w) for w in weights);margin=1/(16*norm)
        candidates.append((margin,ids,weights,det))
    assert candidates
    margin,ids,weights,det=max(candidates,key=lambda r:(r[0],r[1]))
    return {'P_parity':p_parity,'Q_parity':1-p_parity,'columns':columns,'sample_indices':ids,
      'weights':list(map(str,weights)),'row_minor_determinant':str(det),'weight_l1_norm':str(sum(abs(w) for w in weights)),
      'weak_reflection_margin':str(margin),'invertible_five_row_subsets':len(candidates)}

def main():
    certs=[parity_certificate(p) for p in (0,1)]
    smallest=min([F(c['weak_reflection_margin']) for c in certs]+[F(1,2)])
    mu=F(1)
    while mu>smallest:mu/=10
    assert mu>0 and all(abs(sign-gamma(s))>=mu for sign in (-1,1) for s in SAMPLES)
    V=[[s**k for k in range(7)] for s in SAMPLES];inv=inverse(V)
    norm=max(sum(abs(x) for x in row) for row in inv);cross=568*norm
    eta=min(F(2,10**14),mu/8);gamma_min=eta**10/64
    delta=min(F(1,10**150),gamma_min/cross,mu/8,(F(1,10**13)-4*eta)/2)
    assert delta>0 and delta+4*eta<F(1,10**13) and delta+mu/4<mu
    assert cross*delta<2*gamma_min
    cases=parity_checks=one_R_checks=common_zero=0
    fixtures=[]
    for kind,base in CORES.items():
        fixtures.append([e for e in base if e[0]!='R'])
    for Lpos in combinations(range(4),2):
        labels=(1,2,3,4,0)
        fixtures.append([('L' if j in Lpos else 'C',labels[j],labels[j+1],F(j+1,2)) for j in range(4)])
    for graph in fixtures:
        p=pair(graph);P,Q=p['P'],p['Q'];ps={j%2 for j,x in enumerate(P) if x};qs={j%2 for j,x in enumerate(Q) if x}
        assert len(ps)==len(qs)==1 and ps!=qs
        err=max(abs(reference(graph,C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
        assert err>=mu;cases+=1;parity_checks+=1
        for resistance in (F(1,3),F(2)):
            g=graph+[('R',1,0,resistance)];q=pair(g);U,W=q['P'],q['Q']
            assert all(x>=gamma_min for x in U+W if x)
            assert endpoint(U,W)==endpoint(U,W,True)==resistance
            if not U[0] and not W[0]:common_zero+=1
            one_R_checks+=1
    nonparity=pair([('R',1,0,F(1)),('L',1,0,F(1))])
    assert any(len({j%2 for j,x in enumerate(nonparity[k]) if x})==2 for k in ('P','Q'))
    print(json.dumps({'status':'PASS','base_checkpoint':'f88939b267fe6e03af555727a1e770985395bba5',
      'finite_scope':'Two exact parity/normalization dual identities,21 row subsets each; one7x7 interpolation inverse and fixed rational physical controls. No arbitrary physical parameters searched.',
      'lossless_LC_certificates':certs,'selected_lossless_weak_margin':str(mu),
      'cross_interpolation':{'inverse_infinity_norm':str(norm),'cross_coefficient_error_multiplier':str(cross),
        'reason':'|Delta(s)|<=(16*71/2)*max reflection error; Delta degree<=6.'},
      'one_R_support':{'shared_physical_box_eta':str(eta),'normalized_positive_coefficient_floor':str(gamma_min),
        'written_strict_margin':str(delta),'LC_rounding_cost_max':str(4*eta),'R_extreme_surgery_cost_max':str(mu/4),
        'required_cross_lower_bound':str(2*gamma_min),'checked_cross_upper_bound':str(cross*delta),
        'status':'Finite rational support only; the universal one-R argument is proved separately in LOW_RESISTOR_MARGINS.md at the written self-review level.'},
      'controls':{'lossless_physical_graphs':cases,'parity_checks':parity_checks,'one_R_finite_equal_endpoint_checks':one_R_checks,
        'physical_structural_common_zero_cases':common_zero,'resistive_nonparity_guard':1},
      'non_claims':['No useful arbitrary-R balanced margin','No whole-placement count change','No engineering-sized arbitrary-R separator','No independent/formal, hardware or priority claim']},indent=2))

if __name__=="__main__":
    if not __debug__:raise RuntimeError("Assertions must remain enabled")
    main()
