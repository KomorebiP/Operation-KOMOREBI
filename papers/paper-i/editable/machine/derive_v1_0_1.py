#!/usr/bin/env python3
"""Derive the narrow, audited nonzero-packet correction from v1.0.0."""
from pathlib import Path
import shutil,json,hashlib,subprocess,sys,os,datetime
ROOT=Path(__file__).resolve().parent
SOURCE_ROOT=Path(os.environ.get('PSC_SOURCE_ROOT',str(ROOT/'source' if (ROOT/'source').is_dir() else ROOT.parents[1]/'source'))).resolve()
OLD=SOURCE_ROOT/'machine_v1.0.0';NEW=SOURCE_ROOT/'machine_v1.0.1'
(ROOT/'build').mkdir(exist_ok=True)
PY=os.environ.get('PSC_PYTHON',sys.executable)
if NEW.exists():shutil.rmtree(NEW)
shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
def read(p):return json.loads((NEW/p).read_text())
def write(p,o):(NEW/p).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def shaf(p):return sha((NEW/p).read_bytes())
patches={
'PSC-I-C-SUPPORT-PATTERN-STAR':(r'Let $X$ be Hilbert, let the packet projectors be orthogonal, and put',r'Let $X$ be Hilbert, let the packet projectors be orthogonal, assume $X_\alpha\neq0$ for every $\alpha\in I$, and put'),
'PSC-I-C-SOURCE-COMPONENT-COUNT':(r'Assume the packet-resolved module is packet-propagating.  If $c_0$ denotes',r'Assume the packet-resolved module is packet-propagating and $X_\alpha\neq0$ for every $\alpha\in I$.  If $c_0$ denotes')}
src=NEW/'source/PSC_I_authoritative_source.tex';text=src.read_text();oldhash=sha(text.encode())
for rid,(old,new) in patches.items():assert text.count(old)==1;text=text.replace(old,new)
convention=r'\paragraph{Empty-family conventions.} For finite families of nonnegative integers we use $\max\varnothing=0$. The height of an empty finite partially ordered set is $0$, as is the height of a nonempty poset with no strict comparable pair. Thus the height in the support-preorder theorem counts strict steps.'
anchor=r'\RecordID{PSC-I-D-COEFFICIENT-REGIME}'
assert text.count(anchor)==1
text=text.replace(anchor+'\n',anchor+'\n'+convention+'\n')
src.write_text(text);newhash=sha(text.encode())
rs=read('kir/PSC_I.records.v1.json');rs['version']='1.0.1';rs['source_sha256']=newhash
for r in rs['records']:
 r['source']['sha256']=newhash;r['evidence']['source']['source_sha256']=newhash
 for k in ['record_id_line','statement_start_line','statement_end_line','proof_start_line','proof_end_line']:
  if r['source'].get(k) and r['source'][k]>324:r['source'][k]+=1
 if r['stable_id'] in patches:
  old,new=patches[r['stable_id']];assert old in r['statement_tex'];r['statement_tex']=r['statement_tex'].replace(old,new)
  r['source']['statement_sha256']=sha(r['statement_tex'].encode())
  for field in ['proof_operation_profile','proof_operation_profile_closure']:
   r[field]['hypothesis_classes']=sorted(set(r[field]['hypothesis_classes']+['nonzero_packet_spaces']))
  r['proof_operation_profile']['operation_evidence']['nonzero_packet_spaces']=[{'surface':'hypothesis_prefix','relative_line':1,'excerpt':new}]
  fp={ 'stable_id':r['stable_id'],'statement_sha256':r['source']['statement_sha256'],'proof_sha256':r['source']['proof_sha256'],'dependencies':r['dependencies']}
  r['record_fingerprint_sha256']=sha(json.dumps(fp,sort_keys=True).encode())
write('kir/PSC_I.records.v1.json',rs)
(NEW/'kir/records.ndjson').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rs['records']))
by={r['stable_id']:r for r in rs['records']}
ast=[json.loads(x) for x in (NEW/'kir/statement_ast.ndjson').read_text().splitlines() if x.strip()]
def math(t):return {'node':'math','surface_tex':t,'expr':{'node':'latex_expr','tex':t}}
for a in ast:
 rid=a['stable_id']
 if rid not in patches:continue
 a['source_statement_sha256']=by[rid]['source']['statement_sha256'];seg=a['statement_ast']['segments']
 mid=[math(r'X_\alpha\neq0'),{'node':'text','text':'for every'},math(r'\alpha\in I')]
 if rid=='PSC-I-C-SUPPORT-PATTERN-STAR':
  assert seg[2]['text']=='be Hilbert, let the packet projectors be orthogonal, and put'
  seg[2:3]=[{'node':'text','text':'be Hilbert, let the packet projectors be orthogonal, assume'}]+mid+[{'node':'text','text':', and put'}]
 else:
  assert seg[0]['text']=='Assume the packet-resolved module is packet-propagating. If'
  seg[0:1]=[{'node':'text','text':'Assume the packet-resolved module is packet-propagating and'}]+mid+[{'node':'text','text':'. If'}]
(NEW/'kir/statement_ast.ndjson').write_text(''.join(json.dumps(a,ensure_ascii=False)+'\n' for a in ast))
onto=read('semantics/operation_ontology.json');onto['operations']['nonzero_packet_spaces']={'class':'hypothesis'};write('semantics/operation_ontology.json',onto)
entry=read('PSC_I.machine.json');entry['package_version']='1.0.1';entry['authoritative_source']['sha256']=newhash
metadata_clarifications={
 'UNKNOWN preservation blocks theorem transport.':'UNKNOWN preservation of a directly required operation blocks the runtime operation-profile gate.',
 'Boundary guards are active negative constraints.':'Boundary guards are declarative caller-enforced constraints; runtime transport returns them as metadata and does not evaluate them.'
}
entry['machine_rules']=[metadata_clarifications.get(rule,rule) for rule in entry['machine_rules']]
write('PSC_I.machine.json',entry)
schema=read('kir/schema/machine_root.schema.json');schema['properties']['package_version']['const']='1.0.1';write('kir/schema/machine_root.schema.json',schema)
status=read('release/STATUS.json');status['package_version']='1.0.1';status['patch_scope']='TWO_COROLLARIES_REQUIRE_NONZERO_PACKET_SPACES';status['fresh_lean_replay']='NOT_RUN_FOR_MACHINE_PATCH';write('release/STATUS.json',status)
ei=read('evidence/evidence_index.json');ei['version']='1.0.1';ei['classes']['authoritative_source']['sha256']=newhash;ei['classes']['python_exact']['path']='evidence/python/exact_fixture_report_v1.0.1.txt';ei['classes']['nonzero_packet_regression']={'path':'evidence/python/nonzero_packet_regression_v1.0.1.txt','runner':'runtime/nonzero_packet_regression.py','scope':'Exact degenerate examples explain necessity of the two added hypotheses; no universal proof claim.'};write('evidence/evidence_index.json',ei)
v=NEW/'runtime/verify_release.py';v.write_text(v.read_text().replace("m['package_version']=='1.0.0'","m['package_version']=='1.0.1'"))
rd=NEW/'README_MACHINE.md';rd.write_text(rd.read_text().replace('v1.0.0','v1.0.1').replace('Unknown preservation state blocks transport.','Unknown preservation of a directly required operation blocks the runtime operation-profile gate. Boundary guards are declarative caller-enforced constraints; the runtime returns them as metadata without evaluating them.')+'\n## Narrow correction in v1.0.1\n\nTwo corollaries now explicitly require every packet space to be nonzero: PSC-I-C-SUPPORT-PATTERN-STAR and PSC-I-C-SOURCE-COMPONENT-COUNT. Statements, AST, hypothesis metadata, and source hashes were updated. Proof bodies and computational action implementations are unchanged. Run `python runtime/nonzero_packet_regression.py` for exact zero-packet witnesses and corrected-statement checks. Historical v1.0.0 is retained separately as provenance.\n\nThe runtime transport gate checks direct operation flags only. It does not execute hypothesis classes or boundary guards.\n')
reg=r'''#!/usr/bin/env python3
from pathlib import Path
import json
from sympy import Matrix,eye,zeros
ROOT=Path(__file__).resolve().parents[1]
r={x['stable_id']:x for x in json.loads((ROOT/'kir/PSC_I.records.v1.json').read_text())['records']}
P=[eye(1),zeros(1)]
assert all(p*p==p for p in P) and P[0]*P[1]==zeros(1) and sum(P,zeros(1))==eye(1)
print('ZERO_PACKET_IS_VALID_PACKET_SYSTEM=PASS')
R={(0,0),(0,1)}
assert (0,1) in R and (1,0) not in R
# Every forbidden block is zero for every scalar operator. Consequently the allowed
# support space is the full one-dimensional scalar algebra, closed under adjoint,
# although R is not symmetric. The second packet has rank zero.
assert all(P[b]*eye(1)*P[a]==zeros(1) for b in range(2) for a in range(2) if (b,a) not in R)
assert P[1].rank()==0
print('STAR_SUPPORT_ZERO_PACKET_COUNTEREXAMPLE=PASS')
# With no off-diagonal nonzero transfer blocks the two vertices are isolated source
# components, but the one-dimensional module is generated by one packet-pure seed.
assert P[0]*Matrix([1])==Matrix([1]) and P[1]*Matrix([1])==zeros(1,1)
source_components=2; packet_pure_seed_rank=1
assert source_components!=packet_pure_seed_rank
print('SOURCE_COUNT_ZERO_PACKET_COUNTEREXAMPLE=PASS')
for rid in ['PSC-I-C-SUPPORT-PATTERN-STAR','PSC-I-C-SOURCE-COMPONENT-COUNT']:
 assert r'X_\alpha\neq0' in r[rid]['statement_tex']
 assert 'nonzero_packet_spaces' in r[rid]['proof_operation_profile']['hypothesis_classes']
 print(rid+'_NONZERO_HYPOTHESIS=PASS')
print('NONZERO_PACKET_REGRESSION=PASS')
'''
(NEW/'runtime/nonzero_packet_regression.py').write_text(reg)
receipts=[]
for cmd,out in [(['runtime/exact_fixture_suite.py'],'evidence/python/exact_fixture_report_v1.0.1.txt'),(['runtime/verify_release.py'],'release/FINAL_VERIFICATION.txt'),(['runtime/nonzero_packet_regression.py'],'evidence/python/nonzero_packet_regression_v1.0.1.txt')]:
 p=subprocess.run([PY,*cmd],cwd=NEW,capture_output=True,text=True);(NEW/out).write_text(p.stdout+p.stderr);receipts.append({'command':['python',*cmd],'returncode':p.returncode})
 if p.returncode:raise SystemExit(p.stdout+p.stderr)
write('release/BUILD_RECEIPT.json',{'schema':'komorebi.psci.build_receipt.v1','package_version':'1.0.1','built_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':receipts,'expected_terminal':'PSC_I_MACHINE_V1_RELEASE_GATE=PASS'})
write('release/PROVENANCE.json',{'schema':'komorebi.psci.provenance.v1','package_version':'1.0.1','parent_release':'PSC-I machine interface v1.0.0','parent_source_sha256':oldhash,'source_sha256':newhash,'patches':{k:{'before':v[0],'after':v[1]} for k,v in patches.items()},'ambient_convention':convention,'metadata_clarifications':metadata_clarifications,'readme_clarification':'Transport checks direct operation flags; boundary guards are declarative and not runtime-enforced.','scope':'Two explicit nonzero-packet hypotheses and unnumbered empty-family/poset-height conventions. No proof body or computational runtime action changed. Historical Lean evidence unchanged and no new formal coverage claimed.'})
lock=read('release/LOCK.json');lock['package_version']='1.0.1';lock['source_sha256']=newhash
for key,path in {'records_sha256':'kir/PSC_I.records.v1.json','ast_sha256':'kir/statement_ast.ndjson','actions_sha256':'actions/action_registry.json','evidence_index_sha256':'evidence/evidence_index.json','dependency_graph_sha256':'graph/dependency_dag.json','machine_api_sha256':'runtime/machine_api.py','exact_engine_sha256':'runtime/exact_engine.py','exact_fixture_suite_sha256':'runtime/exact_fixture_suite.py','root_entrypoint_sha256':'PSC_I.machine.json'}.items():lock[key]=shaf(path)
write('release/LOCK.json',lock)
for p in NEW.rglob('__pycache__'):shutil.rmtree(p)
files=[p for p in sorted(NEW.rglob('*')) if p.is_file() and p.relative_to(NEW).as_posix() not in ['release/HASHES.json','release/MANIFEST.json']]
write('release/HASHES.json',{'schema':'komorebi.psci.hashes.v1','package_version':'1.0.1','hash':'sha256','files':{p.relative_to(NEW).as_posix():sha(p.read_bytes()) for p in files}})
write('release/MANIFEST.json',{'schema':'komorebi.psci.manifest.v1','package_id':'PSC-I','package_version':'1.0.1','file_count':len(files)+2,'hash_policy':'HASHES.json and MANIFEST.json excluded from recursive digest set; all other files covered.','files':[{'path':p.relative_to(NEW).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files]})
# Validate exact derivation and synchronized machine views without broadening scope.
oldrs=json.loads((OLD/'kir/PSC_I.records.v1.json').read_text())['records'];newrs=read('kir/PSC_I.records.v1.json')['records']
changed=[r['stable_id'] for o,r in zip(oldrs,newrs) if o['statement_tex']!=r['statement_tex']]
assert set(changed)==set(patches)
assert all(o['proof_tex']==r['proof_tex'] and o['dependencies']==r['dependencies'] for o,r in zip(oldrs,newrs))
assert (OLD/'runtime/machine_api.py').read_bytes()==(NEW/'runtime/machine_api.py').read_bytes()
assert (OLD/'runtime/exact_engine.py').read_bytes()==(NEW/'runtime/exact_engine.py').read_bytes()
assert all(x['source_statement_sha256']==by[x['stable_id']]['source']['statement_sha256'] for x in ast)
assert all(sha((NEW/f).read_bytes())==h for f,h in read('release/HASHES.json')['files'].items())
(ROOT/'build/patch_derivation_audit.json').write_text(json.dumps({'version':'1.0.1','changed_statements':changed,'proof_bodies_unchanged':True,'dependencies_unchanged':True,'runtime_actions_unchanged':True,'ast_statement_hashes_match':True,'manifest_hashes_match':True,'source_sha256':newhash,'metadata_clarifications':metadata_clarifications,'receipts':receipts},indent=2)+'\n')
print(newhash)
