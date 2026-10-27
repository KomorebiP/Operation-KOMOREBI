import numpy as np
from projector_signal.polyphase import polyphase_analyze,polyphase_synthesize,residue_project,verify_refinement,polyphase_convolution

def test_analysis_synthesis_exact():
 r=np.random.default_rng(1)
 for n in (1,2,7,32,65):
  x=r.normal(size=n)+1j*r.normal(size=n)
  for N in (1,2,3,4,8): assert np.max(np.abs(polyphase_synthesize(polyphase_analyze(x,N),N,n)-x))==0

def test_projectors_and_refinement():
 r=np.random.default_rng(2);x=r.normal(size=127)
 for N in (2,3,5,8):
  P=[residue_project(x,N,j) for j in range(N)]
  assert np.max(np.abs(sum(P,np.zeros_like(x))-x))==0
  for i in range(N):
   for j in range(N): assert np.max(np.abs(residue_project(P[j],N,i)-(P[j] if i==j else 0)))==0
 for a,b in ((2,4),(2,8),(3,12),(4,16),(5,20)): assert verify_refinement(x,a,b)==0

def test_polyphase_convolution():
 r=np.random.default_rng(3)
 for nx,nh,N in ((13,7,2),(21,8,3),(32,11,4),(17,5,5)):
  x=r.normal(size=nx);h=r.normal(size=nh)
  assert np.max(np.abs(np.convolve(x,h)-polyphase_convolution(x,h,N)))<2e-12
