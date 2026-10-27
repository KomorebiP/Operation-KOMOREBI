from __future__ import annotations
import argparse, ctypes, gc, json, math, pathlib, time
from dataclasses import asdict, dataclass
import torch
from torch import nn
import torch.nn.functional as F

TAU=2*math.pi
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

def phase(t): return torch.stack((torch.cos(TAU*t),torch.sin(TAU*t)),dim=-1)
def tensor_features(a,b): return torch.cat((a,b,(a.unsqueeze(-1)*b.unsqueeze(-2)).flatten(1)),dim=-1)
def make_batch(n,g):
 u=torch.rand(n,generator=g);v=torch.rand(n,generator=g);ra=torch.rand(n,generator=g);rb=torch.rand(n,generator=g)
 values=torch.stack((ra,torch.remainder(u-ra,1.0),rb,torch.remainder(v-rb,1.0)),1);y=torch.remainder(u+v,1.0)
 return {'leaf':phase(values),'actions':phase(torch.remainder(values+y[:,None],1.0))}
class Block(nn.Module):
 def __init__(self,da,db,do,h):
  super().__init__();self.net=nn.Sequential(nn.Linear(da+db+da*db,h),nn.Tanh(),nn.Linear(h,do))
 def forward(self,a,b):return torch.tanh(self.net(tensor_features(a,b)))
class Model(nn.Module):
 def __init__(self,d,h):
  super().__init__();self.d=d;self.h=h;self.la=Block(2,2,d,h);self.lb=Block(2,2,d,h);self.g=Block(d,d,d,h);self.heads=nn.ModuleList(Block(2,d,2,h) for _ in range(4))
 def forward(self,x,cut=False):
  a=self.la(x[:,0],x[:,1]);b=self.lb(x[:,2],x[:,3]);z=self.g(a,b);zz=torch.zeros_like(z) if cut else z
  y=torch.stack([F.normalize(self.heads[i](x[:,i],zz),dim=-1) for i in range(4)],1);return y
 def params(self):return sum(p.numel() for p in self.parameters())
def acc(p,t):return float(((p*t).sum(-1)>=.99).float().mean().item())
@dataclass
class Row:
 dim:int;hidden:int;steps:int;seed:int;params:int;compute:int;train_seconds:float;accuracy:float;cut_accuracy:float;screen_emergence:bool

def trial(dim,h,steps,seed):
 torch.manual_seed(seed);g=torch.Generator().manual_seed(seed^0x5400A11);m=Model(dim,h);o=torch.optim.AdamW(m.parameters(),lr=.003,weight_decay=1e-5)
 t=time.perf_counter();m.train()
 for _ in range(steps):
  b=make_batch(256,g);p=m(b['leaf']);loss=(1-(p*b['actions']).sum(-1)).mean();o.zero_grad(set_to_none=True);loss.backward();o.step()
 seconds=time.perf_counter()-t;m.eval();e=make_batch(1024,torch.Generator().manual_seed(seed^0xA11CE))
 with torch.no_grad(): a=acc(m(e['leaf']),e['actions']);c=acc(m(e['leaf'],cut=True),e['actions'])
 n=m.params();return Row(dim,h,steps,seed,n,n*steps*256,seconds,a,c,bool(a>=.98 and c<=.15))
def main():
 p=argparse.ArgumentParser();p.add_argument('--dim',type=int,required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--hidden',type=int,required=True);p.add_argument('--steps',type=str,required=True);p.add_argument('--seeds',type=str,default='54011,54029,54047');a=p.parse_args()
 rows=[];libc=ctypes.CDLL('libc.so.6')
 for h in [a.hidden]:
  for steps in [int(x) for x in a.steps.split(',') if x]:
   for seed in [int(x) for x in a.seeds.split(',') if x]:
    r=trial(a.dim,h,steps,seed);rows.append(asdict(r));print(json.dumps(asdict(r),sort_keys=True),flush=True)
    gc.collect();libc.malloc_trim(0)
 a.output.write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
