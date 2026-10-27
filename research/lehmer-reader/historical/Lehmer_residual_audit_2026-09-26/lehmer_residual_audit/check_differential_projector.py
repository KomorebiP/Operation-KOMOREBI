"""Exact polynomial certificate for the full fourth-moment identity."""
from pathlib import Path
import json
import sympy as sp
from explore import tau_triangular, sigma_primes
ROOT=Path(__file__).resolve().parent
E2,E4,E6=sp.symbols('E2 E4 E6')
def D(f):
    return sp.expand(sp.diff(f,E2)*(E2**2-E4)/12+
                     sp.diff(f,E4)*(E2*E4-E6)/3+
                     sp.diff(f,E6)*(E2*E6-E4**2)/2)
def powerD(f,n):
    for _ in range(n):f=D(f)
    return f

def main():
    Delta=(E4**3-E6**2)/1728
    assert sp.expand(D(Delta)-E2*Delta)==0
    certificate2=sp.expand(E2*powerD(E2,2)-4*powerD(E2,3)-sp.Rational(3,10)*powerD(E4,2))
    certificate4=sp.expand(E2*powerD(E2,4)-sp.Rational(12,5)*powerD(E2,5)-sp.Rational(1,7)*powerD(E4,4)+sp.Rational(24,35)*Delta)
    assert certificate2==certificate4==0
    A=(1-E2)/24; B=(E4-1)/240
    projector=sp.expand(50*powerD(B,4)+35*powerD(A,4)-84*powerD(A,5)-840*A*powerD(A,4)-Delta)
    assert projector==0
    N=512; tau=tau_triangular(N); sigma,_=sigma_primes(N)
    sigma3=[0]*(N+1)
    for d in range(1,N+1):
        for n in range(d,N+1,d):sigma3[n]+=d**3
    for n in range(1,N+1):
        S4=sum(k**4*sigma[k]*sigma[n-k] for k in range(1,n))
        S2=sum(k**2*sigma[k]*sigma[n-k] for k in range(1,n))
        assert 840*S4==n**4*(50*sigma3[n]+(35-84*n)*sigma[n])-tau[n]
        assert 24*S2==n**2*(3*sigma3[n]+(1-4*n)*sigma[n])
    out={'status':'PASS','coefficient_domain':'Q[E2,E4,E6]',
         'symbolic_remainders':{'D_Delta_minus_E2_Delta':'0','second_derivative_identity':'0','fourth_derivative_identity':'0','cusp_projector':'0'},
         'independent_coefficient_checks':2*N,'coefficient_range':'1 <= n <= 512',
         'external_assumption':'Classical Ramanujan differential identities for normalized Eisenstein series',
         'non_claim':'Extracting Delta does not prove its individual Fourier coefficients nonzero.'}
    (ROOT/'differential_results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
