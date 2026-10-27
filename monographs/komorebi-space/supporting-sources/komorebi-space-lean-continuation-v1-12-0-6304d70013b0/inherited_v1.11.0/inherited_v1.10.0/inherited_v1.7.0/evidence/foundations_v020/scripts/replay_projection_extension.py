#!/usr/bin/env python3
"""Verify the five-module v0.19 extension against a freshly compiled v0.18 baseline.

This does not call an incremental check a second full cumulative build.
The baseline must have passed scripts/verify.py; hashes link every reused
source and .olean to that report. All additions, root imports, full axiom
inventories and the three negative controls are checked again.
"""
from __future__ import annotations
from pathlib import Path
import argparse,datetime as dt,hashlib,json,os,re,shutil,subprocess,time,sys
from verify import axiom_records,uncomment,ALLOWED_AXIOMS,EXPECTED_LEAN,EXPECTED_MATHLIB
NEW=['KernelProjectionBounds','CayleyHolonomyConditioning','HolonomyProjection','HolonomyGapCertificate','HolonomyConditioningExample']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--baseline-report',type=Path,required=True)
 ap.add_argument('--audit-dir',type=Path,required=True);args=ap.parse_args()
 root=Path(__file__).resolve().parents[1];base=args.baseline.resolve();rt=args.runtime.resolve()
 audit=args.audit_dir if args.audit_dir.is_absolute() else root/args.audit_dir;audit.mkdir(parents=True,exist_ok=True)
 br=args.baseline_report.resolve();report=json.loads(br.read_text())
 assert report['status']=='PASS' and report['checks']['clean_compile_all']
 assert report['checks']['axiom_audit_complete'] and report['checks']['only_allowed_axioms']
 build=root/'.lake/replay/lib/lean';basebuild=base/'.lake/replay/lib/lean'
 if build.exists():shutil.rmtree(build)
 (build/'KomorebiSpace').mkdir(parents=True)
 modules=json.loads((root/'audit/module_order.json').read_text())
 idx=json.loads((root/'audit/declaration_index.json').read_text())
 sources=sorted((root/'KomorebiSpace').glob('*.lean'))+[root/'KomorebiSpace.lean']
 before={str(p.relative_to(root)):sha(p) for p in sources}
 rec={'version':'0.19.0','started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'strategy':'fresh v0.18 baseline outputs plus fresh compilation of all five additions and cumulative root',
      'baseline_report_sha256':sha(br),'baseline_report':str(br),'runs':[],'checks':{},'reused':[]}
 rows={x.get('source'):x for x in report['runs'] if x.get('source')}
 base_modules=json.loads((base/'audit/module_order.json').read_text())
 assert len(base_modules)==112
 assert set(modules)==set(base_modules+NEW) and len(modules)==117
 for m in base_modules:
  rel=f'KomorebiSpace/{m}.lean';binary=basebuild/f'KomorebiSpace/{m}.olean'
  assert sha(root/rel)==sha(base/rel)==rows[rel]['source_sha256']==report['source_sha256'][rel]
  assert sha(binary)==rows[rel]['olean_sha256'] and rows[rel]['exit_code']==0
  shutil.copy2(binary,build/f'KomorebiSpace/{m}.olean')
  rec['reused'].append({'module':m,'source_sha256':sha(root/rel),'olean_sha256':sha(binary)})
 rec['checks']['112_unchanged_sources_and_fresh_baseline_binaries']=True
 rec['checks']['module_inventory_complete']=set(modules)=={p.stem for p in (root/'KomorebiSpace').glob('*.lean')}
 rec['checks']['root_imports_complete']=set(re.findall(r'^import KomorebiSpace\.(\w+)$',(root/'KomorebiSpace.lean').read_text(),re.M))==set(modules)
 bad={str(p.relative_to(root)):re.findall(r'\b(?:sorry|admit|axiom|unsafe|native_decide|implemented_by)\b',uncomment(p.read_text())) for p in sources}
 rec['checks']['positive_source_scan']=not any(bad.values())
 packages=rt/'workspace/.lake/packages';lean=rt/'toolchain/bin/lean'
 env=dict(os.environ)
 for k in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:env.pop(k,None)
 env['LEAN_PATH']=os.pathsep.join(map(str,[build]+[x/'.lake/build/lib/lean' for x in sorted(packages.iterdir()) if (x/'.lake/build/lib/lean').is_dir()]))
 def run(label,argv,timeout=120):
  start=time.monotonic()
  try:
   p=subprocess.run(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
   text=p.stdout;code=p.returncode
  except subprocess.TimeoutExpired as exc:text=str(exc.stdout);code=None
  log=audit/(label+'.log');log.write_text(text)
  r={'label':label,'argv':argv,'cwd':str(root),'exit_code':code,'seconds':time.monotonic()-start,
     'log':str(log.relative_to(root)),'log_sha256':sha(log)};rec['runs'].append(r)
  print(label,code,round(r['seconds'],3),flush=True)
  if code!=0 and not label.startswith('negative_'):print(text[:5000],flush=True)
  return code,text
 code,text=run('lean_version',[str(lean),'--version']);rec['lean_version']=text.strip();rec['lean_binary_sha256']=sha(lean)
 rec['checks']['lean_pin']=code==0 and EXPECTED_LEAN in text and sha(lean)==report['lean_binary_sha256']
 code,text=run('mathlib_pin',['git','-C',str(packages/'mathlib'),'rev-parse','HEAD']);rec['mathlib_commit']=text.strip()
 rec['checks']['mathlib_pin']=code==0 and text.strip()==EXPECTED_MATHLIB
 ok=True
 for m in NEW+['ROOT']:
  rel='KomorebiSpace.lean' if m=='ROOT' else f'KomorebiSpace/{m}.lean'
  out=build/Path(rel).with_suffix('.olean')
  code,text=run('compile_'+m,[str(lean),'-j1','-DwarningAsError=true','-DautoImplicit=false','-o',str(out),rel])
  ok=ok and code==0 and out.is_file()
  if not ok:break
 rec['checks']['all_additions_and_root_freshly_compiled']=ok
 if ok:
  for label,path,kind in [('theorem_axioms','checks/AxiomAudit.lean','theorem'),('construction_axioms','checks/ConstructionAudit.lean','other')]:
   code,text=run(label,[str(lean),'-j1','-DwarningAsError=true','-DautoImplicit=false',path])
   actual=axiom_records(text);expected={e['name'] for e in idx if (e['kind']=='theorem')==(kind=='theorem')}
   rec[label]=actual
   rec['checks'][label+'_complete']=code==0 and set(actual)==expected
   rec['checks'][label+'_allowed']=not({a for xs in actual.values() for a in xs}-ALLOWED_AXIOMS)
  for name,marker in [('FalseStatement','error'),('Placeholder','sorry')]:
   code,text=run('negative_'+name,[str(lean),'-j1','-DwarningAsError=true','tests/negative/'+name+'.lean'])
   rec['checks']['reject_'+name]=code not in (None,0) and marker in text
  code,text=run('negative_AxiomInjection',[str(lean),'-j1','-DwarningAsError=true','tests/negative/AxiomInjection.lean'])
  a=axiom_records(text);unexpected={s for xs in a.values() for s in xs}-ALLOWED_AXIOMS
  rec['checks']['reject_custom_axiom']=code==0 and any(x=='injected' or x.endswith('.injected') for x in unexpected)
 rec['source_sha256']=before;rec['compiled_sha256']={str(p.relative_to(build)):sha(p) for p in sorted(build.rglob('*.olean'))}
 rec['checks']['sources_unchanged']=before=={str(p.relative_to(root)):sha(p) for p in sources}
 rec['checks']['all_118_compiled_objects_present']=len(rec['compiled_sha256'])==118
 rec['counts']={'proof_modules':len(modules),'named_theorems':sum(e['kind']=='theorem' for e in idx),'indexed_constructions':sum(e['kind']!='theorem' for e in idx)}
 rec['status']='PASS' if all(rec['checks'].values()) else 'FAIL';rec['finished_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
 (audit/'EXTENSION_VERIFICATION.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(rec['status'],json.dumps(rec['checks'],indent=2),flush=True)
 return 0 if rec['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
