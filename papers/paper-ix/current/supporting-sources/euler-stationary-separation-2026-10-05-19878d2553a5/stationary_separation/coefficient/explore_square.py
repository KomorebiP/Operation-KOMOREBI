from pathlib import Path
import sys,json
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'bernoulli_closure/separation/carry_adapted'))
import check_carry_adapted as ca
b=ca.base
P=384;ca.P=P;ca.MOD=1<<P;M=ca.MOD
b.B=b.bernoullis(P);b.twoB=ca.fast_twoB
src=list(b.source(P))
out=[]
for T in [0,718787533,22831001499602523078606181325]:
 r=(17659+(1<<18)*T)*(1<<640)-161
 Q=(P+r.bit_count()-156)//3
 gam=b.gamma(r,-154,P,Q)
 poly=ca.localize(gam,src)
 K=[v>>178 for v in poly]; h=[i*K[i]//2 for i in range(1,len(K))];c=0
 for j in range(P-179):
  if b.ev(h,c,1<<(j+1)):c+=1<<j
 sq=b.mul(gam,gam,M)
 sp=ca.localize(sq,src)
 val=b.ev(sp,c,M)
 out.append({'T':T,'v_square':b.v2(val,P),'unit8':(val>>b.v2(val,P))%8,'Gauss':min(b.v2(v,P) for v in sp),'derivative':b.v2(b.ev(b.deriv(sp),c,M),P)-15,'packet_values':[(q,b.v2(a,P)+sum(b.v2(10202-i) for i in range(q))) for q,a in enumerate(sq) if a and b.v2(a,P)+sum(b.v2(10202-i) for i in range(q))<315]})
print(json.dumps(out,indent=2))
