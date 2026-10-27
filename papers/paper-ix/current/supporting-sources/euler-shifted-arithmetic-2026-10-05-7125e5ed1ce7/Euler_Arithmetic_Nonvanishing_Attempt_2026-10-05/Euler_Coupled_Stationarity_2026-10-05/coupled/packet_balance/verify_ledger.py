#!/usr/bin/env python3
"""Independent source/gamma and direct Taylor checks for the packet ledger."""
from pathlib import Path
from math import comb
import json,sys,time,hashlib,platform
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
import dyadic_modular as d

P=320;M=1<<P;D=(P-1)//15;N=141

def val(a,cap=P):return cap if not a else (abs(a)&-abs(a)).bit_length()-1

def derivative(a):return [i*a[i] for i in range(1,len(a))]

def direct_local(a,c):
 powers=[pow(c,n,M) for n in range(len(a))]
 return [sum(a[n]*comb(n,i)*powers[n-i] for n in range(i,len(a)))*(1<<(15*i))%M for i in range(min(D,len(a)-1)+1)]

start=time.time();obj=json.loads((ROOT/'packet_ledger.json').read_text())
assert obj['source_sha256']==hashlib.sha256((ROOT/'build_ledger.py').read_bytes()).hexdigest()
assert obj['prior_sha256']==hashlib.sha256((ROOT/'prior_recenter_1096.json').read_bytes()).hexdigest()
for name,h in obj['vendor_sha256'].items():assert hashlib.sha256((ROOT/'vendor'/name).read_bytes()).hexdigest()==h
src=d.trim(d.source_polynomial(P));checks=[];G_all=[]
for rec in obj['cases']:
 r=int(rec['r']);z=int(rec['stationary_Z']);Q=rec['computed_packet_max']
 assert d.trim(list(map(int,rec['source'])))==src
 assert 3*(Q+1)+1-r.bit_count()+154>=P
 weights=[3*q+(r+q).bit_count()-r.bit_count() for q in range((r.bit_count()-1)//3+1)]
 assert min(weights)==-154 and max(q for q,x in enumerate(weights) if x==-154)==161
 byq={row['q']:row for row in rec['packets']};pq=[1];total=[0]*(D+1);gamma_checks=0
 for q in range(Q+1):
  if q:
   i=q-1;pq=d.mul(d.mul(pq,[-i,1],M),[-2*i-1,2],M)
  # A bound proves every omitted local packet is zero without assuming its unit.
  cost=3*q+(r+q).bit_count()-r.bit_count()+154
  locpq=direct_local(pq,10202)
  if q not in byq:
   assert cost+min(map(val,locpq))>=P
   continue
  gam=d.gamma_mod(r,q,-154,P);gamma_checks+=1
  assert gam==int(rec['gamma'][q])
  locsrc=direct_local(src,10202-q)
  term=d.mul(locpq,locsrc,M)[:D+1];term=[gam*a%M for a in term]
  row=byq[q];assert d.trim(term)==d.trim(list(map(int,row['coefficients'])))
  for i,a in enumerate(term):total[i]=(total[i]+a)%M
  p1=derivative(term);p2=derivative(p1)
  for channel,poly,shift in [('value',term,178),('half_derivative',p1,179),('second_derivative',p2,178)]:
   x=d.evaluate(poly,z,M);got=row[channel]
   assert x==int(got['raw_residue']) and val(x)==got['raw_valuation']
   assert got['denominator_power_of_two']==shift
   stable=min([P]+[val(a)+N for a in poly[1:]])
   assert stable==got['stable_at_actual_stationary_point_raw_bits']
   if channel!='value':assert stable==P
 # Direct differentiation and half-derivative lifting at normalized scale.
 assert all(a%(1<<178)==0 for a in total);H=[a>>178 for a in total]
 qpoly=derivative(H);assert all(a%2==0 for a in qpoly);qpoly=[a//2 for a in qpoly]
 zz=0
 for k in range(N):
  mod=1<<(k+1)
  if d.evaluate(qpoly,zz,mod):zz+=1<<k
  assert d.evaluate(qpoly,zz,mod)==0
 assert zz==z
 assert d.evaluate(derivative(total),z,M)==0
 assert val(d.evaluate(derivative(derivative(total)),z,M))-178==1
 assert val(d.evaluate(total,z,M))-178 in(0,30,80)
 # Recompute each valuation layer without q-order summation.
 for channel,ledger in rec['layers'].items():
  layers={}
  for row in rec['packets']:
   rv=row[channel]['raw_valuation']
   if rv<P:layers.setdefault(rv,[]).append(row)
  cum=0;assert len(ledger)==len(layers)
  for ent,(rv,rows) in zip(ledger,sorted(layers.items())):
   assert ent['raw_layer_valuation']==rv and ent['q']==[q['q'] for q in rows]
   s=sum(int(row[channel]['raw_residue']) for row in rows)%M;cum=(cum+s)%M
   assert s==int(ent['layer_sum_raw']) and val(s)==ent['layer_sum_valuation']
   assert cum==int(ent['cumulative_raw']) and val(cum)==ent['cumulative_valuation']
 bal=rec['unit_balance'];assert bal['representative_precision_bits']==152
 assert bal['individual_value_unit_stable_bits']==149 and bal['individual_derivative_unit_stable_bits']==152
 # Joint dependence preserves the obstruction more accurately than each value unit.
 fval=val(d.evaluate(total,z,M))-160
 assert min(160,149+fval)>=bal['certified_obstruction_bits']==152
 assert min(160,152+fval)>=152
 G_all.append(total);checks.append({'T':rec['T'],'retained_packet_coefficients_independently_reconstructed':len(byq),'gamma_coefficients_independently_verified':gamma_checks,'stationary_lift_bits':N,'critical_value_valuation':rec['groups']['total']['value']['normalized_valuation']})
# Exact finite-template coefficient conditions underlying the coupled laws.
H0=list(map(int,obj['affine_parameter_model']['H0']));H1=list(map(int,obj['affine_parameter_model']['H1']))
assert H1[0]%2 and all(a%2==0 for a in H1[1:])
H1d=derivative(H1);assert val(H1d[0])==8 and all(a%512==0 for a in H1d[1:])
Q0=derivative(H0);assert all(a%2==0 for a in Q0);Q0=[a//2 for a in Q0]
assert Q0[1]%2 and all(a%2==0 for a in Q0[2:])
for motion,(a,b) in zip(obj['moving_stationary_point_tests'],[(0,1),(1,2),(0,2)]):
 co,cn=obj['cases'][a],obj['cases'][b];zo=int(co['stationary_Z']);zn=int(cn['stationary_Z']);g=G_all[b]
 fv=d.evaluate(g,zo,M);mv=d.evaluate(g,zn,M)
 assert val(fv)-178==motion['frozen_value_valuation']
 assert val(mv)-178==motion['moved_critical_value_valuation']
 assert val((fv-mv)%M)-178==motion['movement_correction_valuation']==2*val(zo-zn)
 assert val(zo-zn)==7+val(int(co['T'])-int(cn['T']))
result={'status':'passed','checks':checks,'source_and_gamma':'independent distribution/logarithmic implementations','localization':'direct binomial Taylor coefficients from global skeleton polynomials','coefficient_precision':P,'stationary_precision':N,'individual_values':'canonical representative modulo2^320; exact stationary-point values only at recorded reduced precision','stationary_total_value':'full320rawbits by vanishing linear term and quadratic precision gain','coupled_parameter_coefficient_conditions':'passed','frozen_point_countertest':'14vs30 and74vs80 verified','seconds':time.time()-start,'python':platform.python_version(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'data_sha256':hashlib.sha256((ROOT/'packet_ledger.json').read_bytes()).hexdigest(),'nonclaims':obj['nonclaims']}
(ROOT/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
