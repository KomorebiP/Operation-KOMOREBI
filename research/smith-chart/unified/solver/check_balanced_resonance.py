"""Exact controls for the written internal-mode and near-mode theorems.
Author: Komorebi P. Finite fixtures are separate from the universal proof.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations,permutations,product
import json,subprocess,sys,tempfile
from pathlib import Path
from exact_phasor import C,response as reference
from phasor_unit_voltage import response
from natural_graph_polynomials import pair,value
from coefficient_fiber import multiply
from pure_type_margins import SAMPLES,gamma
from real_root_constraints import gcd
import resonant_mode_face as mf
import positive_real_comparison as comparison
from balanced_obstructions import controls as obstruction_controls


def key(edges,n):
    return min(tuple(sorted((k,min(p[u],p[v]),max(p[u],p[v])) for k,u,v in edges)) for p in permutations(range(n)))


def support_inventory():
    alltypes={};labeled=0
    for m in (2,3,4):
        for n in range(2,m+1):
            universe=[(k,u,v) for k in ('L','C') for u,v in combinations(range(n),2)]
            for es in combinations(universe,m):
                kinds=Counter(e[0] for e in es);degrees=Counter(v for k,u,v in es for v in (u,v))
                if max(kinds.values())>2 or len(degrees)!=n or min(degrees.values())<2:continue
                labeled+=1;k=key(es,n);alltypes[k]=(m,n,sorted(degrees.values()))
    assert len(alltypes)==8
    return {'unlabelled_colored_types':len(alltypes),'labeled_controls':labeled,
      'types':[{'edges':[list(e) for e in k],'active_edges':v[0],'active_vertices':v[1],'degrees':v[2]} for k,v in sorted(alltypes.items())]}


def add_resistors(core,w,variant):
    core=list(core);w={0:F(0),1:F(0),**{v:F(x) for v,x in w.items()}}
    for level in sorted(set(w.values())):
        for _ in range(2):w[max(w)+1]=level
    for u,v in combinations(sorted(w),2):
        if w[u]==w[v]:core.append(('R',u,v,F(2+(u*3+v*5+variant)%11,3)))
    return core,w


def fixtures():
    base=[
      ([('L',2,3,F(1)),('C',2,3,F(1)),('L',1,4,F(2)),('C',4,0,F(3,4))],{2:0,3:1,4:0}),
      ([('L',2,3,F(1)),('L',3,4,F(2)),('C',4,2,F(1,3)),('C',1,0,F(2,5))],{2:0,3:1,4:3}),
      ([('L',2,3,F(3)),('C',3,4,F(1)),('C',4,2,F(1,2)),('L',1,0,F(2,5))],{2:0,3:3,4:2}),
      ([('L',2,3,F(1)),('C',2,3,F(3)),('L',2,4,F(1)),('C',4,3,F(2))],{2:0,3:1,4:2}),
      ([('L',2,3,F(1)),('C',2,3,F(1)),('L',3,4,F(2)),('C',3,4,F(1,2))],{2:0,3:1,4:2}),
      ([('L',2,3,F(1)),('C',2,3,F(1)),('L',4,5,F(2)),('C',4,5,F(1,2))],{2:0,3:1,4:0,5:1}),
      ([('L',2,3,F(1)),('L',3,4,F(2)),('C',4,5,F(1)),('C',5,2,F(1,2))],{2:0,3:1,4:3,5:2}),
      ([('L',2,4,F(1)),('C',4,3,F(1)),('L',2,5,F(2)),('C',5,3,F(1,2))],{2:0,3:0,4:1,5:-2}),
      ([('L',2,4,F(1)),('C',4,3,F(1)),('C',2,5,F(1,2)),('L',5,3,F(2))],{2:0,3:0,4:1,5:2}),
      ([('L',2,4,F(1)),('C',4,3,F(1)),('C',2,5,F(1)),('L',5,3,F(1))],{2:0,3:0,4:1,5:1}),
      ([('L',2,3,F(2)),('L',2,3,F(2)),('C',2,3,F(1)),('C',1,0,F(1,2))],{2:0,3:1})]
    out=[]
    for j,(core,w) in enumerate(base):
        for scale,inverted,reverse in product((F(1,2),F(3,2)),(False,True),(False,True)):
            es=[(k,u,v,x*scale if k=='L' else x/scale) for k,u,v,x in core]
            if inverted:es=[('C' if k=='L' else 'L',u,v,1/x) for k,u,v,x in es]
            if reverse:es=[(k,v,u,x) for k,u,v,x in es]
            out.append(add_resistors(es,w,j))
    return out


def zero(poly):return not any(poly)


def mode_checks():
    counts=Counter();comparisons=commonzeros=free=0;noninversion_lower=0;patterns=set();basis_checks=0
    for edges,w in fixtures():
        rec=mf.certificate(edges,w);mf.verify(edges,w,rec);counts[rec['mechanism']]+=1
        modes=mf.find_modes(edges);assert modes
        for candidate in modes:mf.verify(edges,candidate,mf.certificate(edges,candidate));basis_checks+=1
        active=[(k,u,v) for k,u,v,x in mf.fold_parallel(edges) if k!='R' and w[u]!=w[v]]
        nodes=sorted({v for k,u,v in active for v in (u,v)});labels={v:j for j,v in enumerate(nodes)}
        patterns.add(key([(k,labels[u],labels[v]) for k,u,v in active],len(nodes)))
        p=pair(edges);P,Q=p['P'],p['Q']
        assert not value(P,C(0,1)) and not value(Q,C(0,1));commonzeros+=1
        inv=[a-b for a,b in zip(multiply(P,Q[::-1]),multiply(P[::-1],Q))]
        if rec['kind']=='inversion-symmetric':assert zero(inv)
        else:
            reduced=[(k,u,v,F(x)) for k,u,v,x in rec['reduced_edges']]
            rp=pair(reduced)
            assert zero([a-b for a,b in zip(multiply(P,rp['Q']),multiply(rp['P'],Q))])
            assert sum(k!='R' for k,u,v,x in reduced)<=3
            noninversion_lower+=int(not zero(inv))
        imag=response(edges,C(0,1));free+=int(imag['free_internal_variables']>0)
        if rec['kind']=='inversion-symmetric':assert not imag['Y'].im
        err=max(abs((value(P,s)-value(Q,s))/(value(P,s)+value(Q,s))-gamma(s)) for s in SAMPLES)
        assert err>F(rec['strict_margin'])
        if rec['kind']=='inversion-symmetric':assert err>=F(rec['two_sample_weak_margin'])
        for s in SAMPLES:
            out=response(edges,C(s));assert (1-out['Y'])/(1+out['Y'])==reference(edges,C(s))['gamma'];comparisons+=1
    assert noninversion_lower>0
    expected={tuple(tuple(e) for e in row['edges']) for row in support_inventory()['types']}
    assert patterns==expected
    edges,w=fixtures()[0];record=mf.certificate(edges,w);bad=[]
    for name in ('strict_margin','input_sha256','mode'):
        corrupt=deepcopy(record);corrupt[name]='0'
        try:mf.verify(edges,w,corrupt)
        except ValueError:bad.append(name)
        else:raise AssertionError('Corrupt mode certificate accepted')
    # A port-coupled grounded mode is not an internal port-zero mode.
    wrong=[('L',1,2,F(1)),('C',2,0,F(2)),('L',1,3,F(1)),('C',3,0,F(2,3))]
    p=pair(wrong);assert not value(p['Q'],C(0,1)) and value(p['P'],C(0,1)) and not mf.find_modes(wrong)
    assert len(gcd(p['P'],p['Q']))==1
    assert not zero([a-b for a,b in zip(multiply(p['P'],p['Q'][::-1]),multiply(p['P'][::-1],p['Q']))])
    try:mf.certificate(wrong,{0:0,1:1,2:-1,3:3})
    except ValueError:bad.append('port-coupled mode')
    else:raise AssertionError('Nonzero port mode accepted')
    changed=list(edges);k,u,v,x=changed[0];changed[0]=(k,u,v,2*x)
    try:mf.certificate(changed,w)
    except ValueError:bad.append('detuned non-mode')
    else:raise AssertionError('KCL-invalid detuned fixture accepted')
    # The retained target plus a dangling LC mode refutes dropping the budget.
    from transfer_barriers import hughes_port_at_five
    H=[(k,1 if u==5 else u,1 if v==5 else v,x) for k,u,v,x in hughes_port_at_five()]
    extra=H+[('L',0,9,F(1)),('C',0,9,F(1))]
    for s in SAMPLES:assert reference(extra,C(s))['gamma']==C(gamma(s))
    larger=pair(extra);assert not value(larger['P'],C(0,1)) and not value(larger['Q'],C(0,1))
    try:mf.certificate(extra,{v:int(v==9) for v in {0,1}|{u for k,u,v,x in extra}|{v for k,u,v,x in extra}})
    except ValueError:bad.append('higher-reactive target with spectator mode')
    else:raise AssertionError('Higher budget mode certified')
    return {'physical_mode_graphs':commonzeros,'classification_counts':dict(counts),
      'independent_positive_real_phasor_comparisons':comparisons,'compatible_nonunique_imaginary_cases':free,
      'basis_modes_checked':basis_checks,'active_types_realized':len(patterns),
      'lower_budget_controls_not_inversion_symmetric':noninversion_lower,'rejections':bad}


def bridge_checks():
    poly_checks=phasors=imaginary=0
    for ell,r in product((F(1,3),F(1),F(5,2)),(F(1,4),F(2),F(7,3))):
        edges=[('L',1,2,ell),('C',2,0,1/ell),('C',1,3,1/ell),('L',3,0,ell),('R',2,3,r)]
        rec=mf.certificate(edges,{0:0,1:0,2:1,3:1});assert rec['kind']=='inversion-symmetric'
        p=pair(edges);num=(ell*r,2*ell*ell,ell*r);den=(ell,2*r,ell)
        assert zero([a-b for a,b in zip(multiply(p['P'],den),multiply(num,p['Q']))]);poly_checks+=1
        for s in SAMPLES:
            Z=value(num,s)/value(den,s);assert reference(edges,C(s))['gamma']==C((Z-1)/(Z+1));phasors+=1
        assert 1/response(edges,C(0,1))['Y']==C(ell*ell/r);imaginary+=1
    return {'physical_bridges':poly_checks,'exact_rational_response_identities':poly_checks,
      'independent_positive_real_phasors':phasors,'finite_real_port_values_at_i':imaginary}


def comparison_checks():
    eps=F(1,100);bound=comparison.relative_bound(eps);assert bound==F(1,198)
    sym=abs(gamma(F(2))-gamma(F(1,2)))/2;assert sym==F(264,2627)
    budget=bound+F(1,50);assert sym-budget>F(3,40)
    base,base_mode=fixtures()[72];assert mf.certificate(base,base_mode)['kind']=='inversion-symmetric'
    reactive=[x for k,u,v,x in base if k!='R'];cut_indices=[]
    # Add weak cross-level resistors with total conductance1/100.
    groups=sorted(base_mode)
    cross=[(u,v) for u,v in combinations(groups,2) if base_mode[u]!=base_mode[v]][:2]
    for u,v in cross:cut_indices.append(len(base));base.append(('R',u,v,F(200)))
    assert not mf.find_modes(base)
    near_cases=relative_cases=0
    for factors in product((1-eps,1+eps),repeat=4):
        actual=[];j=0
        for k,u,v,x in base:
            actual.append((k,u,v,x*factors[j] if k!='R' else x));j+=int(k!='R')
        cert=comparison.near_mode_certificate(actual,reactive,base_mode,cut_indices,eps,F(3,40))
        comparison.verify(actual,reactive,base_mode,cut_indices,eps,cert)
        for s in SAMPLES:
            a=reference(actual,C(s))['gamma'];b=reference(base,C(s))['gamma']
            assert not (a-b).im and abs((a-b).re)<=bound;relative_cases+=1
        err=max(abs(reference(actual,C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
        assert err>F(3,40);near_cases+=1
    # The all-component positive-real comparison has no branch-count factor.
    for j,(edges,w) in enumerate(fixtures()[::11]):
        for choice in (0,1,2):
            changed=[(k,u,v,x*(1+eps if (j+e+choice)%2 else 1-eps)) for e,(k,u,v,x) in enumerate(edges)]
            for s in SAMPLES:
                a=reference(edges,C(s))['gamma'];b=reference(changed,C(s))['gamma']
                assert not (a-b).im and abs((a-b).re)<=bound;relative_cases+=1
    sharp_controls=0
    for epsilon in (F(0),F(1,1000),F(1,100),F(1,2),F(3,4),F(99,100)):
        for sign in (-1,1):
            changed_R=1+sign*epsilon;err=abs(reference([('R',1,0,changed_R)],C(1))['gamma'].re)
            assert err==epsilon/(2+sign*epsilon) and err<=comparison.relative_bound(epsilon);sharp_controls+=1
    # A strictly damped mixed graph refutes imaginary-frequency extension.
    damped=[('R',1,0,F(1)),('R',1,3,F(1,1000)),('L',3,2,F(1)),('C',2,0,F(1))]
    changed=damped[:-1]+[('C',2,0,1+eps)]
    diff=reference(damped,C(0,1))['gamma']-reference(changed,C(0,1))['gamma']
    assert diff.normsq()>bound*bound
    cert=comparison.near_mode_certificate(base,reactive,base_mode,cut_indices,eps,F(3,40))
    corruptions=0
    for name in ('strict_margin','remaining_slack','input_sha256','opened_R_indices','face_certificate'):
        corrupt=deepcopy(cert);corrupt[name]='1'
        try:comparison.verify(base,reactive,base_mode,cut_indices,eps,corrupt)
        except ValueError:corruptions+=1
        else:raise AssertionError('Corrupt near-mode certificate accepted')
    bad_cases=[]
    excessive=list(base);k,u,v,x=excessive[cut_indices[0]];excessive[cut_indices[0]]=(k,u,v,F(1))
    try:comparison.near_mode_certificate(excessive,reactive,base_mode,cut_indices,eps)
    except ValueError as e:assert 'inconclusive' in str(e);bad_cases.append('nonpositive budget')
    else:raise AssertionError('Insufficient slack certified')
    detuned=list(base);k,u,v,x=detuned[0];detuned[0]=(k,u,v,2*x)
    try:comparison.near_mode_certificate(detuned,reactive,base_mode,cut_indices,eps)
    except ValueError:bad_cases.append('outside relative box')
    else:raise AssertionError('Out-of-box component certified')
    for invalid in (F(-1,10),F(1),0.01):
        try:comparison.relative_bound(invalid)
        except ValueError:bad_cases.append('invalid relative datum')
        else:raise AssertionError('Invalid relative datum accepted')
    return {'relative_error':'1/100','relative_response_bound':str(bound),'relative_phasor_comparisons':relative_cases,
      'near_mode_corner_controls':near_cases,'weak_cross_conductance_budget':'1/100','near_mode_strict_margin':'3/40',
      'exact_margin_slack':str(sym-budget-F(3,40)),'imaginary_false_extension_error_squared':str(diff.normsq()),
      'resistor_factor_controls':sharp_controls,'certificate_corruptions_rejected':corruptions,
      'domain_or_budget_rejections':bad_cases}


def consumer_checks():
    root=Path(__file__).resolve().parent;spec=root/'near_mode_example.json'
    with tempfile.TemporaryDirectory() as tmp:
        output=Path(tmp)/'certificate.json'
        made=subprocess.run([sys.executable,'-B','-S',str(root/'positive_real_comparison.py'),str(spec),'--output',str(output)],capture_output=True,text=True,check=True,timeout=30)
        assert not made.stdout
        run=subprocess.run([sys.executable,'-B','-S',str(root/'positive_real_comparison.py'),str(output),'--verify'],capture_output=True,text=True,check=True,timeout=30)
        assert json.loads(run.stdout)=={'status':'PASS','strict_margin':'3/40'}
        record=json.loads(output.read_bytes());record['certificate']['remaining_slack']='0';output.write_text(json.dumps(record),encoding='utf-8')
        rejected=subprocess.run([sys.executable,'-B','-S',str(root/'positive_real_comparison.py'),str(output),'--verify'],capture_output=True,text=True,timeout=30)
        assert rejected.returncode and 'binding differs' in rejected.stderr
    return {'example_produced':1,'example_consumed':1,'corrupted_output_rejected':1}


def main():
    print(json.dumps({'status':'PASS','support_inventory':support_inventory(),'mode_face':mode_checks(),'bridge_formula':bridge_checks(),
      'near_mode_comparison':comparison_checks(),'balanced_shortcuts':obstruction_controls(),
      'portable_consumer':consumer_checks(),
      'coverage_unchanged':{'covered':1334,'remaining':796},'selected_Lean_statements_unchanged':41,
      'scope':'Written universal internal-mode classification and positive-real comparison, with finite exact controls. The regular balanced region and a uniform near-mode transfer remain open; no whole balanced exclusion, independent review, new Lean, hardware or novelty claim.'},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
