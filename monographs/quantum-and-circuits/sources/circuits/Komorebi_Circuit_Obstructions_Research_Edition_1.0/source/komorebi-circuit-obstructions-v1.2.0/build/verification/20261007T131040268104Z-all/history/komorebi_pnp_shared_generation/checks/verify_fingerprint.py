"""Exact weighted Boolean trace controls in GF(16). No polynomial-time SAT claim."""
from pathlib import Path
from itertools import product
import json
R=Path(__file__).resolve().parents[1]
MOD=0b10011

def multiply(a,b):
 r=0
 while b:
  if b&1:r^=a
  b>>=1;a<<=1
  if a&16:a^=MOD
 return r
M=[[multiply(a,b) for b in range(16)] for a in range(16)]

def anf(f,m):
 c=[(f>>s)&1 for s in range(1<<m)]
 for i in range(m):
  for s in range(1<<m):
   if s>>i&1:c[s]^=c[s^(1<<i)]
 return c

def extract(c,z):
 p=c[:]
 for i,zi in enumerate(z):
  q=p[:];factor=1^zi
  for s,x in enumerate(p):q[s|1<<i]^=M[x][factor]
  p=q
 return p[-1]

def weights(z):
 w=[1]*(1<<len(z))
 for s in range(1,len(w)):
  bit=s&-s;w[s]=M[w[s^bit]][z[bit.bit_length()-1]]
 return w

def evaluate(f,w):
 ans=0
 for s,v in enumerate(w):
  if f>>s&1:ans^=v
 return ans

def main():
 fieldchecks=0
 for a in range(16):
  assert M[a][1]==a and M[a][0]==0
  if a:assert any(M[a][b]==1 for b in range(1,16))
  for b in range(16):
   assert M[a][b]==M[b][a]
   if a and b:assert M[a][b]!=0
   for c in range(16):
    assert M[M[a][b]][c]==M[a][M[b][c]]
    assert M[a][b^c]==M[a][b]^M[a][c]
    fieldchecks+=1
 roots=[];fpchecks=tracechecks=0
 for m in range(1,4):
  functions=1<<(1<<m);zeros=[0]*functions
  polynomials=[anf(f,m) for f in range(functions)]
  grid=range(16)
  for z in product(grid,repeat=m):
   w=weights(z);vals=[0]*functions
   for f in range(1,functions):
    bit=f&-f;vals[f]=vals[f^bit]^w[bit.bit_length()-1]
   for f,val in enumerate(vals):
    zeros[f]+=int(val==0);fpchecks+=1
    if m<=2 or all(zi<4 for zi in z):
     assert extract(polynomials[f],z)==val
     assert evaluate(f,w)==val
     tracechecks+=1
  assert zeros[0]==16**m
  assert all(count<=m*16**(m-1) for count in zeros[1:])
  roots.append({'witness_bits':m,'all_verifiers':functions,'all_field_points_per_verifier':16**m,'largest_zero_count_nonzero_polynomial':max(zeros[1:]),'root_bound':m*16**(m-1),'maximizers':[i for i,z in enumerate(zeros) if i and z==max(zeros[1:])]})
 hom=[]
 # A linear map out of the full witness algebra is determined by its
 # values on primitive point idempotents. Check every small scalar map.
 for points,q in [(2,16),(4,16),(8,2)]:
  examined=valid=0
  for images in product(range(q),repeat=points):
   examined+=1
   total=0
   for a in images:total^=a
   preserves=(total==1 and all(M[a][a]==a for a in images)
              and all(M[images[i]][images[j]]==0 for i in range(points) for j in range(i+1,points)))
   one_hot=(sum(a!=0 for a in images)==1 and 1 in images)
   assert preserves==one_hot
   valid+=int(preserves)
  assert valid==points
  hom.append({'witness_points':points,'field_size':q,'all_linear_scalar_maps':examined,'unital_algebra_homomorphisms':valid})
 disjoint=0
 for fa in range(4):
  for fb in range(4):
   joined=sum((((fa>>(x&1))&1)&((fb>>(x>>1))&1))<<x for x in range(4))
   for za,zb in product(range(16),repeat=2):
    assert evaluate(joined,weights([za,zb]))==M[evaluate(fa,weights([za]))][evaluate(fb,weights([zb]))]
    disjoint+=1
 # Overlap falsifies the attempted local multiplicative compiler.
 z=2;Ew=z;E_notw=1
 assert M[Ew][E_notw]==2 and extract(anf(0,1),[z])==0
 assert extract(anf(0b10,1),[z])==2 and M[Ew][Ew]==4
 report={'status':'PASS','field':'F2[t]/(t^4+t+1)','field_associativity_and_distributivity_triples':fieldchecks,'polynomial_field_evaluations':fpchecks,'independent_boolean_ring_trace_checks':tracechecks,'trace_grid_scope':'all GF16 points for m<=2; coordinates 0..3 for m=3','disjoint_factorization_checks':disjoint,'scalar_algebra_maps':hom,'roots':roots,'overlap_counterexamples':{'z':2,'trace_w_times_trace_notw':2,'trace_of_w_times_notw':0,'trace_w_squared':4,'trace_of_w_squared':2},'nonclaims':['The checked trace algorithm stores 2^m coefficients and is exponential in witness length.','Nonzero-polynomial fingerprints do not give an efficient evaluator.','Randomized conditional evaluation is not a deterministic P=NP proof.']}
 (R/'results/fingerprint.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
