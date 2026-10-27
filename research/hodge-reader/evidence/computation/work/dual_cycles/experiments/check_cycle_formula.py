import sympy as s,time
E1,E2,E3,E4,P,z,k=s.symbols('E1 E2 E3 E4 P z k')
g1=E1**4-5*E1**2*E2+5*E1*E3+5*E2**2-5*E4
g2=-5*E3
x=s.symbols('t0:5'); e=[s.symmetric_poly(i,*x) for i in range(1,6)]
V=s.prod(x[i]-x[j] for i in range(5) for j in range(i+1,5))
J=s.Matrix([[s.diff(f,t) for t in x] for f in e])
t0=time.time()
print('Newton identity:',s.expand(sum(t**5 for t in x)-(e[0]*(e[0]**4-5*e[0]**2*e[1]+5*e[0]*e[2]+5*e[1]**2-5*e[3])-5*e[1]*e[2]+5*e[4]))==0,flush=True)
print('Vandermonde determinant:',s.expand(J.det(method='domain-ge')-V)==0,time.time()-t0,flush=True)
for q in [2,3,5,7,11]:
 f3=P-k*z**5;g3=5*sum(P**(q-1-j)*k**j*z**(5*j) for j in range(q))
 fs=[E1,g1,E2,g2,f3,g3]
 M=s.Matrix([[s.diff(f,v) for v in [E1,E2,E3,E4,P,z]] for f in fs])
 expected=625*q*sum(k**j*P**(q-1-j)*z**(5*j-1) for j in range(1,q))
 print('q',q,'intermediate determinant',s.expand(M.det(method='domain-ge')-expected)==0,flush=True)
