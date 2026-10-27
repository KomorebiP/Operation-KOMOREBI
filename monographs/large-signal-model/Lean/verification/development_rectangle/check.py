from pathlib import Path
import subprocess,os,json,hashlib,re,time
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
mods=['CurvedMomentRecordTV','StructuredRectangle']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze={m:sha(root/'KomorebiLSM'/f'{m}.lean') for m in mods}
controls=['StructuredRectangleCenterOnly']
r={'kind':'P85_record_repair_and_P87_deterministic_rectangle_author_checks','complete':False,'passed':False,'source_sha256':freeze,'stages':[], 'verification_boundary':'Fresh author compilation, named declaration axioms, imported-module kernel replay and semantic control in isolated author library. Most unchanged dependency artifacts inherited after matching current dependency source bytes; cumulative project verification is separate.'}
def run(name,args,extra=None):
 env=os.environ.copy()
 if extra:env.update(extra)
 t=time.monotonic();p=subprocess.run(['lean','-j1','-DwarningAsError=true']+args,cwd=root,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 s={'phase':name,'command':['lean','-j1','-DwarningAsError=true']+args,'returncode':p.returncode,'seconds':round(time.monotonic()-t,3),'stdout':p.stdout,'stderr':p.stderr}
 (out/(name.replace(':','_')+'.stdout')).write_text(p.stdout);(out/(name.replace(':','_')+'.stderr')).write_text(p.stderr)
 r['stages'].append(s);(out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(name,p.returncode,flush=True);return s
for m in mods:
 s=run('compile:'+m,['-o',f'.authorbuild/lib/lean/KomorebiLSM/{m}.olean',f'KomorebiLSM/{m}.lean']);assert s['returncode']==0,s
s=run('axiom_audit',[str(out/'AxiomAudit.lean')]);assert s['returncode']==0,s
a={}
for m in re.finditer(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",s['stdout'],re.S):
 name,raw=m.groups();assert name not in a;a[name]=sorted(x.strip()for x in (raw or '').split(',')if x.strip())
assert set(a)==set(json.loads((out/'DECLARATIONS.json').read_text()))
assert all(set(v)<={'propext','Classical.choice','Quot.sound'}for v in a.values());r['axioms']=a;r['named_declarations']=len(a)
for m in mods:
 s=run('kernel_replay:'+m,['scripts/ReplayModule.lean'],{'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.'+m});assert s['returncode']==0 and 'KERNEL_REPLAY_PASS KomorebiLSM.'+m in s['stdout'],s
for c in controls:
 s=run('negative_control:'+c,[f'negative_controls/{c}.lean']);s['expected_rejection']=True
 assert s['returncode']!=0 and s['stdout'].count('error:')==1 and '⊢ False' in s['stdout'],s
 assert not any(x in s['stdout'] for x in ['unknown constant','unknownIdentifier','failed to synthesize','type mismatch','timeout']),s
assert freeze=={m:sha(root/'KomorebiLSM'/f'{m}.lean')for m in mods}
r['control_sha256']={c:sha(root/'negative_controls'/f'{c}.lean')for c in controls};r['complete']=True;r['passed']=True
(out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print('AUTHOR_CHECKS_PASS',flush=True)
