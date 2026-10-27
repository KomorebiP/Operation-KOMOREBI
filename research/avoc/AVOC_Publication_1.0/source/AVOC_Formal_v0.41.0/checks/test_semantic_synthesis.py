#!/usr/bin/env python3
"""Independent bitset oracle and controlled frozen/feedback comparison.
Runs the actual Lean implementation. Fixed complete three-input domain; not an LLM benchmark.
"""
from __future__ import annotations
import hashlib, itertools, json, os, statistics, subprocess, sys, time
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/v0.26.0/semantic_tests';OUT.mkdir(parents=True,exist_ok=True)
KIT=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))
ENV=os.environ.copy();ENV['LEAN_PATH']=':'.join(map(str,[ROOT/'.lake/build/lib/lean']+[p/'.lake/build/lib/lean' for p in (KIT/'workspace/.lake/packages').iterdir() if p.is_dir()]))
CMD=[str(KIT/'toolchain/bin/lean'),'--run','tools/SemanticSynthesisMain.lean']
PINS=[ROOT/'checks/semantic/protocol.json',Path(__file__).resolve()]+list((ROOT/'AVOC').glob('*Semantic*.lean'))+[ROOT/'AVOC/RecursiveSynthesis.lean',ROOT/'tools/SemanticSynthesisMain.lean']
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in PINS}
@lru_cache(None)
def bits(p):
 op=p[0]
 if op=='literal':return 255 if p[1] else 0
 if op=='variable':return (240,204,170)[p[1]]
 if op=='not':return 255^bits(p[1])
 a,b=bits(p[1]),bits(p[2])
 return {'and':a&b,'or':a|b,'xor':a^b}[op]
@lru_cache(None)
def nodes(p):return 1 if p[0] in ('literal','variable') else 1+sum(nodes(x) for x in p[1:])
def tup(x):return tuple(tup(v) if isinstance(v,list) else v for v in x)
def wire(x):return [wire(v) if isinstance(v,tuple) else v for v in x]
ATOMS=[('literal',False),('literal',True)]+[('variable',i) for i in range(3)]
def expand(xs):return xs+[('not',x) for x in xs]+[(op,a,b) for op in ('and','or','xor') for a in xs for b in xs]
def work(e,n,p):return {'emitted':e,'node_mass':n,'index_probes':p,'ast_visit_tariff':10*n,'probe_tariff':9*p,'charge':e+10*n+9*p}
def add(a,b):return work(a['emitted']+b['emitted'],a['node_mass']+b['node_mass'],a['index_probes']+b['index_probes'])
def indexed(xs):
 # Integer bitset evaluation + dictionary locations, rather than Lean list searches.
 reps=[];locations={};probes=0
 for p in xs:
  key=bits(p)
  if key in locations:
   i=locations[key];probes+=i+1
   if nodes(p)<nodes(reps[i]):reps[i]=p
  else:
   probes+=len(reps);locations[key]=len(reps);reps.append(p)
 return reps,work(len(xs),sum(map(nodes,xs)),probes)
@lru_cache(None)
def build(mode,d):
 raw=ATOMS;total=work(0,0,0);stages=[]
 for k in range(d+1):
  reps,w=indexed(raw);total=add(total,w);stages.append({'depth':k,'retained':len(reps),'work':w})
  if k<d:raw=expand(reps if mode=='feedback' else raw)
 return reps,total,stages

def reserve(count,m):return count+10*count*m+9*256*count

def paid(d,credit):
 if reserve(5,1)>credit:return None
 reps,total,stages=build('feedback',0)
 current=0
 for k in range(1,d+1):
  size=2*len(reps)+3*len(reps)**2
  if reserve(size,2**(k+1)-1)>credit-total['charge']:break
  reps,total,stages=build('feedback',k);current=k
 return current,reps,total,stages

def ref_for(key):
 if key==0:return ('literal',False)
 terms=[]
 for i in range(8):
  if key>>i&1:
   lits=[('variable',v) if (i>>(2-v))&1 else ('not',('variable',v)) for v in range(3)]
   terms.append(('and',('and',lits[0],lits[1]),lits[2]))
 p=terms[0]
 for q in terms[1:]:p=('or',p,q)
 return p
REFS=[ref_for(k) for k in range(256)]

def lean_batch(name,requests):
 inp=OUT/(name+'_requests.json');out=OUT/(name+'_stdout.jsonl');err=OUT/(name+'_stderr.txt')
 inp.write_text(json.dumps(requests,separators=(',',':')))
 t=time.monotonic();proc=subprocess.run(CMD[:3]+['--batch',str(inp)],cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
 elapsed=time.monotonic()-t;out.write_text(proc.stdout);err.write_text(proc.stderr)
 rec={'command':CMD[:3]+['--batch',str(inp)],'seconds':elapsed,'returncode':proc.returncode,
      'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'stdout_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
      'stderr_sha256':hashlib.sha256(err.read_bytes()).hexdigest()}
 (OUT/(name+'_run.json')).write_text(json.dumps(rec,indent=2))
 if proc.returncode:raise AssertionError(proc.stderr+proc.stdout[-2000:])
 replies=[json.loads(s) for s in proc.stdout.splitlines() if s.strip()]
 assert len(replies)==len(requests)
 return replies,rec

def check_build(actual,expected):
 reps,total,stages=expected
 assert actual['work']==total,(actual['work'],total)
 assert actual['stages']==stages
 es=actual['entries'];assert actual['retained']==len(reps)==len(es)
 assert len({tuple(e['bits']) for e in es})==len(es)<=256
 for e,p in zip(es,reps):
  assert tup(e['program'])==p
  assert e['nodes']==nodes(p)
  assert e['bits']==[bool(bits(p)>>i&1) for i in range(8)]

def check_queries(replies,reps,refs):
 assert len(replies)==len(refs)
 for out,r in zip(replies,refs):
  expected=r
  for p in reps:
   if bits(p)==bits(r) and nodes(p)<nodes(expected):expected=p
  assert tup(out['candidate'])==expected
  assert out['candidate_nodes']==nodes(expected)
  assert bits(tup(out['candidate']))==bits(r)
  assert out['exact_equivalence'] is True


def main():
 before=hashes();started=time.monotonic()
 arms=[('frozen',0),('feedback',0),('frozen',1),('feedback',1),('frozen',2),('feedback',2),('feedback',3)]
 replies,runs=lean_batch('builds',[['build',m,d,[wire(p) for p in REFS]] for m,d in arms])
 summary={'protocol_sha256':before['checks/semantic/protocol.json'],'builds':[], 'query_cases':0}
 for (m,d),out in zip(arms,replies):
  assert out['status']=='checked'
  oracle=build(m,d);check_build(out['build'],oracle);check_queries(out['queries'],oracle[0],REFS)
  summary['query_cases']+=len(REFS)
  summary['builds'].append({'mode':m,'depth':d,'retained':len(oracle[0]),'work':oracle[1]})
 for d in range(3):
  frozen={bits(p):nodes(p) for p in build('frozen',d)[0]}
  feedback={bits(p):nodes(p) for p in build('feedback',d)[0]}
  assert frozen==feedback
 assert len(build('feedback',3)[0])==256
 # A resource grid is fixed in the stored protocol, not selected after outcomes.
 credits=[0,100,10000,100000,1000000,10000000,100000000,1000000000]
 budgets=[(d,c) for d in range(4) for c in credits]
 smallrefs=[REFS[k] for k in (0,1,3,85,105,128,240,255)]
 outs,_=lean_batch('budgets',[['budget',d,c,[wire(p) for p in smallrefs]] for d,c in budgets])
 for (d,c),out in zip(budgets,outs):
  expected=paid(d,c)
  if expected is None:assert out['status']=='unfunded' and out['spent']==0
  else:
   reached,reps,w,stages=expected
   assert out['depth']==reached and out['spent']==w['charge']
   assert out['remaining']+out['spent']==c
   check_build(out['build'],(reps,w,stages));check_queries(out['queries'],reps,smallrefs)
 summary['budget_cases']=len(budgets)
 checkrequests=[['check',wire(REFS[i]),wire(REFS[j])] for i,j in [(i,i) for i in range(256)]+[(i,i^255) for i in range(256)]]
 outs,_=lean_batch('equivalence',checkrequests)
 for req,out in zip(checkrequests,outs):
  assert out['equivalent']==(bits(tup(req[1]))==bits(tup(req[2])))
 summary['equivalence_cases']=len(checkrequests)
 pair=('not',('or',('not',('variable',0)),('not',('variable',1))))
 cases=[(d,c,n) for d in range(3) for c in [0,100000,10000000] for n in [0,1,1000000]]
 outs,_=lean_batch('campaigns',[['campaign',wire(pair),d,c,n] for d,c,n in cases])
 for (d,c,n),out in zip(cases,outs):
  search=paid(d,c)
  if search is None:assert out['status']=='unfunded';continue
  reached,reps,w,stages=search;qfee=sum(8*(nodes(pair)+nodes(p)+1) for p in reps)
  if qfee>c-w['charge']:assert out['status']=='query_unfunded';continue
  candidate=pair
  for p in reps:
   if bits(p)==bits(pair) and nodes(p)<nodes(candidate):candidate=p
  remaining=c-w['charge']-qfee;evalfee=8*(nodes(pair)+nodes(candidate)+1)
  evalspent=evalfee if remaining>=evalfee else 0
  promoted=evalspent>0 and remaining>=evalfee+1 and n*(nodes(pair)-nodes(candidate))>=2
  active=candidate if promoted else pair;switch=int(promoted)
  total=w['charge']+qfee+evalspent+switch
  assert out['status']=='checked' and out['total_spent']==total<=c
  assert out['endpoint_net']==n*(nodes(pair)-nodes(active))-total
  assert tup(out['candidate'])==candidate and tup(out['active'])==active
  assert out['query_charge']==qfee and out['promotion_evaluation_charge']==evalspent
 summary['campaign_cases']=len(cases)
 invalid=[[],['build','feedback',4,[]],['build','frozen',3,[]],['build','bad',1,[]],
          ['budget',2,-1,[]],['budget',2,10**9+1,[]],['check',['variable',3],['literal',True]],
          ['check',['python','os.remove'],['literal',True]],['build','feedback',1,[['and',['literal',True]]]],
          ['campaign',wire(pair),1,10**9+1,1],['budget',0,0,[],'extra'],['build','feedback',0,[wire(pair)]*257]]
 outs,_=lean_batch('invalid',invalid)
 assert all(o['status']=='error' for o in outs)
 summary['invalid_wire_cases']=len(outs)
 # Timings are process-inclusive observations, not physical-cost theorems.
 timing=[]
 for i,m in enumerate(['frozen','feedback','feedback','frozen','frozen','feedback']):
  _,rec=lean_batch('timing_'+str(i),[['build',m,2,[]]])
  timing.append({'mode':m,'seconds':rec['seconds']})
 summary['timing_runs']=timing
 summary['median_seconds']={m:statistics.median(x['seconds'] for x in timing if x['mode']==m) for m in ['frozen','feedback']}
 summary['matched_cost_ratio']=build('frozen',2)[1]['charge']/build('feedback',2)[1]['charge']
 summary['raw_depth3_formula_only']=2*21845+3*21845**2
 summary['elapsed_seconds']=time.monotonic()-started
 summary['source_pins_before']=before;summary['source_pins_after']=hashes()
 assert summary['source_pins_before']==summary['source_pins_after']
 summary['passed']=True
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if not k.startswith('source_pins')},indent=2))
if __name__=='__main__':main()
