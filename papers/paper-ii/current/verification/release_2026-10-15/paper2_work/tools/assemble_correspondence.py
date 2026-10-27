#!/usr/bin/env python3
"""Bind current manuscript records to source-level branch maps; never certify release gates."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib,json,re,datetime
ROOT=Path(__file__).resolve().parents[2]
REL=ROOT/'release_package/Komorebi_Paper_II_Release_2026-10-15'
FORMAL=REL/'formal/current'
OUT=ROOT/'paper2_work/audit/current_correspondence.json'
HIST=REL/'formal/coverage/Paper_II_Expanded_Correspondence_v0.3.0.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
rel=lambda p:str(p.relative_to(ROOT))
read=lambda p:json.loads(p.read_text())
hist=read(HIST)
KINDS='definition|theorem|remark|corollary|proposition|example|standardfact|certificate'
ENV=re.compile(r'\\begin\{('+KINDS+r')\}(?:\[([^\]]*)\])?(.*?)\\end\{\1\}',re.S)
PROOF=re.compile(r'\\begin\{proof\}(?:\[[^\]]*\])?.*?\\end\{proof\}',re.S)
allblocks={};chapters={};allproofs=[];listings=[]
for file in hist['chapter_hashes']:
 p=REL/file;s=p.read_text();chapters[file]=sha(p.read_bytes());blocks=[]
 for m in ENV.finditer(s):
  proof=PROOF.search(s,m.end());nxt=ENV.search(s,m.end())
  if proof and nxt and proof.start()>nxt.start():proof=None
  body=m.group(3)
  blocks.append({'kind':m.group(1),'title_tex':m.group(2),'labels':re.findall(r'\\label\{([^{}]+)\}',body),'statement_tex':body,'statement_environment_tex':m.group(),'proof_tex':proof.group() if proof else None,'file':file,'file_sha256':chapters[file],'statement_body_sha256':sha(body.encode()),'statement_sha256':sha(m.group().encode()),'statement_environment_sha256':sha(m.group().encode()),'statement_start_line':s[:m.start()].count('\n')+1,'statement_end_line':s[:m.end()].count('\n')+1,'proof_sha256':sha(proof.group().encode()) if proof else None,'proof_start_line':s[:proof.start()].count('\n')+1 if proof else None,'proof_end_line':s[:proof.end()].count('\n')+1 if proof else None})
 allblocks[file]=blocks
 for m in PROOF.finditer(s):allproofs.append({'file':file,'start_line':s[:m.start()].count('\n')+1,'sha256':sha(m.group().encode()),'proof_tex':m.group()})
 for m in re.finditer(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}',s,re.S):listings.append({'file':file,'start_line':s[:m.start()].count('\n')+1,'sha256':sha(m.group().encode()),'listing_tex':m.group()})
# Lexical declaration inventory only: names are qualified using explicit namespace/section commands.
# Kernel ownership and declaration-existence validation remain a separate aggregate replay gate.
def clean_lean(s):
 out=[];i=0;depth=0;string=False
 while i<len(s):
  if depth:
   if s.startswith('/-',i):depth+=1;out.extend('  ');i+=2
   elif s.startswith('-/',i):depth-=1;out.extend('  ');i+=2
   else:out.append('\n' if s[i]=='\n' else ' ');i+=1
  elif string:
   if s[i]=='\\' and i+1<len(s):out.extend('  ');i+=2
   elif s[i]=='"':string=False;out.append(' ');i+=1
   else:out.append('\n' if s[i]=='\n' else ' ');i+=1
  elif s.startswith('/-',i):depth=1;out.extend('  ');i+=2
  elif s.startswith('--',i):
   j=s.find('\n',i);j=len(s) if j<0 else j;out.extend(' '*(j-i));i=j
  elif s[i]=='"':string=True;out.append(' ');i+=1
  else:out.append(s[i]);i+=1
 return ''.join(out)
index={}
for p in sorted(FORMAL.rglob('*.lean')):
 stack=[];ns=[];h=sha(p.read_bytes());module=str(p.relative_to(FORMAL).with_suffix('')).replace('/','.')
 for lineno,line in enumerate(clean_lean(p.read_text()).splitlines(),1):
  t=line.strip();m=re.match(r'namespace\s+(\S+)',t)
  if m:
   name=m.group(1);stack.append(('namespace',len(ns)));ns.extend(name.split('.'));continue
  if re.match(r'(?:noncomputable\s+)?section(?:\s|$)',t):stack.append(('section',len(ns)));continue
  if re.match(r'end(?:\s|$)',t):
   if stack:kind,n=stack.pop();ns=ns[:n]
   continue
  t=re.sub(r'^@\[[^\]]*\]\s*','',t)
  m=re.match(r'(?:(?:private|protected|noncomputable|unsafe|partial)\s+)*(theorem|lemma|def|abbrev|structure|inductive|class)\s+([^\s({:\[]+)',t)
  if m:
   name=m.group(2);fq=name[len('_root_.'):] if name.startswith('_root_.') else '.'.join(ns+[name]);index[fq]={'name':fq,'module':module,'source':rel(p),'source_sha256':h,'declaration_line':lineno,'declaration_kind':m.group(1),'validation':'lexically located; kernel name existence pending aggregate audit'}
resolution_notes=[]
def resolve(name):
 if name in index:return dict(index[name])
 candidates=[k for k in index if k.endswith('.'+name)]
 if not candidates:candidates=[k for k in index if k.split('.')[-1]==name.split('.')[-1]]
 if len(candidates)==1:
  fq=candidates[0]
  if not fq.endswith('.'+name):resolution_notes.append({'supplied':name,'resolved':fq,'reason':'unique declaration leaf; supplied namespace incomplete'})
  return dict(index[fq])
 raise ValueError(('unresolved or ambiguous declaration',name,candidates))
inputs={};branches={};evidence=defaultdict(list)
def loadmap(label,path):
 p=ROOT/path;d=read(p);inputs[label]={'path':rel(p),'sha256':sha(p.read_bytes())};branches[label]=d;return d

def put(label,branch,names,scope,status='constructed_endpoint_pending_release_gates',extra=None):
 evidence[label].append({'branch':branch,'mapping_input':inputs[branch], 'declarations':[resolve(n) for n in names], 'semantic_scope':scope,'working_status':status,**(extra or {})})
c=loadmap('coordinates','paper2_work/audit/coordinates_closure.json')
for r in c['new_coverage']:
 labels=re.findall(r'(?:thm|cor|prop):[\w-]+',r['claim'])
 if r['claim']=='coordinate Hilbert coherence':labels=['thm:coordinate_coherence']
 for label in labels:put(label,'coordinates',r['endpoint'],r['exact_scope'],extra={'construction':r['construction'],'independent_review':c.get('independent_review') if label=='cor:orthogonal_isometry' else 'Branch raw source review recorded; current exact statement acceptance pending root.'})
w=loadmap('weighted','paper2_work/weighted/COVERAGE.json')
wr=loadmap('weighted_semantic_review','paper2_work/audit/weighted_semantic_review.json')
for r in w['rows']:put(r['label'],'weighted',r['declarations'],r['scope'],extra={'independent_review':inputs['weighted_semantic_review'],'review_verdict':wr['primary_verdict']})
r=loadmap('resultant','paper2_work/audit/resultant_closure.json')
for label,names in r['claims'].items():
 names=[n.split(';')[0].strip() for n in names]
 valuation_closed=any(n.endswith('.resultant_projector_valuation_bound') for n in names)
 put(label,'resultant',names,r['semantics'],'partial_endpoint_open_bridge' if label=='cor:resultant_bound' and not valuation_closed else 'constructed_endpoint_pending_release_gates',{'remaining':r['remaining']})
d=loadmap('defects_models','paper2_work/audit/defects_models_closure.json')
loadmap('defects_models_promotion','paper2_work/audit/defects_models_promotion.json')
for r in d['claims']:
 opened=r['paper'] in ['thm:holomorphic_defect','cor:exact_compatibility']
 put(r['paper'],'defects_models',[x.strip() for x in r['endpoint'].split(';')],r['scope'],'partial_endpoint_open_bridge' if opened else 'constructed_endpoint_pending_release_gates',{'branch_status':r['status'],'open_bridges':d['open_bridges'] if opened else []})
t=loadmap('transfer','paper2_work/audit/transfer_closure.json')
for r in t['manuscript_mapping']:put(r['label'],'transfer',r['declarations'],t['semantic_contract'],extra={'independent_review':t['independent_review'],'remaining':t['remaining']})
if (ROOT/'paper2_work/contour_bridge/ACCEPTED_MODULES.json').exists():
 loadmap('contour_bridge','paper2_work/contour_bridge/ACCEPTED_MODULES.json')
 for label in ['thm:holomorphic_defect','cor:exact_compatibility']:
  put(label,'contour_bridge',[
   'Komorebi.PaperII.ReleaseArcLength.unitIntervalPath_lipschitz',
   'Komorebi.PaperII.ReleaseArcLength.unitIntervalPath_variation',
   'Komorebi.PaperII.ReleaseRectifiable.integral_coordinateVelocity',
   'Komorebi.PaperII.ReleaseRectifiable.cycleOfAbsolutelyContinuous',
   'Komorebi.PaperII.ReleaseRectifiableCycle.cycleOfRectifiable',
   'Komorebi.PaperII.ReleaseRectifiableCycle.curve_cycleOfRectifiable',
   'Komorebi.PaperII.ReleaseRectifiableCycle.trace_cycleOfRectifiable',
   'Komorebi.PaperII.ReleaseRectifiableCycle.variation_curve_cycleOfRectifiable'],
   'Every supplied finite continuous closed rectifiable curve family constructs an actual integral-velocity cycle through arclength and absolute continuity; exact reconstructed trace and variation are proved. Geometric length equals integrated speed, Riemann–Stieltjes reparametrization invariance, and canonical HFC identification remain open.',
   'partial_endpoint_open_bridge')
# Optional late branch maps conform to a simple rows list with label/declarations/scope.
for branch in ['arithmetic','smith']:
 path=ROOT/f'paper2_work/audit/{branch}_closure.json'
 if path.exists():
  m=loadmap(branch,rel(path))
  rows=m.get('correspondence_rows')
  if rows is None and branch=='smith':
   rows=[{'label':label,'declarations':r['declarations'],'scope':r['exact_scope'],'original_claim':r} for r in m['claims'] for label in re.findall(r'(?:thm|cor|prop):[\w-]+',r['manuscript'])]
  if rows is None:raise ValueError(f'{branch} closure needs correspondence_rows adapter')
  for r in rows:put(r['label'],branch,r['declarations'],r['scope'],r.get('working_status','constructed_endpoint_pending_release_gates'),{'branch_record':r})
historical_current_review={}
hp=ROOT/'paper2_work/audit/historical_matches_independent_review.json'
if hp.exists():
 hr=loadmap('historical_current_review',rel(hp))
 for source,digest in hr['source_sha256'].items():
  if sha((ROOT/source).read_bytes())!=digest:raise ValueError(('historical review source changed',source))
 for r in hr['records']:
  if r['current_uncovered_branch'] is not None:raise ValueError(('historical review has uncovered branch',r['record_id']))
  historical_current_review[r['record_id']]=r
  put(r['record_id'],'historical_current_review',r['decisive_endpoints'],r['proof_scope_analysis'],extra={'independent_review':inputs['historical_current_review'],'review_verdict':r['current_scope_verdict'],'certificate_analysis':r['certificate_analysis'],'historical_scope_limit':r['historical_scope_limit'],'reviewed_statement_sha256':r['statement_sha256'],'reviewed_proof_sha256':r['proof_sha256']})
review_inputs={}
for p in sorted((ROOT/'paper2_work/audit').glob('*independent_review.json')):
 review_inputs[p.stem]={'path':rel(p),'sha256':sha(p.read_bytes()),'review':read(p)}
module_bindings=[]
for branch,m in branches.items():
 if isinstance(m,list):rows=m
 elif isinstance(m,dict):rows=m.get('modules',m.get('accepted_modules',m.get('checks',[])))
 else:continue
 for row in rows:
  if not isinstance(row,dict) or not row.get('module'):continue
  module=row['module']
  if not module.startswith('KomorebiVerification.'):module='KomorebiVerification.PaperII.'+module
  p=FORMAL/Path(*module.split('.')).with_suffix('.lean')
  expected=row.get('current_sha256',row.get('promoted_sha256',row.get('production_sha256',row.get('sha256'))))
  if expected is None:continue
  actual=sha(p.read_bytes())
  if actual!=expected:raise ValueError(('stale promoted source in branch map',branch,module,expected,actual))
  binding={'branch':branch,'module':module,'current_source':rel(p),'current_source_sha256':actual,'branch_source_identity_verified':True,'aggregate_replay':'pending'}
  receipt=row.get('receipt',row.get('draft_receipt',row.get('strict_check')))
  if receipt:
   rp=Path(receipt);rp=rp if rp.is_absolute() else ROOT/rp
   rd=read(rp);rh=sha(rp.read_bytes())
   if rd.get('status')!='PASS':raise ValueError(('branch receipt is not PASS',branch,str(rp)))
   if row.get('receipt_sha256',row.get('strict_check_sha256',rh))!=rh:raise ValueError(('branch receipt hash drift',str(rp)))
   expected_draft=row.get('checked_draft_sha256',row.get('draft_sha256'))
   if expected_draft is not None and rd.get('source_sha256')!=expected_draft:raise ValueError(('draft receipt/source mismatch',str(rp)))
   binding.update(strict_receipt=rel(rp),strict_receipt_sha256=rh,checked_source_sha256=rd.get('source_sha256'),current_source_is_exact_checked_source=rd.get('source_sha256')==actual,promotion_note=row.get('promotion_change',row.get('promotion',row.get('adaptation','Byte identity checked above where applicable.'))))
  module_bindings.append(binding)
records=[];used=set();ordinal=defaultdict(int)
for old in hist['records']:
 blocks=allblocks[old['file']];labels=set(old.get('labels',[]))
 if labels:candidates=[(i,b) for i,b in enumerate(blocks) if labels.intersection(b['labels'])]
 else:
  key=(old['file'],old['kind']);n=ordinal[key];ordinal[key]+=1
  candidates=[(i,b) for i,b in enumerate(blocks) if b['kind']==old['kind'] and not b['labels']][n:n+1]
 if len(candidates)!=1:raise ValueError(('record matching failed',old['record_id'],len(candidates)))
 i,cur=candidates[0];key=(old['file'],i)
 if key in used:raise ValueError(('reused block',key))
 used.add(key)
 if cur['kind']!=old['kind']:raise ValueError(('kind drift',old['record_id']))
 if old['record_id'] in historical_current_review:
  review=historical_current_review[old['record_id']]
  if review['statement_sha256']!=cur['statement_sha256'] or review['proof_sha256']!=cur['proof_sha256']:
   raise ValueError(('historical semantic review statement/proof drift',old['record_id']))
 prooflevel=old['kind'] in ['theorem','corollary','proposition']
 ev=evidence.get(old['record_id'],[])
 baseline=[]
 for target in old.get('source_targets',[]):baseline.append(resolve(target))
 if not prooflevel:status='supporting_record_not_in_proof_denominator'
 elif any(e['working_status']=='partial_endpoint_open_bridge' and not any(e['branch'] in x.get('branch_record',{}).get('supersedes_partial_branches',[]) for x in ev) for e in ev):status='partial_endpoint_open_bridge'
 elif ev:status='constructed_endpoint_pending_release_gates'
 elif old['status'] in ['whole_statement_source_match','kernel_checked_constructive_endpoint']:status='historical_match_pending_current_review'
 else:status='unassembled_pending_branch'
 records.append({'record_id':old['record_id'],'kind':old['kind'],'proof_level':prooflevel,'historical_record':old,'current_source':cur,'statement_changed_since_historical':cur['statement_sha256']!=old['statement_sha256'],'historical_targets_located_in_current_source':baseline,'current_evidence':ev,'working_status':status,'aggregate_replay':'pending','current_exact_semantic_acceptance':'pending root review; branch reviews are identified separately'})
if len(used)!=sum(map(len,allblocks.values())):raise ValueError(('unmapped current blocks',len(used),sum(map(len,allblocks.values()))))
assert len(records)==81 and sum(r['proof_level'] for r in records)==53
counts=Counter(r['working_status'] for r in records if r['proof_level'])
assert sorted((r['current_source']['file'],r['current_source']['proof_sha256']) for r in records if r['current_source']['proof_sha256'])==sorted((r['file'],r['sha256']) for r in allproofs)
frozen_binding=None
fp=ROOT/'paper2_work/release_modules.json'
if fp.exists():
 frozen=read(fp);by={r['module']:r['source_sha256'] for r in frozen}
 if not all(sha((FORMAL/r['source']).read_bytes())==r['source_sha256'] for r in frozen):raise ValueError('Current source differs from frozen source manifest')
 targets=[x for r in records for x in r['historical_targets_located_in_current_source']]+[x for r in records for e in r['current_evidence'] for x in e['declarations']]
 if not all(by[x['module']]==x['source_sha256'] for x in targets):raise ValueError('Map target source differs from frozen source manifest')
 frozen_binding={'manifest':rel(fp),'manifest_sha256':sha(fp.read_bytes()),'module_count':len(frozen),'all_manifest_sources_match_current':True,'all_target_sources_match_manifest':True,'unique_mapped_declarations':len({x['name'] for x in targets}),'status':'SOURCE_IDENTITY_BOUND; compilation and kernel replay are separate gates'}
result={'schema':'paper-ii-current-correspondence/1','status':'WORKING_NOT_RELEASE_ACCEPTED','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historical_input':{'path':rel(HIST),'sha256':sha(HIST.read_bytes()),'version':hist['version'],'checkpoint':hist['checkpoint'],'status_definitions':hist['status_definitions'],'counts':hist['counts']},'scope':'All original 81 records and 53 proof-level items retained. Current raw statement and proof hashes bind the traditional manuscript. Source-level branch closure mappings and isolated strict receipts do not certify current whole-release proof coverage.','status_definitions':{'constructed_endpoint_pending_release_gates':'A branch closure maps a constructed endpoint in current source; aggregate exact-source replay and current statement semantic acceptance remain pending.','historical_match_pending_current_review':'Historical whole-statement/source match retained with current located names; no automatic current semantic acceptance.','partial_endpoint_open_bridge':'Current endpoint proves an explicitly restricted or unassembled part; named manuscript bridge remains open.','unassembled_pending_branch':'Historical incomplete status remains; no complete current branch map received.','supporting_record_not_in_proof_denominator':'Definition, remark, example, standard fact or certificate kept outside the 53 proof-level denominator.'},'record_count':len(records),'proof_level_count':53,'working_proof_counts':dict(counts),'current_chapter_sha256':chapters,'explicit_proof_bodies':allproofs,'algorithm_listings':listings,'branch_inputs':inputs,'branch_metadata':branches,'verified_branch_module_bindings':module_bindings,'independent_review_inputs':review_inputs,'declaration_resolution_notes':resolution_notes,'records':records,'release_gates':{'exact_source_aggregate_compile':'PENDING_SOURCE_FREEZE','owned_kernel_type_body_replay':'PENDING','standard_axiom_and_runtime_helper_closure':'PENDING','current_manuscript_semantic_acceptance':'PENDING_ROOT_REVIEW'},'known_open_bridge_labels':['thm:holomorphic_defect','cor:exact_compatibility'],'hash_convention':'SHA256 over exact UTF-8 raw text; statement_sha256 and statement_environment_sha256 include the full environment and title, matching the historical convention; statement_body_sha256 covers only interior text. Proof hashes include proof environment. No whitespace normalization.','extractor':{'path':rel(Path(__file__)),'sha256':sha(Path(__file__).read_bytes())}}
result['frozen_formal_binding']=frozen_binding
ap=ROOT/'paper2_work/audit/current_semantic_acceptance.json'
if ap.exists():
 approval=read(ap);accepted={r['record_id']:r for r in approval['records']}
 if frozen_binding is None or approval['frozen_manifest_sha256']!=frozen_binding['manifest_sha256']:raise ValueError('Semantic approval formal identity differs')
 for r in result['records']:
  if not r['proof_level']:continue
  a=accepted[r['record_id']]
  names=sorted({x['name'] for x in r['historical_targets_located_in_current_source']}|{x['name'] for e in r['current_evidence'] for x in e['declarations']})
  if a['statement_sha256']!=r['current_source']['statement_sha256'] or a['proof_sha256']!=r['current_source']['proof_sha256'] or a['mapped_declaration_names']!=names:raise ValueError(('Semantic approval statement/proof/name identity differs',r['record_id']))
  r['current_exact_semantic_acceptance']=a['semantic_status']
 result['semantic_acceptance_binding']={'path':rel(ap),'sha256':sha(ap.read_bytes()),'complete_scopes':51,'partial_scopes':2,'kernel_gates':'PENDING'}
 result['release_gates']['current_manuscript_semantic_acceptance']='51_COMPLETE_SCOPES_ACCEPTED; 2_ANALYTIC_SCOPES_PARTIAL'
if frozen_binding:result['release_gates']['exact_source_aggregate_compile']='FROZEN; FINAL_VERIFICATION_PENDING'
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'output':rel(OUT),'sha256':sha(OUT.read_bytes()),'records':len(records),'proof_level':53,'proof_bodies':len(allproofs),'listings':len(listings),'counts':dict(counts),'declarations':len({d['name'] for r in records for e in r['current_evidence'] for d in e['declarations']}),'resolution_notes':resolution_notes},indent=2))
