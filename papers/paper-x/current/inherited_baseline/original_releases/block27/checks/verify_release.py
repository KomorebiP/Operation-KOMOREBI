"""Offline clean build, imported-declaration axiom audit, and semantic controls."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
from datetime import datetime,timezone
from lean_env import ROOT,lean_env
from source_scan import without_comments
RELEASE='PRSC_X_v0.27.0_Checked_TwentySeventh_Block'
BASELINE_VERIFICATION='predecessor_evidence/block26/verification.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 kit=Path(sys.argv[1]).resolve();lean,env=lean_env(kit)
 assert sha(Path(lean))=='e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
 actual_manifest=json.loads((kit/'workspace/lake-manifest.json').read_text())
 actual_rev=next(p['rev'] for p in actual_manifest['packages'] if p['name']=='mathlib')
 assert actual_rev=='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
 prov=json.loads((ROOT/'provenance.json').read_text())
 assert prov['release']==RELEASE and prov['predecessor_source_count']==170
 baseline=json.loads((ROOT/BASELINE_VERIFICATION).read_text())
 assert baseline['status']=='passed' and baseline['release']=='PRSC_X_v0.26.0_Checked_TwentySixth_Block'
 predecessor={m['module']:m for m in baseline['modules']}
 sources={p.stem:p for p in (ROOT/'lean/PaperX').glob('*.lean')}
 assert len(predecessor)==prov['predecessor_source_count']
 assert set(sources)-set(prov['new_modules'])==set(predecessor)
 assert set(prov['new_modules']).isdisjoint(predecessor)
 assert all(sha(sources[n])==m['source_sha256'] for n,m in predecessor.items())
 assert sha(ROOT/'references'/prov['baseline_archive']['filename'])==prov['baseline_archive']['sha256']
 # Each verification starts without any prior production proof objects.
 clean=ROOT/'build_clean'
 if clean.exists():shutil.rmtree(clean)
 (clean/'PaperX').mkdir(parents=True)
 (ROOT/'logs').mkdir(exist_ok=True)
 env['LEAN_PATH']=str(clean)+os.pathsep+env['LEAN_PATH'].split(os.pathsep,1)[1]
 order=[];seen=set()
 def visit(n):
  if n in seen:return
  seen.add(n)
  for dep in re.findall(r'^import PaperX\.(\w+)',sources[n].read_text(),re.M):visit(dep)
  order.append(n)
 for n in sorted(sources):visit(n)
 started=datetime.now(timezone.utc).isoformat();t=time.perf_counter();runs=[];decls=[]
 def run(name,args,success=True):
  t0=time.perf_counter();p=subprocess.run([lean,'-DwarningAsError=true',*args],cwd=ROOT/'lean',env=env,capture_output=True,text=True,timeout=240)
  out=p.stdout+p.stderr;log=ROOT/'logs'/f'{name}.log';log.write_text(out)
  runs.append({'name':name,'exit_code':p.returncode,'expected_success':success,'seconds':time.perf_counter()-t0,'log_sha256':sha(log)})
  print(name,p.returncode,round(time.perf_counter()-t0,2),flush=True)
  if (p.returncode==0)!=success:raise RuntimeError(out)
  if not success and 'error' not in out:raise RuntimeError('Uninterpretable rejection')
  return out
 forbidden=re.compile(r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern)\b')
 pat=re.compile(r'^(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?(theorem|lemma|def|abbrev|structure|inductive|instance)\s+(\w+)',re.M)
 modules=[]
 for n in order:
  src=sources[n];s=src.read_text();code=without_comments(s)
  if forbidden.search(code):raise RuntimeError('Forbidden source construct '+n)
  ds=pat.findall(code)
  scopes=[]
  for line in code.splitlines():
   match=re.match(r'^namespace (\S+)',line)
   if match:scopes.append(('namespace',match.group(1)));continue
   if re.match(r'^(?:noncomputable\s+)?section(?:\s|$)',line):scopes.append(('section',''));continue
   if re.match(r'^end(?:\s|$)',line):
    if scopes:scopes.pop()
    continue
   match=pat.match(line)
   if match:
    kind,name=match.groups();ns='.'.join(v for k,v in scopes if k=='namespace')
    decls.append((ns+'.'+name,kind,n))
  out=clean/'PaperX'/f'{n}.olean'
  run(n,['-o',str(out),str(src)])
  modules.append({'module':n,'source_sha256':sha(src),'olean_sha256':sha(out),'theorems':sum(k in ('theorem','lemma') for k,_ in ds)})
 imports=''.join(f'import PaperX.{n}\n' for n in order)
 audit=ROOT/'checks/AxiomAudit.lean';audit.write_text(imports+'\n'+''.join(f'#print axioms {n}\n' for n,_,_ in decls))
 out=run('AxiomAudit',[str(audit)])
 ax={n:[x.strip() for x in s.split(',') if x.strip()] for n,s in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",out)}
 ax.update({n:[] for n in re.findall(r"'([^']+)' does not depend on any axioms",out)})
 assert set(ax)=={n for n,_,_ in decls}
 assert all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in ax.values())
 run('PositivePrecision',[str(ROOT/'checks/PositivePrecision.lean')])
 run('PositiveSummands',[str(ROOT/'checks/PositiveSummands.lean')])
 run('PositiveFamilies',[str(ROOT/'checks/PositiveFamilies.lean')])
 run('PositiveLogarithms',[str(ROOT/'checks/PositiveLogarithms.lean')])
 run('PositiveQuadraticPackets',[str(ROOT/'checks/PositiveQuadraticPackets.lean')])
 run('PositiveLocalArithmetic',[str(ROOT/'checks/PositiveLocalArithmetic.lean')])
 run('PositiveSpineBoundary',[str(ROOT/'checks/PositiveSpineBoundary.lean')])
 run('PositiveRequiredPackets',[str(ROOT/'checks/PositiveRequiredPackets.lean')])
 run('PositiveFiniteAvoidance',[str(ROOT/'checks/PositiveFiniteAvoidance.lean')])
 run('PositivePullback',[str(ROOT/'checks/PositivePullback.lean')])
 run('PositiveCyclotomicInertia',[str(ROOT/'checks/PositiveCyclotomicInertia.lean')])
 run('PositiveGeneralFrobenius',[str(ROOT/'checks/PositiveGeneralFrobenius.lean')])
 controls=['FalseResidualDepth','FalseNoPrecisionLoss','FalseUnchangedLift','FalseShallowProjector','FalseProjectorNoLoss','FalseAverageProjector','FalseIndependentOrthogonal','FalseUniqueFamily','FalseFamilyNoLoss','FalseZeroLogSample','FalseQuadraticLogAnyOrder','FalseMissingOriginalAction','FalseEveryQuadraticPointLifts','FalseResidualQuadraticPacketsUnique','FalseAllQuadraticRootsSigns','FalseDyadicSquareLift','FalseLocalResidualSuffices','FalseInertiaIsLocalTriviality','FalseSpineClosureOmitted','FalseSpineOccupancyOmitted','FalseSomePacketSuffices','FalseFinitePacketSampleSuffices','FalseDensityAfterFiniteDeletion','FalsePullbackWithoutSurjectivity','FalseResidueRootsWithoutUnit','Placeholder']
 for n in controls:
  out=run(n,[str(ROOT/'checks'/f'{n}.lean')],False)
  assert ('sorry' in out) if n=='Placeholder' else ('⊢ False' in out),out
 prov=json.loads((ROOT/'provenance.json').read_text());new=set(prov['new_modules'])
 assert new<=set(sources)
 assert len(modules)==prov['predecessor_source_count']+len(new)
 res={'release':prov['release'],'status':'passed','scope':prov['theorem_scope'],'arithmetic_status':prov['arithmetic_status'],'started_at':started,'seconds':time.perf_counter()-t,'lean_version':subprocess.check_output([lean,'--version'],env=env,text=True).strip(),'lean_sha256':sha(Path(lean)),'lean_shared_sha256':sha(kit/'toolchain/lib/lean/libleanshared.so'),'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','module_count':len(modules),'theorem_declarations':sum(m['theorems'] for m in modules),'new_theorem_declarations':sum(m['theorems'] for m in modules if m['module'] in new),'audited_declarations':len(ax),'axioms':sorted({a for aa in ax.values() for a in aa}),'positive_controls':[r['name'] for r in runs if r['name'].startswith('Positive')],'rejected_controls':list(controls),'modules':modules,'runs':runs,'new_declarations':[n for n,k,m in decls if m in new]}
 (ROOT/'verification.json').write_text(json.dumps(res,indent=2)+'\n');(ROOT/'axioms.json').write_text(json.dumps(ax,indent=2)+'\n')
 print(json.dumps({k:v for k,v in res.items() if k not in ['modules','runs','new_declarations']}))
if __name__=='__main__':main()
