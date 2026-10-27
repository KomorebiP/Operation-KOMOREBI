from pathlib import Path
import hashlib, json, re, shutil, subprocess, datetime as dt, platform
W=Path('/mnt/data/fd_bayes_work')
R=Path('/mnt/data/FD_Gaussian_Bayesian_Conditioning_v0.1.0_Checked')
T=Path('/mnt/data/lean_runtime_parts/Komorebi_Portable_Lean_4.34.0-rc2')
R.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
shutil.copytree(W/'src/Komorebi',R/'Komorebi',dirs_exist_ok=True)
shutil.copytree(W/'audit',R/'audit',dirs_exist_ok=True)
for f in ['MODULE_ORDER.json','declarations.json','CLEAN_REBUILD_INPUTS.json','CLEAN_REBUILD_START.json','runtime_restore.log','verify_blocks.py']:
 shutil.copy2(W/f,R/f)
shutil.copy2(W/'README.release.md',R/'README.md')
shutil.copy2(W/'CONTINUE.release.md',R/'CONTINUE_HERE.md')
(R/'checks').mkdir(exist_ok=True)
shutil.copy2(W/'run_block.py',R/'checks/original_run_block.py')
mods=json.loads((W/'MODULE_ORDER.json').read_text())
start=json.loads((W/'CLEAN_REBUILD_START.json').read_text())['started_at']
snap=json.loads((W/'CLEAN_REBUILD_INPUTS.json').read_text())
records=[]
for mod in mods:
 candidates=[]
 for p in (W/'audit').glob(mod+'.*.json'):
  data=json.loads(p.read_text())
  if data.get('exit_status')==0 and data.get('started_at','')>=start:
   candidates.append((data['started_at'],p,data))
 assert candidates,mod
 _,p,data=max(candidates)
 src=R/'Komorebi'/f'{mod}.lean'
 h=sha(src)
 assert h==data['source_sha256_before']==data['source_sha256_after'],mod
 assert h==snap[mod+'.lean'],(mod,'snapshot changed')
 log=p.with_suffix('.log')
 assert sha(log)==data['log_sha256']
 olean=T/'workspace/.lake/build/lib/lean/Komorebi'/f'{mod}.olean'
 assert sha(olean)==data['olean_sha256']
 records.append({**data,'source':f'Komorebi/{mod}.lean','receipt':f'audit/{p.name}','log':f'audit/{log.name}'})
scans={}
for p in sorted((R/'Komorebi').glob('*.lean')):
 found=re.findall(r'\b(?:sorry|admit|axiom|unsafe)\b',p.read_text())
 assert not found,(p,found)
 scans[p.name]=len(re.findall(r'(?m)^\s*(?:@\[[^\n]*\]\s*)?(?:theorem|lemma)\s+',p.read_text()))
assert sum(scans.values())==51,scans
alog=R/records[-1]['log']
pairs=re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",alog.read_text(),re.S)
assert len(pairs)==51
axioms=sorted({a.strip() for _,deps in pairs for a in deps.split(',') if a.strip()})
assert set(axioms)<={'propext','Classical.choice','Quot.sound'}
baseline=[]
for p in sorted((W/'FD_Joint_Covariance_Matching_v0.1.0_Checked/Komorebi').glob('*.lean')):
 q=R/'Komorebi'/p.name
 assert sha(p)==sha(q),p
 baseline.append({'source':f'Komorebi/{p.name}','sha256':sha(p),'unchanged':True})
lean=subprocess.check_output([str(T/'toolchain/bin/lean'),'--version'],text=True).strip()
ml=T/'workspace/.lake/packages/mathlib'
commit=subprocess.check_output(['git','-c',f'safe.directory={ml}','-C',str(ml),'rev-parse','HEAD'],text=True).strip()
assert commit=='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
assert '6a10ac8c22beadecabdbb0919c2b50214762f91d' in lean
receipt={'status':'CHECKED','checkpoint_local_date':'2026-09-11 America/Chicago',
 'recorded_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
 'claim':'Finite-dimensional Gaussian evidence, exact joint disintegration, and canonical posterior identification',
 'assumptions':['Arbitrary finite real state and observation index types','P positive semidefinite; singular prior permitted','R positive definite','Canonical kernel equality is evidence-almost everywhere'],
 'environment':{'lean_version_output':lean,'lean_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib_commit':commit,'warning_as_error':True,'hardware':platform.platform()},
 'clean_rebuild':{'started_at':start,'all_project_oleans_removed_before_run':True,'pinned_mathlib_cache_reused':True,'modules':len(mods),'successful_modules':len(records),'sum_successful_lean_seconds':round(sum(x['runtime_seconds'] for x in records),3),'one_module_per_successful_lean_process':True,'outer_paired_call_interruption':'Recorded; interrupted module rerun separately. Not accepted as proof evidence.'},
 'inventory':{'total_theorem_lemma_declarations':51,'retained_baseline_declarations':17,'newly_checked_declarations':34,'source_modules_including_audit':18,'declaration_counts':scans},
 'source_scan':{'sorry':0,'admit':0,'custom_axiom_declarations':0,'unsafe':0,'scope':'18 final source modules; includes comments conservatively'},
 'axiom_audit':{'covered_theorems_and_lemmas':51,'axioms':axioms,'all_checked':True,'log':records[-1]['log'],'log_sha256':sha(alog)},
 'baseline_integrity':baseline,
 'execution_records':records,
 'remaining_open':['Finite-dimensional matrix/continuous-linear-map identification and integration with multiscale posterior perturbation budgets','Posterior distribution metric bounds','Singular innovation/pseudoinverse conditioning','Itô-integral derivation and nonlinear/non-Gaussian extensions','Literature priority and novelty'],
 'provenance_limits':['This turn rebuilds the 18-module finite-dimensional layer, not the entire inherited program or mathlib.','Pinned compiled mathlib dependencies are trusted, not rebuilt.','Hashes are integrity checks, not digital signatures.','The declaration count is not a count of independent mathematical discoveries.']}
dump(R/'FINAL_VERIFICATION_RECEIPT.json',receipt)
dump(R/'audit/ALL_THEOREM_AXIOMS.json',[{'declaration':name,'axioms':[a.strip() for a in deps.split(',') if a.strip()]} for name,deps in pairs])
print('PREPARED',R)
print('SUCCESSFUL_MODULES',len(records),'THEOREMS',len(pairs),'TOTAL_LEAN_SECONDS',receipt['clean_rebuild']['sum_successful_lean_seconds'])
