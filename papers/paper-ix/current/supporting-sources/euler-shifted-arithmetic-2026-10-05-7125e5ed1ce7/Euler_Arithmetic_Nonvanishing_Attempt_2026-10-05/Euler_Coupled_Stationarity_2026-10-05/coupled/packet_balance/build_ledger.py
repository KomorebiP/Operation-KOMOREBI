#!/usr/bin/env python3
"""Actual Euler packet values at certified finite stationary residues.
Exact integer arithmetic; packet summation ordered by valuation layers.
"""
from pathlib import Path
from fractions import Fraction
import sys,json,time,hashlib,platform,csv
from functools import lru_cache
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

P=320;M=1<<P;SHIFT=178;N=P-SHIFT-1;CENTER=10202;DEPTH=15
base.B=base.bernoullis(P)

def v(n,cap=P):return cap if not n else (abs(n)&-abs(n)).bit_length()-1

def linmul(a,c,s,D,mod):
 return [((c*(a[i] if i<len(a) else 0))+(s*a[i-1] if i else 0))%mod for i in range(min(len(a)+1,D+1))]

def local_source(src,c,prec,D):
 mod=1<<prec;out=[0]*(D+1)
 for a in reversed(src[:prec]):
  for i in range(D,0,-1):out[i]=(c*out[i]+(1<<DEPTH)*out[i-1])%mod
  out[0]=(c*out[0]+a)%mod
 return out

def conv(a,b,D,mod):
 out=[0]*(min(D,len(a)+len(b)-2)+1)
 for i,x in enumerate(a):
  for j in range(min(len(b),len(out)-i)):out[i+j]=(out[i+j]+x*b[j])%mod
 return out

def packets(r,mu):
 Q=(P+r.bit_count()+mu-2)//3
 assert 3*(Q+1)+1-r.bit_count()-mu>=P
 gam=base.gamma(r,mu,P,Q);src=list(base.source(P));D=(P-1)//DEPTH;pq=[1];out=[]
 assert all(v(a)>=i for i,a in enumerate(src))
 for q,g in enumerate(gam):
  if q:
   i=q-1;pq=linmul(pq,CENTER-i,1<<DEPTH,D,M);pq=linmul(pq,2*CENTER-2*i-1,1<<(DEPTH+1),D,M)
  if not g or not any(pq):continue
  vg=v(g);vp=min(map(v,pq));pe=P-vg-vp
  if pe<=0:continue
  mm=1<<pe;ds=min(D,(pe-1)//DEPTH)
  a=local_source(src,CENTER-q,pe,ds)
  term=conv([(z>>vp)%mm for z in pq],a,D,mm)
  poly=[((g>>vg)*z<<(vg+vp))%M for z in term]
  if any(poly):out.append({'q':q,'coefficients':poly})
 return out,gam,src,Q

def annotate(raw,shift,poly,z):
 raw%=M;vv=v(raw);value=None if vv==P else vv-shift
 unit=None if vv==P else (raw>>vv)%65536
 leading=None if vv==P else str(Fraction(unit*(1<<max(0,value)),1<<max(0,-value)))
 # The integer representative is exact at P; the actual critical point is
 # known mod2^N. Coefficientwise Lipschitzness gives this conservative bound.
 displacement=min([P]+[v(a)+N for a in poly[1:]])
 return {'raw_residue':str(raw),'denominator_power_of_two':shift,'raw_valuation':vv,'normalized_valuation':value,'valuation_is_lower_bound':vv==P,
         'normalized_precision_bits':P-shift,'stable_at_actual_stationary_point_raw_bits':min(P,displacement),'unit_mod65536':unit,'leading_rational_residue_16bits':leading}

def layers(rows,channel):
 groups={}
 for row in rows:
  x=row[channel];groups.setdefault(x['raw_valuation'],[]).append(row)
 out=[];cum=0
 for vv,terms in sorted(groups.items()):
  if vv==P:continue
  lay=sum(int(t[channel]['raw_residue']) for t in terms)%M;cum=(cum+lay)%M
  out.append({'raw_layer_valuation':vv,'q':[t['q'] for t in terms],'layer_sum_raw':str(lay),'layer_sum_valuation':v(lay),'cumulative_raw':str(cum),'cumulative_valuation':v(cum),'cumulative_zero_to_precision':cum==0})
 return out

def run(T,label):
 B=17659+(T<<18);r=(B<<640)-161;desc=tc.terminal_descriptor(r);assert desc['j']==161 and desc['mu']==-154
 recs,gam,src,Q=packets(r,-154);G=[0]*((P-1)//DEPTH+1)
 for row in recs:
  for i,a in enumerate(row['coefficients']):G[i]=(G[i]+a)%M
 assert all(a%(1<<SHIFT)==0 for a in G)
 H=[a>>SHIFT for a in G];DH=base.deriv(H);assert all(a%2==0 for a in DH)
 J=[a//2 for a in DH];assert J[1]%2 and all(a%2==0 for a in J[2:])
 z=0
 for bits in range(1,N+1):
  mm=1<<bits;choices=[zz for zz in(z,z+(1<<(bits-1))) if base.ev(J,zz,mm)==0]
  assert len(choices)==1;z=choices[0]
 rows=[];group_poly={'lower':[0]*len(G),'upper':[0]*len(G)}
 for rr in recs:
  poly=rr['coefficients'];p1=base.deriv(poly);p2=base.deriv(p1);group='lower' if rr['q']<161 else 'upper'
  for i,a in enumerate(poly):group_poly[group][i]=(group_poly[group][i]+a)%M
  row={'q':rr['q'],'group':group,'coefficients':list(map(str,poly)),
       'value':annotate(base.ev(poly,z,M),SHIFT,poly,z),
       'half_derivative':annotate(base.ev(p1,z,M),SHIFT+1,p1,z),
       'second_derivative':annotate(base.ev(p2,z,M),SHIFT,p2,z)};rows.append(row)
 groups={}
 for group,poly in [*group_poly.items(),('total',G)]:
  p1=base.deriv(poly);p2=base.deriv(p1)
  groups[group]={'value':annotate(base.ev(poly,z,M),SHIFT,poly,z),'half_derivative':annotate(base.ev(p1,z,M),SHIFT+1,p1,z),'second_derivative':annotate(base.ev(p2,z,M),SHIFT,p2,z)}
 assert int(groups['total']['half_derivative']['raw_residue'])==0
 assert groups['total']['second_derivative']['normalized_valuation']==1
 # At the stationary point, the first variation vanishes modulo2^P and the
 # higher variation is divisible by2^(SHIFT+2*N)>2^P.
 assert SHIFT+2*N>P
 groups['total']['value']['stable_at_actual_stationary_point_raw_bits']=P
 groups['total']['value']['stationary_quadratic_precision_gain']=True
 assert all(row['half_derivative']['stable_at_actual_stationary_point_raw_bits']==P for row in rows)
 assert all(row['second_derivative']['stable_at_actual_stationary_point_raw_bits']==P for row in rows)
 # Unit-scaled group comparison preserves the precision of cancellation.
 lv=int(groups['lower']['value']['raw_residue']);uv=int(groups['upper']['value']['raw_residue'])
 ld=int(groups['lower']['half_derivative']['raw_residue']);ud=int(groups['upper']['half_derivative']['raw_residue'])
 sv=v(lv);sd=v(ld);assert v(uv)==sv and v(ud)==sd
 bits=min(P-sv,P-sd);mm=1<<bits
 L0=(lv>>sv)%mm;U0=(uv>>sv)%mm;D0=(ld>>sd)%mm;E0=(ud>>sd)%mm
 cb=(1+U0*pow(L0,-1,mm))%mm;sb=(1+E0*pow(D0,-1,mm))%mm
 cross=(L0*E0-U0*D0)%mm
 assert cross==(-(L0+U0)*D0)%mm
 out={'label':label,'T':str(T),'B':str(B),'r':str(r),'precision':P,'normalized_value_bits':P-SHIFT,'stationary_bits':N,'stationary_Z':str(z),'stationary_X':str(CENTER+(z<<DEPTH)),
      'normalization':{'x_center':CENTER,'x_depth':DEPTH,'content':SHIFT},'computed_packet_max':Q,'retained_nonzero_local_packets':len(rows),'gamma':list(map(str,gam)),'source':list(map(str,src)),
      'groups':groups,'packets':rows,'layers':{ch:layers(rows,ch) for ch in ['value','half_derivative','second_derivative']},
      'unit_balance':{'value_group_raw_scale':sv,'derivative_group_raw_scale':sd,'representative_precision_bits':bits,'individual_value_unit_stable_bits':min(groups[g]['value']['stable_at_actual_stationary_point_raw_bits']-sv for g in ['lower','upper']),'individual_derivative_unit_stable_bits':min(groups[g]['half_derivative']['stable_at_actual_stationary_point_raw_bits']-sd for g in ['lower','upper']),'certified_obstruction_bits':bits,'obstruction_precision_reason':'Use stationary total F=L0+U0 (160bits), v(F)>=18, L0 (149bits), derivativeunit D0 (152bits); F/L0 and -F*D0 retain at least152bits. Individual value units do not.','lower_value_unit':str(L0),'upper_value_unit':str(U0),'lower_derivative_unit':str(D0),'upper_derivative_unit':str(E0),'relative_value_imbalance':str(cb),'relative_value_imbalance_valuation':v(cb,bits),'relative_stationary_imbalance':str(sb),'relative_stationary_imbalance_valuation_lower_bound':bits if not sb else v(sb,bits),'cross_obstruction':str(cross),'cross_obstruction_valuation':v(cross,bits)}}
 return out,G

def main():
 started=time.time();old=ROOT/'prior_recenter_1096.json';prior=json.loads(old.read_text());tau=int(prior['candidate_T_residue']);Tnear=tau% (1<<80)
 cases=[];polys=[]
 for T,label in[(0,'T_zero'),(718787533,'T_30bit_cylinder'),(Tnear,'T_old_cylinder_80bit_projection')]:
  rec,poly=run(T,label);cases.append(rec);polys.append(poly)
  print(label,'T',T,'critical_value_valuation',rec['groups']['total']['value']['normalized_valuation'],'curvature',rec['groups']['total']['second_derivative']['normalized_valuation'],'unit_balance',rec['unit_balance']['relative_value_imbalance_valuation'],flush=True)
 motions=[]
 for old_index,new_index in[(0,1),(1,2),(0,2)]:
  oldcase,newcase=cases[old_index],cases[new_index]
  zo=int(oldcase['stationary_Z']);zn=int(newcase['stationary_Z']);poly=polys[new_index]
  frozen=base.ev(poly,zo,M);moved=base.ev(poly,zn,M);change=(frozen-moved)%M;dzv=v(zo-zn)
  assert v(change)-SHIFT==2*dzv
  assert v(base.ev(base.deriv(poly),zo,M))-(SHIFT+1)==dzv
  gm={}
  for name in['lower','upper']:
   pp=[0]*len(poly)
   for rr in newcase['packets']:
    if rr['group']==name:
     for i,a in enumerate(rr['coefficients']):pp[i]=(pp[i]+int(a))%M
   dd=(base.ev(pp,zo,M)-base.ev(pp,zn,M))%M
   gm[name]={'raw_change':str(dd),'normalized_change_valuation':v(dd)-SHIFT}
  motions.append({'from_case':oldcase['label'],'to_case':newcase['label'],'parameter_change_valuation':v(int(newcase['T'])-int(oldcase['T'])),'stationary_point_change_valuation':dzv,'frozen_value_valuation':v(frozen)-SHIFT,'moved_critical_value_valuation':v(moved)-SHIFT,'movement_correction_valuation':v(change)-SHIFT,'frozen_half_derivative_valuation':dzv,'group_motion':gm})
 # Whole finite affine template: two coefficient polynomials are reconstructed
 # from actual B=17659 case and its explicit lower prefix, no finite differencing.
 mnorm=1<<(P-SHIFT);B0=int(cases[0]['B']);G0=polys[0]
 lo=[0]*len(G0)
 for row in cases[0]['packets']:
  if row['q']<161:
   for i,a in enumerate(row['coefficients']):lo[i]=(lo[i]+int(a))%M
 H0=[(B0*a%M)>>SHIFT for a in G0]
 assert all(((1<<18)*a)%M%(1<<SHIFT)==0 for a in lo)
 H1=[(((1<<18)*a)%M)>>SHIFT for a in lo]
 assert H1[0]%2 and all(a%2==0 for a in H1[1:])
 for rec,poly in zip(cases,polys):
  T=int(rec['T']);B=int(rec['B'])
  assert [(B*a%M)>>SHIFT for a in poly]==[(a+T*b)%mnorm for a,b in zip(H0,H1)]
  actual=rec['groups']['total']['value']['normalized_valuation'];expected=v(T-tau,141);assert actual==expected
 out={'status':'passed','purpose':'Joint packet-level cancellation and stationarity ledger at three bounded actual Euler inputs','global_precision':P,'case_count':3,'prior_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'cases':cases,'moving_stationary_point_tests':motions,
      'affine_parameter_model':{'H0':list(map(str,H0)),'H1':list(map(str,H1)),'parameter_slope_constant_mod2':1,'parameter_slope_nonconstant_coefficients_even':True,'min_parameter_slope_derivative_valuation':min(v(a,142) for a in base.deriv(H1)),'coefficientwise_comparison_at_all_cases':'passed'},
      'interpretation':'The derivative condition cancels group slopes. The remaining value imbalance is a separate actual-unit obstruction; its value varies at first order with T in the finite affine template.',
      'nonclaims':['Three actual inputs do not prove universal Euler simplicity','Finite zero residues are not exact zeros','The finite affine multiplier template is not an all-precision undepleted interpolation','No Lean compilation'],
      'python':platform.python_version(),'seconds':time.time()-started,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'vendor_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'vendor').glob('*.py'))}}
 (ROOT/'packet_ledger.json').write_text(json.dumps(out,indent=2)+'\n')
 with (ROOT/'packet_residues.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['case','T','q','group','channel','normalized_valuation','zero_to_precision','leading_rational_residue_16bits','stable_raw_bits_at_actual_stationary_point'])
  for rec in cases:
   for p in rec['packets']:
    for ch in ['value','half_derivative','second_derivative']:
     r=p[ch];w.writerow([rec['label'],rec['T'],p['q'],p['group'],ch,r['normalized_valuation'],r['valuation_is_lower_bound'],r['leading_rational_residue_16bits'],r['stable_at_actual_stationary_point_raw_bits']])
 print('DONE',out['seconds'],flush=True)
if __name__=='__main__':main()
