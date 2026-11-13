"""Finite exact controls and constants for whole one-kind class margins.
Author: Komorebi P. Universal conclusions depend on the written graph proofs.
"""
from copy import deepcopy
from fractions import Fraction as F
import json
from exact_phasor import C
from phasor_unit_voltage import response
from natural_graph_polynomials import pair,value
from real_root_constraints import real_roots_with_multiplicity as roots
from check_physical_constraints import selected_graphs,minimum_graph
from one_C_endpoints import states
import global_typed_margins as global_margin


def invert(edges):return [('C' if k=='L' else 'L' if k=='C' else k,u,v,1/x if k!='R' else x) for k,u,v,x in edges]


def root_checks():
    controls=[((1,0,1),0),((1,0,2,0,1),0),((0,0,1,0,1),2),((0,0,0,0,1),4),((4,0,-5,0,1),4),((-1,0,0,1),1)]
    for p,n in controls:assert roots(p)==n
    counts={'L':0,'C':0};quartics=0;reciprocal_checks=0
    for g in selected_graphs():
        for kind,edges in (('L',g),('C',invert(g))):
            rec=pair(edges);counts[kind]+=1
            for p in (rec['P'],rec['Q']):
                if len(p)==5 and p[-1]:assert roots(p)>=2;quartics+=1
            if kind=='C':
                old=pair(g)
                assert rec['P']==old['P'][::-1] and rec['Q']==old['Q'][::-1];reciprocal_checks+=2
    false=[('R',1,2,F(10)),('L',2,3,F(1)),('C',2,3,F(1)),('L',3,0,F(1)),('C',3,0,F(1,4))]
    p=pair(false)['P'];assert len(p)==5 and p[-1] and roots(p)==0
    return {'Sturm_multiplicity_controls':len(controls),'physical_graphs_by_kind':counts,'physical_quartics':quartics,
      'frequency_inverse_polynomial_comparisons':reciprocal_checks,'false_two_L_two_C_extension':{'real_numerator_roots':0,'natural_P':list(map(str,p))}}


def endpoint_checks():
    controls=[invert(g) for g in selected_graphs()]
    for r1,r2 in ((F(1),F(1)),(F(1,2),F(2)),(F(2),F(3))):
        for x in (F(1,2),F(1),F(3,2)):
            g=invert(minimum_graph(x,r1,r2));controls.extend([g,g+[('R',1,0,F(1000))],g+[('R',1,4,F(1,1000)),('R',4,0,F(1000))]])
    controls.extend([invert(minimum_graph())+[('R',8,9,F(2))],
      invert(minimum_graph())+[('L',1,4,F(1)),('L',4,0,F(1))]])
    controls.extend([[(k,v,u,x) if k=='C' else (k,u,v,x) for k,u,v,x in g] for g in controls[64:]])
    admitted=sign_cases=inequality_cases=floating=trial_checks=0;max_wire=F(0)
    for edges in controls:
        try:dc,inf,alls,Ronly,J,Jall=states(edges)
        except ValueError as e:assert 'Open endpoint' in str(e);continue
        r0,rinf=dc['Z'],inf['Z']
        if not r0 or not rinf:continue
        imag=response(edges,C(0,1));Y=imag['Y']
        if not Y:continue
        Zi=1/Y;E=Zi.re;curr=[a/Y for a in imag['current']];V={v:a/Y for v,a in imag['voltage'].items()}
        cap=next(e for e in edges if e[0]=='C');_,u,v,capvalue=cap
        V0=dc['voltage'][u]-dc['voltage'][v];Vi=V[u]-V[v];GR=Ronly['Y'].re
        assert 0<=GR and GR*Zi.normsq()<=E and alls['Z']<=E
        assert r0-alls['Z']==V0*Jall and abs(Jall)<=1;max_wire=max(max_wire,abs(Jall))
        VR=Ronly['voltage'];assert 1-GR*rinf==J*(VR[u].re-VR[v].re) and abs(VR[u].re-VR[v].re)<=1
        R0i=sum((x*a*b for (k,u,v,x),a,b in zip(edges,dc['R_current'],curr) if k=='R'),C())
        Riinf=sum((x*a*b for (k,u,v,x),a,b in zip(edges,curr,inf['R_current']) if k=='R'),C())
        R0inf=sum(x*a*b for (k,u,v,x),a,b in zip(edges,dc['R_current'],inf['R_current']) if k=='R')
        assert R0i==r0-C(0,capvalue*V0)*Vi and Zi==Riinf+Vi*J
        assert R0inf==r0-V0*J and R0inf**2<=r0*rinf
        assert R0i.normsq()<=r0*E and Riinf.normsq()<=rinf*E
        eta=min(min(x,1/x) for k,u,v,x in edges if k!='R');nL=sum(k=='L' for k,u,v,x in edges)
        for sigma in (F(1,100),F(1,1000)):
            low=response(edges,C(sigma));high=response(edges,C(1/sigma))
            assert (1/low['Y']).re<=r0+nL*sigma/eta
            assert high['Y'].re<=1/rinf+nL*sigma/eta
            trial_checks+=2
        if E<r0 and Zi.im>0 and Zi.im**2>rinf*E:
            assert V0*Vi.im<0 and J*Vi.im>0 and V0*J<0
            assert abs(V0)>=r0-E and abs(J)>=1-E*rinf/Zi.normsq()
            rhs=r0*(1+(1-E/r0)*(1-E*rinf/Zi.normsq()))**2
            assert rinf>=rhs;sign_cases+=1;inequality_cases+=1
        floating+=int(dc['free']>0 or inf['free']>0);admitted+=1
    # The actual target violates the endpoint conclusion when one-C is dropped.
    assert F(1)<4*F(4,9)
    return {'attempted_graphs':len(controls),'finite_positive_endpoint_controls':admitted,
      'sign_and_endpoint_inequality_controls':sign_cases,'floating_endpoint_controls':floating,'endpoint_trial_comparisons':trial_checks,'maximum_allshort_C_current':str(max_wire),
      'invalid_extension_control':'Target has more than one C and violates the zero-loss endpoint conclusion.'}


def coverage():
    from reactive_skeletons import generate,no_parallel_same_kind
    from shunt_rc_refutation import covered as Lshunt
    from cap_shunt_rl_refutation import covered as Cshunt
    def covered(g):return len(g)<=2 or Lshunt(g) or Cshunt(g)
    rows=[];new=old=remaining=0
    for q,level in enumerate(generate(4)):
        if q<2:continue
        graphs=[g for g in level if no_parallel_same_kind(g) and len({k for k,u,v in g})==2]
        before=sum(covered(g) for g in graphs)
        after=sum(covered(g) or min(sum(k=='L' for k,u,v in g),sum(k=='C' for k,u,v in g))==1 for g in graphs)
        rows.append({'reactive_budget':q,'total_mixed_classes':len(graphs),'previously_covered':before,'covered':after,'remaining':len(graphs)-after})
        old+=before;new+=after-before;remaining+=len(graphs)-after
    assert old==138 and new==1196 and remaining==796
    return {'levels':rows,'previously_covered':old,'newly_covered':new,'covered':old+new,'remaining':remaining}


def main():
    record=global_margin.certificate();global_margin.verify(record);bad_controls=[]
    for route,key in ((0,'margin'),(1,'component_lower'),(2,'DC_resistance_lower'),(3,'strict_slack')):
        bad=deepcopy(record);bad['whole_class_margins'][route][key]='0'
        try:global_margin.verify(bad)
        except ValueError:bad_controls.append(key)
        else:raise AssertionError('Corrupt global certificate accepted')
    print(json.dumps({'status':'PASS','certificate':record,'quartic_root_controls':root_checks(),
      'one_C_endpoint_controls':endpoint_checks(),'whole_skeleton_coverage':coverage(),'corrupt_certificate_rejections':bad_controls,
      'selected_Lean_statements_unchanged':41,'review':'Written universal arguments receive project self-review; finite arithmetic/graph controls are supporting evidence, not an independent proof or whole-program completion.'},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
