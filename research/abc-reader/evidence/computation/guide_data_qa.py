#!/usr/bin/env python3
"""Independent guide-data checks. Does not import the figure generator.

Exact classifications and coefficients use int/Fraction. Display decimals are
checked only as display values. Universal theorem proofs are audited separately.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations, permutations, product
from collections import Counter
from math import gcd, prod, factorial, comb, log, isclose, isqrt
import csv, hashlib, json

ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'visual/data.json').read_text())['figures']
CHECKS=Counter()

def check(ok,family):
    assert ok,family
    CHECKS[family]+=1

def factor(n):
    out={}
    for p in range(2, isqrt(n)+2):
        if p*p>n:break
        while n%p==0:
            out[p]=out.get(p,0)+1
            n//=p
    if n>1:out[n]=out.get(n,0)+1
    return out

def rad(n):return prod(factor(n))

def values(n):
    return next(v['values'] for k,v in DATA.items() if k.startswith(f'{n:02d}_'))

def conv(a,b,limit):
    out=[F(0)]*(limit+1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b[:limit-i+1]):
                if y:out[i+j]+=x*y
    return out

def direct_formal_det(rank,limit,K=None):
    # Leibniz determinant expansion of truncated moment polynomials.
    K=K or limit
    moments={s:[F(0)]+[F(1,k**s) if k<=K else F(0) for k in range(1,limit+1)] for s in range(1,2*rank)}
    answer=[F(0)]*(limit+1)
    for pi in permutations(range(rank)):
        sign=(-1)**sum(pi[i]>pi[j] for i in range(rank) for j in range(i+1,rank))
        term=[F(1)]+[F(0)]*limit
        for i,j in enumerate(pi):term=conv(term,moments[i+j+1],limit)
        answer=[a+sign*b for a,b in zip(answer,term)]
    return answer

check(len(DATA)==24,'figure_inventory')
check(values(1)['radical']==6 and values(1)['factors']=={'2':3,'3':2},'radical')
for number in (2,3,9,10):
    d=values(number)
    a,b,c=d['a'],d['b'],d['c']
    check(a+b==c and gcd(a,b)==1,'primitive_examples')
    R=rad(a)*rad(b)*rad(c)
    check(d['R']==R and d['Q']*R==a*b*c,'example_radical_and_Q')
    check(F(d['balanced'])==F(c,R) and F(d['Q'],a*b)==F(c,R),'balanced_defect')
    check(isclose(d['quality_approx'],log(c)/log(R),rel_tol=1e-12),'display_quality')
check(values(3)['c']==23**5 and values(3)['b']==109*3**10,'high_quality_power_equality')

d=values(4)
csv_path=ROOT/'evidence/computation/controls_run/abc_census_high_quality.csv'
source_rows=[{k:int(v) for k,v in row.items() if k in ('a','b','c','R')} for row in csv.DictReader(csv_path.open())]
check(d['high_quality_triples']==source_rows and d['plotted_count']==121,'census_plotted_rows')
check(d['source_csv_sha256']==hashlib.sha256(csv_path.read_bytes()).hexdigest(),'census_source_hash')
original=json.loads((ROOT/'evidence/computation/controls_run/results.json').read_text())['census']
check(d['primitive_triples']==original['primitive_triples']==15198743,'census_count')
for row in source_rows:
    a,b,c,R=(row[k] for k in ('a','b','c','R'))
    check(a<=b and a+b==c and gcd(a,b)==1 and c<=10000 and c>R,'census_domain')
    check(rad(a)*rad(b)*rad(c)==R,'census_radicals')

for row in values(5)['rows']:
    n,b,c=row['n'],row['b'],row['c']
    check(c==3**(2**n) and b==c-1 and gcd(b,c)==1,'epsilon_zero_family')
    v=0
    while b%2==0:b//=2;v+=1
    check(v==row['v2_b']==n+2,'epsilon_zero_LTE')
    check(F(row['lower_bound_c_over_R'])==F(2**(n+1)*c,3*row['b']),'epsilon_zero_lower_bound')
check(values(6)['abc_quantifiers']==['forall epsilon>0','exists K_epsilon','forall primitive triples'],'quantifier_order')

check(values(7)['wronskian']=='3X^2' and values(7)['radical_degree']==4 and values(7)['maximum_degree']==3,'Mason_example')
check(values(8)['D_one']==0,'integer_derivation')
counter=Counter((u+2*v)%13 for u,v in product((-1,0,1),repeat=2))
check(values(11)['counts']==[counter[h] for h in range(13)],'toy_cyclic_counts')
check(counter[1]==2 and counter[6]==0 and sum(counter.values())==9,'toy_cyclic_controls')
check(values(12)['row']==[1,-1] and values(12)['kernel_vector']==[1,1],'lattice_kernel_vector')

for m,ordinary,canonical in zip(values(13)['M'],values(13)['projective_coefficients'],values(13)['canonical_coefficients']):
    check(F(ordinary)==F(1,m) and F(canonical)==F(m-3,m),'Fermat_height_coefficients')

for row in values(14)['rows']:
    m=row['m']
    cs=[0]+[(-1)**(m-s)*sum(prod(subset) for subset in combinations(range(1,m+1),s)) for s in range(m+1)]
    check(cs==row['P_coefficients_ascending'],'jet_polynomial_by_symmetric_sums')
    check(sum(abs(x) for x in cs)==factorial(m+1) and abs(cs[1])==1,'jet_norm_and_primitive')
    for k in range(1,9):
        coefficient=sum(F(c,factorial(m+1)*k**s) for s,c in enumerate(cs))
        expected=F((-1)**m*comb(k,m+1),k**(m+2)) if k>=m+1 else F(0)
        check(coefficient==expected,'jet_series_coefficients')
    check(row['contact']==m+1 and F(row['leading'])==F((-1)**m,(m+1)**(m+2)),'jet_display_contact')

for row in values(16)['rows']:
    r,s=row['r'],row['s_r']
    polynomial=direct_formal_det(r,s)
    check(all(x==0 for x in polynomial[:s]) and polynomial[s]==F(row['leading']),'contact_by_Leibniz_expansion')
    check(s==r*(r+1)//2,'triangular_contact')
check(values(15)['first_coefficient']=='1/8' and values(15)['first_power']==3,'rank_two_first_term')

positive=values(17)
check(len(positive['terms'])==15,'positive_pair_inventory')
for row in positive['terms']:
    i,j=row['indices']
    check(F(row['term'])==F((j-i)**2,2**(i+j)*i**3*j**3) and F(row['term'])>0,'positive_terms')
moments=[sum(F(1,2**k*k**s) for k in range(1,7)) for s in (1,2,3)]
check(F(positive['finite_determinant'])==moments[0]*moments[2]-moments[1]**2,'positive_sum_by_direct_moments')
for row in values(18)['examples']:
    check(row['p']>3*row['r']-1 and row['contact']==row['r']*(row['r']+1)//2,'good_prime_pairs')
check(values(18)['threshold']=='p>3r-1','strict_threshold')
check(values(19)['first_surviving_coefficient']=='-1/625' and values(19)['depleted_contact']==5,'depleted_jet')
for row in values(20)['rows']:
    p=row['p'];indices=row['unit_indices']
    check(len(indices)==4 and all(k%p for k in indices),'unit_indices')
    E=0;mod=p
    while mod<=max(indices):
        classes=Counter(k%mod for k in indices)
        E+=sum(n*(n-1)//2 for n in classes.values());mod*=p
    check(E==row['E'] and sum(indices)==row['S'] and sum(indices)+2*E==row['valuation_e1'],'residue_collision_energy')

budget=values(21)
check(budget['C_p']=={'2':7,'3':3} and budget['B']==3456,'small_prime_budget')
for p,expected in ((2,7),(3,3),(5,0)):
    exact=sum(max([0]+[3*h-(p**h*((i+p**h-1)//p**h)-i) for h in range(1,13)]) for i in (1,2))
    check(exact==expected,'budget_independent_finite_maximum')
trunc=direct_formal_det(2,5,K=3)
check(trunc[3:]==[F(1,8),F(4,27),F(1,216)],'truncation_by_Leibniz_expansion')
for p in (5,7,11):
    for a in range(1,p):
        c=p
        W=a**3*(27*c*c+32*a*c+a*a)
        check(W%p==pow(a,5,p)!=0,'truncation_congruence')
check(values(24)['normalization']=='Q/(ab)=c/R','global_bridge_normalization')

pins=['evidence/computation/guide_data_qa.py','visual/main.tex','visual/body.tex','visual/figures.py','visual/data.json',
      'pdf/Komorebi_ABC_Visual_Guide_v1.0.pdf',
      'evidence/computation/controls_run/abc_census_high_quality.csv',
      'evidence/computation/jet_replay/run/results.json',
      'evidence/computation/good_prime_run/results.json']
report={'status':'PASS','counts':dict(CHECKS),'total_comparisons':sum(CHECKS.values()),
        'scope':'Independent int/Fraction checks of displayed finite data, plus manual reading of 24 spreads and contact images. Does not reprove all universal theorems, re-audit IUT, or establish abc.',
        'pins':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in pins}}
(ROOT/'evidence/computation/guide_data_qa_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
