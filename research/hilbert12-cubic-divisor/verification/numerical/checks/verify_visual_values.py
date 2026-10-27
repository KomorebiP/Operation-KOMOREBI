"""Independent read-only exact/floating validation of H12 finite chart inputs."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,collections,datetime,hashlib,itertools,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'dependencies'))
import mpmath as mp
ap=argparse.ArgumentParser();ap.add_argument('--control',type=Path,required=True);ap.add_argument('--result',type=Path,required=True);a=ap.parse_args()
tic=time.monotonic();j=json.loads(a.control.read_text());c=j['checks'];checks=[]
def ck(name,ok):
    if not ok:raise AssertionError(name)
    checks.append(name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ck('generator hash',sha(a.control.parent/'generate_figures.py')==j['script_sha256'])
for f in j['figure_files']:assert sha(a.control.parent/f['path'])==f['sha256']
ck('all declared figure payload hashes',True)
def mul(A,B):return [[sum(A[i][k]*B[k][l] for k in range(3)) for l in range(3)] for i in range(3)]
N=[[2,-1,0],[4,0,-15],[1,0,-2]];N5=[[2,-1,0],[4,0,-3],[5,0,-2]];M=[[2*int(i==k)-N[i][k] for k in range(3)] for i in range(3)];seven=[[7*int(i==k) for k in range(3)] for i in range(3)]
mat=c['principal_matrices'];ck('exact principal matrices and cubes',mat['M']==M and mat['N']==N and mat['N5']==N5 and mat['N_cubed']==mul(mul(N,N),N)==seven and mat['N5_cubed']==mul(mul(N5,N5),N5)==seven)
ck('16 family count rows',len(c['family_counts'])==16 and all(r['n']==n and r['distinct_zeros']==n**3 and r['distinct_poles']==4*n**3 and r['zero_multiplicity']==r['pole_multiplicity']==4*n**3 for n,r in enumerate(c['family_counts'],1)))
ck('recorded independent Fraction lift range',c['fraction_lift_comparison']=={'box':[-6,6],'triples':2197,'all_seven_lifts':True})
counts=[0]*7
for b,z in itertools.product(range(-8,9),repeat=2):
    pivot=-((2*b-3*z)//7);digit=7*pivot+2*b-3*z;assert 0<=digit<7;counts[digit]+=1
ck('all 289 ceiling digits',c['ceiling_plot']=={'b':[-8,8],'c':[-8,8],'digit_counts':counts})
lines=[[(0,0),(1,0),(2,0)],[(0,0),(0,1),(0,2)],[(0,0),(1,1),(2,2)],[(0,0),(1,2),(2,1)]]
actual=[list(map(tuple,L)) for L in c['four_norm_lines']['lines']]
inc=collections.Counter(p for L in lines for p in L)
ck('four F3 lines and incidence',actual==lines and c['four_norm_lines']['incidence']=={f'{x},{y}':v for (x,y),v in inc.items()})
cycles=[];seen=set()
for k in range(7):
 if k not in seen:
  orbit=[];v=k
  while v not in seen:seen.add(v);orbit.append(v);v=4*v%7
  cycles.append(orbit)
ck('rho multiplier4 seven-label cycles',c['seven_action']=={'multiplier':4,'modulus':7,'cycles':cycles})
ck('exact local canonical coefficients',[[Q(v) for v in row] for row in c['canonical_local_log_coefficients']]==[[Q(0) if k<=g else Q(-1,k) for k in range(1,5)] for g in range(4)])
ck('exact reflection/transition/cube coefficient vectors',{k:[Q(v) for v in x] for k,x in c['polynomial_reconstruction'].items()}=={'reflection_z2':[Q(0),Q(2),Q(0)],'transition_second_derivative':[Q(0),Q(0),Q(6)],'cube_exponents':[Q(0),Q(-2,3),Q(-8,9)]})
max_error=mp.mpf(0);points=0
with mp.workdps(90):
 beta=mp.root(7,3)*mp.exp(4j*mp.pi/3);tau=(beta**2+2*beta)/15;s=-(beta+2)/15;t=-tau;delta=(tau+2*s+4)/7
 for name,value in [('beta',beta),('tau',tau),('s',s),('t',t),('delta',delta)]:
  rec=c['fixed_periods_numerical'][name];err=abs(value-mp.mpc(rec['real'],rec['imag']));assert err<mp.mpf('1e-70');max_error=max(max_error,err)
 ck('fixed embedding signs and five period values',mp.im(beta)<0 and mp.im(t)>0 and mp.im(s)>0)
 for n in [2,3]:
  data=c['plotted_embeddings'][str(n)];expected_z={(-i,l,5*(n+k)) for i,l,k in itertools.product(range(1,n+1),repeat=3)};expected_p={(-i,l,5*(n+k)-r) for i,l,k in itertools.product(range(1,n+1),repeat=3) for r in range(1,5)}
  for label,expected,target in [('zeros',expected_z,4),('poles',expected_p,-1)]:
   records=data[label];assert len(records)==len(expected) and {tuple(v['triple']) for v in records}==expected
   for v in records:
    aa,bb,cc=v['triple'];pivot=-((2*bb-3*cc)//7);w=4 if cc%5==0 else -1
    order=w*(int(pivot>0)-int(2*pivot-aa>0)-int(aa>0)+int(bb>0));assert order==v['order']==target
    value=(aa*tau+bb*s+mp.mpf(cc)/5)/beta;rec=v['coordinate'];err=abs(value-mp.mpc(rec['real'],rec['imag']));assert err<mp.mpf('1e-70');max_error=max(max_error,err);points+=1
 ck('all175 plotted family memberships, signed orders and coordinates',points==175)
 out={'result':'PASS','control_sha256':sha(a.control),'generator_sha256':j['script_sha256'],'named_checks':checks,'plot_points':points,'periods':5,'ceiling_digits':289,'figure_payloads':len(j['figure_files']),'comparison_working_digits':90,'coordinate_tolerance':'1e-70','max_coordinate_absolute_error':mp.nstr(max_error,30),'runtime_seconds':time.monotonic()-tic,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Exact finite integer/rational chart data and independent high-precision coordinate comparisons. Coordinates are floating illustrations, not interval enclosures. No infinite divisor count or canonical-product value is certified.'}
a.result.write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'named checks;',points,'plotted coordinates;',len(j['figure_files']),'figure payload hashes')
