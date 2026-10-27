from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'checkpoint_v0.3.0' if (ROOT/'checkpoint_v0.3.0').exists() else ROOT.parent/'Paper_III_Continuation_v0.3.0'
OUT=Path(__file__).resolve().parents[1]/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=json.loads((BASE/'verification/AUDITED_OBJECT_IDENTITIES.json').read_text())['inputs']
matched=[];fail=[]
for row in records:
 f=BASE/row['source']
 if not f.is_file() or sha(f)!=row['source_sha256']:
  fail.append({'module':row['module'],'problem':'source hash mismatch'});continue
 for obj in row['artifacts']:
  rel=Path('checked_objects')/Path(row['module'].replace('.','/')).with_suffix('.olean')
  if obj.get('suffix') not in ['',None]:
   continue  # there are no extra artifacts in checked_objects; main .olean validated
  target=BASE/rel
  if not target.is_file(): fail.append({'module':row['module'],'problem':'missing .olean'});continue
  if sha(target)!=obj['sha256']:
   fail.append({'module':row['module'],'problem':'object SHA mismatch'});continue
  matched.append(row['module'])
owned=json.loads((BASE/'verification/OWNED_REPLAY_CORRESPONDENCE.json').read_text())
assert owned.get('replayed')==558 and owned.get('generated_runtime')==14
assert owned.get('logical_names_exactly_match')
assert owned.get('transitive_axioms')==['Classical.choice','Quot.sound','propext']
assert len(records)==12
assert set(matched)=={r['module'] for r in records},fail
assert len(matched)==12
# Static prohibited proof syntax scan in *current* production sources; comments excluded.
prod=BASE/'formal/current'
mods=json.loads((BASE/'coverage/PRODUCTION_MODULES.json').read_text())
assert len(mods)==12
imported=[]
for mod in mods:
 s=prod/(mod.replace('.','/')+'.lean')
 assert s.is_file(),s
 t=s.read_text()
 # basic strip block and line comments. This is an additional lexical audit, not a Lean proof.
 t=re.sub(r'/-(?:.|\n)*?-/', '', t)
 t=re.sub(r'--[^\n]*','',t)
 bad=re.findall(r'(?m)^\s*(?:sorry|admit|axiom|constant\s+\S+\s*:|unsafe\s+(?:def|theorem)|partial\s+def)\b',t)
 if bad:fail.append({'module':mod,'problem':'production forbidden token','matches':bad})
 imported.extend(re.findall(r'(?m)^import\s+([^\n]+)',t))
assert not any('MultilinearPacketJets' in s or 'BoundedPacketJetNorm' in s for s in imported)
assert not fail,fail
receipt={'schema':'paper_iii.inherited_formal_evidence_reauthentication/1','status':'PASS','source_object_pairs':len(matched),
 'matched_production_modules':matched,'logical_declarations_in_historical_replay':558,
 'separately_reviewed_generated_runtime_helpers':14,'recorded_allowed_axioms':owned['transitive_axioms'],
 'fresh_lean_compilation':False,'fresh_kernel_replay':False,'not_imported_section17_drafts':True,
 'static_scan_scope':'lexical gate after comment stripping; not kernel certification',
 'limits':'Validates current bytes against saved successful compiler receipts. This does not independently execute Lean or certify correctness of the English manuscript.'}
OUT.mkdir(exist_ok=True)
(OUT/'INHERITED_FORMAL_EVIDENCE_RECHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
