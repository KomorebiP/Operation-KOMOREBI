"""Independent sampled causal assay for the interactive editor; not a new primary study."""
from causal_support import *
import time, platform
start=time.time();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
frame_path=ROOT/'app/frames.json';before=hashlib.sha256(frame_path.read_bytes()).hexdigest()
frames=json.loads(frame_path.read_text());N=256;seed=927711;spec=fixture_bank(N,seed)
world=torch.tensor([s['world'] for s in spec]);role=torch.tensor([s['roles'] for s in spec]).T
original=torch.tensor([pair_value(s) for s in spec]);delta=torch.tensor([1,2,3][0:1]*0) if False else (torch.arange(N)%3)+1
target=original^delta
prefix=torch.stack([torch.where((delta&1)>0,1,0),torch.where((delta&2)>0,2,0)],1)
rows=[];raw={};references=[]
with torch.no_grad():
 for lin in ['A','B']:
  m=load(lin);hs=source(m,spec);factual=program(m,hs,[0,0]);donor=program(m,hs,prefix);sham=program(m,hs,[1,1])
  fs=frames['lineages'][lin];std=[s['scales'] for s in fs['statistics']]
  for suffix in [[],[3]]:
   fv=original if not suffix else (original%2)*2+original//2
   tv=target if not suffix else (target%2)*2+target//2
   truth=torch.stack([tv,tv%2^(tv//2),tv^3,(tv==1).long()])
   facttruth=torch.stack([fv,fv%2^(fv//2),fv^3,(fv==1).long()])
   for method in ['none','J','PCA','interaction','random','complement','native','sham_J','J_agent0','J_agent1']:
    key='J' if method in ['none','complement','native','sham_J','J_agent0','J_agent1'] else method
    basis=[x[key] for x in fs['frames']]
    h=patch(factual,sham if method=='sham_J' else donor,basis,agent=method[-1] if method.startswith('J_agent') else 'both',
           mode=method if method in ['none','complement','native'] else 'project')
    h=m.base.silent(program(m,h,suffix))
    logits=read(m,h);pred=logits.argmax(-1)
    private=torch.stack([a.private(h[i]).argmax(-1) for i,a in enumerate(m.base.agents)])
    mem=memory(m,h,spec,'calibrated')
    contrast=facttruth!=truth
    row={'lineage':lin,'method':method,'suffix':suffix,'cases':N,'agent_views':2,
     'exact_donor_pair':float((pred[:,0]==tv).float().mean()),
     'consumer_donor_match':[float((pred[:,q]==truth[q]).float().mean()) for q in range(4)],
     'contrast_case_count_by_consumer':contrast.sum(-1).tolist(),
     'contrast_donor_match':[float((pred[:,q,contrast[q]]==truth[q,contrast[q]]).float().mean()) for q in range(4)],
     'factual_match':float((pred[:,0]==fv).float().mean()),
     'private_preservation':float((private==role).float().mean()),
     'all_eight_memory':float((mem==world[None]).all(-1).float().mean()),
     'memory_bit_accuracy':float((mem==world[None]).float().mean())}
    rows.append(row)
    raw[f'{lin}_{method}_suffix{len(suffix)}_pred']=pred.numpy();raw[f'{lin}_{method}_suffix{len(suffix)}_private']=private.numpy();raw[f'{lin}_{method}_suffix{len(suffix)}_memory']=mem.numpy()
    if not suffix:print(lin,method,round(row['exact_donor_pair'],4),round(row['all_eight_memory'],4),flush=True)
  # Numerical reference paths: native fork, arbitrary offsets, partial and unilateral edits.
  for i in range(12):
   sp=spec[i];hc=[x[i:i+1] for x in factual];hd=[x[i:i+1] for x in donor]
   for method,alpha,offsets,agent,suf in [('J',0,[0,0,0],'both',[]),('J',1,[0,0,0],'both',[]),
        ('J',.45,[.2,-.1,.3],'both',[3]),('J',1,[0,0,0],'0',[1]),('random',1,[0,0,0],'both',[]),
        ('complement',1,[0,0,0],'both',[]),('native',1,[0,0,0],'both',[2])]:
    basis=[x['J' if method in ['complement','native'] else method] for x in fs['frames']]
    edited=patch(hc,hd,basis,alpha,offsets,std if method=='J' else None,agent,
                 method if method in ['native','complement'] else 'project')
    end=m.base.silent(program(m,edited,suf))
    references.append({'lineage':lin,'spec_index':i,'target':int(target[i]),'method':method,'strength':alpha,'offsets':offsets,
                      'agent':agent,'suffix':suf,'edited':[x[0].tolist() for x in edited],
                      'state':[x[0].tolist() for x in end],'logits':read(m,end)[:,:,0].tolist()})
np.savez_compressed(ROOT/'checks/causal_raw.npz',world=world.numpy(),original=original.numpy(),target=target.numpy(),roles=role.numpy(),**raw)
(ROOT/'checks/causal_specs.json').write_text(json.dumps(spec,separators=(',',':')))
(ROOT/'checks/causal_reference.json').write_text(json.dumps(references,separators=(',',':')))
assert before==hashlib.sha256(frame_path.read_bytes()).hexdigest()
summary={'schema':'komorebi.causal-editor.sampled-assay.v1','status':'EXECUTED_DEVELOPMENT_INTERVENTIONS',
 'seed':seed,'cases_per_lineage':N,'lineages':2,'rows':rows,'frames_sha256':before,'frames_unchanged':True,
 'reference_paths':len(references),'runtime_seconds':time.time()-start,
 'scope':'Two previously selected frozen lineages. Fixed frame before fresh procedural bank, not untouched primary. No new training. Projected support NOT validated.',
 'software':{'torch':torch.__version__,'python':platform.python_version()}}
(ROOT/'checks/causal_assay.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
print('done',summary['runtime_seconds'])
