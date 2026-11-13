"""Physical stability, one-L energy and branch-rounding controls.
Author: Komorebi P. Exact finite controls are separate from universal proofs.
"""
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations,product
import json
from exact_phasor import C,response as reference_response
from pure_type_margins import SAMPLES,gamma
from coefficient_fiber import fiber,certificate as old_fiber
from reactive_skeletons import generate,no_parallel_same_kind,vertices
from natural_graph_polynomials import pair,laplacian,determinant,value
from phasor_unit_voltage import response,dc_one_L
from branch_change_phasor import thevenin,open_branch,short_branch
import stable_fiber as sf
import one_L_energy as energy
import branch_rounding as rounding


def compositions(total,parts):
    if parts==1:yield (total,);return
    for first in range(total+1):
        for rest in compositions(total-first,parts-1):yield (first,)+rest


def selected_graphs():
    levels=generate(4);out=[]
    for q in (3,4):
        choices=sorted(g for g in levels[q] if no_parallel_same_kind(g) and sum(k=='L' for k,_,_ in g)==1)
        for j in range(32):
            g=choices[j*(len(choices)-1)//31];n=vertices(g);index=len(out)
            R=[('R',u,v,F(2+((index+u*3+v*5)%7),3)) for u,v in combinations(range(n),2)]
            out.append(R+[(k,u,v,F(2+(index+e)%5,4)) for e,(k,u,v) in enumerate(g)])
    return out


def stable_checks(graphs):
    record=sf.certificate();sf.verify(record);algebra_controls=0;repairs=0
    vertices=[list(map(F,m)) for m in old_fiber(4)['exact_nonnegative_fiber']['multiplier_vertices']]
    for weights in compositions(8,4):
        m=tuple(sum(F(w,8)*v[j] for w,v in zip(weights,vertices)) for j in range(3))
        x=fiber(4,m);a,b,c=m;G=(6*a-4*c)**2+(6*b+3*c)*(3*a+4*b)
        assert sf.delta3(x[:5])==3*b*G
        if b<0:
            assert G>=F(1,2)*(a+c)**2>=F(1,1800)
            fixed=sf.triangle_repair(m);y=fiber(4,fixed)
            assert min(fixed)>=0 and sum(fixed)==F(1,30)
            assert max(abs(u-v) for u,v in zip(x,y))<=9*abs(b);repairs+=1
        algebra_controls+=1
    polynomial_graphs=0;det_comparisons=0;regional_members=0
    for edges in graphs:
        rec=pair(edges);P,Q=rec['P'],rec['Q'];q=rec['degree_cap']
        assert q in (3,4) and min(P+Q)>=0 and sum(P+Q)==1
        assert sf.delta3(P)>=0 and sf.delta3(Q)>=0
        for s in (F(1,2),F(3,4),F(5,4),F(7,4),F(7,3)):
            A,B,nL,_=laplacian(edges,s)
            assert value(P,s)*rec['scale']==s**nL*determinant(B)
            assert value(Q,s)*rec['scale']==s**nL*determinant(A)
            out=response(edges,C(s));assert out['Y']==C(value(Q,s)/value(P,s));det_comparisons+=1
        p_i=value(P,C(0,1));q_i=value(Q,C(0,1))
        if p_i:
            assert response(edges,C(0,1))['Y']==q_i/p_i;det_comparisons+=1
        try:dc=dc_one_L(edges)
        except ValueError as e:
            assert 'DC input short' in str(e);dc=None
        if dc and dc['Y0']>=F(1,4) and (q==3 or p_i.normsq()>=F(1,10000)):
            error=max(abs((value(P,s)-value(Q,s))/(value(P,s)+value(Q,s))-gamma(s)) for s in SAMPLES)
            assert error>F(energy.region(q)['margin']);regional_members+=1
        polynomial_graphs+=1
    negative=[]
    for key in ('quantitative_triangle_factor','negative_b_G_lower','fiber_coordinate_bound'):
        bad=deepcopy(record);bad[key]=0
        try:sf.verify(bad)
        except ValueError:negative.append(key)
        else:raise AssertionError('Corrupt stable-fiber certificate accepted')
    return {'certificate':record,'barycentric_controls':algebra_controls,'negative_multiplier_repairs':repairs,
      'physical_polynomial_graphs':polynomial_graphs,'independent_determinant_and_phasor_comparisons':det_comparisons,
      'physical_members_meeting_regional_guards':regional_members,'negative_controls':negative}


def minimum_graph(L=F(1),r1=F(1),r2=F(1)):
    return [('R',1,2,r1),('R',0,3,r2),('C',1,3,1/L),('C',0,2,1/L),('L',2,3,L)]


def common_DC_graph():
    return [('R',1,2,F(1)),('L',2,0,F(1)),('R',3,4,F(1)),
            ('C',1,3,F(1,2)),('C',4,0,F(1,2))]


def energy_checks(graphs):
    record=energy.certificate();energy.verify(record)
    controls=list(graphs)
    for L in (F(1,2),F(1),F(3,2)):
        g=minimum_graph(L);controls.extend((g,g+[('C',1,0,F(1,2))],g+[('R',1,0,F(1,100))]))
    controls.extend([
      [('R',1,0,F(1)),('L',1,2,F(1)),('C',1,2,F(1))],
      minimum_graph()+[('R',4,5,F(1)),('C',1,4,F(1,100)),('C',0,5,F(1,100))],
      minimum_graph()+[('R',8,9,F(3))],
      common_DC_graph(),
      [('R',1,2,F(1)),('L',2,0,F(1))]])
    # Reverse each L orientation in a separate copy of every sparse control.
    controls.extend([[(k,v,u,x) if k=='L' else (k,u,v,x) for k,u,v,x in g] for g in controls[64:]])
    admitted=0;dc_short=0;small_loss=0;free_dc=0;free_imag=0;reference_comparisons=0;rounded_bounds=0
    for edges in controls:
        lindex=next(j for j,e in enumerate(edges) if e[0]=='L');_,u,v,L=edges[lindex]
        try:dc=dc_one_L(edges)
        except ValueError as e:
            assert 'DC input short' in str(e);dc_short+=1;continue
        real=response(edges,C(F(1,2)));imag=response(edges,C(0,1));Ronly=response([e for e in edges if e[0]=='R'],C(1),dc['voltage'])
        Y0,IL0=dc['Y0'],dc['IL0'];Ys=real['Y'].re;Yi=imag['Y'];E=Yi.re
        assert not real['Y'].im and not Ronly['Y'].im
        GR=Ronly['Y'].re;VR=Ronly['voltage'];assert all(not z.im and 0<=z.re<=1 for z in VR.values())
        assert Y0-GR==IL0*(VR[u].re-VR[v].re)
        assert 0<=Y0-GR<=abs(IL0) and GR<=E
        ILs=real['current'][lindex];ILi=imag['current'][lindex];assert not ILs.im and abs(ILs.re)<=Ys
        R0i=sum((x*a*b for (k,_,_,x),a,b in zip(edges,dc['R_current'],imag['current']) if k=='R'),C())
        Rsi=sum((x*a*b for (k,_,_,x),a,b in zip(edges,real['current'],imag['current']) if k=='R'),C())
        assert R0i==Y0-C(0,L*IL0)*ILi
        s=F(1,2);K=(s*Yi-C(0,Ys))/(s-C(0,1))
        assert Rsi==K-(s+C(0,1))*L*ILs*ILi
        assert R0i.normsq()<=Y0*E and Rsi.normsq()<=Ys*E
        assert sum((x*a.normsq() for (k,_,_,x),a in zip(edges,dc['R_current']) if k=='R'),F(0))==Y0
        if E<Y0:
            assert IL0 and abs(ILs.re/IL0)<=Ys/(Y0-E)
            A=(Ys+C(0,s)*Yi)/(1+s*s)
            r=energy.sqrt_upper(E/Y0)
            if r<1:
                bound=Ys/(1-r)+energy.sqrt_upper(Ys*E/(1+s*s));assert A.normsq()<=bound*bound
                rounded_bounds+=1
            small_loss+=1
        for point,out in ((C(s),real),(C(0,1),imag)):
            try:ref=reference_response(edges,point)
            except ValueError:continue
            assert (1-ref['gamma'])/(1+ref['gamma'])==out['Y'];reference_comparisons+=1
        free_dc+=int(dc['free_internal_variables']>0);free_imag+=int(imag['free_internal_variables']>0);admitted+=1
    # Unit voltage is impossible for a series LC short at resonance.
    singular=[('L',1,2,F(1)),('C',2,0,F(1))]
    try:response(singular,C(0,1))
    except ValueError as e:assert 'No finite' in str(e)
    else:raise AssertionError('Incompatible resonant phasor accepted')
    assert not value(pair(singular)['P'],C(0,1))
    common=pair(common_DC_graph());dc_common=dc_one_L(common_DC_graph())
    assert common['P'][0]==common['Q'][0]==0 and dc_common['Y0']==1
    assert value(common['P'],C(0,1))
    # The retained Hughes circuit has three L, and violates the proposed
    # inequality if its exactly-one-L hypothesis is removed.
    from transfer_barriers import hughes_port_at_five
    H=[(k,1 if u==5 else u,1 if v==5 else v,x) for k,u,v,x in hughes_port_at_five()]
    yi=response(H,C(0,1))['Y'];ys=response(H,C(F(1,2)))['Y'].re
    assert yi==C(0,-1) and ys==F(23,14)
    A=(ys+C(0,F(1,2))*yi)/F(5,4);assert A.normsq()>ys*ys
    negative=[]
    for key in ('margin','working_P_i_lower','strict_slack'):
        bad=deepcopy(record);bad['regions'][0][key]='0'
        try:energy.verify(bad)
        except ValueError:negative.append(key)
        else:raise AssertionError('Corrupt regional certificate accepted')
    return {'certificate':record,'attempted_one_L_graphs':len(controls),'admitted_finite_DC_graphs':admitted,
      'DC_shorts_outside_hypothesis':dc_short,'E_less_than_Y0_cases':small_loss,
      'outward_rounded_energy_bound_checks':rounded_bounds,
      'DC_floating_cases':free_dc,'compatible_nonunique_imaginary_cases':free_imag,
      'independent_reference_phasor_comparisons':reference_comparisons,
      'DC_common_factor_control':{'P0':'0','Q0':'0','Y0':'1','meaning':'The intrinsic DC guard can hold while the old sufficient coefficient guard fails.'},
      'invalid_extensions_rejected':['incompatible finite-voltage resonance','removing the exactly-one-L hypothesis'],
      'negative_controls':negative}


def rounding_checks():
    record=rounding.certificate();rounding.verify(record)
    cases=[[('R',1,0,F(2))],[('L',1,0,F(2))],[('C',1,0,F(2))],minimum_graph(),
      [('L',1,2,F(1)),('R',2,0,F(2)),('R',1,3,F(1)),('R',3,0,F(1)),('C',2,3,F(1))],
      minimum_graph()+[('C',1,0,F(2))],
      [('R',1,0,F(3)),('L',1,2,F(1)),('C',1,2,F(1)),('R',5,6,F(2))]]
    finite=opened=shorted=0;max_potential=max_current=F(0)
    for edges in cases:
        for s in SAMPLES:
            base=thevenin(edges,C(s));ref=reference_response(edges,C(s))
            assert base['gamma']==ref['gamma']
            for z in base['voltage'].values():assert not z.im and 0<=z.re<=1;max_potential=max(max_potential,z.re)
            for z in base['current']:assert not z.im and abs(z.re)<=1;max_current=max(max_current,abs(z.re))
            for j,(kind,u,v,physical) in enumerate(edges):
                y=1/physical if kind=='R' else s*physical if kind=='C' else 1/(s*physical);z=1/y
                changed=edges.copy();changed[j]=(kind,u,v,physical*F(5,4));other=thevenin(changed,C(s))
                y2=1/changed[j][3] if kind=='R' else s*changed[j][3] if kind=='C' else 1/(s*changed[j][3])
                drop=base['voltage'][u]-base['voltage'][v];drop2=other['voltage'][u]-other['voltage'][v]
                diff=other['gamma']-base['gamma']
                assert diff==-2*(y2-y)*drop*drop2
                assert diff==2*(1/y2-z)*base['current'][j]*other['current'][j];finite+=1
                op=open_branch(edges,j,C(s));diff=op['gamma']-base['gamma']
                assert diff==2*y*drop*(op['voltage'][u]-op['voltage'][v]) and abs(diff.re)<=2*y and not diff.im;opened+=1
                sh=short_branch(edges,j,C(s));diff=sh['gamma']-base['gamma']
                assert diff==-2*z*base['current'][j]*sh['wire_current'] and abs(diff.re)<=2*z and not diff.im;shorted+=1
    # Tiny-L shorting and tiny-C opening both fail at an imaginary resonance.
    eps=F(1,10**6)
    g1=[('R',1,2,F(1,1000)),('L',2,0,eps),('C',2,0,1/eps)]
    g2=[('R',1,0,F(1000)),('L',1,2,1/eps),('C',2,0,eps)]
    a=reference_response(g1,C(0,1))['gamma'];b=short_branch(g1,1,C(0,1))['gamma']
    c=reference_response(g2,C(0,1))['gamma'];d=open_branch(g2,2,C(0,1))['gamma']
    assert (a-b).normsq()==(c-d).normsq()==F(2000,1001)**2 and abs(a.re-b.re)>2*eps
    negative=[]
    for key in ('fit_error_threshold','one_reactive_rounding_error','accepted_two_reactive_margin'):
        bad=deepcopy(record);bad[key]='0'
        try:rounding.verify(bad)
        except ValueError:negative.append(key)
        else:raise AssertionError('Corrupt rounding certificate accepted')
    return {'certificate':record,'physical_families':len(cases),'finite_change_identities':finite,
      'open_comparisons':opened,'short_comparisons':shorted,'maximum_fixed_source_potential':str(max_potential),
      'maximum_fixed_source_branch_current':str(max_current),
      'imaginary_axis_false_extension_controls':{'cases':2,'reflection_error_squared':str(F(2000,1001)**2),'hypothetical_bound':str(2*eps)},
      'negative_controls':negative}


def main():
    graphs=selected_graphs()
    print(json.dumps({'status':'PASS','stable_fiber':stable_checks(graphs+[common_DC_graph()]),'one_L_energy':energy_checks(graphs),
      'branch_rounding':rounding_checks(),'whole_skeleton_coverage_unchanged':{'covered':138,'remaining':1992},
      'selected_Lean_statements_unchanged':41,
      'scope':'Finite exact controls plus separate written physical proofs; no universal three/four-reactive margin, new Lean, hardware, independent review or priority result.'},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
