"""Exact controls for backbone transfer; written proof supplies universal scope."""
from fractions import Fraction as F
from itertools import combinations,product
import json
from exact_phasor import C,response as phasor
from natural_graph_polynomials import pair,value
from regular_balanced import CORES,endpoint
from pure_type_margins import SAMPLES,gamma
from real_root_constraints import derivative
from backbone_transfer import unit_current,groups,maximum_forest,scale_surgery,repair,chart_graph,tree_completion_check

def main():
    # Sixteen feature-box corners at each response, plus a center control.
    h=F(1,10**3);charts=0;maximum=F(0)
    for kind in CORES:
        for signs in product((-1,1),repeat=4):
            data=[c+s*h for c,s in zip((F(1),F(5),F(4,9),F(1)),signs)]
            g=chart_graph(kind,*data)
            rel=max(abs(x/y-1) for (_,u,v,x),(_,a,b,y) in zip(g,CORES[kind]))
            maximum=max(maximum,rel);assert rel<=10*h
            z=unit_current(g)['Z'];assert z.re==0 and z.im==data[0]
            pp=pair(g);assert endpoint(pp['P'],pp['Q'])==data[2] and endpoint(pp['P'],pp['Q'],True)==data[3]
            pi,qi=value(pp['P'],C(0,1)),value(pp['Q'],C(0,1))
            jet=(value(derivative(pp['P']),C(0,1))*qi-pi*value(derivative(pp['Q']),C(0,1)))/(qi*qi)
            assert jet==C(data[1])
            err=max(abs(phasor(g,C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
            assert err>F(1,300);charts+=1
    assert F(25,2769)-F(1,198)>F(1,300)
    repairs=[]
    for kind,base in CORES.items():
        for power in (12,16,20):
            eps=F(1,10**power)
            g=[(k,u,v,z*(1+(-1)**j*eps) if k!='R' else z) for j,(k,u,v,z) in enumerate(base)]
            state=unit_current(g);n=max(state['potentials'])+1
            x=[state['potentials'].get(v,C(0)).im for v in range(n)]
            new,phi,record=repair(g,x,F(1,1000),F(1,10**8))
            result=unit_current(new);assert result['Z']==C(0,phi[1])
            assert all(result['potentials'][v]==C(0,p) for v,p in enumerate(phi))
            assert F(record['relative_physical_change'])<F(1,10**8)
            repairs.append({'core':kind,'detuning':str(eps),**record})
    # Backbone floor remains valid with an arbitrarily weak redundant R chord.
    floors=[];surgeries=0;completions=[]
    for small_power in (8,16,32):
        alpha=F(1,100)
        g=list(CORES['forest'])+[('R',1,0,F(10**small_power))]
        p=pair(g);positive=[x for x in p['P']+p['Q'] if x]
        assert min(positive)>=alpha**18/F(2**50)
        assert min(1/x for k,u,v,x in g if k=='R')<alpha
        floors.append({'tiny_R_conductance':str(F(1,10**small_power)),'minimum_positive_coefficient':str(min(positive))})
        completions.append(tree_completion_check(g))
    # A connected R component with a very strong backbone edge, a moderate
    # backbone edge and a weak cut; internal weak chords must remain.
    for power in (6,10,14):
        tiny=F(1,10**power)
        g=[('L',1,2,F(1)),('C',2,0,F(1)),('L',3,4,F(2)),('C',4,0,F(2)),
          ('R',1,3,tiny),('R',3,4,F(1)),('R',4,2,1/tiny),('R',1,4,F(10**(power-1)))]
        out,cost=scale_surgery(g,F(1,100),F(1,10**(power-2)))
        for s in SAMPLES:
            a,b=phasor(g,C(s))['gamma'].re,phasor(out,C(s))['gamma'].re
            assert abs(a-b)<=2*cost
        surgeries+=1
    # Exact internal-mode repair with two inactive reactive branches.
    modes=[]
    for power in (12,16,20):
        eps=F(1,10**power)
        g=[('L',2,3,1+eps),('C',2,3,1-eps),('L',1,0,F(2)),('C',1,0,F(3)),
          ('R',1,0,F(1)),('R',3,0,F(2))]
        x=[F(0),eps,1+eps,-eps]
        new,phi,report=repair(g,x,F(1,1000),F(1,10**8),mode=True)
        p=pair(new)
        assert value(p['P'],C(0,1))==value(p['Q'],C(0,1))==C(0)
        assert report['active_LC']==report['inactive_LC']==2
        modes.append(report)
    # A dense ten-vertex graph reaches all45 R slots before surgery.
    strong=({0,2,3},{1,4,5},{6,7},{8,9})
    cls={v:j for j,vs in enumerate(strong) for v in vs}
    dense=[('L',1,6,F(1)),('C',6,0,F(1)),('L',1,8,F(2)),('C',8,0,F(2))]
    for u,v in combinations(range(10),2):
        g=F(10**8) if cls[u]==cls[v] else F(1,10**14) if 3 in (cls[u],cls[v]) else F(1)
        dense.append(('R',u,v,1/g))
    rounded,cost=scale_surgery(dense,F(1,100),F(1,10**6))
    for s in SAMPLES:assert abs(phasor(dense,C(s))['gamma'].re-phasor(rounded,C(s))['gamma'].re)<=2*cost
    surgeries+=1
    # Wrong active/inactive partition is rejected, rather than silently repaired.
    try:repair(CORES['forest'],[F(0)]*5,F(1),F(1,100))
    except ValueError:negative=1
    else:raise AssertionError('Incompatible port component was accepted')
    B=10000;K=B+1;N=16*B*K**9
    assert N+1<10**45 and 200*F(1,10**16)<F(1,4)
    assert F(2000-18,9)>220
    assert F(10000-2003,2)-2040>70
    assert 34*F(1,10**16)+12*F(1,10**176)<1
    print(json.dumps({'status':'PASS','feature_corner_graphs':charts,'largest_corner_relative_change':str(maximum),
      'driven_flow_repairs':repairs,'weak_redundant_R_coefficient_controls':floors,'MST_surgery_graphs':surgeries,
      'tree_completion_crosschecks':completions,'mode_flow_repairs':modes,
      'dense_R_slots':45,'incompatible_component_guard':negative,
      'scale_gap':{'bounded_backbone_exponent':B,'scale_exponent_multiplier':K,'spanning_forest_edges_max':9,
        'needed_decimal_error_exponent':str(N),'chosen_decimal_error_exponent':str(10**45)},
      'scope':'Finite exact controls and integer exponent checks. Universal proof/review is separate.'},indent=2))

if __name__=="__main__":
    if not __debug__:raise RuntimeError("Assertions must remain enabled")
    main()
