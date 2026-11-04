#!/usr/bin/env python3
"""Bounded independent K-COS audit. Run serially: mpmath.iv is shared state."""
from __future__ import annotations
import argparse, hashlib, json, platform, sys, time
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ENGINE=ROOT/'engine' if (ROOT/'engine').is_dir() else ROOT.parents[1]/'monographs/cos-method/engine'
sys.path.insert(0,str(ENGINE))
import mpmath as mp
import numpy as np
import scipy
import sympy as sp
from interval_kcos import interval_positive_logsf, design_positive_tail_parameters, scaled_chi_square_target_point
from directed_accuracy import directed_relative_accuracy, interval_endpoint_strings
from accuracy_driven import certified_positive_logsf
from independent_reference import exact_law_tail, imhof_quad
PIN='332d8c86b712fbbabf799c0476a9991848c91c2e'
BLOBS={'directed_accuracy.py':'e9ebc7d07fa3d96edbdf97d5b6ca6d66082cb4b1',
       'interval_kcos.py':'49db8e11f8ef591d72f7f2369de64d4f90743903',
       'accuracy_driven.py':'b113179002cda9f5e6a66d88ff998a7241147535'}

def clean(x):
    if isinstance(x,float) and not np.isfinite(x):return str(x)
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x

def save(name,x):
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results'/name).write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')

def check_sources():
    rows=[]
    for name,expected in BLOBS.items():
        b=(ENGINE/name).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        if actual!=expected:raise RuntimeError('Published source identity mismatch: '+name)
        rows.append({'path':'monographs/cos-method/engine/'+name,'git_blob_sha1':actual,
                     'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
    save('environment.json',{'source_revision':PIN,'sources':rows,'python':sys.version,
         'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,
         'mpmath':mp.__version__,'sympy':sp.__version__,'parallel_interval_calls':False})

def analyze(interval,reference,tolerance):
    a,b=map(Decimal,interval_endpoint_strings(interval));ra,rb=map(Decimal,reference['log10'])
    finite=a.is_finite() and b.is_finite()
    return {'finite_enclosure':finite,'reference_fully_contained':bool(a<=ra and rb<=b) if finite else None,
            'requested_relative_accuracy':str(tolerance),
            'accuracy_decision':asdict(directed_relative_accuracy(interval,tolerance,dps=180))}

def exact_structure():
    A=sp.Matrix([[1,1,1,1,1,1],[1,-1,1,-1,1,-1],[1,1,-1,-1,-1,-1],[1,-1,-1,1,-1,1]])/2
    U=sp.Matrix([[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]])/2
    H=A*A.T;blocks=[A[:,i:i+2] for i in (0,2,4)];v=sp.Matrix([1,2,-1,0])
    q=sp.Symbol('q',nonnegative=True);sf=2*sp.exp(-q/4)-sp.exp(-q/2)
    checks={'orthogonality':U.T*U==sp.eye(4),'diagonalization':H==U*sp.diag(1,1,2,2)*U.T,
      'storage_partition':sum((B*B.T for B in blocks),sp.zeros(4))==H,
      'streamed_action':sum((B*(B.T*v) for B in blocks),sp.zeros(4,1))==H*v,
      'law_derivative':sp.simplify(sp.diff(sf,q)+(sp.exp(-q/4)-sp.exp(-q/2))/2)==0,
      'law_at_zero':sf.subs(q,0)==1}
    assert all(checks.values())
    def matrix(M):return [[str(x) for x in row] for row in M.tolist()]
    save('matrix_example.json',{'factor':matrix(A),'covariance':'I_4',
      'statistic':'Q = Z^T (A A^T) Z; no extra factor of one half','gram':matrix(H),
      'orthogonal_basis':matrix(U),'spectrum':['1','1','2','2'],
      'storage_blocks':[matrix(B) for B in blocks],'action_input':matrix(v),'action_output':matrix(H*v),
      'checks':checks,'survival':'2 exp(-q/4) - exp(-q/2), q >= 0',
      'scope':'Exact symbolic finite-factor calculation, not black-box eigensolver post-verification'})
    print('Exact matrix/law checks:',len(checks),'passed',flush=True)

def running():
    exact_structure();eig=['1','1','2','2'];ref=exact_law_tail('40',eig)
    with mp.workdps(100):theta=mp.nstr((14-mp.sqrt(26))/40,90)
    for modes in (8192,16384):
        start=time.perf_counter()
        out=interval_positive_logsf('40',eig,theta_decimal=theta,upper_decimal='512',eta_decimal='0.245',K=modes,interval_dps=60)
        row={'id':f'running-{modes}','input':{'q':'40','eigenvalues':eig},'engine':asdict(out),
             'seconds':time.perf_counter()-start,'independent_reference':ref,**analyze(out.log10_interval,ref,'0.02')}
        row['tight_request_0_001_accepted']=directed_relative_accuracy(out.log10_interval,'0.001',dps=180).accepted
        assert row['reference_fully_contained'] and row['accuracy_decision']['accepted']==(modes==16384)
        assert not row['tight_request_0_001_accepted']
        save(row['id']+'.json',row)
        print(row['id'],'accepted',row['accuracy_decision']['accepted'],'ratio',row['accuracy_decision']['ratio_upper'],flush=True)

CASES=[('equal-8','40',['1']*8),
 ('clustered-8','32',[v for v in ['0.999999','1','1.000001','1.000002'] for _ in range(2)]),
 ('mixed-12','70',[v for v in ['0.25','0.5','1','2','3','4'] for _ in range(2)]),
 ('wide-8','1000',[v for v in ['0.000001','0.01','1','100'] for _ in range(2)]),
 ('scale-small','0.000000000032',[v for v in ['0.000000000000999999','0.000000000001','0.000000000001000001','0.000000000001000002'] for _ in range(2)]),
 ('scale-large','32000000000000',[v for v in ['999999000000','1000000000000','1000001000000','1000002000000'] for _ in range(2)])]

def spectra():
    for name,q,eig in CASES:
        ref=exact_law_tail(q,eig);ref2=exact_law_tail(q,eig,digits=220)
        assert Decimal(ref['log10'][0])<=Decimal(ref2['log10'][0])<=Decimal(ref2['log10'][1])<=Decimal(ref['log10'][1])
        start=time.perf_counter()
        out=certified_positive_logsf(q,eig,relative_accuracy='0.0001',initial_K=128,initial_L='10',max_K=1024,
                                    max_L=14,initial_interval_dps=60,max_interval_dps=60,working_dps=140)
        row={'id':name,'input':{'q':q,'eigenvalues':eig},'engine':asdict(out),'seconds':time.perf_counter()-start,
             'independent_reference':ref,'reference_220_digit_contained_in_180_digit':True,
             **analyze(out.log10_interval,ref,'0.0001'),'imhof_quad':imhof_quad(q,eig)}
        if row['finite_enclosure']:assert row['reference_fully_contained'],name
        assert out.certified==row['accuracy_decision']['accepted']
        midpoint=(Decimal(ref['probability'][0])+Decimal(ref['probability'][1]))/2
        row['imhof_absolute_difference_from_reference_midpoint']=str(abs(Decimal.from_float(row['imhof_quad']['probability'])-midpoint))
        save(name+'.json',row)
        print(name,'certified',out.certified,'K',out.K,'finite',row['finite_enclosure'],flush=True)

def deep():
    for depth in (100,1000,5000):
        eig=['0.02']*80
        q=scaled_chi_square_target_point(-depth,coefficient_decimal='0.02',df=80,working_dps=220,output_digits=180)
        ref=exact_law_tail(q,eig,digits=220)
        p=design_positive_tail_parameters(q,eig,L='10',working_dps=220,output_digits=180)
        start=time.perf_counter()
        out=interval_positive_logsf(q,eig,theta_decimal=p['theta'],upper_decimal=p['upper'],eta_decimal=p['eta'],K=128,interval_dps=90)
        row={'id':f'deep-{depth}','input':{'q':q,'eigenvalues':eig},'engine':asdict(out),
             'seconds':time.perf_counter()-start,'independent_reference':ref,**analyze(out.log10_interval,ref,'1e-8'),
             'binary64_comparison':'Not assessed: absolute-error quadrature cannot establish this relative tail accuracy'}
        assert row['reference_fully_contained'] and row['accuracy_decision']['accepted']
        save(row['id']+'.json',row)
        print(row['id'],'reference contained; ratio',row['accuracy_decision']['ratio_upper'],flush=True)
        if depth==5000:
            start=time.perf_counter()
            r=certified_positive_logsf(q,eig,relative_accuracy='1e-18',max_K=512,max_L=20,
                                      initial_interval_dps=60,max_interval_dps=90,working_dps=220)
            r2={'id':'deep-5000-tight','input':row['input'],'engine':asdict(r),'seconds':time.perf_counter()-start,
                'independent_reference':ref,**analyze(r.log10_interval,ref,'1e-18')}
            assert r.certified and r2['reference_fully_contained']
            save(r2['id']+'.json',r2)
            print(r2['id'],'ratio',r2['accuracy_decision']['ratio_upper'],flush=True)

def controls():
    rows=[]
    base=dict(q_decimal='40',eigenvalue_decimals=['1','1','2','2'],theta_decimal='0.2',upper_decimal='512',eta_decimal='0.245',K=32,interval_dps=50)
    bad=[('rank-one',{'eigenvalue_decimals':['1']}),('rank-two',{'eigenvalue_decimals':['1','2']}),
         ('zero-coefficient',{'eigenvalue_decimals':['1','1','0','2']}),('negative-coefficient',{'eigenvalue_decimals':['1','1','-1','2']}),
         ('nan-coefficient',{'eigenvalue_decimals':['1','1','NaN','2']}),('infinite-threshold',{'q_decimal':'Infinity'}),
         ('negative-threshold',{'q_decimal':'-1'}),('zero-tilt',{'theta_decimal':'0'}),('reversed-tilts',{'eta_decimal':'0.1'}),
         ('mgf-boundary',{'eta_decimal':'0.25'}),('support-equals-threshold',{'upper_decimal':'40'}),('zero-modes',{'K':0}),('zero-precision',{'interval_dps':0})]
    for name,changes in bad:
        try:interval_positive_logsf(**(base|changes))
        except (ValueError,ArithmeticError) as exc:rows.append({'id':name,'rejected':True,'exception':type(exc).__name__,'message':str(exc)})
        else:raise AssertionError('Invalid input accepted: '+name)
    kwargs=dict(relative_accuracy='1e-40',initial_K=32,max_K=32,initial_L='8',max_L=8,initial_interval_dps=30,max_interval_dps=30,working_dps=100)
    r=certified_positive_logsf('100',['1']*8,**kwargs);assert not r.certified
    rows.append({'id':'exhausted-budget','certified':r.certified,'result':asdict(r)})
    probes=[]
    for name,changes in [('initial-K-exceeds-max',{'initial_K':128,'max_K':32}),('odd-L-cap',{'initial_L':'8','max_L':9}),
                         ('initial-dps-exceeds-max',{'initial_interval_dps':60,'max_interval_dps':30})]:
        kw=kwargs|changes;r=certified_positive_logsf('100',['1']*8,**kw)
        exceeded=r.K>kw['max_K'] or int(r.L)>kw['max_L'] or r.interval_dps>kw['max_interval_dps']
        probes.append({'id':name,'requested':kw,'returned':{'K':r.K,'L':r.L,'interval_dps':r.interval_dps},
                       'exceeded_declared_resource_cap':exceeded,'certified':r.certified})
    save('negative-controls.json',{'domain_and_budget_controls':rows,'resource_api_probes':probes})
    print('Domain/budget controls:',len(rows),'passed; resource-cap findings:',sum(r['exceeded_declared_resource_cap'] for r in probes),flush=True)

def packet():
    rows=[]
    with mp.workdps(120):
        s=mp.mpc('0.1','0.4');lams=list(map(mp.mpf,['1.96','1.98','2.02','2.04']));center=mp.mpf(2);delta=[l-center for l in lams]
        alpha=2*s/(1-2*s*center);rho=abs(alpha)*max(map(abs,delta));exact=-mp.fsum(mp.log(1-2*s*l) for l in lams)/2
        for order in (0,2,4,6,8,10):
            approx=-2*mp.log(1-2*s*center)+mp.fsum(alpha**m*mp.fsum(d**m for d in delta)/m for m in range(1,order+1))/2
            error=abs(exact-approx);bound=2*rho**(order+1)/((order+1)*(1-rho));assert error<=bound
            rows.append({'order':order,'point_error':mp.nstr(error,80),'analytic_bound_point_value':mp.nstr(bound,80)})
    save('packet-control.json',{'scope':'Six high-precision point checks of the analytic packet bound, not directed packet certification',
         's':['0.1','0.4'],'spectrum':['1.96','1.98','2.02','2.04'],'center':'2','rows':rows})
    print('Packet analytic comparisons: 6 passed',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['running','spectra','deep','controls','packet','all']);args=p.parse_args()
    check_sources()
    for name,f in {'running':running,'spectra':spectra,'deep':deep,'controls':controls,'packet':packet}.items():
        if args.stage in (name,'all'):f()
