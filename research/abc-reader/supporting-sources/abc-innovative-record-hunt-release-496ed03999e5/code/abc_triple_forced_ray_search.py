from __future__ import annotations
import math,heapq,time,json,csv
from dataclasses import dataclass,asdict
import mpmath as mp
import sympy as sp
mp.mp.dps=80
TARGET=mp.mpf('1.6299116841270482');ALPHA=1/TARGET
PX=[2,3,5,7];PG=[11,13,17,19]
def fac(n):return {int(p):int(e) for p,e in sp.factorint(int(n)).items()}
def rad(n):return math.prod(fac(n).keys()) if n>1 else 1
def crt(a,m,b,n):
 if math.gcd(m,n)!=1:return None
 return (a+m*((b-a)*pow(m,-1,n)%n))%(m*n),m*n
def hensel_ratio(B,C,d,q,e):
 if math.gcd(B*C*d,q)!=1:return []
 out=[]
 for r in range(1,q):
  if (C*pow(r,d,q)-B)%q:continue
  der=C*d*pow(r,d-1,q)%q
  if not der:continue
  rr=r;M=q
  for lev in range(1,e):
   F=C*pow(rr,d)-B;t=(-(F//M)*pow(der,-1,q))%q;rr+=t*M;M*=q
  out.append((M,rr))
 return out
def cf(z,maxden=10**8):
 p0,p1=0,1;q0,q1=1,0;out=[];z=mp.mpf(z)
 for _ in range(60):
  a=int(mp.floor(z));p=a*p1+p0;q=a*q1+q0
  if q>0:out.append((p,q))
  if q>maxden:break
  f=z-a
  if abs(f)<mp.mpf('1e-70'):break
  z=1/f;p0,p1=p1,p;q0,q1=q1,q
 return out
def lift_poly_root(B,C,d,M,Xb,Yb,DX,DY,p,e):
 # roots t mod p, then Hensel to p^e for G(t)=(C X(t)^d-BY(t)^d)/M
 roots=[]
 def G(t):
  num=C*pow(Xb+DX*t,d)-B*pow(Yb+DY*t,d)
  if num%M:raise AssertionError('not divisible M')
  return num//M
 def D(t):
  num=d*(C*DX*pow(Xb+DX*t,d-1)-B*DY*pow(Yb+DY*t,d-1))
  if num%M:raise AssertionError('derivative not divisible M')
  return num//M
 for t in range(p):
  if G(t)%p or D(t)%p==0:continue
  rr=t;mod=p
  for lev in range(1,e):
   corr=(-(G(rr)//mod)*pow(D(rr)%p,-1,p))%p;rr+=corr*mod;mod*=p
  roots.append((rr,mod))
 return roots
@dataclass
class Hit:
 B:int;C:int;d:int;q:int;qe:int;px:int;ex:int;py:int;ey:int;pg:int;eg:int;k:int;x:int;y:int;a:int;b:int;c:int
 score:float;exact_quality:float|None=None;radical:int|None=None;fa:str='';fb:str='';fc:str=''
def cores(d):
 vals=[int(p) for p in sp.primerange(2,151)]
 ranked=[]
 for n in range(2,1501):
  f=sp.factorint(n)
  if len(f)>3 or any(e>=d for e in f.values()):continue
  r=math.prod(f.keys());eff=math.log(n)/math.log(r)
  if eff>1.2:ranked.append((eff,n))
 ranked.sort(reverse=True);return sorted(set(vals+[n for _,n in ranked[:8]]))
def run():
 st={'lines':0,'xy_forced':0,'third_lifts':0,'candidates':0,'definite_beats':0};heap=[];uid=0;seen=set();t0=time.time()
 for d in (3,4):
  for u in cores(d):
   for B,C in ((u,1),(1,u)):
    alpha=mp.power(mp.mpf(B)/C,mp.mpf(1)/d)
    for q in (3,5,7):
     for qe in (8,12):
      for M,r in hensel_ratio(B,C,d,q,qe):
       cv=cf((alpha-r)/M)
       if len(cv)<2:continue
       # use two deepest usable rays only
       usable=[]
       for i in range(1,len(cv)):
        p0,y0=cv[i-1];p1,y1=cv[i]
        x0=r*y0+M*p0;x1=r*y1+M*p1
        if y0>=2 and y0<=10**8 and x0>0 and x1>0:usable.append((x0,y0,x1,y1))
       for x0,y0,x1,y1 in usable[-2:]:
        st['lines']+=1
        for px in PX:
         if px==q:continue
         for py in PX:
          if py in (q,px):continue
          for ex in (2,3):
           mx=px**ex
           if math.gcd(x1,mx)!=1:continue
           kx=-x0*pow(x1,-1,mx)%mx
           for ey in (2,3):
            my=py**ey
            if math.gcd(y1,my)!=1:continue
            ky=-y0*pow(y1,-1,my)%my
            z=crt(kx,mx,ky,my)
            if not z:continue
            kb,step=z;Xb=x0+x1*kb;Yb=y0+y1*kb;DX=x1*step;DY=y1*step;st['xy_forced']+=1
            for pg in PG:
             if pg in (q,px,py):continue
             for eg in (2,3):
              for t,mod in lift_poly_root(B,C,d,M,Xb,Yb,DX,DY,pg,eg):
               st['third_lifts']+=1;k=kb+step*t;x=x0+x1*k;y=y0+y1*k
               if x<=0 or y<=0 or math.gcd(x,y)!=1:continue
               L=C*pow(x,d);R=B*pow(y,d);gg=math.gcd(L,R);L//=gg;R//=gg;a=abs(L-R);b=min(L,R);c=max(L,R)
               if c<=2**63 or math.gcd(a,b)!=1 or a%(q*pg):continue
               key=(a,b,c)
               if key in seen:continue
               seen.add(key);st['candidates']+=1
               res=a
               for pp in (q,pg):
                while res%pp==0:res//=pp
               Rup=rad(B)*rad(C)*q*pg*px*py*max(1,res)*(x//px)*(y//py)
               score=float(ALPHA*mp.log(c)-mp.log(max(Rup,2)))
               uid+=1;h=Hit(B,C,d,q,qe,px,ex,py,ey,pg,eg,k,x,y,a,b,c,score);it=(score,uid,h)
               if len(heap)<5000:heapq.heappush(heap,it)
               elif score>heap[0][0]:heapq.heapreplace(heap,it)
 arr=[v[2] for v in sorted(heap,reverse=True)]
 exact=[]
 for h in arr[:120]:
  try:
   if max(h.a.bit_length(),h.b.bit_length(),h.c.bit_length())<400:
    fa,fb,fc=fac(h.a),fac(h.b),fac(h.c);RR=math.prod(fa)*math.prod(fb)*math.prod(fc);h.radical=RR;h.exact_quality=float(mp.log(h.c)/mp.log(RR));h.fa=' '.join(f'{p}^{e}' for p,e in sorted(fa.items()));h.fb=' '.join(f'{p}^{e}' for p,e in sorted(fb.items()));h.fc=' '.join(f'{p}^{e}' for p,e in sorted(fc.items()))
  except:pass
  exact.append(h)
 exact.sort(key=lambda h:h.exact_quality if h.exact_quality is not None else -1,reverse=True)
 st.update(elapsed=time.time()-t0,retained=len(arr),exact_factored=sum(h.exact_quality is not None for h in exact))
 return st,exact
if __name__=='__main__':
 st,h=run();open('/mnt/data/ABC_Triple_Forced_Ray_RESULTS.json','w').write(json.dumps({'stats':st,'target':float(TARGET),'top':[asdict(x) for x in h[:200]]},indent=2)+'\n')
 with open('/mnt/data/ABC_Triple_Forced_Ray_HITS.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(asdict(h[0]).keys()));w.writeheader();w.writerows(asdict(x) for x in h)
 print(json.dumps(st,indent=2))
 for x in h[:25]:print(x.exact_quality,x.a,x.b,x.c,'d=',x.d,'q,pg=',x.q,x.pg,'powers',x.px,x.ex,x.py,x.ey,x.pg,x.eg)
