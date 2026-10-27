import sys,json,itertools,time
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/mnt/data/beal65_session/frozen64/Komorebi_Beal_Block64/work64/computations')
import conductor64 as c
c.GEN[379]=(-2,-2,-1,1,-2,-2)
data=json.loads(Path('/mnt/data/beal65_session/release/Komorebi_Beal_Block65/work65/source_records/inherited_fixture.json').read_text())
p=json.loads(Path('/mnt/data/beal65_session/exploration/count379_probe.json').read_text())
data['good_trace_sets']['379']=p['trace_defect_set'];data['paired_trace_sets']['379']=[list(z) for z in sorted({tuple(x['defect_roots']) for x in p['rows'] if x['residual_pass']})];data['kummer_rows']['379']=[[5,1,4],[2,1,4]]
allq=sorted(set(c.CONTROL)|{q for q in range(11,2001) if c.prime(q) and q%7==1 and q%5 in(2,3)})
cols={q:c.column(q) for q in allq}

def points(state,n):
 free=[j for j in range(n) if j not in [p for p,a,b in state]]
 for vv in itertools.product(range(7),repeat=len(free)):
  x=[0]*n
  for j,b in zip(free,vv):x[j]=b
  for p,a,b in reversed(state):x[p]=(b-sum(i*j for i,j in zip(a,x)))%7
  if any(x):yield x

def run(Q):
 ans=[];sizes=[]
 for r in range(1,7):
  C=[q for q in Q if cols[q]['ratio'] in(r,'all')];order=[71,29,491]+([] if 43 in C else[43])+[211,239,281,379]
  rr={l:[cols[q]['rows'][str(l)] for q in C] for l in order};counts=[0]*len(order)
  for v in range(1,7):
   u=7*v;states=[[]]
   for j,l in enumerate(order):
    B=[0] if l in(71,29) else[b for b in range(7) if c.allowed(data,l,u,r,b,True)]
    states=[new for st in states for b in B if (new:=c.affine_add(st,rr[l],b)) is not None]
    counts[j]+=sum(7**(len(C)-len(st))-(all(b==0 for _,_,b in st)) for st in states)
    if not states:break
   for st in states:
    for x in points(st,len(C)):ans.append(dict(alpha=[u,r,1],columns=C,inertia=x))
  sizes.append(dict(r=r,columns=C,order=order,counts=counts))
 print('Q=',Q, 'count',len(ans),'counts',sizes,'ans first',ans[:20],flush=True)
 return dict(Q=Q,stages=sizes,answers=ans)
t=time.monotonic();out={}
for name,Q in [('control',list(c.CONTROL)),('small',sorted(set(c.CONTROL)|{q for q in allq if q<=1000})),('full2000',allq)]:out[name]=run(Q)
Path('/mnt/data/beal65_session/exploration/primefield_probe.json').write_text(json.dumps(out,indent=2));print('seconds',time.monotonic()-t)
