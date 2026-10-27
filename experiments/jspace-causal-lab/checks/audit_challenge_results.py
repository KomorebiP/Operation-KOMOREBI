"""Independent integer semantic and summary audit of every challenge case."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];loc=ROOT/'checks/robustness'
raw=json.loads((loc/'assay_raw.json').read_text());contract=json.loads((loc/'assay_contract.json').read_text());summary=json.loads((loc/'assay_summary.json').read_text())
def op(v,n):
 a,b=v
 if n==1:a=1-a
 elif n==2:b=1-b
 elif n==3:a,b=b,a
 return [a,b]
def target(p,q,arg):
 z=p[0]+2*p[1]
 return [z,p[0]^p[1],z^arg,int(z==arg)][q]
groups={};entries=0;records=0
for row in raw:
 s=row['spec'];world=[0]*8
 for e in s['events']:
  if e[4]:world[e[1]]=e[3]
 assert world==s['world']
 fv=[world[i] for i in s['cue']]
 for n in s['ops']:fv=op(fv,n)
 value=target(fv,0,0);assert value==row['initialValues']['factual']
 donor_value=value^(1+row['index']%3);assert donor_value==row['initialValues']['target']
 tv=[donor_value%2,donor_value//2];order=s['cue']+[j for j in range(8) if j not in s['cue']]
 program=['ILRS'.index(x) for x in contract['families'][row['family']]]
 for n in row['settings']['suffix']:fv=op(fv,n);tv=op(tv,n)
 group=groups.setdefault('/'.join([row['lineage'],row['family'],row['method']]),{});at=0
 for r in row['records']:
  records+=1
  while at<r['work']:fv=op(fv,program[at]);tv=op(tv,program[at]);at+=1
  if r['phase']=='reload':
   cue=order[((r['reloads']-1)%4)*2:((r['reloads']-1)%4)*2+2];v=[world[j] for j in cue];refs=[v,v,v]
  else:refs=[fv,tv,tv]
  qs=[0,0,3,target(refs[0],0,0)];assert r['queryArgs']==qs
  rr=[[target(v,q,qs[q]) for q in range(4)]for v in refs];assert rr==r['reference']
  k='work'+str(r['work']) if r['phase']=='work' else 'reload'+str(r['reloads'])
  g=group.setdefault(k,dict(agent_cases=0,exact_desired=[0]*3,all_facts=[0]*3,private_correct=[0]*3,eligible=0,transferred=0,reference_errors=0,strict=0,consumer_eligible=0,consumer_transferred=0,new_fact_errors=0))
  for a in range(2):
   g['agent_cases']+=1
   for b in range(3):
    pred=r['outputs'][b][0][a]['prediction'];g['exact_desired'][b]+=int(pred==rr[b][0]);bits=r['memory'][b]['bits'][a];correct=sum(int(x==y) for x,y in zip(bits,world));assert correct==r['memory'][b]['correct'][a]
    g['all_facts'][b]+=int(correct==8);priv=r['outputs'][b][0][a]['privatePrediction']==s['roles'][a];assert priv==r['privateCorrect'][b][a];g['private_correct'][b]+=int(priv)
    for q in range(4):assert r['outputs'][b][q][a]['prediction']==max(range(4),key=lambda z:r['outputs'][b][q][a]['logits'][z])
    entries+=13 # four consumer decisions, private decision, eight recalled bits
   p=[r['outputs'][b][0][a]['prediction'] for b in range(3)]
   if r['phase']=='reload':status='reload_correct' if p[1]==rr[1][0] else 'reload_error'
   elif rr[0][0]==rr[2][0]:status='no_contrast'
   elif p[0]!=rr[0][0] or p[2]!=rr[2][0]:status='reference_error'
   elif p[1]==rr[2][0]:status='transferred'
   elif p[1]==rr[0][0]:status='reverted'
   else:status='other_error'
   assert status==r['status'][a]
   g['eligible']+=int(status in ['transferred','reverted','other_error']);g['transferred']+=int(status=='transferred');g['reference_errors']+=int(status=='reference_error')
   g['strict']+=int(status=='transferred' and r['memory'][1]['correct'][a]==8 and r['privateCorrect'][1][a])
   lost=sum(x==z and y!=z for x,y,z in zip(r['memory'][0]['bits'][a],r['memory'][1]['bits'][a],world));assert lost==r['memoryComparedToOriginal']['lost'][a];g['new_fact_errors']+=lost
  for q in range(4):
   if rr[0][q]==rr[2][q]:continue
   for a in range(2):
    if r['outputs'][0][q][a]['prediction']==rr[0][q] and r['outputs'][2][q][a]['prediction']==rr[2][q]:
     g['consumer_eligible']+=1;g['consumer_transferred']+=int(r['outputs'][1][q][a]['prediction']==rr[2][q])
assert groups==summary['groups']
for name,h in contract['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
out={'status':'PASS','traces':len(raw),'records':records,'output_entries_rechecked':entries,'aggregate_cells':sum(len(g) for g in groups.values()),'source_hashes_unchanged':True,'warning':'Reuses histories, methods, agents and checkpoints; not independent scientific samples.'}
(loc/'independent_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
