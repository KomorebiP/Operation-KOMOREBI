from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
BASE=Path('/workspace/scratch/ea498747acd5')
ROOT=BASE/'work/Komorebi_LSM_Lean_0.18.0'
PARENT=BASE/'output_v017/Large_Signal_Model_Lean_and_Monograph_Checked.zip'
PARENT_SHA='dc3e6a2877b94db1eba0e50334859cd1cf2f83171cca5b0e22ea60717556479b'
PREFIX='Large_Signal_Model/Lean/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writej(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
require=lambda p,m: None if p else (_ for _ in ()).throw(ValueError(m))
require(sha(PARENT)==PARENT_SHA,'Parent archive changed')
z=zipfile.ZipFile(PARENT);cfg=json.loads(Path(sys.argv[1]).read_text())
require(set(cfg['claims']) <= {str(n) for n in range(1,88)},'Invalid proposition ID')
require(all(c.get('status','complete') in {'complete','partial'} for c in cfg['claims'].values()),'Invalid accepted status')
require(cfg.get('accepted_source_sha256')=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in cfg['modules']},'Accepted raw-source hashes missing or stale')
require(bool(cfg.get('review_records')),'Missing source correspondence reviews')
for rel,h in cfg['review_records'].items():require(sha(ROOT/rel)==h,'Changed acceptance review '+rel)
base_modules=re.findall(r'^import KomorebiLSM\.(\w+)$',z.read(PREFIX+'KomorebiLSM.lean').decode(),re.M)
require(len(base_modules)==133,'Wrong baseline module list')
modules=base_modules+cfg['modules']
require(len(set(modules))==len(modules),'Duplicate import')
require(set(modules)=={p.stem for p in (ROOT/'KomorebiLSM').glob('*.lean')},'Active module omission')
for m in base_modules:require((ROOT/'KomorebiLSM'/f'{m}.lean').read_bytes()==z.read(PREFIX+f'KomorebiLSM/{m}.lean'),'Changed inherited proof '+m)
for name in ['README.md','AUDIT.md','LEAN_GUIDE.md','CONTINUE_HERE.md','PROGRESS.md','PROGRESS.json','PROGRESS_LEDGER.md','ROADMAP_1.0.md','ROADMAP_1.0.json','PUBLICATION_STATUS.md','CURRENT_CHECKPOINT.json','scripts/check_metadata.py','scripts/verify.py']:
 (ROOT/'history'/('PREDECESSOR_0.17.0_'+name.replace('/','_'))).write_bytes(z.read(PREFIX+name))
snapshot=ROOT/'history/PREDECESSOR_0.17.0_Source_Snapshot.zip'
with zipfile.ZipFile(snapshot,'w',zipfile.ZIP_DEFLATED) as out:
 for name in z.namelist():
  if name.startswith(PREFIX) and not name.endswith(('/','.zip')):out.writestr(name,z.read(name))
(ROOT/'KomorebiLSM.lean').write_text(''.join(f'import KomorebiLSM.{m}\n' for m in modules))
v=ROOT/'scripts/verify.py';t=v.read_text();t=re.sub(r'MODULES = \[.*?\]\nEXPECTED_LEAN',f'MODULES = {modules!r}\nEXPECTED_LEAN',t,flags=re.S);t=t.replace("'release':'0.17.0'","'release':'0.18.0'");v.write_text(t)
p=ROOT/'lakefile.toml';p.write_text(re.sub(r'version = "[^"]+"','version = "0.18.0"',p.read_text(),count=1))
subprocess.run([sys.executable,str(ROOT/'scripts/build_inventory.py'),'--write'],check=True)
decls=json.loads((ROOT/'DECLARATIONS.json').read_text());by={d['name']:d for d in decls}
cover=json.loads(z.read(PREFIX+'COVERAGE.json'))
for e in cover['entries']:
 c=cfg['claims'].get(str(e['proposition']))
 if c:
  require(all(n in by for n in c['endpoints']),'Missing accepted endpoint')
  require(set(c['modules']) <= set(cfg['modules']),'Accepted mapping includes an unreviewed module')
  require(all(by[n]['module'] in c['modules'] for n in c['endpoints']),'Endpoint outside mapped modules')
  e.update(status=c.get('status','complete'),scope=c['scope'],lean_targets=[{**d,'source_sha256':sha(ROOT/d['file'])} for d in decls if d['module'] in c['modules']])
  require(bool(e['lean_targets']),'Empty mapping')
complete=[e['proposition'] for e in cover['entries'] if e['status']=='complete'];partial=[e['proposition'] for e in cover['entries'] if e['status']=='partial'];unformal=[e['proposition'] for e in cover['entries'] if e['status']=='not_formalized'];unfinished=sorted(partial+unformal)
cover.update(formalization_version='0.18.0',complete=complete,partial=partial,not_formalized_count=len(unformal));writej(ROOT/'COVERAGE.json',cover)
road=json.loads(z.read(PREFIX+'ROADMAP_1.0.json'));road.update(release='0.18.0',completed=complete,partial=partial,unformalized=unformal,unformalized_count=len(unformal),remaining_count=len(unfinished),remaining_count_semantics='All unfinished mappings, including partial mappings.')
for track in road['tracks']:track['propositions']=[n for n in track['propositions'] if n in unfinished]
writej(ROOT/'ROADMAP_1.0.json',road)
lin=json.loads(z.read(PREFIX+'SOURCE_LINEAGE.json'));lin.update(formalization_version='0.18.0',predecessor_archive={'path':snapshot.relative_to(ROOT).as_posix(),'sha256':sha(snapshot),'bytes':snapshot.stat().st_size,'kind':'source_snapshot_without_nested_archives'},inherited_proof_files={f'KomorebiLSM/{m}.lean':sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in base_modules},inherited_control_files={n[len(PREFIX):]:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith(PREFIX+'negative_controls/') and n.endswith('.lean')},parent_delivered_archive={'filename':PARENT.name,'sha256':PARENT_SHA})
writej(ROOT/'SOURCE_LINEAGE.json',lin)
nt=sum(d['kind']=='theorem' for d in decls);nex=sum(d['kind']=='theorem' and(d['module']=='Examples' or bool(re.fullmatch(r'Block\d+.*Examples',d['module']))) for d in decls);nc=len(list((ROOT/'negative_controls').glob('*.lean')))
counts={'release':'0.18.0','proof_modules':len(modules),'named_declarations':len(decls),'named_theorems':nt,'example_theorems':nex,'supporting_theorems':nt-nex,'new_theorems':nt-1753,'new_example_theorems':nex-331,'complete_propositions':len(complete),'partial_propositions':len(partial),'unformalized_propositions':len(unformal),'negative_controls':nc};writej(ROOT/'RELEASE_COUNTS.json',counts)
cp={'checkpoint':'LSM-0.18.0','parent_archive_sha256':PARENT_SHA,'target':'Formalize all87propositions and maintain the finalized monograph.','goal_reached':len(complete)==87,'accepted_new_propositions':[int(n) for n,c in cfg['claims'].items() if c.get('status','complete')=='complete'],'complete_ids':complete,'partial_ids':partial,'remaining_ids':unformal,'counts':counts,'new_module_hashes':{m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in cfg['modules']},'review_provenance':'Raw-source coordinator and separate-agent internal reviews; not external independent certification.','verification_status':'See verification/current/report.json for the fresh source-bound cumulative result.'};writej(ROOT/'CURRENT_CHECKPOINT.json',cp)
writej(ROOT/'PROGRESS.json',{'release':'0.18.0','checkpoint':cp['checkpoint'],'goal_reached':cp['goal_reached'],'completed':complete,'partial':partial,'unformalized':unformal,'outstanding':unfinished,'next_chronological':min(unformal) if unformal else None,'counts':counts,'verification_report':'verification/current/report.json','scope':'Immutable source checkpoint with execution recorded separately.'})
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
s=s.replace("progress['next_chronological']==min(progress['unformalized'])","progress['next_chronological']==(min(progress['unformalized']) if progress['unformalized'] else None)")
pos=s.index("    result={'kind'");extra=''
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
print(json.dumps(counts))
