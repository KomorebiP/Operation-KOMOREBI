#!/usr/bin/env python3
"""Exact finite certificate regressions with an independent determinant oracle."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, permutations
from collections import Counter
from datetime import datetime, timezone
import copy, json, sys, hashlib
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'examples'))
import inexact_repair_certificate as c
import budgeted_repair as b
counts=Counter(); cases=Counter(); rejected=[]; invalid=[]
def check(value,label):
    counts[label]+=1
    if not value:raise AssertionError(label)
def determinant(a):
    # Leibniz formula, independent of the certificate program's elimination.
    n=len(a);total=F(0)
    for p in permutations(range(n)):
        sign=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=F(sign)
        for i in range(n):term*=a[i][p[i]]
        total+=term
    return total

def cramer(a,r):
    de=determinant(a)
    if not de:raise ArithmeticError('Singular independent oracle')
    out=[]
    for j in range(len(a)):
        aj=[row[:] for row in a]
        for i in range(len(a)):aj[i][j]=r[i]
        out.append(determinant(aj)/de)
    return out

def oracle(d,p,r,alpha):
    n=len(d[0]);k=len(p);q=n+k
    a=[[F(0) for _ in range(q)] for _ in range(q)]
    rhs=[F(0)]*q
    for i in range(n):
        rhs[i]=sum(d[h][i]*r[h] for h in range(len(d)))
        for j in range(n):a[i][j]=sum(d[h][i]*d[h][j] for h in range(len(d)))+(alpha if i==j else 0)
    for h in range(k):
        for i in range(n):a[n+h][i]=a[i][n+h]=p[h][i]
    return cramer(a,rhs)[:n]

ps=[[],[[F(1),F(0)]],[[F(1),F(-1)]],[[F(1),F(0)],[F(0),F(1)]]]
for idx,vals in enumerate(product([-1,0,1],repeat=4)):
    d=[[F(vals[0]),F(vals[1])],[F(vals[2]),F(vals[3])]]
    p=ps[idx%len(ps)];basis=b.kernel_basis(p,2);k=len(basis[0])
    for al in [F(1,4),F(1),F(4)]:
      for r in [[F(0),F(0)],[F(1),F(-1)],[F(2),F(1)]]:
        optimum=oracle(d,p,r,al)
        jstar=b.norm2(b.sub(r,b.mv(d,optimum)))+al*b.norm2(optimum)
        for cs in [[F(0)]*k,[F(i+1,2) for i in range(k)]]:
          a=b.mv(basis,cs);record=c.certify(d,p,[1,2],al,a,measured_residual=r)
          x=record['certificate'];err=b.sub(a,optimum);cases['ambient_kkt_comparisons']+=1
          check(x['protected_before']==x['protected_after'],'exact protection')
          check(x['normal_residual_norm_squared']==b.norm2(x['normal_residual']),'actual gradient norm')
          check(b.norm2(err)<=x['correction_error_norm_squared_upper'],'normal-residual error certificate')
          check(b.norm2(b.mv(d,err))<=x['fitted_error_norm_squared_upper'],'sharp fitted-error certificate')
          check(F(0)<=x['objective']-jstar<=x['objective_suboptimality_upper'],'objective certificate')
          check(x['objective']-jstar==b.norm2(b.mv(d,err))+al*b.norm2(err),'energy identity against determinant oracle')
          check(x['dual_value']<=jstar<=x['objective'],'independent primal dual bracket')
          check(x['duality_gap']==x['normal_residual_norm_squared']/al,'residual witness exact gap')
          check(b.norm2(err)<=x['dual_correction_error_norm_squared_upper'],'dual distance certificate')
          check(c.verify_record(b.jsonable(record)),'serialized certificate replay')
          if cs==[F(0)]*k:
            z=[r[0]+1,r[1]-2]
            alt=c.certify(d,p,[1,2],al,a,measured_residual=r,dual_witness=z)['certificate']
            cases['independent_dual_witnesses']+=1
            check(alt['dual_value']<=jstar,'arbitrary witness lower bound')
            check(alt['duality_gap_identity_residual']==0,'arbitrary witness gap identity')
          if k and al==1 and r==[F(1),F(-1)]:
            transforms=[[[F(7) if i==j else F(0) for j in range(k)] for i in range(k)],
                        [[F(1,7) if i==j else F(0) for j in range(k)] for i in range(k)]]
            if k==2:transforms.append([[F(1),F(1)],[F(0),F(1)]])
            for change in transforms:
                newbasis=b.mm(basis,change)
                alt=c.certify(d,p,[1,2],al,a,measured_residual=r,basis=newbasis)['certificate']
                cases['nonorthogonal_basis_changes']+=1
                for key in ['normal_residual','normal_residual_norm_squared','objective','dual_value','duality_gap','candidate','correction_error_norm_squared_upper']:
                    check(alt[key]==x[key],'basis-invariant '+key)

# Structured higher-dimensional and redundant-prescription fixtures.
# The independent KKT oracle uses an explicitly supplied independent row set.
fixtures=[
 ([[1,2,-1],[0,1,2]],[[1,-1,0]],[[1,-1,0]],[1,2,3],[1,-2], 'three-dimensional'),
 ([[1,0,2,-1],[0,2,1,1]],[[1,0,1,0],[0,1,0,-1]],[[1,0,1,0],[0,1,0,-1]],[1,2,3,4],[2,-1], 'four-dimensional'),
 ([[1,2,-1],[0,1,2]],[[1,-1,0],[2,-2,0]],[[1,-1,0]],[1,2,3],[1,-2], 'redundant-prescription')]
for draw,praw,indraw,fraw,rraw,label in fixtures:
    d=[[F(x) for x in row] for row in draw];p=[[F(x) for x in row] for row in praw]
    independent=[[F(x) for x in row] for row in indraw];f=list(map(F,fraw));r=list(map(F,rraw))
    basis=b.kernel_basis(p,len(f));k=len(basis[0])
    for al in [F(1,4),F(1),F(3)]:
        optimum=oracle(d,independent,r,al)
        jstar=b.norm2(b.sub(r,b.mv(d,optimum)))+al*b.norm2(optimum)
        for cs in [[F(0)]*k,[F(i+1,3) for i in range(k)]]:
            proposal=b.mv(basis,cs)
            record=c.certify(d,p,f,al,proposal,measured_residual=r)
            x=record['certificate'];e=b.sub(proposal,optimum)
            cases['structured_'+label]+=1
            check(x['protected_before']==x['protected_after'],'structured exact protection')
            check(b.norm2(e)<=x['correction_error_norm_squared_upper'],'structured correction bound')
            check(b.norm2(b.mv(d,e))<=x['fitted_error_norm_squared_upper'],'structured fitted bound')
            check(F(0)<=x['objective']-jstar<=x['objective_suboptimality_upper'],'structured objective bound')
            check(x['objective']-jstar==b.norm2(b.mv(d,e))+al*b.norm2(e),'structured energy identity')
            check(x['dual_value']<=jstar<=x['objective'],'structured primal dual bracket')
            check(x['duality_gap']==x['normal_residual_norm_squared']/al,'structured residual-witness gap')
            check(c.verify_record(b.jsonable(record)),'structured serialized certificate replay')

for t,al,noise,offset in product([F(0),F(1,2),F(1),F(2)], [F(1,16),F(1,4),F(1),F(4)],
                                 [F(-1,10),F(0),F(1,10)], [F(-1,5),F(0),F(1,5)]):
    r=F(1);s=r+noise;astar=t*r/(t*t+al);anom=t*s/(t*t+al);a=anom+offset
    g=(t*t+al)*a-t*s;root={F(1,16):F(1,4),F(1,4):F(1,2),F(1):F(1),F(4):F(2)}[al]
    check(abs(a-astar)<=abs(g)/al+abs(noise)/(2*root),'combined solver and data error')
    cases['scalar_noise_solver_cases']+=1

base=c.certify([[1,0]],[[1,-1]],[1,0],1,['1/4','1/4'])
x=base['certificate']
for key,val in [('normal_residual_norm_squared',F(1,32)),('objective',F(11,16)),('dual_value',F(21,32)),('duality_gap',F(1,32))]:
    check(x[key]==val,'printed rational worked value')
scaled=c.certify([[1,0]],[[1,-1]],[1,0],1,['1/4','1/4'],basis=[['1/100'],['1/100']])['certificate']
controls={
    'raw covector norm is basis invariant': x['coordinate_covector_norm_squared_not_a_Hilbert_certificate']==scaled['coordinate_covector_norm_squared_not_a_Hilbert_certificate'],
    'duality gap equals true suboptimality': x['duality_gap']==x['objective']-F(2,3),
    'nonzero fit residual rejects the optimizer': b.protected_regularize([[1,0]],[[1,-1]],[1,0],1)['residual_norm_squared']==0,
    'Gram matrix may be omitted': F(1,2)==F(1,3),
    'ambient adjoint is the restricted adjoint': [F(3,4),F(0)]==[F(3,8),F(3,8)]}
for n in [2,4,8,16,32]:
    z=c.certify([[0]],[],[0],F(1,n*n),[1])['certificate']
    check(z['normal_residual_norm_squared']==F(1,n**4),'vanishing normal residual example')
    check(z['correction_error_norm_squared_upper']==1,'parameter-rescaled error stays one')
    controls[f'normal error alone bounds correction n={n}']=F(1)<=z['normal_residual_norm_squared']
for label,false in controls.items():
    check(not false,'false-claim rejection');rejected.append(label)

problem=base['problem']
mutations=[('zero alpha',{'alpha':0}),('negative alpha',{'alpha':-1}),('float alpha',{'alpha':.1}),
 ('bool entry',{'f':[True,0]}),('wrong correction dimension',{'correction':[0]}),
 ('changed protected data',{'correction':[1,0]}),('incomplete kernel basis',{'basis':[[],[]]}),
 ('dependent basis',{'basis':[[0],[0]]}),('basis outside kernel',{'basis':[[1],[0]]}),
 ('bad witness dimension',{'dual_witness':[1,2]}),('bad residual dimension',{'measured_residual':[1,2]}),
 ('ragged matrix',{'d':[[1,0],[1]]})]
for label,change in mutations:
    args=copy.deepcopy(problem);args.update(change)
    try:c.certify(**args)
    except (TypeError,ValueError,ArithmeticError):invalid.append(label);check(True,'invalid-input rejection')
    else:raise AssertionError('Invalid input accepted: '+label)
for key in ['normal_residual_norm_squared','objective','duality_gap','correction_error_norm_squared_upper']:
    tampered=copy.deepcopy(b.jsonable(base));tampered['certificate'][key]='0'
    try:c.verify_record(tampered)
    except ValueError:invalid.append('tampered '+key);check(True,'tampered-output rejection')
    else:raise AssertionError('Tampered certificate accepted')

out={'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),
     'assertions':sum(counts.values()),'assertion_groups':dict(counts),'cases':dict(cases),
     'rejected_false_claims':rejected,'rejected_invalid_or_tampered':invalid,
     'program_sha256':hashlib.sha256((ROOT/'examples/inexact_repair_certificate.py').read_bytes()).hexdigest(),
     'scope':'Exact finite regression. Independent determinant-based ambient KKT oracle. Not a universal proof of this Python program.'}
(ROOT/'audit/inexact_certificates_exact.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
