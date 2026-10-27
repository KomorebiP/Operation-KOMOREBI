import numpy as np
from projector_signal.smith import *

def test_cayley_and_passivity():
 z=np.array([.2+.4j,1+0j,3-1.5j,20+8j]);assert np.max(np.abs(z_from_gamma(gamma_from_z(z))-z))<1e-12
 r=np.random.default_rng(7);zz=r.uniform(0,20,500)+1j*r.uniform(-20,20,500);assert np.max(np.abs(gamma_from_z(zz)))<=1+1e-12

def test_mobius_group_and_n2():
 z=np.array([.3+.2j,1+1j,5-2j])
 for N in (2,3,4,5,8):
  for k in range(N): assert np.max(np.abs(gamma_from_z(phase_mobius(z,N,k))-rotate_gamma(gamma_from_z(z),N,k)))<3e-12
  for k in range(N):
   for l in range(N): assert np.max(np.abs(phase_mobius(phase_mobius(z,N,l),N,k)-phase_mobius(z,N,(k+l)%N)))<4e-11
 assert np.max(np.abs(phase_mobius(z,2,1)-1/z))<2e-12
 assert np.max(np.abs(admittance_from_gamma(gamma_from_z(z))-z_from_gamma(-gamma_from_z(z))))<2e-12

def test_circle_equations_and_weight():
 for r in (0,.2,.5,1,2,5):
  g=constant_resistance_circle(r,500);res=(g.real-r/(1+r))**2+g.imag**2-1/(1+r)**2;assert np.max(np.abs(res))<1e-12
 for x in (-5,-1,-.2,.2,1,5):
  g=constant_reactance_arc(x,700);res=(g.real-1)**2+(g.imag-1/x)**2-1/x**2;assert np.max(np.abs(res))<3e-10
 g=np.array([.2+.3j,-.4+.1j,.7-.2j]);assert np.max(np.abs(smith_sensitivity(g)-smith_sensitivity(-g)))<1e-12
