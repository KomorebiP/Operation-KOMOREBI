from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, math
from pathlib import Path
from typing import Any
import torch
from torch import nn
import torch.nn.functional as F

VERSION="0.53.0.dev1"; TAU=2*math.pi
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical_digest(v:Any)->str:
 return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def phase(t): return torch.stack((torch.cos(TAU*t),torch.sin(TAU*t)),dim=-1)
def tensor_features(a,b): return torch.cat((a,b,(a.unsqueeze(-1)*b.unsqueeze(-2)).flatten(1)),dim=-1)
def make_batch(n:int,g:torch.Generator):
 u=torch.rand(n,generator=g);v=torch.rand(n,generator=g);ra=torch.rand(n,generator=g);rb=torch.rand(n,generator=g)
 values=torch.stack((ra,torch.remainder(u-ra,1.0),rb,torch.remainder(v-rb,1.0)),1)
 y=torch.remainder(u+v,1.0); actions=torch.remainder(values+y[:,None],1.0)
 private=torch.randint(0,4,(n,4),generator=g)
 return {"leaf_phase":phase(values),"action_phase":phase(actions),"u_phase":phase(u),"v_phase":phase(v),"y_phase":phase(y),"private":private,"values":values,"u":u,"v":v,"y":y}
class TensorProductBlock(nn.Module):
 def __init__(self,da,db,do,h=32):
  super().__init__(); self.net=nn.Sequential(nn.Linear(da+db+da*db,h),nn.Tanh(),nn.Linear(h,do))
 def forward(self,a,b): return torch.tanh(self.net(tensor_features(a,b)))
class NestedWorkspaceModel(nn.Module):
 def __init__(self,local_dim=2,global_dim=2):
  super().__init__(); self.local_dim=local_dim; self.global_dim=global_dim
  self.local_a=TensorProductBlock(2,2,local_dim);self.local_b=TensorProductBlock(2,2,local_dim);self.global_workspace=TensorProductBlock(local_dim,local_dim,global_dim)
  self.action_heads=nn.ModuleList(TensorProductBlock(2,global_dim,2) for _ in range(4))
  self.private_heads=nn.ModuleList(nn.Linear(4,4,bias=False) for _ in range(4))
  for h in self.private_heads:
   with torch.no_grad(): h.weight.copy_(torch.eye(4))
   h.weight.requires_grad_(False)
 def parameter_count(self): return sum(p.numel() for p in self.parameters() if p.requires_grad)
 def forward(self,leaf_phase,private,*,local_a_override=None,local_b_override=None,global_override=None,leaf_workspace_cut=None,topdown_cut=False):
  wi=leaf_phase.clone()
  if leaf_workspace_cut is not None: wi[:,int(leaf_workspace_cut)]=0.0
  za=self.local_a(wi[:,0],wi[:,1]) if local_a_override is None else local_a_override
  zb=self.local_b(wi[:,2],wi[:,3]) if local_b_override is None else local_b_override
  zg=self.global_workspace(za,zb) if global_override is None else global_override
  ag=torch.zeros_like(zg) if topdown_cut else zg
  actions=torch.stack([F.normalize(self.action_heads[i](leaf_phase[:,i],ag),dim=-1) for i in range(4)],1)
  priv=torch.stack([self.private_heads[i](F.one_hot(private[:,i],4).float()) for i in range(4)],1)
  return {"action_phase":actions,"private_logits":priv,"local_a":za,"local_b":zb,"global":zg}
class FlatController(nn.Module):
 def __init__(self,global_dim=4):
  super().__init__(); self.global_dim=global_dim
  self.global_network=nn.Sequential(nn.Linear(24,32),nn.Tanh(),nn.Linear(32,global_dim),nn.Tanh())
  self.action_heads=nn.ModuleList([nn.Sequential(nn.Linear(2+global_dim,24),nn.Tanh(),nn.Linear(24,2)) for _ in range(4)])
 def parameter_count(self): return sum(p.numel() for p in self.parameters() if p.requires_grad)
 def _kron4(self,x):
  r=x[:,0]
  for i in range(1,4): r=(r.unsqueeze(-1)*x[:,i].unsqueeze(1)).flatten(1)
  return r
 def forward(self,x):
  zg=self.global_network(torch.cat((x.flatten(1),self._kron4(x)),1))
  a=torch.stack([F.normalize(self.action_heads[i](torch.cat((x[:,i],zg),1)),dim=-1) for i in range(4)],1)
  return {"action_phase":a,"global":zg}
def cosine_loss(p,t): return (1-(p*t).sum(-1)).mean()
def strict_phase_accuracy(p,t,threshold=.99): return float(((p*t).sum(-1)>=threshold).float().mean().item())
def mean_phase_cosine(p,t): return float((p*t).sum(-1).mean().item())
def fit_linear_phase_probe(cz,ct,ez,et):
 ca=torch.cat((cz,torch.ones(len(cz),1)),1); ea=torch.cat((ez,torch.ones(len(ez),1)),1); w=torch.linalg.lstsq(ca,ct).solution; p=F.normalize(ea@w,dim=-1)
 return {"mean_cosine":mean_phase_cosine(p,et),"strict_accuracy":strict_phase_accuracy(p,et)}
@dataclass(frozen=True)
class TrainConfig: steps:int=1400; batch_size:int=256; learning_rate:float=.003; weight_decay:float=1e-5; private_loss_weight:float=.05
@dataclass(frozen=True)
class EvaluationConfig: calibration_cases:int=4096; holdout_cases:int=8192; patch_cases:int=4096; strict_cosine_threshold:float=.99
def train_nested_model(seed,local_dim=2,global_dim=2,config=TrainConfig()):
 torch.manual_seed(int(seed));g=torch.Generator().manual_seed(int(seed)^0x53A11);m=NestedWorkspaceModel(local_dim,global_dim);o=torch.optim.AdamW(m.parameters(),lr=config.learning_rate,weight_decay=config.weight_decay);m.train()
 for _ in range(config.steps):
  b=make_batch(config.batch_size,g);z=m(b["leaf_phase"],b["private"]);loss=cosine_loss(z["action_phase"],b["action_phase"])+config.private_loss_weight*F.cross_entropy(z["private_logits"].flatten(0,1),b["private"].flatten());o.zero_grad(set_to_none=True);loss.backward();o.step()
 return m.eval()
def train_flat_model(seed,config=TrainConfig()):
 torch.manual_seed(int(seed)^0xF1A7);g=torch.Generator().manual_seed(int(seed)^0xF1A753);m=FlatController();o=torch.optim.AdamW(m.parameters(),lr=config.learning_rate,weight_decay=config.weight_decay);m.train()
 for _ in range(config.steps):
  b=make_batch(config.batch_size,g);z=m(b["leaf_phase"]);loss=cosine_loss(z["action_phase"],b["action_phase"]);o.zero_grad(set_to_none=True);loss.backward();o.step()
 return m.eval()
def private_acc(o,p): return float((o["private_logits"].argmax(-1)==p).float().mean().item())
def evaluate_nested_model(m,seed,config=EvaluationConfig()):
 cg=torch.Generator().manual_seed(int(seed)^0xCA11B);hg=torch.Generator().manual_seed(int(seed)^0xA11CE);pg=torch.Generator().manual_seed(int(seed)^0xFA7C4)
 c=make_batch(config.calibration_cases,cg);h=make_batch(config.holdout_cases,hg);s=make_batch(config.patch_cases,pg);t=make_batch(config.patch_cases,pg)
 with torch.no_grad():
  co=m(c["leaf_phase"],c["private"]);ho=m(h["leaf_phase"],h["private"]);so=m(s["leaf_phase"],s["private"]);to=m(t["leaf_phase"],t["private"])
  modes={"intact":{"action_cosine":mean_phase_cosine(ho["action_phase"],h["action_phase"]),"action_accuracy":strict_phase_accuracy(ho["action_phase"],h["action_phase"]),"private_accuracy":private_acc(ho,h["private"])}}
  for i in range(4):
   o=m(h["leaf_phase"],h["private"],leaf_workspace_cut=i);modes[f"leaf_{i}_cut"]={"action_cosine":mean_phase_cosine(o["action_phase"],h["action_phase"]),"action_accuracy":strict_phase_accuracy(o["action_phase"],h["action_phase"]),"private_accuracy":private_acc(o,h["private"])}
  specs={"local_a_cut":{"local_a_override":torch.zeros_like(ho["local_a"])},"local_b_cut":{"local_b_override":torch.zeros_like(ho["local_b"])},"global_cut":{"global_override":torch.zeros_like(ho["global"])},"topdown_cut":{"topdown_cut":True}}
  for n,kw in specs.items():
   o=m(h["leaf_phase"],h["private"],**kw);modes[n]={"action_cosine":mean_phase_cosine(o["action_phase"],h["action_phase"]),"action_accuracy":strict_phase_accuracy(o["action_phase"],h["action_phase"]),"private_accuracy":private_acc(o,h["private"])}
  pa=m(s["leaf_phase"],s["private"],local_a_override=to["local_a"],local_b_override=so["local_b"]);eya=torch.remainder(t["u"]+s["v"],1.0);eta=phase(torch.remainder(s["values"]+eya[:,None],1.0))
  pb=m(s["leaf_phase"],s["private"],local_a_override=so["local_a"],local_b_override=to["local_b"]);eyb=torch.remainder(s["u"]+t["v"],1.0);etb=phase(torch.remainder(s["values"]+eyb[:,None],1.0))
  pz=m(s["leaf_phase"],s["private"],global_override=to["global"]);etz=phase(torch.remainder(s["values"]+t["y"][:,None],1.0))
 probes={"local_a_to_u":fit_linear_phase_probe(co["local_a"],c["u_phase"],ho["local_a"],h["u_phase"]),"local_b_to_v":fit_linear_phase_probe(co["local_b"],c["v_phase"],ho["local_b"],h["v_phase"]),"global_to_y":fit_linear_phase_probe(co["global"],c["y_phase"],ho["global"],h["y_phase"])}
 patches={"local_a":{"mean_cosine":mean_phase_cosine(pa["action_phase"],eta),"strict_accuracy":strict_phase_accuracy(pa["action_phase"],eta)},"local_b":{"mean_cosine":mean_phase_cosine(pb["action_phase"],etb),"strict_accuracy":strict_phase_accuracy(pb["action_phase"],etb)},"global":{"mean_cosine":mean_phase_cosine(pz["action_phase"],etz),"strict_accuracy":strict_phase_accuracy(pz["action_phase"],etz)}}
 return {"seed":int(seed),"local_dim":m.local_dim,"global_dim":m.global_dim,"parameter_count":m.parameter_count(),"modes":modes,"probes":probes,"patches":patches,"uses_intermediate_workspace_labels_for_training":False,"valence_model_present":False,"self_preservation_reward":0.0}
def evaluate_flat_model(m,seed,config=EvaluationConfig()):
 g=torch.Generator().manual_seed(int(seed)^0xF1A7E);b=make_batch(config.holdout_cases,g)
 with torch.no_grad():o=m(b["leaf_phase"])
 return {"action_cosine":mean_phase_cosine(o["action_phase"],b["action_phase"]),"action_accuracy":strict_phase_accuracy(o["action_phase"],b["action_phase"]),"parameter_count":m.parameter_count()}
def save_model(m,path,metadata):
 torch.save({"version":VERSION,"metadata":metadata,"state_dict":m.state_dict()},path);return hashlib.sha256(path.read_bytes()).hexdigest()
