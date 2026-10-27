#!/usr/bin/env python3
"""Fresh source-bound checks for the P81 predictable multiplier helper."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
LEAN='/workspace/scratch/ea498747acd5/runtime/gated-bin/lean'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
M='ConditionalRandomMultiplier';C='ConditionalRandomUnpredictable'
r={'kind':'P81_conditional_random_multiplier_individual_checks','passed':False,'complete':False,
 'source_sha256':{M:sha(ROOT/'KomorebiLSM'/f'{M}.lean')},'stages':[],
 'control_support_sha256':{n:sha(ROOT/'KomorebiLSM'/f'{n}.lean') for n in ['ConditionalHoeffding','ConditionalBernoulli']}}
def save():(OUT/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
def run(phase,args,extra=None):
 env=os.environ.copy()
 if extra:env.update(extra)
 start=time.monotonic();q=subprocess.run([LEAN,'-j1','-DwarningAsError=true']+args,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 s=dict(phase=phase,command=[LEAN,'-j1','-DwarningAsError=true']+args,returncode=q.returncode,seconds=round(time.monotonic()-start,3),stdout=q.stdout,stderr=q.stderr)
 r['stages'].append(s);save();print(phase,q.returncode,flush=True);return s
save()
s=run('compile',['-o',f'.build/lib/lean/KomorebiLSM/{M}.olean',f'KomorebiLSM/{M}.lean']);assert s['returncode']==0,s
s=run('axiom_audit',[str(OUT/'AxiomAudit.lean')]);assert s['returncode']==0,s
decls=json.loads((OUT/'DECLARATIONS.json').read_text());expected={d['name'] for d in decls};parsed={}
for m in re.finditer(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",s['stdout'],re.S):
 name,raw=m.groups();assert name not in parsed
 parsed[name]=sorted(a.strip() for a in (raw or '').split(',') if a.strip())
assert set(parsed)==expected,(set(parsed),expected)
assert all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in parsed.values())
r['axioms']=parsed;r['named_declarations']=len(decls);r['named_theorems']=sum(d['kind']=='theorem' for d in decls);save()
s=run('kernel_replay',[str(ROOT/'scripts/ReplayModule.lean')],{'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.'+M})
assert s['returncode']==0 and 'KERNEL_REPLAY_PASS KomorebiLSM.'+M in s['stdout'],s
r['control_sha256']={C:sha(ROOT/'negative_controls'/f'{C}.lean')};save()
s=run('negative_control',[str(ROOT/'negative_controls'/f'{C}.lean')]);s['expected_rejection']=True;save()
assert s['returncode']!=0 and 'False' in s['stdout'],s
assert not any(x in s['stdout'] for x in ['unknown constant','unknownIdentifier','failed to synthesize','type mismatch','Type mismatch','timeout','unused','noncomputable']),s
assert r['source_sha256'][M]==sha(ROOT/'KomorebiLSM'/f'{M}.lean')
assert r['control_sha256'][C]==sha(ROOT/'negative_controls'/f'{C}.lean')
r['passed']=True;r['complete']=True;save();print('P81_RANDOM_MULTIPLIER_PASS',flush=True)
