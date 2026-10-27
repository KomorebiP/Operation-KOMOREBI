"""Finite controls for closing edits; not general theorem proofs."""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
import json,re,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'engine'))
checks=[]
def record(name,detail): checks.append({'check':name,'passed':True,'detail':detail})
# The proof's boundary cases and zero-risk ties, compared with exhaustive subsets.
cases=0
for risks in [(),(0,),(0,0,1,3),(1,2,5),(Fraction(1,3),Fraction(1,2),2)]:
 for tau in [Fraction(0),Fraction(1,3),Fraction(1),Fraction(3),Fraction(10)]:
  ordered=sorted(risks);r=0;s=Fraction(0)
  for a in ordered:
   if s+a<=tau:r+=1;s+=a
   else:break
  feasible=[len(c) for k in range(len(risks)+1) for c in combinations(range(len(risks)),k) if sum((risks[i] for i in c),Fraction(0))<=tau]
  assert r==max(feasible);cases+=1
record('Cardinality pruning boundary cases',f'{cases} exact rational finite cases; empty set, r=0, r=N, and zero-risk ties.')
# Execute the actual book listing, rather than a rewritten copy.
text=(ROOT/'book/chapters/C_reproduction.tex').read_text()
listing=re.search(r'\\begin\{lstlisting\}\[language=Python\](.*?)\\end\{lstlisting\}',text,re.S).group(1)
namespace={};exec(compile(listing,'Appendix_C_listing','exec'),namespace)
A=np.array([[1,1,1,1,1,1],[1,-1,1,-1,1,-1],[1,1,-1,-1,-1,-1],[1,-1,-1,1,-1,1]],dtype=float)/2
V=np.array([1,2,-1,0],dtype=int)
blocks=[A[:,i:i+2] for i in (0,2,4)]
assert np.array_equal(namespace['stream_KV'](blocks,V),A@(A.T@V))
P=np.diag([1.,0.,1.,1.]);project=lambda x:P@x
assert np.array_equal(namespace['stream_KV'](blocks,V,project),P@A@A.T@P@V)
VV=np.column_stack([V,2*V]);assert np.array_equal(namespace['stream_KV'](blocks,VV),A@A.T@VV)
record('Executable appendix listing','Integer vector and two-column input, identity projector, and supplied orthogonal projector agree exactly on dyadic data.')
from streaming_skat import estimate_working_set
m=estimate_working_set(2000,10000,4,16,1024,256)
assert round(m.streamed_kernel_action_bytes/2**20,3)==16.308
assert round(m.tiled_gram_bytes/2**20,3)==8.555
record('Declared memory-table parameters','n=2000, p=4, s=16, c=1024, t=256 reproduce 16.308 and 8.555 MiB after rounding.')
result={'all_passed':True,'control_groups':len(checks),'checks':checks,'scope':'Finite examples only; no new performance measurements or general formal proof.'}
Path(__file__).with_name('closing_controls.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
