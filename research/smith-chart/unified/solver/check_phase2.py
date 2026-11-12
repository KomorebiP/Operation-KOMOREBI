"""Exact regression and falsification for systematic closure. Author: Komorebi P."""
from copy import deepcopy
from fractions import Fraction as F
from itertools import product,combinations
import json
from pathlib import Path
import first_order
import cauer
from exact_phasor import C,from_checked_graph,response,target_gamma
from composition_certificate import verify_composition_certificate
from pure_type_margins import certificate as margins
from resistor_bounds import endpoint_bound,verify_bound,verify_resistor_minimum
from parallel_refutation import certificate as parallel_certificate,verify as verify_parallel

FREQUENCIES=tuple(map(F,('1/100','1/10','1/2','1','3','10','100')))


def polyadd(p,q):
    out=[F(0)]*max(len(p),len(q))
    for i,v in enumerate(p):out[i]+=v
    for i,v in enumerate(q):out[i]+=v
    return out


def polymul(p,q):
    out=[F(0)]*(len(p)+len(q)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(q):out[i+j]+=a*b
    return out


def debye(poles,residues,constant=F(0)):
    # Forward partial-fraction generation shares no Cauer extraction code.
    P,Q=[F(constant)],[F(1)]
    for p,a in zip(poles,residues):
        factor=[F(p),F(1)]
        P=polyadd(polymul(P,factor),[F(a)*v for v in Q]);Q=polymul(Q,factor)
    return {'P':list(map(str,P)),'Q':list(map(str,Q))}


def check_output(result,target):
    check=verify_composition_certificate(result['certificate'],expected_target=target,
        expected_budget=result.get('reactive_minimum',result['reduced_degree'] if 'reduced_degree' in result else 0))
    assert check['global_minimum_proved_by_degree']
    edges=from_checked_graph(check['rebuilt_graph'])
    for frequency in FREQUENCIES:
        s=C(0,frequency)
        assert response(edges,s)['gamma']==target_gamma(target['P'],target['Q'],s)
    return edges


def main():
    first_cases=0;first_certificates=0;first_boundary=0;nonpassive=0;graph_samples=0
    cases={};robust_graphs=[]
    for a,b,c,d in product(range(5),repeat=4):
        if c==d==0:continue
        target={'P':[b,a],'Q':[d,c]}
        result=first_order.synthesize(target);first_cases+=1
        if a==b==0:
            assert result['status']=='IDEAL_SHORT_BOUNDARY';first_boundary+=1;continue
        assert result['status']=='CERTIFIED',(target,result)
        edges=check_output(result,target);graph_samples+=len(FREQUENCIES);first_certificates+=1
        cases[result['case']]=cases.get(result['case'],0)+1
        assert len([e for e in edges if e[0]=='R'])==result['resistor_minimum']
        lower=endpoint_bound(target)
        assert verify_bound(lower,target)==result['resistor_minimum']
        if not any(old[0]==result['case'] for old in robust_graphs):robust_graphs.append((result['case'],edges))
    controls=[]
    for target,status in [
        ({'P':[-1],'Q':[1]},'NOT_POSITIVE_REAL'),
        ({'P':[1,1],'Q':[-1,1]},'NOT_POSITIVE_REAL'),
        ({'P':[-1,2],'Q':[1,1]},'NOT_POSITIVE_REAL'),
        ({'P':[1,-2],'Q':[1,1]},'NOT_POSITIVE_REAL'),
        ({'P':[1,0,1],'Q':[1,1]},'UNKNOWN'),
        ({'P':[True,1],'Q':[1,1]},'INVALID_INPUT'),
        ({'P':[1.0,1],'Q':[1,1]},'INVALID_INPUT'),
        ({'P':[1],'Q':[0]},'INVALID_INPUT')]:
        result=first_order.synthesize(target);assert result['status']==status,(target,result)
        controls.append(status)
    fixtures=[]
    for n in range(1,5):
        for offset in range(3):
            poles=[F(j+offset,2) for j in range(n)]
            residues=[F((j+offset)%3+1,j+1) for j in range(n)]
            for constant in (F(0),F(3,4)):
                fixtures.append(debye(poles,residues,constant))
    fixtures.extend([{'P':[2,1],'Q':[2,4,1]},
        debye([F(j+1) for j in range(15)],[F(1,j+1) for j in range(15)],F(1,2))])
    cauer_cases=0
    for target in fixtures:
        for kind in ('RC','RL'):
            if kind=='RL':
                power=max(len(target['P']),len(target['Q']))
                current={name:list(reversed(target[name]+['0']*(power-len(target[name])))) for name in ('P','Q')}
            else:current=target
            result=cauer.synthesize(current,kind);assert result['status']=='CERTIFIED',(kind,current,result)
            edges=check_output(result,current);graph_samples+=len(FREQUENCIES);cauer_cases+=1
            assert {e[0] for e in edges}<={'R','C' if kind=='RC' else 'L'}
            if len(edges)<=7 and len([e for e in edges if e[0]!='R'])>=2:
                if not any(old[0]==kind for old in robust_graphs):robust_graphs.append((kind,edges))
    # Keep mutations outside the producer and consumer. A changed branch must not
    # be accepted merely because the surrounding target metadata is unchanged.
    witness=first_order.synthesize({'P':[1,2],'Q':[1,1]})['certificate']
    corrupted=deepcopy(witness);corrupted['target']['P'][0]='2'
    try:verify_composition_certificate(corrupted,expected_target=witness['target'],expected_budget=1)
    except ValueError:controls.append('corrupted_target_rejected')
    else:raise AssertionError('Consumer accepted corrupted target')
    changed=deepcopy(witness)
    def corrupt_branch(node):
        if node['op']=='element':node['value']=str(F(node['value'])+1);return
        corrupt_branch(node['children'][0])
    corrupt_branch(changed['expression'])
    try:verify_composition_certificate(changed,expected_target=witness['target'],expected_budget=1)
    except ValueError:controls.append('corrupted_physical_branch_rejected')
    else:raise AssertionError('Consumer accepted corrupted physical branch')
    scaled={'P':['-3/5','-6/5'],'Q':['-3/5','-3/5']}
    scaled_result=first_order.synthesize(scaled)
    assert scaled_result['status']=='CERTIFIED';check_output(scaled_result,scaled)
    graph_samples+=len(FREQUENCIES)
    controls.append('negative_common_scaling')
    for kind in ('RC','RL'):
        outside=cauer.synthesize({'P':[4,3,6],'Q':[9,2,6]},kind)
        assert outside['status']=='OUTSIDE_CERTIFIED_CLASS',outside
        controls.append('Hughes_outside_'+kind)
    large=debye([F(j+1) for j in range(16)],[F(1) for _ in range(16)])
    assert cauer.synthesize(large)['status']=='UNKNOWN';controls.append('Cauer_degree_cap_UNKNOWN')
    hughes=json.loads((Path(__file__).resolve().parent/'hughes_two_resistor.json').read_bytes())
    hughes_R=verify_resistor_minimum(hughes,hughes['target'],5)
    assert hughes_R['resistor_minimum_certified'] and hughes_R['lower_bound']==2
    false_bound=endpoint_bound({'P':[1,2],'Q':[1,1]});false_bound['resistors_at_least']=3
    try:verify_bound(false_bound,{'P':[1,2],'Q':[1,1]})
    except ValueError:controls.append('corrupted_resistor_bound_rejected')
    else:raise AssertionError('False resistor bound accepted')
    delta=F(1,100);bound=delta/(1-delta);tolerance_cases=0;power_cases=0
    bridge=[('R',1,2,F(2)),('R',2,0,F(3)),('R',1,3,F(5)),
            ('C',3,0,F(7,5)),('C',2,3,F(4,3))]
    robust_graphs.append(('bridge_RC',bridge))
    robust_graphs.append(('bridge_RL',[(('L' if k=='C' else k),u,v,x) for k,u,v,x in bridge]))
    for label,edges in robust_graphs:
        for frequency in FREQUENCIES:
            base=response(edges,C(0,frequency))
            gamma=base['gamma'];power=C()
            for (kind,_,_,value),current in zip(edges,base['currents']):
                z=C(value) if kind=='R' else C(0,frequency*value) if kind=='L' else C(0,-1/(frequency*value))
                power+=z*current.normsq()
            assert 4*power.re==1-gamma.normsq()
            assert 2*power.im==gamma.im
            # Same-sign reactances prevent the LC cancellation used by the
            # mixed-network counterexample below.
            assert power.im<=0 if all(e[0] in ('R','C') for e in edges) else power.im>=0
            power_cases+=1
            for signs in product((-1,1),repeat=len(edges)):
                perturbed=[(kind,u,v,value*(1+sign*delta)) for (kind,u,v,value),sign in zip(edges,signs)]
                new_response=response(perturbed,C(0,frequency));changed=new_response['gamma']
                assert (changed-gamma).normsq()<=bound*bound,(label,frequency,signs)
                variation=C()
                for old,new,i,j in zip(edges,perturbed,base['currents'],new_response['currents']):
                    kind,_,_,v=old;new_v=new[3]
                    dz=C(new_v-v) if kind=='R' else C(0,frequency*(new_v-v)) if kind=='L' else C(0,(1/v-1/new_v)/frequency)
                    variation+=dz*i*j
                assert changed-gamma==2*variation
                tolerance_cases+=1
    # A universal extension to mixed RLC is false, even with one resistor.
    R,L,cap=F(1,1000),F(1,1000000),F(1000000)
    mixed=[('R',1,2,R),('L',2,0,L),('C',2,0,cap)]
    changed=[(kind,u,v,value*(1+delta) if kind=='L' else value) for kind,u,v,value in mixed]
    g0=response(mixed,C(0,1))['gamma'];g1=response(changed,C(0,1))['gamma']
    assert g0==C(1) and (g1-g0).normsq()>F(199,100)**2
    record=margins()
    parallel=parallel_certificate();parallel_check=verify_parallel(parallel)
    broken=deepcopy(parallel);broken['proof']['squares'][0]['weight']='0'
    try:verify_parallel(broken)
    except ValueError:controls.append('corrupted_parallel_refutation_rejected')
    else:raise AssertionError('False refutation accepted')
    print(json.dumps({'status':'PASS','first_order_inputs':first_cases,'first_order_certificates':first_certificates,
        'ideal_short_boundaries':first_boundary,'first_order_cases':cases,'adversarial_controls':controls,
        'cauer_certificates':cauer_cases,'cauer_maximum_degree':15,'independent_exact_phasor_samples':graph_samples,
        'power_identity_checks':power_cases,'one_percent_tolerance_checks':tolerance_cases,
        'Hughes_resistor_minimum':hughes_R,
        'proved_RC_RL_uniform_bound':'1/99','mixed_RLC_counterexample':{'relative_L_change':'1/100',
        'R':str(R),'L':str(L),'C':str(cap),'omega':'1','error_norm_squared':str((g1-g0).normsq()),'error_strictly_above':'199/100'},
        'pure_type_margins':record,'parallel_RLC_refutation':parallel_check,
        'scope':'Exact finite implementation and falsification checks. Universal subclass scope comes from the written proofs and explicitly scoped Lean lemmas, not the case count.'},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
