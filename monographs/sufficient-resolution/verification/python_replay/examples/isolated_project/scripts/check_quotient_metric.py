#!/usr/bin/env python3
"""Deterministic bounded rational controls; universal claims are in separate Lean proofs."""
from fractions import Fraction as Q
import copy, json, random
from hilbert_certificate import (Matrix,add,scale,transpose,inverse,kernel_basis,
    projector_from_basis,norm_sq,column_basis)
from quotient_metric_certificate import certificate,run_document,verify_output

rng=random.Random(20260913)
checks=negatives=systems=vectors=0

def check(p:bool)->None:
    global checks
    checks+=1
    if not p: raise AssertionError(f'Failed assertion {checks}')

def reject(f)->None:
    global negatives
    try: f()
    except (ValueError,TypeError,KeyError,ArithmeticError):
        negatives+=1
        return
    raise AssertionError('Invalid input accepted.')

def shear(n:int)->Matrix:
    s=Matrix.eye(n)
    for _ in range(n+2):
        if n < 2: break
        i,j=rng.sample(range(n),2)
        a=[list(row) for row in Matrix.eye(n).rows]
        a[i][j]=Q(rng.choice([-2,-1,1,2]))
        s=Matrix(tuple(map(tuple,a)),n)@s
    return s

def vec(n:int)->Matrix:
    return Matrix.parse([[rng.randrange(-4,5)] for _ in range(n)],1)

for n in range(6):
 for trial in range(5):
    s=shear(n); si=inverse(s)
    k=rng.randrange(n+1); r=rng.randrange(k+1)
    b=Matrix(tuple(tuple(row[j] for j in range(k)) for row in s.rows),k)
    a=Matrix(tuple(tuple(row[j] for j in range(r)) for row in s.rows),r)
    # Duplicate a global column when nonzero: redundant global presentations are supported.
    if r: a=Matrix(tuple(row+(row[0],) for row in a.rows),r+1)
    delta=Matrix(tuple(si.rows[i] for i in range(k,n)),n)
    r1=r+rng.randrange(k-r+1)
    a1=Matrix(tuple(tuple(row[j] for j in range(r1)) for row in s.rows),r1)
    u=shear(k); rebased=b@u
    pr=projector_from_basis(column_basis(a)); pr1=projector_from_basis(column_basis(a1))
    systems+=1
    for _ in range(6):
        v,w=vec(n),vec(n);vectors+=1
        c=certificate(a,delta,v,b);d=certificate(a,delta,w,b)
        cr=certificate(a,delta,v,rebased)
        check(c['minimum_representative']==cr['minimum_representative'])
        check(c['quotient_norm_squared']==cr['quotient_norm_squared'])
        check(c['minimum_coordinates']==u@cr['minimum_coordinates'])
        check(c['gram_matrix']==transpose(b)@b)
        check(cr['gram_matrix']==transpose(u)@c['gram_matrix']@u)
        check(c['reconstruction_error_squared']==c['quotient_norm_squared']+c['inconsistency_squared'])
        shift=a@vec(a.ncols)
        cs=certificate(a,delta,add(v,shift),b)
        check(cs['minimum_representative']==c['minimum_representative'])
        check(cs['quotient_norm_squared']==c['quotient_norm_squared'])
        cd=certificate(a,delta,add(v,w,Q(-1)),b)
        check(cd['minimum_representative']==add(c['minimum_representative'],d['minimum_representative'],Q(-1)))
        check(cd['quotient_norm_squared']<=norm_sq(add(v,w,Q(-1))))
        cp=certificate(a,delta,add(v,w),b)
        check(cp['quotient_norm_squared']+cd['quotient_norm_squared']==
              2*c['quotient_norm_squared']+2*d['quotient_norm_squared'])
        t=Q(rng.choice([-3,-1,0,1,2]),2)
        ct=certificate(a,delta,scale(v,t),b)
        check(ct['quotient_norm_squared']==t*t*c['quotient_norm_squared'])
        check(ct['minimum_representative']==scale(c['minimum_representative'],t))
        cf=certificate(a1,delta,v,b)
        gain=add(pr1@v,pr@v,Q(-1))
        check(c['quotient_norm_squared']==cf['quotient_norm_squared']+norm_sq(gain))
        check(cf['quotient_norm_squared']<=c['quotient_norm_squared'])
        check(cf['inconsistency']==c['inconsistency'])
        compatible=add(v,c['inconsistency'],Q(-1))
        representative=add(compatible,shift)
        check(norm_sq(representative)==c['quotient_norm_squared']+
              norm_sq(add(representative,c['minimum_representative'],Q(-1))))

sample={'schema_version':1,'coefficient_domain':'Q','local_dimension':3,'global_dimension':1,
 'residual_dimension':1,'compatible_dimension':2,'A':[[1],[0],[0]],'delta':[[0,0,2]],
 'compatible_basis':[[1,1],[0,2],[0,0]],'local_vector':[3,4,5]}
out=run_document(sample);verify_output(sample,out)
check(out['evaluation']['quotient_norm_squared']=='16')
check(out['evaluation']['naive_identity_metric_quotient_squared']=='4')
check(out['evaluation']['reconstruction_error_squared']=='41')
check(out['evaluation']['minimum_coordinates']==[['-2'],['2']])
check(out['evaluation']['minimum_representative']==[['0'],['4'],['0']])
for patch in ({'schema_version':True},{'schema_version':2},{'coefficient_domain':'R'},
 {'local_dimension':17},{'local_dimension':-1},{'local_dimension':True},{'global_dimension':2},
 {'residual_dimension':0},{'local_vector':[1,2]},{'local_vector':[1.0,2,3]},
 {'delta':[[1,0,2]]},{'compatible_dimension':1},{'compatible_basis':[[1,1],[0,0],[0,0]]},
 {'compatible_basis':[[1,0],[0,1],[0,1]]},{'compatible_basis':[[True,1],[0,2],[0,0]]}):
    reject(lambda patch=patch:run_document({**sample,**patch}))
for key,value in [('quotient_norm_squared','4'),('minimum_coordinates',[['0'],['2']]),
 ('minimum_representative',[['1'],['4'],['0']]),('gram_matrix',[['1','0'],['0','1']]),
 ('reconstruction_error_squared','29')]:
    corrupt=copy.deepcopy(out);corrupt['evaluation'][key]=value
    reject(lambda corrupt=corrupt:verify_output(sample,corrupt))
reject(lambda:run_document([]))
print(json.dumps({'passed':True,'seed':20260913,'systems':systems,'vectors':vectors,
 'ambient_dimensions':[0,5],'exact_assertions':checks,'negative_controls_rejected':negatives,
 'arithmetic':'fractions.Fraction','comparisons':'Ambient projection vs compatible-basis Gram minimization; basis changes, translations, refinement and parallelogram checks.',
 'non_claim':'Finite tests only; Python, elimination and JSON parsing are not formally verified.'},indent=2))
