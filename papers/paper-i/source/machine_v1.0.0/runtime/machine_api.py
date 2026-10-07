#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECS=json.load(open(ROOT/'kir/PSC_I.records.v1.json'))['records']
BY={r['stable_id']:r for r in RECS}
AST={json.loads(x)['stable_id']:json.loads(x) for x in open(ROOT/'kir/statement_ast.ndjson') if x.strip()}
ACTIONS=json.load(open(ROOT/'actions/action_registry.json'))

def out(x): print(json.dumps(x,indent=2,sort_keys=True))
def closure(rid):
 seen=set(); stack=list(BY[rid].get('dependencies',[]))
 while stack:
  x=stack.pop()
  if x in seen or x not in BY: continue
  seen.add(x); stack += BY[x].get('dependencies',[])
 return sorted(seen)
def transport(rid,profile):
 r=BY[rid]; prof=json.load(open(profile)) if isinstance(profile,str) else profile
 states=prof.get('preserves',prof)
 required=(r.get('proof_operation_profile') or {}).get('action_required_operations',[])
 missing=[];unknown=[]
 for op in required:
  v=states.get(op,'UNKNOWN')
  if v in (True,'VERIFIED','PRESERVED'): continue
  if v in (False,'NOT_PRESERVED'): missing.append(op)
  else: unknown.append(op)
 status='PASS' if not missing and not unknown else 'BLOCKED'
 return {'record':rid,'status':status,'required_operations':required,'not_preserved':missing,'unknown':unknown,'boundary_guards':r.get('boundary_guards',[])}

def execute(action,payload):
 from exact_engine import validate_packet_system,analyze,blockify,reconstruct,compose_blocks,lower_intertwiner
 if action=='VALIDATE_PACKET_SYSTEM': return validate_packet_system(payload['projectors'])
 if action=='ANALYZE_PACKETS': return analyze(payload['projectors'],payload['vector'])
 if action=='BLOCKIFY_OPERATOR': return blockify(payload['projectors'],payload['operator'])
 if action=='RECONSTRUCT_OPERATOR': return reconstruct(payload['blocks'])
 if action=='COMPOSE_TRANSFER_BLOCKS': return compose_blocks(payload['projectors'],payload['S'],payload['T'])
 if action=='LOWER_INTERTWINER': return lower_intertwiner(payload['P'],payload['Q'],payload['T'],payload['S'],payload['U'])
 if action in ('CHECK_REALIZATION_PROFILE','TRANSPORT_THEOREM'):
  return transport(payload['record'],payload['profile'])
 raise SystemExit('unsupported runtime action: '+action)

def main():
 p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='cmd',required=True)
 sp.add_parser('status')
 q=sp.add_parser('record');q.add_argument('id')
 q=sp.add_parser('deps');q.add_argument('id');q.add_argument('--transitive',action='store_true')
 q=sp.add_parser('ast');q.add_argument('id')
 q=sp.add_parser('actions');q.add_argument('id')
 q=sp.add_parser('search');q.add_argument('text')
 q=sp.add_parser('transport');q.add_argument('id');q.add_argument('profile')
 q=sp.add_parser('execute');q.add_argument('action');q.add_argument('input')
 a=p.parse_args()
 if a.cmd=='status': return out(json.load(open(ROOT/'release/STATUS.json')))
 if a.cmd=='record': return out(BY[a.id])
 if a.cmd=='deps': return out({'record':a.id,'dependencies':closure(a.id) if a.transitive else BY[a.id].get('dependencies',[])})
 if a.cmd=='ast': return out(AST[a.id])
 if a.cmd=='actions': return out({'record':a.id,'actions':BY[a.id].get('machine_actions',[])})
 if a.cmd=='search':
  s=a.text.lower(); return out([{'stable_id':r['stable_id'],'title':r['title']} for r in RECS if s in (r['title']+' '+(r.get('statement_tex') or '')).lower()])
 if a.cmd=='transport': return out(transport(a.id,a.profile))
 if a.cmd=='execute': return out(execute(a.action,json.load(open(a.input))))
if __name__=='__main__': main()
