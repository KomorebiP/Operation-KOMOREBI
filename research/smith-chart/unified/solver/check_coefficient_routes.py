"""Exact independent controls for the coefficient/shape/template phase.
Author: Komorebi P. Finite controls do not replace the written universal proofs.
"""
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations,product
import json
import coefficient_fiber as cf
import series_type_margins as sm
from exact_phasor import C,response
from pure_type_margins import SAMPLES,P,Q,gamma
from reactive_skeletons import generate,no_parallel_same_kind
from universal_reactive_template import lift,verify_lift
from transfer_barriers import check_example
from single_kind_minimum import checks as minimum_checks


def dot(a,b):return sum(x*y for x,y in zip(a,b))
def ev(poly,s):return sum(x*s**i for i,x in enumerate(poly))


def quotient(poly,divisor):
    rem=list(poly);out=[F(0)]*(len(poly)-len(divisor)+1)
    for k in reversed(range(len(out))):
        out[k]=rem[k+len(divisor)-1]/divisor[-1]
        for j,a in enumerate(divisor):rem[k+j]-=out[k]*a
    assert not any(rem)
    return out


def compositions(total,parts):
    if parts==1:yield (total,);return
    for first in range(total+1):
        for rest in compositions(total-first,parts-1):yield (first,)+rest


def fiber_checks():
    records=[];negative=[];controls=0;vertices_checked=0
    for q in (3,4):
        rec=cf.certificate(q);cf.verify(rec);n=2*q+2
        N=[[F(x) for x in row] for row in rec['inverse']]
        indices=rec['sample_indices'];M=cf.matrix(q,indices);bound=F(rec['coefficient_error_factor'])
        x0=cf.fiber(q,list(map(F,rec['interior_multiplier'])));rho=F(rec['interior_minimum_coefficient'])
        vertices=[list(map(F,row)) for row in rec['exact_nonnegative_fiber']['multiplier_vertices']]
        # Independently enumerate every polygon vertex as a feasible intersection
        # of two boundary lines in (a,c); no producer vertex list is used here.
        if q==4:
            lines=((F(1),F(0),F(0)),(F(0),F(1),F(0)),
                   (F(7,9),F(1),F(1,30)),(F(1),F(2,3),F(1,30)))
            found=set()
            for (A,B,D),(E,G,H) in combinations(lines,2):
                det=A*G-B*E
                if not det:continue
                a=(D*G-B*H)/det;c=(A*H-D*E)/det;b=F(1,30)-a-c
                if a>=0 and c>=0 and b>=-2*a/9 and b>=-c/3:found.add((a,b,c))
            assert found==set(map(tuple,vertices))
        for weights in compositions(6,len(vertices)):
            m=[sum(F(w,6)*v[j] for w,v in zip(weights,vertices)) for j in range(q-1)]
            x=cf.fiber(q,m);assert min(x)>=0 and sum(x)==1
            assert all((ev(x[:q+1],s)-ev(x[q+1:],s))/(ev(x[:q+1],s)+ev(x[q+1:],s))==gamma(s) for s in SAMPLES)
            assert quotient(x[:q+1],tuple(map(F,P)))==m and quotient(x[q+1:],tuple(map(F,Q)))==m
            vertices_checked+=1
        # All simplex vertices, then nonnegative normalized perturbations of
        # an interior fiber member in every ordered pair of coefficient axes.
        vectors=[[F(i==j) for i in range(n)] for j in range(n)]
        for i,j in product(range(n),repeat=2):
            if i==j:continue
            x=x0.copy();x[i]+=F(1,100000);x[j]-=F(1,100000);vectors.append(x)
        for x in vectors:
            actual=[(ev(x[:q+1],s)-ev(x[q+1:],s))/(ev(x[:q+1],s)+ev(x[q+1:],s)) for s in SAMPLES]
            delta=max(abs(v-gamma(s)) for v,s in zip(actual,SAMPLES))
            rhs=[F(0)]*(q+3)+[F(1)]+x[3:q+1]
            y=[dot(row,rhs) for row in N]
            assert quotient(y[:q+1],tuple(map(F,P)))==quotient(y[q+1:],tuple(map(F,Q)))
            assert sum(y)==1
            epsilon=bound*delta
            assert max(abs(a-b) for a,b in zip(x,y))<=epsilon
            z=[(rho*a+epsilon*b)/(rho+epsilon) for a,b in zip(y,x0)]
            assert min(z)>=0 and sum(z)==1
            assert max(abs(a-b) for a,b in zip(x,z))<=epsilon/(rho+epsilon)
            quotient(z[:q+1],tuple(map(F,P)));quotient(z[q+1:],tuple(map(F,Q)))
            controls+=1
        for key in ('coefficient_error_factor','interior_minimum_coefficient'):
            bad=deepcopy(rec);bad[key]='0'
            try:cf.verify(bad)
            except ValueError:negative.append('degree-'+str(q)+'-'+key)
            else:raise AssertionError('Corrupt fiber certificate accepted')
        bad=deepcopy(rec);bad['inverse'][0][0]='0'
        try:cf.verify(bad)
        except ValueError:negative.append('degree-'+str(q)+'-inverse')
        else:raise AssertionError('Corrupt inverse accepted')
        records.append(rec)
    return {'certificates':records,'projection_controls':controls,'barycentric_fiber_controls':vertices_checked,'negative_controls':negative}


def series_checks():
    record=sm.certificate();sm.verify(record);comparisons=0;stencils=0
    for j in range(12):
        for kind in ('RC','RL'):
            base=[('R',7,2,F(j+2,3)),('R',2,0,F(j+3,4)),('R',7,3,F(5,j+2)),
                  ('R',3,0,F(7,j+3)),('C' if kind=='RC' else 'L',2,3,F(j+1,5)),
                  ('C' if kind=='RC' else 'L',3,0,F(j+2,7))]
            edges=base+[('L' if kind=='RC' else 'C',1,7,F(j+1,9))]
            values=[];errors=[]
            for s in SAMPLES:
                g=response(edges,C(s))['gamma'];assert not g.im
                values.append((1+g.re)/(1-g.re));errors.append(abs(g.re-gamma(s)));comparisons+=1
            cert=record['certificates'][0 if kind=='RC' else 1]
            stencil=sum(F(w)*values[i] for i,w in zip(cert['sample_indices'],cert['Z_weights']))
            assert stencil>=0 and max(errors)>F(cert['reflection_margin']);stencils+=1
    # A realizable one-L bridge violates convexity: the series support
    # hypothesis cannot be discarded or inferred from the reactive count.
    bridge=[('L',1,2,F(1)),('R',2,0,F(2)),('R',1,3,F(1)),('R',3,0,F(1)),('C',2,3,F(1))]
    z=[]
    for s in SAMPLES[:3]:
        g=response(bridge,C(s))['gamma'];z.append((1+g.re)/(1-g.re));comparisons+=1
    residual=z[0]-2*z[1]+z[2];assert residual<0
    negative=[]
    for key in ('target_residual','reflection_margin','kernel_numerator'):
        bad=deepcopy(record);bad['certificates'][0][key]='0'
        try:sm.verify(bad)
        except ValueError:negative.append(key)
        else:raise AssertionError('Corrupt series margin accepted')
    return {'certificate':record,'physical_graphs':24,'physical_sample_comparisons':comparisons,
            'physical_stencils':stencils,'one_L_bridge_convexity_counterexample':str(residual),'negative_controls':negative}


def template_checks():
    levels=generate(4);counts={};distributions={}
    for q in (2,3,4):
        graphs=[g for g in levels[q] if len({e[0] for e in g})==2 and no_parallel_same_kind(g)]
        counts[q]=len(graphs)
        for g in graphs:
            verify_lift(g);key=(q,sum(k=='L' for k,_,_ in g));distributions[key]=distributions.get(key,0)+1
    assert counts=={2:26,3:246,4:1858}
    cases=[(('L',1,2),('C',2,0),('C',1,0)),(('L',1,2),('L',2,0),('C',1,0)),
           (('L',1,2),('C',2,3),('C',3,0),('C',1,0)),
           (('L',1,2),('L',2,3),('C',3,0),('C',1,0)),
           (('L',1,2),('L',2,3),('L',3,0),('C',1,0))]
    comparisons=0;errors=[]
    for reactive in cases:
        rec=verify_lift(reactive);mapping=rec['original_node_of_copy']
        origR={(u,v):F(2+u+v,3) for u,v in combinations(sorted(set(mapping)),2)}
        react=[(k,u,v,F(j+2,5)) for j,(k,u,v) in enumerate(reactive)]
        original=[('R',u,v,r) for (u,v),r in origR.items()]+react
        target=[response(original,C(s))['gamma'].re for s in SAMPLES]
        previous=None
        for epsilon in (F(1,100),F(1,10000),F(1,1000000)):
            resistors=[]
            for u,v in combinations(range(len(mapping)),2):
                if (u,v) in rec['wires']:r=epsilon
                elif (u,v) in rec['resistor_positions']:r=origR[tuple(sorted((mapping[u],mapping[v])))]
                else:r=1/epsilon
                resistors.append(('R',u,v,r))
            lifted=resistors+[(k,u,v,F(j+2,5)) for j,(k,u,v) in enumerate(rec['reactive'])]
            actual=[response(lifted,C(s))['gamma'].re for s in SAMPLES]
            error=max(abs(a-b) for a,b in zip(actual,target));assert error>0
            if previous is not None:assert error<previous/50
            previous=error;comparisons+=7
        assert previous<F(1,10000);errors.append(str(previous))
    return {'boundary_lifts_checked':sum(counts.values()),'by_budget':counts,
      'universal_mixed_templates_at_three_and_four':5,
      'distribution_counts':[{'budget':q,'inductors':k,'classes':v} for (q,k),v in sorted(distributions.items())],
      'finite_positive_approximant_families':5,'finite_positive_sample_comparisons':comparisons,
      'last_errors':errors,'scope':'Exact graph lift for every listed representative; universal coverage comes from the written splitting/energy limit. No new full-skeleton margin.'}


def main():
    records={'status':'PASS','coefficient_fiber':fiber_checks(),'series_margins':series_checks(),
             'universal_templates':template_checks(),
             'single_kind_minima':minimum_checks(),
             'passive_transfer_counterexamples':[check_example(k,F(1,10**e)) for k in ('DC','infinity','resonance') for e in (3,6,8)],
             'non_claims':['No useful universal three/four-reactive margin','No added full-skeleton exclusion','No new Lean theorem','No hardware measurement','No independent review or novelty claim']}
    print(json.dumps(records,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
