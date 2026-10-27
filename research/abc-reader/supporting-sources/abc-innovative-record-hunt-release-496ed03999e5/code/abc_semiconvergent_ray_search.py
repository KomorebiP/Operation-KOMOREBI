from __future__ import annotations
import math, heapq, json, csv, time
from dataclasses import dataclass, asdict
import mpmath as mp
import sympy as sp
mp.mp.dps=90
TARGET=mp.mpf('1.6299116841270482'); ALPHA=1/TARGET
P_FORCE=[2,3,5,7,11,13]

def fac(n):return {int(p):int(e) for p,e in sp.factorint(int(n)).items()}
def rad(n):return math.prod(fac(n).keys()) if n>1 else 1
def hensel(B,C,d,q,emax):
 if math.gcd(B*C*d,q)!=1:return []
 out=[]
 for r in range(1,q):
  if (C*pow(r,d,q)-B)%q:continue
  der=(C*d*pow(r,d-1,q))%q
  if not der:continue
  rr=r;M=q;br=[(1,M,rr)]
  for e in range(1,emax):
   f=C*pow(rr,d)-B
   t=(-(f//M)*pow(der,-1,q))%q
   rr+=t*M;M*=q;br.append((e+1,M,rr))
  out.append(br)
 return out

def cf(x,maxden=10**9):
 z=mp.mpf(x);p0,p1=0,1;q0,q1=1,0;out=[]
 for _ in range(70):
  a=int(mp.floor(z));p=a*p1+p0;q=a*q1+q0
  if q>0:out.append((p,q))
  if q>maxden:break
  f=z-a
  if abs(f)<mp.mpf('1e-80'):break
  z=1/f;p0,p1=p1,p;q0,q1=q1,q
 return out

def crt(a,m,b,n):
 if math.gcd(m,n)!=1:return None
 return (a+m*((b-a)*pow(m,-1,n)%n))%(m*n),m*n
@dataclass
class Hit:
 B:int;C:int;d:int;q:int;qe:int;M:int;px:int;ex:int;py:int;ey:int;k:int
 x:int;y:int;a:int;b:int;c:int;score:float;lower_quality:float
 exact_quality:float|None=None;radical:int|None=None;fa:str='';fb:str='';fc:str=''

def cores(d):
 vals=[1]+[int(p) for p in sp.primerange(2,211)]
 ranked=[]
 for n in range(2,2001):
  f=sp.factorint(n)
  if len(f)>3 or any(e>=d for e in f.values()):continue
  r=math.prod(f.keys());eff=math.log(n)/math.log(r)
  if eff>1.15:ranked.append((eff,n))
 ranked.sort(reverse=True);vals+= [n for _,n in ranked[:12]]
 return sorted(set(vals))
def prelim(B,C,d,q,qe,M,px,ex,py,ey,k,x,y):
 if x<=0 or y<=0 or math.gcd(x,y)!=1:return None
 L=C*pow(x,d);R=B*pow(y,d);g=math.gcd(L,R)
 L//=g;R//=g;a=abs(L-R);b=min(L,R);c=max(L,R)
 if a<=0 or c<=2**63 or math.gcd(a,b)!=1 or a%q:return None
 residual=a
 while residual%q==0:residual//=q
 # pessimistic score, but credits forced powers because radical uses px,py once
 Rup=rad(B)*rad(C)*q*px*py*max(1,residual)*(x//(px**min(ex,1)))*(y//(py**min(ey,1)))
 # Actually retain raw score primarily by small residual and large height.
 score=float(ALPHA*mp.log(c)-mp.log(max(Rup,2)))
 lq=float(mp.log(c)/mp.log(max(Rup,2)))
 return Hit(B,C,d,q,qe,M,px,ex,py,ey,k,x,y,a,b,c,score,lq)

def run(dmin=3,dmax=6):
 t0=time.time();heap=[];uid=0;seen=set();st={'branches':0,'lines':0,'forced_states':0,'candidates':0,'definite_beats':0}
 for d in range(dmin,dmax+1):
  for u in cores(d):
   if u==1:continue
   for B,C in [(u,1),(1,u)]:
    alpha=mp.power(mp.mpf(B)/C,mp.mpf(1)/d)
    for q in [3,5,7,11,13]:
     for br in hensel(B,C,d,q,12):
      for qe in [8,12]:
       e,M,r=br[qe-1];st['branches']+=1
       conv=cf((alpha-r)/M)
       pairs=[]
       for i in range(1,len(conv)):
        p0,y0=conv[i-1];p1,y1=conv[i]
        if y0<2 or y1<2 or y0>10**9:continue
        x0=r*y0+M*p0;x1=r*y1+M*p1
        if x0<=0 or x1<=0:continue
        pairs.append((x0,y0,x1,y1))
       for x0,y0,x1,y1 in pairs[-3:]:
        st['lines']+=1
        for px in P_FORCE:
         if px==q:continue
         for py in P_FORCE:
          if py in (q,px):continue
          for ex in (2,3,4):
           mx=px**ex
           if math.gcd(x1,mx)!=1:continue
           kx=(-x0*pow(x1,-1,mx))%mx
           for ey in (2,3,4):
            my=py**ey
            if math.gcd(y1,my)!=1:continue
            ky=(-y0*pow(y1,-1,my))%my
            z=crt(kx,mx,ky,my)
            if z is None:continue
            k0,step=z
            for j in (0,):
             k=k0+j*step
             if k<1:continue
             x=x0+k*x1;y=y0+k*y1;st['forced_states']+=1
             h=prelim(B,C,d,q,qe,M,px,ex,py,ey,k,x,y)
             if h is None:continue
             key=(h.a,h.b,h.c)
             if key in seen:continue
             seen.add(key);st['candidates']+=1
             if h.lower_quality>TARGET:st['definite_beats']+=1
             uid+=1;it=(h.score,uid,h)
             if len(heap)<6000:heapq.heappush(heap,it)
             elif h.score>heap[0][0]:heapq.heapreplace(heap,it)
 arr=[x[2] for x in sorted(heap,reverse=True)]
 exact=[]
 for h in arr[:100]:
  try:
   if max(h.a.bit_length(),h.b.bit_length(),h.c.bit_length())<420:
    fa,fb,fc=fac(h.a),fac(h.b),fac(h.c);RR=math.prod(fa)*math.prod(fb)*math.prod(fc)
    h.radical=RR;h.exact_quality=float(mp.log(h.c)/mp.log(RR))
    h.fa=' '.join(f'{p}^{e}' for p,e in sorted(fa.items()));h.fb=' '.join(f'{p}^{e}' for p,e in sorted(fb.items()));h.fc=' '.join(f'{p}^{e}' for p,e in sorted(fc.items()))
  except:pass
  exact.append(h)
 exact.sort(key=lambda h:h.exact_quality if h.exact_quality is not None else h.lower_quality,reverse=True)
 st.update(elapsed=time.time()-t0,retained=len(arr),exact_factored=sum(h.exact_quality is not None for h in exact))
 return st,exact
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--dmin',type=int,default=3);ap.add_argument('--dmax',type=int,default=6);ap.add_argument('--prefix',default='/mnt/data/ABC_Semiconvergent_Ray')
 args=ap.parse_args();st,hits=run(args.dmin,args.dmax)
 open(args.prefix+'_RESULTS.json','w').write(json.dumps({'stats':st,'target':float(TARGET),'top':[asdict(h) for h in hits[:200]]},indent=2)+'\n')
 with open(args.prefix+'_HITS.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(asdict(hits[0]).keys()));w.writeheader();w.writerows(asdict(h) for h in hits)
 print(json.dumps(st,indent=2))
 for h in hits[:25]:print(h.exact_quality,h.a,h.b,h.c,'d,B,C,q=',h.d,h.B,h.C,h.q,'forced',h.px,h.ex,h.py,h.ey)
