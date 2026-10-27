#!/usr/bin/env python3
"""Block57 exact forced-bad-prime reciprocity certificate (standard library).
The finite assertion does not prove a bound on arbitrary conductor support.
The inherited field arithmetic is used only by this primary implementation.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
from inherited_reciprocity_checks import places, rref, kernel, require

UNIVERSE = [97,197,293,491,587,883,1373,1471,1567,1667]
ELEMENTS = [
 ('phi',(0,1)), ('2',(2,0)), ('3',(3,0)), ('sqrt5',(-1,2)), ('7',(7,0)),
 ('pi11',(3,1)), ('bar_pi11',(4,-1)), ('pi19',(4,1)),
 ('bar_pi19',(5,-1)), ('pi31',(5,2)), ('bar_pi31',(7,-2))]

def restrict(a, cols):
    return [[row[j] % 7 for j in cols] for row in a]

def rank(a):
    return len(rref(a)[1])

def determinant(a):
    """Integer Bareiss determinant, with row pivoting and exact division."""
    if not a: return 1
    b=[list(row) for row in a]; n=len(b); previous=1; sign=1
    require(all(len(row)==n for row in b), 'nonsquare determinant')
    for k in range(n-1):
        j=next((i for i in range(k,n) if b[i][k]),None)
        if j is None: return 0
        if j!=k: b[k],b[j]=b[j],b[k]; sign=-sign
        pivot=b[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                value=pivot*b[i][j]-b[i][k]*b[k][j]
                require(value%previous==0,'inexact Bareiss division')
                b[i][j]=value//previous
            b[i][k]=0
        previous=pivot
    return sign*b[-1][-1]

def zero_set(K,a,b=(0,0,0)):
    return tuple(i for i,row in enumerate(K)
                 if sum(x*y for x,y in zip(row,a))%7==0
                 and sum(x*y for x,y in zip(row,b))%7==0)

def inflate(v,indices,length):
    out=[0]*length
    for j,x in zip(indices,v):out[j]=x%7
    return out

def normalize(v):
    j=next(i for i in range(len(v)-1,-1,-1) if v[i])
    z=pow(v[j],-1,7)
    return [z*x%7 for x in v]

def data():
    records=[];power_symbols=0
    for q in UNIVERSE:
        for label,f in places(q):
            h,z,old=f.logs(); require(h>=2,'not a high place')
            co=(f.Q-1)//7**h
            table={f.power(z,j):j for j in range(7**h)}
            logs={name:table[f.power(f.elm(*ab),co)]%7 for name,ab in ELEMENTS}
            require(all(logs[name]==old[name]%7 for name,_ in ELEMENTS[:5]),'inherited normalization drift')
            for name,ab in ELEMENTS:
                s=f.power(f.elm(*ab),(f.Q-1)//7)
                require(s==f.power(z,logs[name]*7**(h-1)),'direct power/log mismatch')
                power_symbols+=1
            records.append({'label':label,'q':q,'norm':f.Q,'phi_root':f.phi_root,
                            'h':h,'primary_generator':list(z),'logs_mod7':logs})
    M=[[p['logs_mod7'][name] for p in records] for name,_ in ELEMENTS]
    K=[[p['logs_mod7'][name] for name in ('phi','3','sqrt5')] for p in records]
    return records,M,K,power_symbols

def main(output:Path):
    ps,M,K,power_count=data();d=len(ps)
    require(d==12,'wrong prime-ideal coverage')
    R,pivcols=rref(M);bas=kernel(M)
    require(len(pivcols)==10 and len(bas)==2,'augmented rank changed')
    transposed=[list(row) for row in zip(*restrict(M,pivcols))]
    pivrows=rref(transposed)[1]
    minor=[[M[i][j] for j in pivcols] for i in pivrows]
    det=determinant(minor)
    require(len(pivrows)==10 and det%7!=0,'rank witness failed')
    for v in bas:
        require(all(sum(x*y for x,y in zip(row,v))%7==0 for row in M),'invalid null vector')
    directions=[]
    for u in range(7):
        for ratio in range(1,7):
            a=(u,ratio,1);z=zero_set(K,a);b=kernel(restrict(M,z))
            directions.append({'alpha':list(a),'zero_indices':list(z),'rank':rank(restrict(M,z)),
                               'nullity':len(b),'full_kernel_basis':[normalize(inflate(v,z,d)) for v in b]})
    survivors=[x for x in directions if x['nullity']]
    require([x['alpha'] for x in survivors]==[[0,1,1],[0,3,1]],'surviving coefficients changed')
    require(all(x['nullity']==1 for x in survivors),'surviving spaces are not lines')
    patterns=[]
    for row in survivors:
        v=row['full_kernel_basis'][0];indices=[i for i,x in enumerate(v) if x]
        patterns.append({'alpha':row['alpha'],'inertia_vector':v,'support_indices':indices,
                         'prime_ideals':[ps[i]['label'] for i in indices],
                         'rational_support':sorted({ps[i]['q'] for i in indices}),
                         'kummer_rank':rank([K[i] for i in indices])})
        require(patterns[-1]['kummer_rank']==2,'no support-forced coefficient descent')
        require(all(ps[i]['h']==2 for i in indices),'order-seven conclusion needs h=2')
    extension_directions=[]
    for u0,u1,r0,r1 in itertools.product(range(7),repeat=4):
        if r0==r1==0:continue
        z=zero_set(K,(u0,r0,1),(u1,r1,0));nullity=len(z)-rank(restrict(M,z))
        extension_directions.append({'u':[u0,u1],'r':[r0,r1],'zero_indices':list(z),'nullity':nullity})
    require(len(extension_directions)==2352,'incomplete F49 coverage')
    survivors49=[x for x in extension_directions if x['nullity']]
    require([(x['u'],x['r'],x['nullity']) for x in survivors49]==[([0,0],[1,0],1),([0,0],[3,0],1)],
            'nonprime-field or extra compatible direction survived')
    classifications=[];good=[];bad=[]
    for mask in range(1<<len(UNIVERSE)):
        qs=[q for i,q in enumerate(UNIVERSE) if mask>>i&1]
        ix={i for i,p in enumerate(ps) if p['q'] in qs};which=[]
        for a in directions:
            z=sorted(ix.intersection(a['zero_indices']))
            if rank(restrict(M,z))<len(z):which.append(a['alpha'])
        passed=not which
        (good if passed else bad).append(qs)
        classifications.append({'mask':mask,'prime_support':qs,'criterion_passed':passed,'surviving_alphas':which})
    minbad=[s for s in bad if not any(set(t)<set(s) for t in bad)]
    maxgood=[s for s in good if not any(set(s)<set(t) for t in good)]
    require(len(good)==912 and len(bad)==112,'finite support classification changed')
    require(sorted(minbad)==[[97,293,1471,1567],[97,491,587,1567]],'minimal survivors changed')
    two=[i for i,p in enumerate(ps) if p['q'] in (97,293)]
    old=restrict(M[:5],two);new=restrict(M,two)
    require(kernel(old)==[[6,1]] and not kernel(new),'old line/new exclusion failed')
    two_minor=[[M[i][j] for j in two] for i in (0,5)]
    require(two_minor==[[1,1],[6,3]] and determinant(two_minor)%7==4,'two-place witness failed')
    old_vector=[6,1]
    old_evaluations={name:sum(M[i][j]*v for j,v in zip(two,old_vector))%7
                     for i,(name,_) in enumerate(ELEMENTS)}
    require(old_evaluations['pi11']==4 and old_evaluations['pi19']==5 and old_evaluations['pi31']==6,
            'actual Frobenius incompatibility changed')
    norm_checks={name:a*a+a*b-b*b for name,(a,b) in ELEMENTS[5:]}
    require(list(norm_checks.values())==[11,11,19,19,31,31],'wrong principal generators')
    # Both surviving lines cancel on every rational unit: inert supporting
    # primes are -1 mod7, and the coefficients at split conjugate places sum0.
    rational_tests=[]
    for pattern in patterns:
        v=pattern['inertia_vector']
        support=[(i,ps[i]) for i in pattern['support_indices']]
        for i,rec in support:
            if rec['phi_root'] is None:
                require(rec['q']%7==6,'inert rational cancellation unavailable')
            else:
                pair=[j for j,p in enumerate(ps) if p['q']==rec['q']]
                require(len(pair)==2 and sum(v[j] for j in pair)%7==0,'split rational cancellation failed')
        fields={}
        for i,rec in support:
            f=next(f for label,f in places(rec['q']) if label==rec['label'])
            h,z,_=f.logs();co=(f.Q-1)//7**h
            fields[i]=(f,co,{f.power(z,j):j for j in range(7**h)})
        values=[]
        for a in [2,3,7,11,13,19,29,31,43,71,197,883,1373,1667]:
            total=0
            for i,(f,co,tab) in fields.items():
                require(a%f.q!=0,'rational probe meets conductor')
                total+=v[i]*tab[f.power(f.elm(a),co)]
            require(total%7==0,'nonzero rational principal value')
            values.append({'rational_element':a,'value_mod7':0})
        # Under COMPLETE H(C) subset U and nontrivial eta, the written proof
        # forces n=3. Apply its two filters for additional beta support.
        possible_beta=[];forced_beta=pattern['support_indices']
        for j,rec in enumerate(ps):
            if j in forced_beta:
                possible_beta.append(j);continue
            if sum(a*b for a,b in zip(K[j],pattern['alpha']))%7:continue
            if rec['phi_root'] is None and rec['h']<3:continue
            possible_beta.append(j)
        extras=[j for j in possible_beta if j not in forced_beta]
        expected=[] if pattern['alpha'][1]==3 else [i for i,p in enumerate(ps) if p['q']==1373]
        require(extras==expected,'conditional depth3 beta filter changed')
        pattern['depth3_beta_forced_indices']=forced_beta
        pattern['depth3_beta_possible_indices']=possible_beta
        pattern['depth3_beta_support_scope']='Only under COMPLETE H(C) subset U and eta nontrivial'
        rational_tests.append({'alpha':pattern['alpha'],'values':values,
                               'unramified_inert_1373_value':0})
    result={'schema':'komorebi.beal.block57.augmented.v1' ,'status':'PASS',
       'arithmetic':'exact phi-basis finite fields, integer Bareiss determinants, F7 row reduction',
       'contract':'Necessary actual highest-layer system. Universe bounds maximal ramification, not all divisors of C.',
       'universe':UNIVERSE,'row_elements':[{ 'name':name,'phi_coefficients':list(ab)} for name,ab in ELEMENTS],
       'prime_generator_norms':norm_checks,'places':ps,'matrix_mod7':M,'kummer_rows_mod7':K,
       'rank':10,'kernel_basis':bas,'rank_minor':{'rows':pivrows,'columns':pivcols,'integer_determinant':det,'mod7':det%7},
       'prime_field_directions':directions,'complete_F49_directions':extension_directions,
       'F49_directions_checked':2352,'nonzero_compatible_F49_directions':2,
       'actual_candidate_patterns':patterns,'classification':classifications,
       'classified_rational_subsets':1024,'criterion_pass_count':912,'criterion_survivor_count':112,
       'minimal_surviving_rational_supports':minbad,'maximal_passing_rational_supports':maxgood,
       'two_prime_exclusion':{'columns':two,'old_kernel':[[6,1]],'minor':two_minor,
                              'integer_determinant':-3,'mod7':4,'old_line_evaluations':old_evaluations},
       'direct_power_symbol_cross_checks':power_count,
       'rational_cancellation':rational_tests,'rational_unit_checks':28,
       'negative_controls':{'old_five_row_line_nonzero':True,'two_augmented_patterns_still_nonzero':True},
       'nonclaims':['No bound on arbitrary prime support','No construction of a Frey representation',
                    'No elimination of depth one or all depth two','No Lean proof or independent mathematical review']}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','rank':10,'directions':2352,'nonzero_directions':2,
                      'pass_subsets':912,'survivor_subsets':112,'two_place_determinant_mod7':4},sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path)
    main(ap.parse_args().output)
