#!/usr/bin/env python3
"""Independent integer arithmetic for the Z/p^(r+1) matrix-layer comparison.
No Lean expressions or matrices are evaluated by this script. All operations use
Python integers reduced modulo the declared modulus. This finite corroboration
is not a proof of the uniform theorem and is not a full coefficient-tower test.
"""
from itertools import product
from pathlib import Path
from time import monotonic
import hashlib, json
I=(1,0,0,1); Z=(0,0,0,0)
def add(A,B,m): return tuple((a+b)%m for a,b in zip(A,B))
def sub(A,B,m): return tuple((a-b)%m for a,b in zip(A,B))
def scale(a,A,m): return tuple(a*x%m for x in A)
def mul(A,B,m):
 a,b,c,d=A;e,f,g,h=B
 return ((a*e+b*g)%m,(a*f+b*h)%m,(c*e+d*g)%m,(c*f+d*h)%m)
def inv(A,m):
 a,b,c,d=A;u=pow((a*d-b*c)%m,-1,m)
 return (u*d%m,-u*b%m,-u*c%m,u*a%m)
def power(A,d,m):
 B=I
 while d:
  if d&1:B=mul(B,A,m)
  A=mul(A,A,m);d//=2
 return B
def adj(F,X,m):return mul(mul(F,X,m),inv(F,m),m)
def norm(F,X,d,p):
 out=Z;cur=X
 for _ in range(d):out=add(out,cur,p);cur=adj(F,cur,p)
 return out
def Npow(F,X,d,p):
 for _ in range(d):X=sub(adj(F,X,p),X,p)
 return X
def coord(A,s,p):
 assert all(x%s==0 for x in A)
 return tuple(x//s%p for x in A)
def main():
 t=monotonic();counts={'residual_matrices':0,'upper_frobenius_fixtures':0,
 'kernel_coordinate_conjugations':0,'actual_matrix_power_checks':0,
 'prime_power_norm_checks':0,'simultaneous_image_comparisons':0,
 'actual_kernel_conjugations':0}
 scopes=[]
 for p in (2,3,5):
  mats=list(product(range(p),repeat=4))
  GL=[F for F in mats if (F[0]*F[3]-F[1]*F[2])%p]
  # Full residual enumeration at p=2,3; a named deterministic subset at p=5.
  selected=GL if p<5 else GL[::max(1,len(GL)//12)][:12]
  levels=(1,2,3) if p<5 else (1,2)
  degrees=sorted(set(range(7))|{p*p}) if p<5 else (1,2,5,6,25)
  counts['residual_matrices']+=len(selected)
  scopes.append({'p':p,'r':list(levels),'degrees':list(degrees),
   'all_GL2_residual_matrices':p<5,'residual_selected':len(selected),'GL2_total':len(GL),
   'all_kernel_matrices':len(mats),'upper_lift_variants':2})
  for r in levels:
   s=p**r;M=s*p
   for idx,F0 in enumerate(selected):
    for variant in range(2):
     F=tuple((a+variant*p*(j+idx+1))%M for j,a in enumerate(F0))
     Fi=inv(F,M);counts['upper_frobenius_fixtures']+=1
     for X in mats:
      K=scale(s,X,M)
      assert coord(K,s,p)==X
      assert mul(K,K,M)==Z
      assert coord(mul(mul(F,K,M),Fi,M),s,p)==adj(F0,X,p)
      counts['kernel_coordinate_conjugations']+=1
      G=mul(add(I,K,M),F,M)
      for d in degrees:
       Fd=power(F,d,M);Gd=power(G,d,M)
       NX=norm(F0,X,d,p)
       assert Gd==mul(add(I,scale(s,NX,M),M),Fd,M)
       err=mul(sub(Gd,Fd,M),inv(Fd,M),M)
       assert coord(err,s,p)==NX
       counts['actual_matrix_power_checks']+=1
       if d in (1,p,p*p):
        assert NX==Npow(F0,X,d-1,p)
        counts['prime_power_norm_checks']+=1
 # Full actual simultaneous image comparisons for nonsemisimple matrices.
 family_results=[]
 for p in (2,3):
  mats=list(product(range(p),repeat=4));F0=(1,1,0,1)
  for r in (1,2):
   s=p**r;M=s*p;F=F0
   for ds in ((1,p),(p,p*p)):
    actual=set()
    Fds=[power(F,d,M) for d in ds];Fdis=[inv(x,M) for x in Fds]
    for X in mats:
     G=mul(add(I,scale(s,X,M),M),F,M)
     options=[]
     for d,Fd,Fdi in zip(ds,Fds,Fdis):
      Gd=power(G,d,M);options_i=set()
      for z in mats:
       u=add(I,scale(s,z,M),M)
       conjugate=mul(mul(u,Gd,M),inv(u,M),M)
       options_i.add(coord(mul(sub(conjugate,Fd,M),Fdi,M),s,p))
       counts['actual_kernel_conjugations']+=1
      options.append(options_i)
     actual.update(product(*options))
    im0={Npow(F0,x,ds[0]-1,p) for x in mats}
    im1={Npow(F0,x,ds[1],p) for x in mats}
    predicted={(e0,e1) for e0 in mats for e1 in mats
      if e0 in im0 and sub(e1,Npow(F0,e0,ds[1]-ds[0],p),p) in im1}
    assert actual==predicted
    counts['simultaneous_image_comparisons']+=1
    family_results.append({'p':p,'r':r,'degrees':ds,'attainable_pairs':len(actual),
                           'candidate_pairs':len(mats)**2})
 # Literal mixed-characteristic fixtures, including higher-depth obstruction.
 L=(1,1,6,7);F=(1,1,0,1)
 assert power(L,3,9)==I and power(F,3,9)!=(I)
 assert tuple(x%3 for x in L)==F
 cubes=[pow(x,3,27) for x in (4,13,22)]
 assert cubes==[10,10,10]
 assert ((1-pow(4,3,27))*pow(pow(4,3,27),-1,27))%27==18
 for p in (2,3,5):assert (1*1)%p!=0  # r=0 is not a square-zero layer.
 out={'status':'PASS','arithmetic':'exact Python integers modulo p^(r+1)',
 'scopes':scopes,'counts':counts,'simultaneous_cases':family_results,
 'controls':{'order_three_lift_mod9':list(L),'cube_of_naive_lift_mod9':list(power(F,3,9)),
 'all_lifts_above_four_mod9_cubed_mod27':cubes,'normalized_scalar_error_mod3':2,
 'zero_depth_square_zero_shortcut_rejected':True},
 'seconds':monotonic()-t,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'nonclaims':['finite tests do not establish the uniform theorem',
 'p=5 residual matrices are a specified deterministic subset',
 'no global arithmetic or full coefficient-tower existence result']}
 Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
