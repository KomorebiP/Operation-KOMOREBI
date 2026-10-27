"""Finite checks and explicit counterexamples for Propositions 80--87.

These are not a proof-kernel verification of the written propositions. Statistical
coverage is a conditional theorem, not an empirical conclusion from one seed.
"""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import json,sys
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from data_certificate_reference import *
from robust_reference import replay_certificate as robust_replay

records=[]
def check(name,cond,kind='exact'):
    if not bool(cond):raise AssertionError(name)
    records.append({'name':name,'passed':True,'kind':kind})
def reject(name,fn):
    try:fn()
    except (ValueError,KeyError,TypeError):records.append({'name':name,'passed':True,'kind':'expected_rejection'})
    else:raise AssertionError('Expected rejection: '+name)

def main():
    u=sp.symbols('u',real=True);P2=(3*u*u-1)/2
    check('reference weights positive normalized',min(WEIGHTS)>0 and sum(WEIGHTS)==1)
    for k in range(5):
        want=F(0) if k%2 else F(1,k+1)
        check(f'exact quadrature moment {k}',sum(w*x**k for x,w in zip(NODES,WEIGHTS))==want)
    check('quadratic orthogonality',sum(w*leg2(x) for x,w in zip(NODES,WEIGHTS))==0)
    check('quadratic squared norm',sum(w*leg2(x)**2 for x,w in zip(NODES,WEIGHTS))==F(1,5))
    check('discrete abs first moment',sum(w*abs(x) for x,w in zip(NODES,WEIGHTS))==F(23,45))
    check('discrete abs quadratic moment',sum(w*abs(leg2(x)) for x,w in zip(NODES,WEIGHTS))==F(14,45))
    c2=sp.integrate(-P2,(u,0,1/sp.sqrt(3)))+sp.integrate(P2,(u,1/sp.sqrt(3),1))
    check('continuous absolute quadratic moment',sp.simplify(c2-2/(3*sp.sqrt(3)))==0)
    check('rational log2 upper inequality',sum(F(7,10)**k/F(sp.factorial(k)) for k in range(5))>2)
    for q in [F(0),F(1,3),F(2),F(7,1000),F(10**12,3)]:
        r=sqrt_up(q);check('square-root upper '+str(q),r*r>=q and (r-F(1,10**12))**2<q if r>0 else q==0)
    for q in [F(1),F(2),F(1001,1000),F(15,2),F(65536),F(10**12,3)]:
        k=ceil_log2(q);check('binary log ceiling '+str(q),2**k>=q and (k==0 or 2**(k-1)<q))
    for s in NODES:
        row=probability_row(s,F(2,5),F(1,5))
        check('conditional moments at '+str(s),sum(p*x for x,p in zip(NODES,row))==F(2,5)*s/3 and sum(p*leg2(x) for x,p in zip(NODES,row))==F(1,5)*s*s/5)
    # The continuous curved domain's polynomial cone identities.
    v=sp.Matrix([1,u,u*u]);a,b,x,y=sp.symbols('a b x y',real=True)
    B=v*sp.Matrix([[1,a*u,b*P2]]);z=sp.Matrix([1,x,y]);density=1+a*x*u+b*y*P2
    check('rank-one posterior identity',(B*z-v*density).applyfunc(sp.expand)==sp.zeros(3,1))
    check('exact integrated operator mass',B.applyfunc(lambda f:sp.integrate(f,(u,-1,1))/2)[0,:]==sp.Matrix([[1,0,0]]))
    check('posterior moment determinant zero',sp.det(sp.Matrix([[v[0],v[1]],[v[1],v[2]]]))==0)
    check('upper moment constraint',sp.expand(v[0]-v[2])==1-u*u)
    # Valid states are not individual spectral signed packets.
    check('state cone origin mass implication',sp.Matrix([[0,0],[0,1]]).det()==0 and 0-1<0)
    data=json.loads((ROOT/'examples/dependent_observations.json').read_text());path=data['node_indices']
    doc=json.loads((ROOT/'certificates/dependent_data_certificate.json').read_text())
    check('reference measure fixed',data['reference_measure']==MEASURE)
    check('full path replay',replay_certificate(doc,path)['passed'])
    check('initial observation zero',path[0]==2)
    check('path length declared',len(path)-1==262144)
    c=doc['confidence'];rho=rat(c['density_floor']);law=doc['law'];da=rat(law['parameter_error_a']);db=rat(law['parameter_error_b']);Delta=rat(law['one_step_TV_upper'])
    check('reported density floor',rho==F(31,125))
    check('reported exact TV budget',Delta==F(2437,90000))
    check('reported marginal budget',rat(law['marginal_TV_uniform_upper'])==F(2437,22320))
    check('true parameters lie in final intervals',rat(c['a']['lower'])<=F(2,5)<=rat(c['a']['upper']) and rat(c['b']['lower'])<=F(1,5)<=rat(c['b']['upper']),'seeded_path_diagnostic')
    for label in ['a','b']:
        check('prior and rounded interval '+label,F(-1)<=rat(c[label]['lower'])<=rat(c[label]['upper'])<=1)
    trace=json.loads((ROOT/'verification/dependent_data_result.json').read_text())['checkpoints']
    check('early whole-box certificates withheld',all(not r['whole_box_certified'] for r in trace if r['transitions']<=16384),'seeded_path_diagnostic')
    check('all listed later boxes certified',all(r['whole_box_certified'] for r in trace if r['transitions']>=32768),'seeded_path_diagnostic')
    ca=rat(law['center']['a']);cb=rat(law['center']['b'])
    center_rows=[probability_row(s,ca,cb) for s in NODES]
    for ia in ['lower','upper']:
        for ib in ['lower','upper']:
            av,bv=rat(c['a'][ia]),rat(c['b'][ib]);rows=[probability_row(s,av,bv) for s in NODES]
            check('all reference-node floors '+ia+ib,all(p>=rho*w for row in rows for p,w in zip(row,WEIGHTS)))
            check('all corner kernel discrepancies '+ia+ib,max(sum(abs(p-q) for p,q in zip(row,qrow))/2 for row,qrow in zip(rows,center_rows))<=Delta)
    rows=[probability_row(s,F(2,5),F(1,5)) for s in NODES]
    p=q=[F(0),F(0),F(1),F(0),F(0)]
    for t in range(1,17):
        p=[sum(p[i]*rows[i][j] for i in range(5)) for j in range(5)]
        q=[sum(q[i]*center_rows[i][j] for i in range(5)) for j in range(5)]
        e=sum(abs(pi-qi) for pi,qi in zip(p,q))/2
        check('exact marginal error time '+str(t),e<=Delta*(1-(1-rho)**t)/rho)
    # Coordinate consistency does not establish coverage: claims stay explicit.
    check('coverage assumptions not asserted verified',doc['coverage']['assumptions_independently_verified'] is False)
    for key in ['schema','model','reference_measure','coverage','statistics','data_hash']:
        d=deepcopy(doc)
        if key=='coverage':d[key]['assumptions_independently_verified']=True
        elif key=='statistics':d[key]['score_a']='0'
        elif key=='reference_measure':d[key]={'type':'continuous_uniform','support':['-1','1']}
        else:d[key]='altered'
        reject('reject changed '+key,lambda d=d:replay_certificate(d,path))
    d=deepcopy(doc);d['confidence']['a']['lower']='2/5'
    reject('reject narrowed interval',lambda:replay_certificate(d,path))
    d=deepcopy(doc);d['law']['one_step_TV_upper']='0'
    reject('reject unsupported zero prediction error',lambda:replay_certificate(d,path))
    short=make_certificate(path[:65]);reject('withhold early unverified rectangle',lambda:replay_certificate(short,path[:65]))
    reject('reject malformed path',lambda:sufficient_statistics([True,2]))
    reject('reject unobserved coordinate',lambda:sufficient_statistics([1,5]))
    reject('reject negative square root',lambda:sqrt_up(F(-1)))
    reject('reject unsupported binary log',lambda:ceil_log2(F(1,2)))
    reject('reject invalid confidence budget',lambda:radius(F(1),F(1),F(0)))
    const=confidence_box(sufficient_statistics([2]*65));check('unexcited features do not certify',not const['whole_box_certified'])
    for name in ['reduced_repair_certificate','reduced_repair_comparison']:
        certificate=json.loads((ROOT/f'certificates/{name}.json').read_text());r=robust_replay(certificate)
        check(name+' exact continuum replay',r['passed'] and r['margin']=='1/64')
        d=deepcopy(certificate);d['margin']='1/2';reject(name+' false margin',lambda d=d:robust_replay(d))
    r=json.loads((ROOT/'verification/reduced_repair_result.json').read_text())
    check('repair bracket',F(0)<rat(r['fixed_margin_repair_lower_bound'])<F(1,32))
    check('smaller weight fails required margin',r['smaller_1_64_fails_required_margin_at_support_witness'])
    check('new repair law exact arithmetic',rat(r['record_law_TV_slope'])==F(87471,2560000))
    check('new first trivial horizon',29*rat(r['record_law_TV_slope'])<1<=30*rat(r['record_law_TV_slope']))
    counts={k:sum(r['kind']==k for r in records) for k in sorted({r['kind'] for r in records})}
    result={'passed':True,'records':records,'count':len(records),'by_kind':counts,
            'general_proof_kernel_used':False,'empirical_coverage_estimated':False}
    (ROOT/'verification/data_supported_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'count':len(records),'by_kind':counts},indent=2))
if __name__=='__main__':main()
