"""Adversarial exact physical checks of the finite mixed-loss theorem candidate."""
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from exact_phasor import C,response
import loss_certificate as loss

def problem(branches,delta='1/100',reference='1'):
    return {'branches':branches,'frequency_band':['1/2','2'],'relative_tolerance':delta,
      'reference_R':reference,'samples':['1/2','1','2']}

def item(kind,u,v,value,R=None):
    out={'kind':kind,'nodes':[u,v],'value':str(value)}
    if kind!='R':out['series_R']=str(R)
    return out

def main():
    graphs=[
      [item('R',1,0,1)],
      [item('L',1,0,'1/4',1)],
      [item('C',1,0,4,1)],
      [item('L',1,2,'1/4','1/2'),item('C',2,0,4,'1/2')],
      [item('L',1,2,'1/1000000','1/1000'),item('C',2,0,1000000,'1/1000'),item('R',1,0,3)],
      [item('L',1,2,'1/3',2),item('R',2,0,3),item('C',1,3,'5/2',2),
       item('R',3,0,5),item('L',2,3,'4/5',3)],
      [item('C',1,2,2,'1/2'),item('R',3,4,7)],  # structurally open port
      [item('C',1,0,4,1),item('L',1,1,3,2)],  # loop is harmless
      [item('L',1,2,'1/4','1/20'),item('C',2,3,4,'1/20'),item('R',3,0,'9/10')],
    ]
    corners=0;branch_checks=0;bilinear_checks=0;power_checks=0;reconstruction_checks=0;max_ratio=F(0)
    records=[]
    for k,raw in enumerate(graphs):
        p=problem(raw,reference='2' if k==4 else '1')
        cert=loss.certificate(p);loss.verify(cert);records.append(cert)
        branches,band,delta,reference,samples=loss.parse(p)
        B=F(cert['branch_mismatch_squared_budget'])
        original,indices=loss.expand(branches,reference)
        for omega in samples:
            physical=response(original,C(0,omega));z=loss.impedances(branches,omega,reference)
            compound=loss.response_impedances(z)
            assert physical['gamma']==compound['gamma'];reconstruction_checks+=1
            g=compound['gamma'];P=sum(e[2].re*i.normsq() for e,i in zip(z,compound['currents']))
            assert 4*P==1-g.normsq();power_checks+=1
            for signs in product((-1,1),repeat=len(original)):
                perturbed=[(kind,u,v,x*(1+delta*sign)) for (kind,u,v,x),sign in zip(original,signs)]
                new_branches=[]
                for branch,loc in zip(branches,indices):
                    kind,u,v,value,R=branch
                    if kind=='R':
                        new_branches.append((kind,u,v,perturbed[loc[0]][3]*reference,perturbed[loc[0]][3]*reference))
                    else:
                        new_R=perturbed[loc[0]][3]*reference
                        new_value=perturbed[loc[1]][3]*(reference if kind=='L' else 1/reference)
                        new_branches.append((kind,u,v,new_value,new_R))
                fresh_z=loss.impedances(new_branches,omega,reference)
                actual=response(perturbed,C(0,omega));fresh=loss.response_impedances(fresh_z)
                assert actual['gamma']==fresh['gamma'];gp=fresh['gamma']
                variation=C()
                for old,new,i,j in zip(z,fresh_z,compound['currents'],fresh['currents']):
                    dz=new[2]-old[2]
                    assert dz.normsq()<=4*B*old[2].re*new[2].re
                    branch_checks+=1;variation+=dz*i*j
                assert gp-g==2*variation;bilinear_checks+=1
                error=(gp-g).normsq();right=B*(1-g.normsq())*(1-gp.normsq())
                assert error<=right,(k,omega,signs,error,right)
                if right:max_ratio=max(max_ratio,error/right)
                disk=next(row for row in cert['sample_disks'] if F(row['omega'])==omega)
                center=C(F(disk['center']['re']),F(disk['center']['im']))
                assert (gp-center).normsq()<=F(disk['radius_squared'])
                corners+=1
    # Exact local worst case for capacitive pairs and exact strongly damped example.
    delta=F(1,100);B=loss.budget(delta,F(1))
    assert B==F(19801,388119600) and B<F(1,19600)
    z=C(1,-1);zp=C(1-delta,-1/(1-delta))
    assert (zp-z).normsq()==4*B*z.re*zp.re
    matched=records[3];at_one=next(r for r in matched['sample_disks'] if r['omega']=='1')
    assert at_one['nominal_gamma']=={'re':'0','im':'0'}
    assert F(at_one['radius_squared'])==B/(1+B)
    moderate=records[8];at_one=next(r for r in moderate['sample_disks'] if r['omega']=='1')
    assert moderate['nominal_band_quality_bound']=='10'
    assert at_one['nominal_gamma']=={'re':'0','im':'0'}
    assert F(at_one['radius_squared'])==F(1009801,389129401)<F(1,385)
    controls=[]
    for field in ('branch_mismatch_squared_budget','nominal_band_quality_bound'):
        bad=deepcopy(matched);bad[field]='0'
        try:loss.verify(bad)
        except ValueError:controls.append(field)
        else:raise AssertionError('Corrupted certificate accepted')
    bad=deepcopy(matched);bad['sample_disks'][0]['radius_squared']='0'
    try:loss.verify(bad)
    except ValueError:controls.append('disk_mutation')
    else:raise AssertionError('Corrupted disk accepted')
    for value in (0,True,1.0):
        p=problem([item('L',1,0,1,1)]);p['branches'][0]['series_R']=value
        try:loss.certificate(p)
        except ValueError:controls.append('invalid_or_missing_loss_'+str(value))
        else:raise AssertionError('Invalid loss hypothesis accepted')
    for name,mutate in (
      ('non_object_branch',lambda p:p['branches'].__setitem__(0,3)),
      ('zero_denominator',lambda p:p.__setitem__('reference_R','1/0')),
      ('oversized_integer',lambda p:p.__setitem__('reference_R',1<<1025)),
      ('nonpositive_band',lambda p:p.__setitem__('frequency_band',['0','2']))):
        p=problem([item('L',1,0,1,1)]);mutate(p)
        try:loss.certificate(p)
        except ValueError:controls.append(name)
        else:raise AssertionError('Malformed component model accepted')
    print(json.dumps({'status':'PASS','graphs':len(graphs),'nominal_graph_reconstructions':reconstruction_checks,
      'physical_tolerance_corners':corners,'branch_mismatch_checks':branch_checks,
      'bilinear_checks':bilinear_checks,'power_identity_checks':power_checks,
      'largest_observed_squared_bound_ratio':str(max_ratio),'adversarial_controls':controls,
      'matched_example':matched,'sharp_capacitive_local_budget':str(B),
      'moderate_loss_matched_example':moderate,
      'scope':'Exact finite physical implementation/falsification controls only; the universal graph and continuous-box claims require the separate proof.'},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
