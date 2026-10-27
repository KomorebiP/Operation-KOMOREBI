import numpy as np
from projector_signal.edges import *

def test_exact_edge_identity_1d():
 n=512;t=np.linspace(-1,1,n,endpoint=False);s=.2+.12*np.cos(2*np.pi*t)+.08*np.sin(4*np.pi*t);e=.7*(np.abs(t)<=.35);f=s+e
 for m in (2,5,12,30):
  r=exact_edge_reconstruct_1d(s,e,m)
  assert abs(rmse(f,r)-rmse(s,fft_lowpass_1d(s,m)))<1e-14

def test_known_edge_beats_global_1d():
 n=512;t=np.linspace(-1,1,n,endpoint=False);s=.15+.1*np.cos(2*np.pi*t);e=.8*(np.abs(t)<=.35);f=s+e
 assert rmse(f,exact_edge_reconstruct_1d(s,e,14))<.15*rmse(f,fft_lowpass_1d(f,14))

def test_data_mask_1d():
 n=512;t=np.linspace(-1,1,n,endpoint=False);s=.15+.1*np.cos(2*np.pi*t);m=np.abs(t)<=.35;f=s+.8*m
 assert mask_iou(m,estimate_packet_1d(f))>.95

def test_exact_edge_identity_2d():
 n=128;x=np.linspace(-1,1,n,endpoint=False);X,Y=np.meshgrid(x,x);s=.15+.12*np.exp(-((X+.35)**2+(Y-.2)**2)/.12);m=X**2+Y**2<=.35**2;e=.7*m;f=s+e
 assert abs(rmse(f,exact_edge_reconstruct_2d(s,e,12))-rmse(s,fft_lowpass_2d(s,12)))<1e-14

def test_data_mask_2d():
 n=128;x=np.linspace(-1,1,n,endpoint=False);X,Y=np.meshgrid(x,x);s=.16+.1*np.exp(-((X+.4)**2+(Y+.3)**2)/.1);m=X**2+Y**2<=.36**2;f=s+.75*m
 assert mask_iou(m,estimate_packet_2d(f))>.95

def test_boundary_band():
 m=np.zeros((64,64),bool);m[20:44,18:47]=1;b=boundary_band(m,2)
 assert 0<b.sum()<m.size//2
