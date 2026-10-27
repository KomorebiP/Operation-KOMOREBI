#!/usr/bin/env python3
"""Exact stored-coefficient checks for the affine-model stationary geometry.
No new critical W lift. No analytic interpolation of the actual Euler family.
"""
import json,math,hashlib,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parent
P=128; M=1<<P; N=7

def val(n):
 n%=M
 return P if n==0 else (n&-n).bit_length()-1

def ev(p,z):
 out=0
 for a in reversed(p):out=(out*z+a)%M
 return out

def der(p):return [i*p[i] for i in range(1,len(p))]

def mul(a,b):
 out=[0]*(N+1)
 for i,x in enumerate(a):
  for j,y in enumerate(b[:N+1-i]):out[i+j]=(out[i+j]+x*y)%M
 return out

def evaluate_series(p,c):
 out=[0]*(N+1)
 for a in reversed(p):
  out=mul(out,c);out[0]=(out[0]+a)%M
 return out

def run():
 started=time.monotonic();path=BASE/'model_coefficients.json';D=json.loads(path.read_text())
 H0=list(map(int,D['H0']));H1=list(map(int,D['H1']))
 assert [val(a) for a in H0[:7]]==[0,3,0,8,19,28,39]
 assert [val(a) for a in H1[:7]]==[0,8,25,42,58,74,90]
 assert all(val(a)>=8 for a in H0[3:])
 assert all(val(a)>=25 for a in H1[2:])
 assert H0[2]%8==3
 q0=[x//2 for x in der(H0)];q1=[x//2 for x in der(H1)]
 assert all(x%2==0 for x in der(H0)+der(H1))
 assert [z%2 for z in q0[:2]]==[0,1]
 assert all(z%2==0 for z in q0[2:]+q1)
 # Only c(0), not a joint singular parameter, is lifted.
 c0=0
 for _ in range(8):c0=(c0-ev(q0,c0)*pow(ev(der(q0),c0),-1,M))%M
 assert ev(q0,c0)==0 and val(c0)==2
 c=[c0]+[0]*N;unit=ev(der(q0),c0)
 for n in range(1,N+1):
  a=evaluate_series(q0,c);b=evaluate_series(q1,c)
  residual=(a[n]+b[n-1])%M
  c[n]=-residual*pow(unit,-1,M)%M
 a=evaluate_series(q0,c);b=evaluate_series(q1,c)
 assert a[0]==0 and all((a[n]+b[n-1])%M==0 for n in range(1,N+1))
 A=evaluate_series(H0,c);B=evaluate_series(H1,c)
 psi=[(A[n]+(B[n-1] if n else 0))%M for n in range(N+1)]
 c_der=[val(c[n]*math.factorial(n)) for n in range(1,N+1)]
 psi_der=[val(psi[n]*math.factorial(n)) for n in range(1,N+1)]
 assert c_der==[7+15*(n-1) for n in range(1,N+1)]
 assert psi_der==[15*(n-1) for n in range(1,N+1)]
 # Exact derivative identities with denominator powers tracked explicitly.
 a=ev(der(der(H0)),c0);b=ev(der(H1),c0)
 e=ev(der(der(H1)),c0);d=ev(der(der(der(H0))),c0)
 assert [val(a),val(b),val(e),val(d)]==[1,8,26,9]
 # Jacobian(H,H_Z/2) determinant is odd at every binary residue pair.
 jac=[]
 for t in range(2):
  for z in range(2):
   h1=ev(H1,z);hz=(ev(der(H0),z)+t*ev(der(H1),z))%M
   qt=ev(q1,z);qz=(ev(der(q0),z)+t*ev(der(q1),z))%M
   det=(h1*qz-hz*qt)%M
   assert det%2==1;jac.append({'T':t,'Z':z,'det_mod8':det%8})
 return {'status':'PASS','precision_bits':P,'Taylor_degree':N,'arithmetic':'exact integer modular arithmetic',
 'coefficient_input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'H0_valuation_prefix':[val(a) for a in H0[:10]],'H1_valuation_prefix':[val(a) for a in H1[:8]],
 'stationary_c0_mod128':c0%128,'c_derivative_valuations_at_0':c_der,
 'critical_value_derivative_valuations_at_0':psi_der,
 'stationary_Taylor_coefficients_mod2_128':[str(x) for x in c],
 'critical_value_Taylor_coefficients_mod2_128':[str(x) for x in psi],
 'Morse_quadratic_square_class_mod8':H0[2]%8,'jacobian_binary_checks':jac,
 'scope':'Proves the stated finite stored-model checks only. General stationary and Morse claims use the accompanying structural argument. Higher-derivative valuations through order7 are not extrapolated to all orders or to actual global parameter interpolation.',
 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'elapsed_seconds':time.monotonic()-started}

if __name__=='__main__':
 result=run();out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else BASE/'GEOMETRY_CHECKS.json'
 out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','stationary_c0_mod128','c_derivative_valuations_at_0','critical_value_derivative_valuations_at_0','Morse_quadratic_square_class_mod8']},indent=2))
