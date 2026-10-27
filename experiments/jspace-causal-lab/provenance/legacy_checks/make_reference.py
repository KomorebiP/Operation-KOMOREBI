"""Independent PyTorch reference for browser port; no neural training."""
from pathlib import Path
import sys,json,random,torch,platform,time,hashlib
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'recovered/Komorebi_Workspace_Incubator_v0_6'
sys.path.insert(0,str(SRC/'src'))
import access_repair as ar,working as wk
from types import SimpleNamespace
start=time.time();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
rng=random.Random(92762026);specs=[]
for i,L in enumerate([0,3,12,24,48,96,48,48,12,0,6,48]):
 world=[rng.randrange(2) for _ in range(8)];order=list(range(8));rng.shuffle(order)
 events=[[0,j,j,world[j],1,rng.randrange(2),rng.randrange(2)] for j in order]
 # Also validate fresh/stale event semantics, though UI initializes facts only.
 for k in range(2):events.append([rng.randrange(2),rng.randrange(8),rng.randrange(8),rng.randrange(2),k,rng.randrange(2),rng.randrange(2)])
 pat=[3,1,3,2] if i%2 else [1,2,1,2]
 ops=[pat[t%4] for t in range(L)] if i>=4 else [rng.randrange(4) for _ in range(L)]
 spec={'id':i,'events':events,'roles':[rng.randrange(4),rng.randrange(4)],'cue':rng.sample(range(8),2),'alias':rng.randrange(2),'ops':ops,'opAliases':[rng.randrange(2)for _ in range(L)],'mode':['intact']*1,'recalls':[{'cue':rng.sample(range(8),2),'alias':rng.randrange(2)}for _ in range(8 if i in (5,9) else 2)]}
 spec['mode']=['intact','intact','intact','intact','intact','intact','cut','cut_AtoB','cut_BtoA','intact','skip_exchange','intact'][i]
 specs.append(spec)

def tensor(x):return torch.tensor([x],dtype=torch.long)
def outputs(m,h):
 out=[]
 for q in range(4):
  arg=3 if q==2 else 1 if q==3 else 0;row=[]
  for j,a in enumerate(m.base.agents):
   logits=a.read(h[j],tensor(q),tensor(arg))[0];p=a.private(h[j])[0]
   row.append({'logits':logits.tolist(),'prediction':int(logits.argmax()),'privateLogits':p.tolist(),'privatePrediction':int(p.argmax())})
  out.append(row)
 return out
res=[]
with torch.no_grad():
 for lin in ['A','B']:
  for variant in ['parent','access','calibrated']:
   path=SRC/(f'inputs/v05_{lin}_random.pt' if variant=='parent' else f'runs/{lin}_{variant}/checkpoint.pt')
   m=ar.load(path)
   for s in specs:
    b=SimpleNamespace(events=tensor(s['events']),roles=tensor(s['roles']))
    h=m.base.encode(b);h=m.base.cue(h,tensor(s['cue']),tensor(s['alias']),delay=0)
    h=m.base.program(h,tensor(s['ops']),tensor(s['opAliases']));h=m.base.silent(h)
    phases=[{'name':'post_work','state':[x[0].tolist()for x in h],'outputs':outputs(m,h)}]
    for t,r in enumerate(s['recalls']):
     h=(m.legacy_retrieve if variant=='parent' else m.retrieve)(h,tensor(r['cue']),tensor(r['alias']),s['mode'])
     phases.append({'name':f'recall_{t}','state':[x[0].tolist()for x in h],'outputs':outputs(m,h)})
    res.append({'lineage':lin,'variant':variant,'specId':s['id'],'phases':phases})
obj={'schema':'komorebi.browser-port.reference.v1','seed':92762026,'torch':torch.__version__,'python':platform.python_version(),'seconds':time.time()-start,'specs':specs,'results':res}
(ROOT/'checks/pytorch_reference.json').write_text(json.dumps(obj,separators=(',',':')))
print(json.dumps({'runs':len(res),'seconds':obj['seconds']}))
