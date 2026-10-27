#!/usr/bin/env python3
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'bernoulli_closure/separation/carry_adapted'))
import check_carry_adapted as ca
b=ca.base;P=384;M=1<<P;ca.P=P;ca.MOD=M

def main(output):
 start=time.monotonic();b.B=b.bernoullis(P);b.twoB=ca.fast_twoB;src=list(b.source(P));records=[]
 assert all(b.v2(a,P)>=i for i,a in enumerate(src))
 for x0,expected_v,expected_u in [(10202,153,5),(10201,152,3)]:
  prod=1;derivative=0
  for j in range(161):
   fac=(x0-j)*(2*x0-2*j-1);dfac=4*x0-4*j-1
   derivative=derivative*fac+prod*dfac;prod*=fac
  assert b.v2(derivative)==expected_v and (derivative>>expected_v)%8==expected_u
 for T in [0,718787533,22831001499602523078606181325]:
  r=(17659+(1<<18)*T)*(1<<640)-161;cut=(P+r.bit_count()-156)//3
  gam=b.gamma(r,-154,P,cut);ca.CENTER=10202
  gp=ca.localize(gam,src);K=[a>>178 for a in gp]
  assert all((i*K[i])%2==0 for i in range(1,len(K)))
  hh=[i*K[i]//2 for i in range(1,len(K))];assert hh[1]%2 and all(v%2==0 for v in hh[2:])
  c=0
  for j in range(P-179):
   if b.ev(hh,c,1<<(j+1)):c+=1<<j
  assert c%128==20
  vp=ca.localize([i*a%M for i,a in enumerate(gam)],src)
  up=ca.localize([i*(i-1)*a%M for i,a in enumerate(gam)],src)
  cp=ca.localize(gam,[1]);c9p=ca.localize([a*pow(pow(9,i,M),-1,M)%M for i,a in enumerate(gam)],[1])
  ca.CENTER=10201;neighbor=ca.localize(gam,src);ca.CENTER=10202
  val=lambda a:b.ev(a,c,M)
  dx=lambda a:b.ev(b.deriv(a),c,M)>>15
  x=(10202+(1<<15)*c)%M;Q=x*(2*x-1)%M;D=(x+1)*(2*x+1)%M;Qp=(4*x-1)%M;Dp=(4*x+3)%M
  g,v,u,cc,c9,gn=map(val,[gp,vp,up,cp,c9p,neighbor])
  gx,vx,ux,cx,c9x,gnx=map(dx,[gp,vp,up,cp,c9p,neighbor])
  assert (2*u-(4*x+1)*v+D*g-9*Q*gn-cc)%M==0
  md=1<<(P-15)
  assert (2*ux-(4*x+1)*vx-4*v+Dp*g+D*gx-9*Q*gnx-9*Qp*gn-cx)%md==0
  # Source resummation uses the same p-adic branch 9^x for integral x.
  nine_x=pow(9,x,M)
  assert (8*Q*gn-nine_x*c9+cc)%M==0
  terms={'V':v,'U':u,'C1':cc,'C9':c9,'G_shift':gn,
         'V_x':vx,'U_x':ux,'C1_x':cx,'C9_x':c9x,'G_shift_x':gnx,
         'shift_derivative_term':9*Q*gnx,'factor_derivative_term':9*Qp*gn,
         'shift_pair_derivative':9*(Q*gnx+Qp*gn),
         'complete_right_derivative':9*(Q*gnx+Qp*gn)+cx,
         'complete_left_derivative':2*ux-(4*x+1)*vx-4*v}
  out={}
  for name,a in terms.items():
   bits=P-15 if name.endswith('_x') or 'derivative' in name else P
   a%=1<<bits;k=b.v2(a,bits)
   out[name]={'valuation_or_bound':k,'unit_mod8':(a>>k)%8 if k+3<=bits else None}
  assert out['V']['valuation_or_bound']==154 and out['U']['valuation_or_bound']==159
  assert out['C1']['valuation_or_bound']==155 and out['C1']['unit_mod8']==7
  assert out['C9']['valuation_or_bound']==155 and out['C9']['unit_mod8']==3
  assert out['G_shift']['valuation_or_bound']==153 and out['G_shift']['unit_mod8']==1
  assert out['G_shift_x']['valuation_or_bound']==152
  assert out['G_shift_x']['unit_mod8']==3
  assert out['V_x']['valuation_or_bound']==155 and out['U_x']['valuation_or_bound']>=158
  assert out['C1_x']['valuation_or_bound']>=156
  assert out['shift_derivative_term']=={'valuation_or_bound':153,'unit_mod8':5}
  assert out['factor_derivative_term']=={'valuation_or_bound':153,'unit_mod8':7}
  assert out['shift_pair_derivative']['valuation_or_bound']==155
  assert out['complete_right_derivative']['valuation_or_bound']==155
  assert out['complete_left_derivative']['valuation_or_bound']==155
  assert out['complete_right_derivative']['unit_mod8']==out['complete_left_derivative']['unit_mod8']==3
  records.append({'T':str(T),'terms':out})
 result={'status':'passed','global_bits':P,'critical_Z_bits':P-179,'records':records,'seconds':time.monotonic()-start,
         'nonclaims':['No new parameters or ranks.','No nonvanishing conclusion from shifted G.','No half-shift dictionary.']}
 Path(output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'CHECKS.json')
