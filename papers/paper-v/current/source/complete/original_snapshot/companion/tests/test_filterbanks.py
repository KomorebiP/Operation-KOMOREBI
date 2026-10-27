import numpy as np
from projector_signal.filterbanks import haar_analyze,haar_synthesize,haar_packet_analyze,haar_packet_synthesize,lifting_analyze,lifting_synthesize,packet_energy

def test_haar_pr_energy():
 r=np.random.default_rng(4)
 for n in (2,8,64,256):
  x=r.normal(size=n);lo,hi=haar_analyze(x);y=haar_synthesize(lo,hi)
  assert np.max(np.abs(x-y))<5e-15
  assert abs(np.vdot(x,x).real-np.vdot(lo,lo).real-np.vdot(hi,hi).real)<2e-12

def test_wavelet_packet_pr():
 r=np.random.default_rng(5);x=r.normal(size=256)
 for d in range(5):
  p=haar_packet_analyze(x,d);y=haar_packet_synthesize(p)
  assert np.max(np.abs(x-y))<8e-15
  assert abs(np.vdot(x,x).real-packet_energy(p))<3e-12

def test_lifting_pr():
 x=np.random.default_rng(6).normal(size=128);s,d=lifting_analyze(x)
 assert np.max(np.abs(x-lifting_synthesize(s,d)))<2e-15
