#!/usr/bin/env python3
"""Fresh individual P69 checks. Run after sourcing runtime/env_v019.sh."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
LEAN=Path('/workspace/scratch/ea498747acd5/runtime/gated-bin/lean')
MODULES=['KernelTVMeasurable','ObservationLawKernels','ObservationLawComparison']
CONTROLS=['ObservationLawWrongInitial','ObservationLawUnsharedPolicy','ObservationLawNullFallback']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'kind':'P69_individual_fresh_checks','passed':False,'complete':False,'stages':[],
 'source_sha256':{m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in MODULES},
 'control_sha256':{m:sha(ROOT/'negative_controls'/f'{m}.lean') for m in CONTROLS},
 'dependencies':{m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in
  ['MeasureTVCalculus','ContinuousTVDensity','ContinuousRecords','SequentialLowerCertificate']}}
def save():
 (OUT/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
def run(phase,args,extra=None):
 start=time.monotonic();env=os.environ.copy()
 if extra:env.update(extra)
 p=subprocess.run([str(LEAN),'-j1','-DwarningAsError=true']+args,cwd=ROOT,env=env,
  text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 rec={'phase':phase,'command':[str(LEAN),'-j1','-DwarningAsError=true']+args,
  'returncode':p.returncode,'seconds':round(time.monotonic()-start,3),'stdout':p.stdout,'stderr':p.stderr}
 report['stages'].append(rec);save();print(phase,p.returncode,flush=True)
 return rec
save()
for m in MODULES:
 r=run('compile:'+m,['-o',f'.build/lib/lean/KomorebiLSM/{m}.olean',f'KomorebiLSM/{m}.lean'])
 if r['returncode']!=0:raise SystemExit(1)
r=run('axiom_audit',[str(OUT/'AxiomAudit.lean')])
if r['returncode']!=0:raise SystemExit(1)
decls=json.loads((OUT/'DECLARATIONS.json').read_text());expected={d['name'] for d in decls}
parsed={}
for m in re.finditer(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",r['stdout'],re.S):
 name,raw=m.groups()
 if name in parsed:raise RuntimeError('duplicate axiom record '+name)
 parsed[name]=sorted(a.strip() for a in (raw or '').split(',') if a.strip())
assert set(parsed)==expected,(expected-set(parsed),set(parsed)-expected)
assert all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in parsed.values())
report['axioms']=parsed;report['named_declarations']=len(decls)
report['named_theorems']=sum(d['kind']=='theorem' for d in decls)
report['named_proof_instances']=sum(d['kind']=='instance' for d in decls);save()
for m in MODULES:
 r=run('kernel_replay:'+m,[str(ROOT/'scripts/ReplayModule.lean')],{'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.'+m})
 assert r['returncode']==0 and 'KERNEL_REPLAY_PASS KomorebiLSM.'+m in r['stdout']
for m in CONTROLS:
 r=run('negative_control:'+m,[str(ROOT/'negative_controls'/f'{m}.lean')])
 r['expected_rejection']=True
 assert r['returncode']!=0 and 'False' in r['stdout'],r
 assert not any(s in r['stdout'] for s in ['unknown constant','unknown module','failed to synthesize','type mismatch','Type mismatch','timeout','unused']),r
 save()
assert report['source_sha256']=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in MODULES}
assert report['control_sha256']=={m:sha(ROOT/'negative_controls'/f'{m}.lean') for m in CONTROLS}
report['passed']=True;report['complete']=True;save();print('P69_INDIVIDUAL_PASS',flush=True)
