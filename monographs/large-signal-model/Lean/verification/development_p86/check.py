#!/usr/bin/env python3
"""Fresh individual checks for the four P86 marginal/window modules."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
LEAN='/workspace/scratch/ea498747acd5/runtime/gated-bin/lean'
freeze=json.loads((OUT/'SOURCE_FREEZE.json').read_text());mods=list(freeze)
controls=['MarkovContractionWithoutMinorization','MarkovRefreshDropsKernelError','MarkovRefreshRetainedRecord']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(v['source_sha256']==sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m,v in freeze.items())
r={'kind':'P86_actual_marginal_window_individual_checks','passed':False,'complete':False,'stages':[],
 'source_sha256':{m:v['source_sha256']for m,v in freeze.items()},
 'control_sha256':{c:sha(ROOT/'negative_controls'/f'{c}.lean')for c in controls},
 'dependency_sha256':{m:sha(ROOT/'KomorebiLSM'/f'{m}.lean')for m in ['MeasureTVCalculus','SequentialLowerCertificate']}}
def save():(OUT/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
def run(phase,args,extra=None):
 env=os.environ.copy()
 if extra:env.update(extra)
 start=time.monotonic();q=subprocess.run([LEAN,'-j1','-DwarningAsError=true']+args,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 s=dict(phase=phase,command=[LEAN,'-j1','-DwarningAsError=true']+args,returncode=q.returncode,seconds=round(time.monotonic()-start,3),stdout=q.stdout,stderr=q.stderr)
 r['stages'].append(s);save();print(phase,q.returncode,flush=True);return s
save()
for m in mods:
 s=run('compile:'+m,['-o',f'.build/lib/lean/KomorebiLSM/{m}.olean',f'KomorebiLSM/{m}.lean']);assert s['returncode']==0,s
s=run('axiom_audit',[str(OUT/'AxiomAudit.lean')]);assert s['returncode']==0,s
d=json.loads((OUT/'DECLARATIONS.json').read_text());expected={x['name']for x in d};a={}
for m in re.finditer(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",s['stdout'],re.S):
 name,raw=m.groups();assert name not in a;a[name]=sorted(x.strip()for x in (raw or '').split(',')if x.strip())
assert set(a)==expected,(set(a),expected)
assert all(set(v)<={'propext','Classical.choice','Quot.sound'}for v in a.values())
r['axioms']=a;r['named_declarations']=len(d);r['named_theorems']=sum(x['kind']=='theorem'for x in d);r['named_instances']=sum(x['kind']=='instance'for x in d);save()
for m in mods:
 s=run('kernel_replay:'+m,[str(ROOT/'scripts/ReplayModule.lean')],{'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.'+m})
 assert s['returncode']==0 and 'KERNEL_REPLAY_PASS KomorebiLSM.'+m in s['stdout'],s
for c in controls:
 s=run('negative_control:'+c,[str(ROOT/'negative_controls'/f'{c}.lean')]);s['expected_rejection']=True;save()
 assert s['returncode']!=0 and s['stdout'].count('error:')==1 and '⊢ False' in s['stdout'],s
 assert not any(x in s['stdout']for x in ['unknown constant','unknownIdentifier','failed to synthesize','type mismatch','Type mismatch','timeout','unused','noncomputable']),s
assert r['source_sha256']=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean')for m in mods}
assert r['control_sha256']=={c:sha(ROOT/'negative_controls'/f'{c}.lean')for c in controls}
assert r['dependency_sha256']=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean')for m in r['dependency_sha256']}
r['passed']=True;r['complete']=True;save();print('P86_MAIN_CORE_PASS',flush=True)
