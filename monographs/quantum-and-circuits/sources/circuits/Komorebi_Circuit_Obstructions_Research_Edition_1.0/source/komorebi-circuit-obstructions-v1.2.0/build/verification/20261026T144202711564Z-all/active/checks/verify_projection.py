"""Exact Boolean grade-extraction controls. Counts Toffoli separately from CNOT."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
from reversible import variables,one,degree,trace,validate

def gf2rank(rows):
 basis={}
 for v in rows:
  while v:
   p=v.bit_length()-1
   if p not in basis:basis[p]=v;break
   v^=basis[p]
 return len(basis)

def full_oracle(m,labels):
 n=len(labels);ls=list(range(n,n+m));nextwire=n+m
 prefix=[('C',i,ls[j]) for j in range(m) for i,v in enumerate(labels) if v>>j&1]
 if m==2:
  y=nextwire;ops=prefix+[('T',ls[0],ls[1],y)]+prefix[::-1]
 else:
  anc=list(range(nextwire,nextwire+m-2));y=nextwire+m-2
  p=[('T',ls[0],ls[1],anc[0])]
  for j in range(2,m-1):p.append(('T',anc[j-2],ls[j],anc[j-1]))
  ops=prefix+p+[('T',anc[-1],ls[-1],y)]+p[::-1]+prefix[::-1]
 validate(ops,y+1);return ops,y+1,y

def q_oracle(labels,a):
 n=len(labels);idx={v:i for i,v in enumerate(labels)}
 ops=[('T',i,idx[v^a],n) for i,v in enumerate(labels) if v<(v^a)]
 validate(ops,n+1);return ops,n+1,n

def check_oracle(n,ops,w,y,f):
 mask=one(n);v=variables(n)+[0]*(w-n)
 for bit in (0,1):
  v[y]=mask if bit else 0;want=v[:];want[y]^=f
  assert trace(ops,v,mask)[-1]==want
 return 2*(1<<n)

def main():
 rows=[];pairchecks=rankcases=fulltruth=oracleinputs=0
 for m in range(2,11):
  a=(1<<m)-1;labels=list(range(1,a));n=len(labels);pairs=[(i,j) for i,u in enumerate(labels) for j in range(i+1,n) if (u^labels[j])==a]
  assert len(pairs)==n//2
  forms=[sum(((v>>j)&1)<<i for i,v in enumerate(labels)) for j in range(m)]
  assert gf2rank(forms)==m
  # Independent pair-coefficient evaluation, not assuming the matching formula.
  def val(syndrome):return int(syndrome==a)
  qr=[0]*n
  for i,u in enumerate(labels):
   assert val(u)==0
   for j in range(i+1,n):
    c=val(u^labels[j])^val(u)^val(labels[j])^val(0)
    assert c==int((u^labels[j])==a)
    if c:qr[i]|=1<<j;qr[j]|=1<<i
    pairchecks+=1
  assert gf2rank(qr)==n;rankcases+=1
  ops,w,y=full_oracle(m,labels);qops,qw,qy=q_oracle(labels,a)
  assert sum(g[0]=='T' for g in ops)==2*m-3
  assert sum(g[0]=='C' for g in ops)==2*m*(n//2)
  assert len(qops)==n//2
  row={'m':m,'input_bits':n,'full_linear_rank':m,'full_AND_optimum':m-1,'full_restored_Toffoli_optimum':2*m-3,'full_total_constructed_gates':len(ops),'quadratic_polar_rank':n,'quadratic_AND_and_restored_Toffoli_optimum':n//2,'full_truth_table_checked':m<=4}
  if m<=4:
   vs=variables(n);ls=[]
   for form in forms:
    t=0
    for i in range(n):
     if form>>i&1:t^=vs[i]
    ls.append(t)
   f=one(n)
   for l in ls:f&=l
   q=0
   for i,j in pairs:q^=vs[i]&vs[j]
   assert degree(f,n)==m and degree(q,n)==2
   # Independent scalar syndrome evaluation on every input.
   syn=[0]*(1<<n)
   for x in range(1,1<<n):
    bit=x&-x;syn[x]=syn[x^bit]^labels[bit.bit_length()-1]
   sf=sum(int(s==a)<<x for x,s in enumerate(syn));assert f==sf
   # Independent full Möbius ANF extraction.
   coefficients=[(f>>x)&1 for x in range(1<<n)]
   for i in range(n):
    for x in range(1<<n):
     if x>>i&1:coefficients[x]^=coefficients[x^(1<<i)]
   q2=0
   for x,c in enumerate(coefficients):
    if c and x.bit_count()==2:
     ids=[i for i in range(n) if x>>i&1];q2^=vs[ids[0]]&vs[ids[1]]
   assert q==q2
   fulltruth+=1<<n;oracleinputs+=check_oracle(n,ops,w,y,f)+check_oracle(n,qops,qw,qy,q)
   bad=q&(~f&one(n));row['quadratic_false_positive_count']=bad.bit_count()
   row['smallest_unsafe_projection_witness']=((bad&-bad).bit_length()-1) if bad else None
   row['full_positive_count']=f.bit_count();row['quadratic_positive_count']=q.bit_count()
  rows.append(row)
 report={'status':'PASS','arithmetic':'exact F2, Boolean truth tables and integer rank','quadratic_coefficient_checks':pairchecks,'full_rank_cases':rankcases,'full_function_truth_inputs':fulltruth,'restored_input_target_cases_both_oracles':oracleinputs,'rows':rows,'nonclaims':['No superpolynomial ordinary total-gate lower bound.','Projection growth is exponential in m but linear in the actual input length.','For m>4 only symbolic forms, pair coefficients, rank and construction counts are checked; no full truth table.']}
 (R/'results/projection.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
