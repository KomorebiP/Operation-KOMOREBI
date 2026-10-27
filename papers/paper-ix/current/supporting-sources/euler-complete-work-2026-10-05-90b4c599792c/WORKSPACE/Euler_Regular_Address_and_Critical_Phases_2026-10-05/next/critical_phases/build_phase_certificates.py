#!/usr/bin/env python3
"""Exact finite coefficient certificates, lifted by the inherited uniform template.
No parameter sampling. No all-precision undepleted parameter interpolation.
"""
from pathlib import Path
from functools import lru_cache
import sys,json,time,hashlib,platform
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
import euler_packet_engine as base
import dyadic_modular as d
import terminal_carry_v6 as tc

@lru_cache(None)
def fast_twoB(n,P):
 M=1<<P;unit=1;valuation=0;total=0
 for k in range(min(n,P)+1):
  if k:
   numerator=n-k+1;vn=base.v2(numerator);vd=base.v2(k)
   unit=unit*((numerator>>vn)%M)*pow(k>>vd,-1,M)%M
   valuation+=vn-vd
   assert valuation>=0
  if base.B[k]:
   weight=base.fmod((1<<k)*base.B[k],P)
   bc=(unit<<valuation)%M if valuation<P else 0
   total=(total+bc*weight)%M
 return total*pow((1-pow(2,n-1,M))%M,-1,M)%M
base.twoB=fast_twoB

def build(L,P):
 started=time.time();j=161;M=1<<P;r=(1<<L)-j
 desc=tc.terminal_descriptor(r);mu=desc['mu'];delta=desc['delta']
 assert desc['j']==161 and desc['L']==L
 qmax=(P+r.bit_count()+mu-2)//3
 assert 3*(qmax+1)+1-r.bit_count()-mu>=P
 stability=L+1-(2*(j+2*P)).bit_length()
 assert stability>=P and (1<<L)>2*(j+2*P) and 2*r-1>P
 gam=base.gamma(r,mu,P,qmax);src=list(base.source(P))
 low=[0];high=[0];pq=[1]
 for q,g in enumerate(gam):
  if q:
   i=q-1;pq=d.mul(d.mul(pq,[-i,1],M),[-2*i-1,2],M)
  if g:
   term=[g*a%M for a in d.mul(pq,d.affine(src,-q,1,M),M)]
   if q<j:low=d.add(low,term,M)
   else:high=d.add(high,term,M)
 assert all(a%(1<<delta)==0 for a in low)
 V=d.trim([(a>>delta)%128 for a in low])
 assert V==[2,19,84,16,32,64]
 assert [x for x in range(128) if d.evaluate(V,x,128)==0]==[90]
 tmp={'j':j,'L':L,'mu':mu,'precision':P,'qcut':2*P,'computed_qmax':qmax,
      'stability_margin':stability,'low':low,'high':high}
 out={'L':L,'j':j,'delta':delta,'template':tmp,'gamma':gam,
      'source':src,'lower_V_mod128':V,'lower_root_mod128':[90]}
 if L!=640:
  cert=tc.parameter_certificate(tmp,1,1,max_depth=20)
  assert cert['complete'];assert cert['root_count']=={639:1,641:3}[L]
  out['certificates']=[cert]
 else:
  lo=base.local(low,90,7,P);hi=base.local(high,90,7,P)
  assert all(z%(1<<160)==0 for z in lo+hi)
  A=[z>>160 for z in lo];C=[z>>160 for z in hi];N=P-160;m=1<<N
  assert A[1]%2==1 and all(a%2==0 for i,a in enumerate(A) if i!=1)
  W=d.add(d.mul(A,base.deriv(C),m),[-z for z in d.mul(C,base.deriv(A),m)],m)
  at=d.root_atlas({'coefficients':W,'precision':N},max_depth=30)
  assert len(at)==2 and at[0]['kind']=='constant' and at[0]['s']==0 and at[0]['k']==1 and at[0]['value']==4
  assert at[1]['kind']=='simple_root' and at[1]['s']==1 and at[1]['k']==1 and at[1]['content']==4
  y=at[1]['root_mod'];bits=at[1]['root_bits'];mod=1<<bits
  b=-d.evaluate(C,y,mod)*pow(d.evaluate(A,y,mod),-1,mod)%mod
  assert bits==61 and b==606767000650532091
  assert b%(1<<18)==17659 and y%256==79
  out.update(low_local=A,high_local=C,wronskian=W,wronskian_atlas=at,
             joint_precision=bits,candidate_B=b,candidate_Y=y,
             candidate_X_mod32768=(90+128*y)%32768)
 out['status']='finite coefficient assertion verified'
 out['scope']='All positive odd B whose actual terminal is 161; coefficientwise finite congruence on parity balls.'
 out['nonclaims']=['No universal Euler simplicity','No exact multiple root constructed','No Lean compilation','No all-precision analytic B-family asserted']
 out['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),*sorted((ROOT/'vendor').glob('*.py'))]}
 out['python']=platform.python_version();out['seconds']=time.time()-started
 (ROOT/f'phase_{L}.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'L':L,'precision':P,'root_count':out.get('certificates',[{}])[0].get('root_count'),'candidate_B':out.get('candidate_B'),'seconds':out['seconds']}),flush=True)

if __name__=='__main__':
 for L,P in ((639,180),(640,224),(641,180)):build(L,P)
