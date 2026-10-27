from pathlib import Path
import re,os,subprocess,time,json,hashlib
root=Path(__file__).resolve().parents[2]; kit=root.parent/'runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2'; out=root/'evidence/actual_adapter'; source=root/'formalization/PaperXI/ActualScalarLift113.lean'; module='PaperXI.ActualScalarLift113'
namespace='PaperXI.ActualScalarLift113'; decl=[]
for line in source.read_text().splitlines():
 if line=='namespace ScalarLift': namespace='PaperXI.ActualScalarLift113.ScalarLift'
 if line=='end ScalarLift': namespace='PaperXI.ActualScalarLift113'
 match=re.match(r'(?:@\[.*\]\s*)?(def|theorem|structure)\s+(\w+)',line)
 if match: decl.append({'kind':match[1],'name':namespace+'.'+match[2]})
text='import '+module+'\n'+''.join('#check '+d['name']+'\n#print axioms '+d['name']+'\n' for d in decl)
audit=out/'ActualScalarLift113_Audit.lean';audit.write_text(text)
env=os.environ.copy();env['LD_PRELOAD']=str(kit/'compat/app_path.so');env['PATH']=str(kit/'toolchain/bin')+':'+env['PATH'];env['LEAN_PATH']=':'.join(map(str,[out/'objects',*sorted((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]))
receipt={'module':module,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'declarations':decl}
for name,cmd in [('axioms',[str(kit/'toolchain/bin/lean'),'-j1','-DwarningAsError=true',str(audit)]),('leanchecker',[str(kit/'toolchain/bin/leanchecker'),'--verbose',module])]:
 t=time.monotonic();r=subprocess.run(cmd,env=env,cwd=root,capture_output=True,text=True,timeout=120);log=r.stdout+r.stderr;(out/f'ActualScalarLift113_{name}.log').write_text(log);receipt[name]={'exit_code':r.returncode,'seconds':time.monotonic()-t};assert r.returncode==0,log
 if name=='axioms':
  found=re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",log,re.S);empty=re.findall(r"'([^']+)' does not depend on any axioms",log)
  assert {n for n,_ in found}|set(empty)=={d['name'] for d in decl}
  axioms={a.strip() for _,s in found for a in s.split(',') if a.strip()};assert axioms<={'Classical.choice','Quot.sound','propext'},axioms
  receipt['allowed_axioms']=sorted(axioms)
receipt['status']='PASS';receipt['exports_audited']=len(decl);receipt['objects']={ext:hashlib.sha256((out/'objects/PaperXI/ActualScalarLift113').with_suffix(ext).read_bytes()).hexdigest() for ext in ('.olean','.ilean')}
(out/'ACTUAL_ADAPTER_AUDIT113.json').write_text(json.dumps(receipt,indent=2)+'\n'); print(json.dumps({k:receipt[k] for k in ('status','source_sha256','exports_audited','allowed_axioms')}))
