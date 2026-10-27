"""Independent exact finite audit examples. No project mathematics is imported."""
from pathlib import Path
import json,itertools
out=Path('/mnt/data/Strong_Artin_Audit_2026-09-11')
R=range(4)
roots_original=[x for x in R if (x*x+1)%4==0]
roots_augmented=[(x,y) for x,y in itertools.product(R,repeat=2) if (x*x+1+y)%4==0 and x%2==1 and y%2==0]
assert not roots_original and (1,2) in roots_augmented
C={2*x%4 for x in R}; twoC={2*x%4 for x in C}
assert 2 in C and 2 not in twoC
x=2;F=(x%8,x*x%8);B=(-x%8,1)
assert F==(2,4) and (B[0]*F[0]+B[1]*F[1])%8==0 and F[1]!=0
# Local extension spectra over F_7, quotient of order 3, degree 2.
z=2;A=(z,pow(z,2,7));Id=(1,1)
assert pow(z,3,7)==1 and (A[0]*A[1])%7==1
assert tuple(pow(v,3,7) for v in A)==Id
scalar_twists=[(pow(z,j,7),pow(z,j,7)) for j in range(3)]
assert A not in scalar_twists
# Full matrix conjugation by diag(1,-1) over F_3. Ordered matrix units 11,12,21,22.
p=3;Ad_diagonal=(1,2,2,1)
Norm=[sum(pow(a,i,p) for i in range(6))%p for a in Ad_diagonal]
D=[(1-a)%p for a in Ad_diagonal]
rank_D=sum(d!=0 for d in D)
assert Norm==[0]*4 and 4-rank_D==2
# Two nonzero functionals need not have identical kernels in dimension two.
v=(1,0);f=v[0];g=v[1]
assert f!=0 and g==0
# k[t]/t^2, k=F_5: cotangent differential multiplication by 2t.
S=list(itertools.product(range(5),repeat=2))
def mul(a,b):return ((a[0]*b[0])%5,(a[0]*b[1]+a[1]*b[0])%5)
ker=[a for a in S if mul((0,2),a)==(0,0)]
assert ker==[(0,b) for b in range(5)]
assert all(a[0]==0 for a in ker)  # inclusion followed by residue is zero
result={
 'arithmetic':'exact integers modulo 3,4,5,7,8; no floating point',
 'domain':'explicit finite examples only; not counterexamples to Strong Artin or correctly stated project theorems',
 'augmented_equation':{'original_roots_mod4':roots_original,'augmented_residually_correct_roots_mod4':roots_augmented,'refutes':'augmented solution automatically descends with auxiliary variables zero'},
 'submodule_divisibility':{'C':sorted(C),'2C':sorted(twoC),'witness':2,'refutes':'ambient pi-divisibility automatically equals intrinsic pi-divisibility'},
 'moving_syzygy':{'F_2_mod8':F,'B_at_2_mod8':B,'exact_relation_value':0,'frozen_relation_value':4,'refutes':'a residual/frozen syzygy annihilates every integral nonlinear error'},
 'determinant_selector':{'coefficient_field':7,'quotient_prime':3,'rank':2,'A_diagonal':A,'B_diagonal':Id,'scalar_twists_B':scalar_twists,'equal_determinants':True,'equal_cube':True,'same_scalar_twist_orbit':False,'qualification':'the lower local restriction is reducible; does not refute the irreducible-restriction theorem'},
 'finite_cyclic_normalization':{'field':3,'cyclic_order':6,'Ad':Ad_diagonal,'Norm':Norm,'rank_1_minus_Ad':rank_D,'H1_dimension':4-rank_D,'conclusion':'full H1 cannot be identified with a one-dimensional line in this rank-two example'},
 'nonzero_functionals':{'vector':v,'first_coordinate':f,'second_coordinate':g,'refutes':'nonzero functionals have the same nonvanishing set without a 1-dimensional or explicit compatibility assumption'},
 'cotangent_base_change':{'field':5,'ring':'F_5[t]/t^2','differential':'multiplication by 2t','kernel_elements':ker,'residue_of_included_kernel':'zero','kernel_after_residue_dimension':1,'conclusion':'kernel/base-change identification needs an actual derived comparison; tensoring a kernel can destroy its inclusion'},
 'all_assertions_passed':True}
(out/'negative_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
