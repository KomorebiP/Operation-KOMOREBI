#!/usr/bin/env python3
"""Independent sqrt(5)-basis computation and exhaustive six-variable kernel.
No import from the primary computation. All arithmetic is integer/exact.
"""
import argparse
import itertools
import json
from pathlib import Path


def check(c,msg):
    if not c:raise ArithmeticError(msg)


def mul(a,b,p,quadratic):
    if not quadratic:return a*b%p
    x,y=a%p,a//p;z,w=b%p,b//p
    return (x*z+5*y*w)%p + p*((x*w+y*z)%p)


def power(a,n,p,quadratic):
    r=1
    while n:
        if n%2:r=mul(r,a,p,quadratic)
        a=mul(a,a,p,quadratic);n//=2
    return r


def factors(n):
    out=[];d=2
    while d*d<=n:
        if n%d==0:
            out.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:out.append(n)
    return out


def data(p,root_phi):
    quad=root_phi is None;Q=p*p if quad else p
    prime_factors=factors(Q-1)
    generator=next(x for x in range(1,Q) if all(power(x,(Q-1)//ell,p,quad)!=1 for ell in prime_factors))
    lookup={};x=1
    for i in range(Q-1):
        check(x not in lookup,'generator order failure')
        lookup[x]=i;x=mul(x,generator,p,quad)
    check(x==1 and len(lookup)==Q-1,'incomplete field group')
    if quad:
        phi=pow(2,-1,p)+p*pow(2,-1,p);s=p
    else:
        phi=root_phi;s=(2*root_phi-1)%p
    vals=[phi,2,3,s,7]
    h=0;temp=Q-1
    while temp%7==0:temp//=7;h+=1
    logs=[lookup[x]%7 for x in vals]
    return {'q':p,'phi_root':root_phi,'generator_encoded':generator,'logs_mod7':logs,
            'full_multiplicative_group_checked':Q-1, 'h':h,
            'logs_full_seven_primary':[lookup[x]%(7**h) for x in vals]}


def replay_certificate(case):
    # Separate elementary-operation interpreter, with no Smith routine imported.
    B=[list(row) for row in case['relation_matrix']]
    for rec in case['unimodular_operations']:
        kind=rec[0]
        if kind=='rn':
            i=rec[1];B[i]=[-z for z in B[i]]
        elif kind in ('rs','ra'):
            i,j=rec[1:3];check(i!=j,'noninvertible row operation')
            if kind=='rs':B[i],B[j]=B[j],B[i]
            else:B[i]=[B[i][k]+rec[3]*B[j][k] for k in range(len(B[i]))]
        elif kind in ('cs','ca'):
            i,j=rec[1:3];check(i!=j,'noninvertible column operation')
            C=list(map(list,zip(*B)))
            if kind=='cs':C[i],C[j]=C[j],C[i]
            else:C[i]=[C[i][k]+rec[3]*C[j][k] for k in range(len(C[i]))]
            B=list(map(list,zip(*C)))
        else:raise ArithmeticError('unrecognized elementary operation')
    check(B==case['smith_matrix'],'certificate target mismatch')
    for i,row in enumerate(B):
        for j,x in enumerate(row):
            check((x>0 if i==j else x==0),'not positive diagonal')
    ds=[B[i][i] for i in range(len(B))]
    check(all(ds[i+1]%ds[i]==0 for i in range(len(ds)-1)),'Smith divisibility')
    check([x for x in ds if x>1]==case['nontrivial_invariant_factors'],'reported invariants mismatch')
    return len(case['unimodular_operations'])


def independent_ray_cases(path):
    records=json.loads(path.read_text())['cases'];cache={};summary=[];joint=None
    for case in records:
        d=len(case['places']);cols=[];scales=[]
        for j,place in enumerate(case['places']):
            q=place['q'];label=place['label']
            root=None if 'inert' in label else int(label.split('phi=')[1])
            key=(q,root)
            if key not in cache:cache[key]=data(q,root)
            rec=cache[key];e=place['effective_h'];M=7**e
            new=[x%M for x in rec['logs_full_seven_primary']]
            old=[case['relation_matrix'][j][d+i] for i in range(5)]
            # Cyclic coordinate generators may differ by any unit, including
            # when every displayed generator has nonunit logarithm.
            matches=[u for u in range(1,M) if u%7 and all(y==u*x%M for x,y in zip(old,new))]
            check(bool(matches),'exceptional full-order logarithms disagree')
            scales.append(matches[0]);cols.append(new)
        operations=replay_certificate(case)
        enum=None
        if case['capacity_loss']==1:
            check(all(p['effective_h']==1 for p in case['places']),'fixture no longer exponent seven')
            survivors=0
            for v in itertools.product(range(7),repeat=d):
                if all(sum(cols[j][i]*v[j] for j in range(d))%7==0 for i in range(5)):survivors+=1
            expected=1
            for x in case['nontrivial_invariant_factors']:expected*=x
            check(survivors==expected,'independent reduced quotient count')
            enum={'vectors':7**d,'characters':survivors}
            if d==4:
                nonzero=[]
                for v in itertools.product(range(7),repeat=4):
                    if any(v) and all(sum(cols[j][i]*v[j] for j in range(4))%7==0 for i in range(5)):
                        nonzero.append(v)
                check(len(nonzero)==6 and all(all(v) for v in nonzero),'independent forced support')
                K=[[col[j] for j in (0,2,3)] for col in cols]
                count=passed=0
                for u0,u1,r0,r1 in itertools.product(range(7),repeat=4):
                    if r0==r1==0:continue
                    count+=1
                    passed+=int(all((row[0]*u0+row[1]*r0+row[2])%7==0 and
                                    (row[0]*u1+row[1]*r1)%7==0 for row in K))
                check(count==2352 and passed==0,'independent simultaneous Kummer obstruction')
                joint={'nonzero_F7_ray_vectors':nonzero,'kummer_matrix_independent':K,
                       'normalized_F49_vectors_checked':count,'survivors':passed}
        summary.append({'primes':case['primes'],'loss':case['capacity_loss'],
                        'certificate_operations':operations,'column_scales':scales,'exhaustive_reduced_case':enum})
    return {'cases':summary,'independent_full_group_elements':sum(x['full_multiplicative_group_checked'] for x in cache.values()),
            'distinct_places':len(cache),'depth_three_joint_compatibility':joint}


def main(output,primary_path,ray_path):
    primary=json.loads(primary_path.read_text())
    cases=[(13,None),(29,6),(29,24),(43,None),(71,9),(71,63)]
    records=[data(*c) for c in cases]
    M=[[r['logs_mod7'][i] for r in records] for i in range(5)]
    scales=[]
    for j in range(6):
        old=[row[j] for row in primary['matrix_mod7']]
        new=[row[j] for row in M]
        i=next(i for i,x in enumerate(old) if x)
        s=new[i]*pow(old[i],-1,7)%7
        check(s!=0 and all(y==s*x%7 for x,y in zip(old,new)),'column coordinate comparison failed')
        scales.append(s)
    count=0;hist={};survivors=[]
    for v in itertools.product(range(7),repeat=6):
        count+=1
        if all(sum(a*b for a,b in zip(row,v))%7==0 for row in M):
            survivors.append(v);support=tuple(i for i,x in enumerate(v) if x)
            hist[support]=hist.get(support,0)+1
    check(count==117649 and len(survivors)==49,'exhaustive kernel cardinality mismatch')
    predicted={tuple(row['indices']):row['count'] for row in primary['support_counts_F7']}
    check(hist==predicted,'support distribution mismatch')
    # Directly enumerate the relation subgroup, independent of row reduction.
    subgroup=set()
    for cs in itertools.product(range(7),repeat=5):
        subgroup.add(tuple(sum(cs[i]*M[i][j] for i in range(5))%7 for j in range(6)))
    check(len(subgroup)==2401,'relation subgroup cardinality mismatch')
    check(7**6//len(subgroup)==49,'quotient cardinality mismatch')
    # Universal local-order formula tested in a different coefficient model.
    # Units 1+7^j(a+b sqrt5), with all 48 nonzero residue coefficients.
    order_tests=0
    for n in range(2,9):
        mod=7**n
        def rmul(x,y):
            return ((x[0]*y[0]+5*x[1]*y[1])%mod,(x[0]*y[1]+x[1]*y[0])%mod)
        def rpow(x,k):
            r=(1,0)
            while k:
                if k&1:r=rmul(r,x)
                x=rmul(x,x);k//=2
            return r
        for j in range(1,n):
            for a,b in itertools.product(range(7),repeat=2):
                if a==0 and b==0:continue
                x=((1+7**j*a)%mod,7**j*b%mod)
                check(rpow(x,7**(n-j))==(1,0),'claimed order does not annihilate')
                check(rpow(x,7**(n-j-1))!=(1,0),'claimed order not exact')
                order_tests+=1
    result={'status':'PASS','arithmetic':'encoded sqrt5 basis; full cyclic logarithms; exhaustive vectors',
            'residue_fields':records,'matrix_mod7':M,'column_scaling_from_primary':scales,
            'six_variable_vectors_checked':count,'kernel_cardinality':len(survivors),
            'five_relation_vectors_checked':7**5,'relation_subgroup_cardinality':len(subgroup),
            'quotient_cardinality':49,'quotient_invariant_factors':[7,7],
            'support_counts':[{'indices':list(k),'count':v} for k,v in sorted(hist.items())],
            'nonrational_coefficient_unit_order_tests':order_tests,
            'negative_control_mod7_dimension_does_not_determine_exponent':
                {'C7_character_dimension':1,'C49_character_dimension':1,'different_exponents':[7,49]},
            'exceptional_ray_audit':independent_ray_cases(ray_path),
            'nonclaims':['This is an independent implementation, not an independent reviewer',
                         'No prime support bound or actual Frey realization established']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','vectors':count,'kernel':len(survivors),'unit_order_tests':order_tests,
                      'column_scales':scales},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--primary-result',type=Path,required=True)
    p.add_argument('--ray-result',type=Path,required=True);a=p.parse_args();main(a.output,a.primary_result,a.ray_result)
