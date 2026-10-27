import numpy as np
from projector_signal.nonlinear import *

def test_packet_product():
 r=np.random.default_rng(8);a=r.normal(size=15);b=r.normal(size=12);d=np.convolve(a,b)
 for N in (2,3,4,5):
  p=packet_product(a,b,N);assert np.max(np.abs(sum(p,np.zeros_like(d))-d))<2e-12
  for u,v in zip(p,coefficient_packets(d,N),strict=True): assert np.max(np.abs(u-v))<2e-12

def test_nonlinear_reconstruction():
 x=np.random.default_rng(9).normal(size=97);d=nonlinear_shift_filter(x,.4)
 for N in (2,3,5,8): assert np.max(np.abs(d-nonlinear_packet_reconstruct(x,N,.4)))==0
