from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
import argparse
ap=argparse.ArgumentParser(description="Integrate reviewed .19 sources and mappings; cumulative execution is recorded separately.")
ap.add_argument("claims",type=Path)
ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
ap.add_argument("--parent",type=Path,required=True)
ap.add_argument("--release",choices=["0.19.0","1.0.0"],default="0.19.0")
ap.add_argument("--parent-sha256",default="fd3ad2df1431eb0e92af144a2f8408ed9d2d7f0ecb10dd2540ef41fe638809eb")
args=ap.parse_args()
ROOT=args.root.resolve()
PARENT=args.parent.resolve()
PARENT_SHA=args.parent_sha256
PREFIX='Large_Signal_Model/Lean/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writej(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
require=lambda p,m: None if p else (_ for _ in ()).throw(ValueError(m))
require(sha(PARENT)==PARENT_SHA,'Parent archive changed')
z=zipfile.ZipFile(PARENT);cfg=json.loads(args.claims.read_text());pc=json.loads(z.read(PREFIX+'RELEASE_COUNTS.json'))
require(set(cfg['claims']) <= {str(n) for n in range(1,88)},'Invalid proposition ID')
parent_coverage=json.loads(z.read(PREFIX+'COVERAGE.json'))
require(set(cfg['claims']) <= {str(e['proposition']) for e in parent_coverage['entries'] if e['status']!='complete'},'Reviewed inherited complete mappings must remain unchanged')
require(all(c.get('status','complete') in {'complete','partial'} for c in cfg['claims'].values()),'Invalid accepted status')
require(cfg.get('accepted_source_sha256')=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in cfg['modules']},'Accepted raw-source hashes missing or stale')
require(bool(cfg.get('review_records')),'Missing source correspondence reviews')
if args.release=='1.0.0':
 predicted={e['proposition']:e['status'] for e in parent_coverage['entries']}
 predicted.update({int(n):c.get('status','complete') for n,c in cfg['claims'].items()})
 require(all(status=='complete' for status in predicted.values()),'Release1.0 requires all87 registered mappings complete')
for rel,h in cfg['review_records'].items():require(sha(ROOT/rel)==h,'Changed acceptance review '+rel)
base_modules=re.findall(r'^import KomorebiLSM\.(\w+)$',z.read(PREFIX+'KomorebiLSM.lean').decode(),re.M)
require(len(base_modules)==pc['proof_modules']==155,'Wrong .18 baseline module list')
# Retain inherited import order; append every new source in dependency order.
new_set={p.stem for p in (ROOT/'KomorebiLSM').glob('*.lean')}-set(base_modules)
require(set(cfg['modules'])==new_set,'Reviewed new-module inventory differs from active sources')
new_order=[];seen=set(base_modules);visiting=set()
def visit(m):
 if m in seen:return
 require(m not in visiting,'Cyclic project imports: '+m)
 require(m in new_set,'Missing project dependency: '+m)
 visiting.add(m)
 source=(ROOT/'KomorebiLSM'/f'{m}.lean').read_text()
 for dep in re.findall(r'^import KomorebiLSM\.(\w+)\s*$',source,re.M):visit(dep)
 visiting.remove(m);seen.add(m);new_order.append(m)
for m in sorted(new_set):visit(m)
cfg['modules']=new_order
modules=base_modules+new_order
require(len(set(modules))==len(modules),'Duplicate import')
require(set(modules)=={p.stem for p in (ROOT/'KomorebiLSM').glob('*.lean')},'Active module omission')
for m in base_modules:require((ROOT/'KomorebiLSM'/f'{m}.lean').read_bytes()==z.read(PREFIX+f'KomorebiLSM/{m}.lean'),'Changed inherited proof '+m)
for name in ['README.md','AUDIT.md','LEAN_GUIDE.md','CONTINUE_HERE.md','PROGRESS.md','PROGRESS.json','PROGRESS_LEDGER.md','ROADMAP_1.0.md','ROADMAP_1.0.json','PUBLICATION_STATUS.md','CURRENT_CHECKPOINT.json','scripts/check_metadata.py','scripts/verify.py','COVERAGE.json','COVERAGE.md','RELEASE_COUNTS.json','SOURCE_LINEAGE.json','CURRENT_STATUS.json']:
 (ROOT/'history').mkdir(parents=True,exist_ok=True)
 (ROOT/'history'/('PREDECESSOR_0.18.0_'+name.replace('/','_'))).write_bytes(z.read(PREFIX+name))
snapshot=ROOT/'history/PREDECESSOR_0.18.0_Source_Snapshot.zip'
with zipfile.ZipFile(snapshot,'w',zipfile.ZIP_DEFLATED) as out:
 for name in z.namelist():
  if name.startswith(PREFIX) and not name.endswith(('/','.zip')):out.writestr(name,z.read(name))
(ROOT/'KomorebiLSM.lean').write_text(''.join(f'import KomorebiLSM.{m}\n' for m in modules))
v=ROOT/'scripts/verify.py';t=v.read_text();t=re.sub(r'MODULES = \[.*?\]\nEXPECTED_LEAN',f'MODULES = {modules!r}\nEXPECTED_LEAN',t,flags=re.S);t=t.replace("'release':'0.18.0'","'release':'0.19.0'");v.write_text(t)
p=ROOT/'lakefile.toml';p.write_text(re.sub(r'version = "[^"]+"','version = "0.19.0"',p.read_text(),count=1))
subprocess.run([sys.executable,str(ROOT/'scripts/build_inventory.py'),'--write'],check=True)
decls=json.loads((ROOT/'DECLARATIONS.json').read_text());by={d['name']:d for d in decls}
cover=json.loads(z.read(PREFIX+'COVERAGE.json'))
for e in cover['entries']:
 c=cfg['claims'].get(str(e['proposition']))
 if c:
  require(all(n in by for n in c['endpoints']),'Missing accepted endpoint')
  require(set(c['modules']) <= set(modules),'Accepted mapping includes an unavailable module')
  require(all(by[n]['module'] in c['modules'] for n in c['endpoints']),'Endpoint outside mapped modules')
  e.update(status=c.get('status','complete'),scope=c['scope'],lean_targets=[{**d,'source_sha256':sha(ROOT/d['file'])} for d in decls if d['module'] in c['modules']])
  require(bool(e['lean_targets']),'Empty mapping')
complete=[e['proposition'] for e in cover['entries'] if e['status']=='complete'];partial=[e['proposition'] for e in cover['entries'] if e['status']=='partial'];unformal=[e['proposition'] for e in cover['entries'] if e['status']=='not_formalized'];unfinished=sorted(partial+unformal)
cover.update(formalization_version='0.19.0',complete=complete,partial=partial,not_formalized_count=len(unformal));writej(ROOT/'COVERAGE.json',cover)
road=json.loads(z.read(PREFIX+'ROADMAP_1.0.json'));road.update(release='0.19.0',completed=complete,partial=partial,unformalized=unformal,unformalized_count=len(unformal),remaining_count=len(unfinished),remaining_count_semantics='All unfinished mappings, including partial mappings.')
for track in road['tracks']:track['propositions']=[n for n in track['propositions'] if n in unfinished]
writej(ROOT/'ROADMAP_1.0.json',road)
lin=json.loads(z.read(PREFIX+'SOURCE_LINEAGE.json'));lin.update(formalization_version='0.19.0',predecessor_archive={'path':snapshot.relative_to(ROOT).as_posix(),'sha256':sha(snapshot),'bytes':snapshot.stat().st_size,'kind':'source_snapshot_without_nested_archives'},inherited_proof_files={f'KomorebiLSM/{m}.lean':sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in base_modules},inherited_control_files={n[len(PREFIX):]:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith(PREFIX+'negative_controls/') and n.endswith('.lean')},parent_delivered_archive={'filename':PARENT.name,'sha256':PARENT_SHA})
require((ROOT/'source/FOUNDATIONS_REVIEWED.md').is_file(),'Missing exact current reviewed manuscript source')
lin['source_files']['FOUNDATIONS_REVIEWED.md']=sha(ROOT/'source/FOUNDATIONS_REVIEWED.md')
repair_manifest=ROOT/'history/control_repairs/CONTROL_REPAIR_LINEAGE.json'
if repair_manifest.is_file():
 repair_data=json.loads(repair_manifest.read_text());lin['inherited_control_repairs']={}
 for e in repair_data['repairs']:
  name=e['control'];require(lin['inherited_control_files'].get(name)==e['before_sha256'],'Repair original differs from inherited control')
  require(sha(ROOT/name)==e['after_sha256'],'Active repaired control hash differs')
  lin['inherited_control_repairs'][name]={'original_sha256':e['before_sha256'],'active_sha256':e['after_sha256'],'preserved_original':e['preserved_original'],'preserved_repaired':e['preserved_repaired'],'reason':e['reason'],'clean_receipt':e['clean_receipt'],'clean_receipt_sha256':e['clean_receipt_sha256']}
 lin['control_repair_manifest']={'path':repair_manifest.relative_to(ROOT).as_posix(),'sha256':sha(repair_manifest),'total_inherited':len(lin['inherited_control_files']),'unchanged':len(lin['inherited_control_files'])-len(lin['inherited_control_repairs']),'repaired':len(lin['inherited_control_repairs'])}
writej(ROOT/'SOURCE_LINEAGE.json',lin)
nt=sum(d['kind']=='theorem' for d in decls);nex=sum(d['kind']=='theorem' and(d['module']=='Examples' or bool(re.fullmatch(r'Block\d+.*Examples',d['module']))) for d in decls);nc=len(list((ROOT/'negative_controls').glob('*.lean')))
counts={'release':'0.19.0','proof_modules':len(modules),'named_declarations':len(decls),'named_theorems':nt,'example_theorems':nex,'supporting_theorems':nt-nex,'new_theorems':nt-pc['named_theorems'],'new_example_theorems':nex-pc['example_theorems'],'complete_propositions':len(complete),'partial_propositions':len(partial),'unformalized_propositions':len(unformal),'negative_controls':nc};writej(ROOT/'RELEASE_COUNTS.json',counts)
cp={'checkpoint':'LSM-0.19.0','parent_archive_sha256':PARENT_SHA,'target':'Formalize all87propositions and maintain the finalized monograph.','goal_reached':len(complete)==87,'accepted_new_propositions':[int(n) for n,c in cfg['claims'].items() if c.get('status','complete')=='complete'],'complete_ids':complete,'partial_ids':partial,'remaining_ids':unformal,'counts':counts,'new_module_hashes':{m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in cfg['modules']},'review_provenance':'Raw-source coordinator and separate-agent internal reviews; not external independent certification.','verification_status':'See verification/current/report.json for the fresh source-bound cumulative result.'};writej(ROOT/'CURRENT_CHECKPOINT.json',cp)
writej(ROOT/'PROGRESS.json',{'release':'0.19.0','checkpoint':cp['checkpoint'],'goal_reached':cp['goal_reached'],'completed':complete,'partial':partial,'unformalized':unformal,'outstanding':unfinished,'next_chronological':min(unformal) if unformal else None,'counts':counts,'verification_report':'verification/current/report.json','scope':'Immutable source checkpoint with execution recorded separately.'})
# Preserve predecessor mathematical/metadata contracts, changing exact inventories only.
pc=json.loads(z.read(PREFIX+'RELEASE_COUNTS.json'))
s=z.read(PREFIX+'scripts/check_metadata.py').decode()
s=s.replace("r'\\s+'+re.escape(d['name'].split('.')[-1])", "r'\\s+(?:\\w+\\.)*'+re.escape(d['name'].split('.')[-1])")
s=s.replace("n.endswith('/DECLARATIONS.json')", "n=='Large_Signal_Model/Lean/DECLARATIONS.json'")
def sub_once(pattern,replacement,label):
 global s
 s,n=re.subn(pattern,replacement,s)
 require(n==1,f'{label}: expected one predecessor contract, got {n}')
sub_once(r"record\('\d+ unique named declarations'",lambda m:f"record('{len(decls)} unique named declarations'",'Declaration label')
sub_once(r"counts\['named_declarations'\] == \d+",lambda m:f"counts['named_declarations'] == {len(decls)}",'Declaration count')
sub_once(r"record\('\d+ named theorems, \d+ in example modules'",lambda m:f"record('{nt} named theorems, {nex} in example modules'",'Theorem label')
sub_once(r"counts\['named_theorems'\]==\d+",lambda m:f"counts['named_theorems']=={nt}",'Theorem count')
example_modules=sorted({d['module'] for d in decls if d['module']=='Examples' or re.fullmatch(r'Block\d+.*Examples',d['module'])})
sub_once(r"d\['module'\] in \[[^\n]+?\] for d in decls\)==counts\['example_theorems'\]==\d+",lambda m:f"d['module'] in {example_modules!r} for d in decls)==counts['example_theorems']=={nex}",'Example classifier/count')
a=s.index("    record('Coverage matches reviewed");b=s.index('    lineage =',a)
s=s[:a]+f"    record('Coverage matches reviewed complete/partial/unformalized IDs',\n           [x['proposition'] for x in cover['entries'] if x['status']=='complete']=={complete!r}\n           and [x['proposition'] for x in cover['entries'] if x['status']=='partial']=={partial!r}\n           and [x['proposition'] for x in cover['entries'] if x['status']=='not_formalized']=={unformal!r})\n"+s[b:]
sub_once(r'All \d+ inherited proof files',lambda m:f"All {pc['proof_modules']} inherited proof files",'Inherited proof label')
sub_once(r"(\n\s+)len\(lineage\['inherited_proof_files'\]\)==\d+",lambda m:m.group(1)+f"len(lineage['inherited_proof_files'])=={pc['proof_modules']}",'Inherited proof count')
sub_once(r'All \d+ inherited declaration records',lambda m:f"All {pc['named_declarations']} inherited declaration records",'Inherited declaration label')
sub_once(r'len\(previous\)==\d+',lambda m:f"len(previous)=={pc['named_declarations']}",'Inherited declaration count')
sub_once(r'All \d+ proof modules',lambda m:f'All {len(modules)} proof modules','Module label')
sub_once(r'len\(set\(root_modules\)\)==\d+',lambda m:f'len(set(root_modules))=={len(modules)}','Module count')
sub_once(r'All \d+ negative controls',lambda m:f'All {nc} negative controls','Control label')
sub_once(r"counts\['negative_controls'\]==\d+",lambda m:f"counts['negative_controls']=={nc}",'Control count')
sub_once(r"(len\(list\(\(ROOT/'KomorebiLSM'\)\.glob\('\*\.lean'\)\)\)-len\(lineage\['inherited_proof_files'\]\)==)\d+",lambda m:m.group(1)+str(len(cfg['modules'])),'Proof increment')
sub_once(r"counts\['negative_controls'\]-\d+==\d+",lambda m:f"counts['negative_controls']-{pc['negative_controls']}=={nc-pc['negative_controls']}",'Control increment')
sub_once(r"counts\['named_theorems'\]-\d+",lambda m:f"counts['named_theorems']-{pc['named_theorems']}",'Theorem increment')
sub_once(r'len\(set\(remaining\)\)==\d+',lambda m:f'len(set(remaining))=={len(unfinished)}','Remaining list')
sub_once(r'All \d+ predecessor rejection-control sources',lambda m:f"All {pc['negative_controls']} predecessor rejection-control sources",'Inherited control label')
sub_once(r"len\(lineage\['inherited_control_files'\]\)==\d+",lambda m:f"len(lineage['inherited_control_files'])=={pc['negative_controls']}",'Inherited control count')
for n,c in cfg['claims'].items():
 s=s.replace(f"cover['entries'][{int(n)-1}]['status']=='partial'",f"cover['entries'][{int(n)-1}]['status']=={c.get('status','complete')!r}")
control_checks="    inherited_controls=lineage['inherited_control_files']\n    control_repairs=lineage.get('inherited_control_repairs',{})\n    expected_repairs={'negative_controls/PositiveLiftMustBeStrict.lean',\n      'negative_controls/InconsistentDataAlwaysFits.lean',\n      'negative_controls/ImpossibleConditionalPrior.lean'}\n    record('Original 137 inherited-control hashes are retained',len(inherited_controls)==137)\n    record('Exactly three authorized inherited-control repairs are explicit',set(control_repairs)==expected_repairs)\n    changed_controls={name for name,h in inherited_controls.items() if digest(ROOT/name)!=h}\n    record('Only the three documented active controls differ from the predecessor',changed_controls==expected_repairs)\n    record('134 inherited controls remain byte-identical',\n      sum(digest(ROOT/name)==h for name,h in inherited_controls.items())==134)\n    repair_manifest=lineage['control_repair_manifest']\n    require(digest(ROOT/repair_manifest['path'])==repair_manifest['sha256'],'Changed control-repair manifest')\n    manifest_records=json.loads((ROOT/repair_manifest['path']).read_text())['repairs']\n    require({e['control'] for e in manifest_records}==expected_repairs,'Control-repair manifest set mismatch')\n    manifest_by_name={e['control']:e for e in manifest_records}\n    for name,repair in control_repairs.items():\n        original_hash=inherited_controls[name]\n        require(repair['original_sha256']==original_hash,'Changed inherited original-control hash')\n        require(digest(ROOT/repair['preserved_original'])==original_hash,'Preserved original control changed')\n        require(digest(ROOT/name)==repair['active_sha256'],'Active control repair hash changed')\n        require(digest(ROOT/repair['preserved_repaired'])==repair['active_sha256'],'Preserved repaired control changed')\n        require(bool(repair['reason']),'Missing control repair reason')\n        original_record=manifest_by_name[name]\n        require(original_record['before_sha256']==original_hash and\n          original_record['after_sha256']==repair['active_sha256'],'Control-repair manifest hash mismatch')\n        require(digest(ROOT/repair['clean_receipt'])==repair['clean_receipt_sha256'],'Control-repair receipt changed')\n        receipt=json.loads((ROOT/repair['clean_receipt']).read_text())\n        require(receipt['control']==name and receipt['source_sha256']==repair['active_sha256'] and\n          receipt['source_sha256_final']==repair['active_sha256'],'Control receipt/source mismatch')\n        require(receipt['returncode']==1 and receipt['timed_out'] is False and\n          receipt['valid_rejection'] is True and receipt['stderr']=='' and\n          receipt['stdout'].count('error:')==1 and '⊢ False' in receipt['stdout'] and\n          receipt['infrastructure_error_matches']==[],'Control repair lacks the sole intended False rejection')\n        require(mod.classify_negative_control(receipt)['valid_rejection'],'Canonical classifier rejects a clean repaired control')\n        original_stdout=(ROOT/'history/control_repairs'/(Path(name).stem+'.before.stdout.txt')).read_text()\n        require(not mod.classify_negative_control({'returncode':1,'timed_out':False,'stdout':original_stdout,'stderr':''})['valid_rejection'],'Canonical classifier accepts a superseded mixed diagnostic')\n        for module,pin in receipt['dependencies_execution'].items():\n            if module.startswith('KomorebiLSM.'):\n                source=ROOT/'KomorebiLSM'/(module.removeprefix('KomorebiLSM.')+'.lean')\n                require(digest(source)==pin['source_sha256'],'Control receipt dependency source changed')\n    record('All three original and repaired control bytes are preserved and hash-bound',True)\n    record('All three repaired controls have current clean intended-rejection receipts',True)\n    record('Canonical classifier accepts all three repaired clean diagnostics',True)\n    record('Canonical classifier rejects all three original mixed diagnostics',True)\n"
s,n=re.subn(r"    record\('All \d+ predecessor rejection-control sources are unchanged',.*?(?=    record\('Actual infimum)",lambda _:control_checks,s,flags=re.S)
require(n==1,'Inherited control exception block was not installed')
s=s.replace("progress['next_chronological']==min(progress['unformalized'])","progress['next_chronological']==(min(progress['unformalized']) if progress['unformalized'] else None)")
pos=s.index("    result={'kind'");extra='    record(\'Nested Lean comments do not trigger prohibited tokens\', mod.prohibited_source_hits(\'/- sorry /- axiom -/ unsafe -/\\n-- admit\\nexample : True := by trivial\')==[])\n    record(\'Active proof bypass tokens are rejected after comments\', [h[\'token\'] for h in mod.prohibited_source_hits(\'/- allowed comment -/ example : True := by sorry\')]==[\'sorry\'])\n    record(\'Strings cannot open comments hiding later code\', [h[\'token\'] for h in mod.prohibited_source_hits(\'def note := "-- /-"; example : True := by admit\')]==[\'admit\'])\n    record(\'Interpolated string expressions retain prohibited-token checks\', [h[\'token\'] for h in mod.prohibited_source_hits(\'def note := s!"text {by admit}"\')]==[\'admit\'])\n'
for n,c in cfg['claims'].items():extra+=f"    record('P{n}: accepted endpoints and mapped scope resolve', cover['entries'][{int(n)-1}]['status']=={c.get('status','complete')!r} and all(n in by_name for n in {c['endpoints']!r}))\n"
s=s[:pos]+extra+s[pos:];(ROOT/'scripts/check_metadata.py').write_text(s)
# Readable exact coverage/remaining views.
lines=['# Formal coverage','',f'{len(complete)} complete mappings, {len(partial)} partial, {len(unformal)} unformalized. Counts are not weighted by proof difficulty.','','| Proposition | Status | Mapped scope |','|---|---|---|']
for e in cover['entries']:lines.append(f"| P{e['proposition']}: {e['title']} | {e['status']} | {e['scope'].replace('|','/')} |")
(ROOT/'COVERAGE.md').write_text('\n'.join(lines)+'\n')
lines=['# Remaining formalization obligations','',f'{len(unfinished)} unfinished mappings: {len(partial)} partial and {len(unformal)} unformalized.','', '## Partial mappings','']
for n in partial:lines.append(f"- P{n}: {cover['entries'][n-1]['scope']}")
lines+=['','## Unformalized propositions','']
for n in unformal:lines.append(f"- P{n}: {cover['entries'][n-1]['title']}")
(ROOT/'ROADMAP_1.0.md').write_text('\n'.join(lines)+'\n')
writej(ROOT/'verification/current_scope/INTEGRATION_INPUT.json',cfg)
writej(ROOT/'CURRENT_STATUS.json',{'goal_reached':False,'scope_goal_reached':len(complete)==87,'complete_propositions':len(complete),'partial_propositions':len(partial),'unformalized_propositions':len(unformal),'verification_passed':False,'verification_report':'verification/current/report.json','source_checkpoint':'CURRENT_CHECKPOINT.json','note':'Reviewed correspondence is integrated. A fresh cumulative execution is still required before acceptance.'})
if args.release!='0.19.0':
 for name in ['COVERAGE.json','ROADMAP_1.0.json','SOURCE_LINEAGE.json','RELEASE_COUNTS.json','CURRENT_CHECKPOINT.json','PROGRESS.json','scripts/verify.py','lakefile.toml']:
  p=ROOT/name;p.write_text(p.read_text().replace('0.19.0',args.release))
 counts['release']=args.release
print(json.dumps(counts))
