#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
def ok(name,cond):
 print(f"{name}={'PASS' if cond else 'FAIL'}")
 if not cond: raise SystemExit(1)
m=json.load(open(ROOT/'PSC_I.machine.json'));s=json.load(open(ROOT/'release/STATUS.json'));r=json.load(open(ROOT/'kir/PSC_I.records.v1.json'))
ok('ENTRYPOINT_VERSION',m['package_version']=='1.0.1')
ok('RECORD_COUNT',len(r['records'])==108 and len({x['stable_id'] for x in r['records']})==108)
# Dependency DAG acyclicity
BY={x['stable_id']:x for x in r['records']}
color={}
def dfs(u):
 color[u]=1
 for v in BY[u].get('dependencies',[]):
  if color.get(v)==1: return False
  if color.get(v,0)==0 and not dfs(v): return False
 color[u]=2; return True
ok('DEPENDENCY_ACYCLIC',all(color.get(u,0)!=0 or dfs(u) for u in BY))
ids={x['stable_id'] for x in r['records']}; ok('DEPENDENCIES_RESOLVE',all(d in ids for x in r['records'] for d in x.get('dependencies',[])))
ast=[json.loads(x) for x in open(ROOT/'kir/statement_ast.ndjson') if x.strip()]
ok('AST_COVERAGE',len(ast)==108 and {x['stable_id'] for x in ast}==ids)
acts=json.load(open(ROOT/'actions/action_registry.json'))
ok('ACTION_REGISTRY',acts.get('count')==len(acts.get('actions',[])) and all(a.get('records') for a in acts.get('actions',[])))
ok('SOURCE_HASH',hashlib.sha256((ROOT/'source/PSC_I_authoritative_source.tex').read_bytes()).hexdigest()==m['authoritative_source']['sha256'])
# API queries
for args in [['status'],['record','PSC-I-T-OPERATOR-RECONSTRUCTION'],['deps','PSC-I-T-BLOCK-MULTIPLICATION','--transitive'],['ast','PSC-I-T-BLOCK-INTERTWINING']]:
 p=subprocess.run([sys.executable,str(ROOT/'runtime/machine_api.py'),*args],capture_output=True,text=True); ok('API_'+args[0].upper(),p.returncode==0 and p.stdout.lstrip().startswith(('{','[')))
# Exact action smoke
p=subprocess.run([sys.executable,str(ROOT/'runtime/machine_api.py'),'execute','BLOCKIFY_OPERATOR',str(ROOT/'tests/blockify_input.json')],capture_output=True,text=True); ok('EXECUTE_BLOCKIFY',p.returncode==0 and 'blocks' in json.loads(p.stdout))
p=subprocess.run([sys.executable,str(ROOT/'runtime/machine_api.py'),'execute','VALIDATE_PACKET_SYSTEM',str(ROOT/'tests/packet_input.json')],capture_output=True,text=True); ok('EXECUTE_PACKET_VALIDATE',p.returncode==0 and json.loads(p.stdout).get('valid') is True)
# Transport gate: packet profile should either pass or give a structured block, never error
p=subprocess.run([sys.executable,str(ROOT/'runtime/machine_api.py'),'transport','PSC-I-T-BLOCK-MULTIPLICATION',str(ROOT/'profiles/packet_linear.json')],capture_output=True,text=True); tr=json.loads(p.stdout); ok('TRANSPORT_GATE_STRUCTURED',p.returncode==0 and tr.get('status') in {'PASS','BLOCKED'})
# Fresh exact finite fixture replay
p=subprocess.run([sys.executable,str(ROOT/'runtime/exact_fixture_suite.py')],capture_output=True,text=True)
ok('EXACT_FIXTURE_REPLAY',p.returncode==0 and 'EXACT_FINITE_FIXTURE_SUITE=PASS' in p.stdout)
print('PSC_I_MACHINE_V1_RELEASE_GATE=PASS')
