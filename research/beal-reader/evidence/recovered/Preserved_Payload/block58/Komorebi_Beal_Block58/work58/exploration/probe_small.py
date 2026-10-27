import sys,json,time
sys.path.insert(0,'/mnt/data/beal58_sources/Komorebi_Beal_Block56/work56/computations')
from frobenius_certificate import tables,count1,count2,polynomial,twisted,character

def probe(q):
 f=1 if q%5 in (1,4) else 2;Q=q**f
 nu=(1 if Q%5==1 else -1)*character(-3,q)**f
 tab=tables(q);pows=[(pow(u,5,q),pow(u,3,q)) for u in range(1,q)]
 powers7={pow(c,7,q) for c in range(1,q)}
 eligible={(a,b) for a in range(q) for b in range(q) if (a**3+b**5)%q in powers7}
 unseen=set(eligible);ns={7:0,49:0,343:0};details=[];n1s=n2s=0
 target=[Q*Q,-2*Q*(Q+1),(Q+1)**2+2*Q,-2*(Q+1),1]
 while unseen:
  a,b=min(unseen);o={(a*u5%q,b*u3%q) for u5,u3 in pows};e=o & eligible
  assert e<=unseen;unseen-=e
  n1=count1(a,b,q,tab);n1s+=1
  if f==1 and (nu*(q+1-n1)-2*(Q+1))%7:continue
  n2=count2(a,b,q,tab);n2s+=1
  p=polynomial(q,n1,n2);t=twisted(q,p,nu,f)
  m={str(m):all((x-y)%m==0 for x,y in zip(t,target)) for m in ns}
  for mod in ns:ns[mod]+=len(e)*m[str(mod)]
  details.append(dict(a=a,b=b,p=p,t=t,weight=len(e),matches=m))
 return dict(q=q,f=f,Q=Q,nu=nu,pairs=len(eligible),n1=n1s,n2=n2s,ns=ns,details=details)
if __name__=='__main__':
 for q in [41,59,61,79,89,101,109]:
  t=time.time();x=probe(q);open(f'/mnt/data/beal58_exploration/probe_{q}.json','w').write(json.dumps(x,indent=2));print({k:v for k,v in x.items() if k!='details'},'seconds',time.time()-t,flush=True)
