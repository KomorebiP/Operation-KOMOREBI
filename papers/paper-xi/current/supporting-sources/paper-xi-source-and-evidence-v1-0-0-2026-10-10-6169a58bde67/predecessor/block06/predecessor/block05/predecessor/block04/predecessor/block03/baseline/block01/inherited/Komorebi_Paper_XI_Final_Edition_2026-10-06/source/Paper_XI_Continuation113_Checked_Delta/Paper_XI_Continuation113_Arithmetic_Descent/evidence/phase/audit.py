from pathlib import Path
import os, subprocess, json, hashlib, time, re, collections, sys
root=Path('/workspace/scratch/bec226d7ce4b')
proj=root/'Paper_XI_Continuation113_Arithmetic_Descent'
kit=root/'runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2'
evidence=proj/'evidence/phase'
source=proj/'formalization/PaperXI/CyclicNormalization113.lean'
objects=evidence/'objects'
base=root/'Paper_XI_Continuation112_Realization_Test/build'
env=os.environ.copy();env['LD_PRELOAD']=str(kit/'compat/app_path.so')
env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
env['LEAN_PATH']=':'.join(map(str,[objects]+sorted((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
text=source.read_text();decls=[]
for line in text.splitlines():
 m=re.match(r'^(?:@\[[^\n]+\]\s*)?(?:noncomputable\s+)?(theorem|lemma|def|abbrev|instance|structure)\s+([\w.\']+)',line)
 if m:decls.append({'kind':m[1],'name':'PaperXI.CyclicNormalization113.'+m[2]})
assert len(set(d['name'] for d in decls))==len(decls)
audit=evidence/'CyclicNormalization113_Audit.lean'
audit.write_text('import PaperXI.CyclicNormalization113\n'+''.join('#check '+d['name']+'\n#print axioms '+d['name']+'\n' for d in decls))
receipt={'status':'RUNNING','source_sha256':sha(source),'module':'PaperXI.CyclicNormalization113','declarations':decls,'counts':dict(collections.Counter(d['kind'] for d in decls)),'baseline_rebuilt':False,'checks':[]}
for kind,argv in [('axioms',[str(kit/'toolchain/bin/lean'),'-j1','-DmaxHeartbeats=3000000','-DwarningAsError=true',str(audit)]),('leanchecker',[str(kit/'toolchain/bin/leanchecker'),'--verbose','PaperXI.CyclicNormalization113'])]:
 t0=time.monotonic();r=subprocess.run(argv,env=env,cwd=proj,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
 (evidence/('CyclicNormalization113_'+kind+'.log')).write_text(r.stdout)
 receipt['checks'].append({'kind':kind,'argv':argv,'seconds':time.monotonic()-t0,'exit_code':r.returncode})
 if r.returncode: print(r.stdout);raise RuntimeError(kind+' failed')
 if kind=='axioms':
  found=re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",r.stdout,re.S)
  empty=re.findall(r"'([^']+)' does not depend on any axioms",r.stdout)
  assert {n for n,_ in found}|set(empty)=={d['name'] for d in decls}
  axioms={a.strip() for _,body in found for a in body.split(',') if a.strip()}
  assert axioms<={'Classical.choice','propext','Quot.sound'}
  receipt['axioms']=sorted(axioms);receipt['exports_audited']=len(decls)
receipt['objects']={suffix:sha(objects/('PaperXI/CyclicNormalization113'+suffix)) for suffix in ['.olean','.ilean']}
receipt['status']='PASS'
(evidence/'FINAL_PHASE_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
