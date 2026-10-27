from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path('/workspace/scratch/9f53d520971c')
evidence=root/'release_work/evidence'
source=evidence/'CoverageDeclarations.lean'
env=os.environ.copy();env['LEAN_PATH']=str(root/'release_work/final_audit_v4/objects')+os.pathsep+env['LEAN_PATH']
command=['lean','-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false',str(source)]
started=time.monotonic();result=subprocess.run(command,env=env,capture_output=True,text=True)
log=evidence/'coverage_declarations_final_entry.log';log.write_text(result.stdout+result.stderr)
receipt={'status':'PASS' if result.returncode==0 else 'FAIL','exit':result.returncode,'command':command,'elapsed_seconds':time.monotonic()-started,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'unique_declarations':468,'entrypoint':'PaperIRelease','accepted_formal_receipt_sha256':hashlib.sha256((root/'release_work/final_audit_v4/verification.json').read_bytes()).hexdigest()}
(evidence/'coverage_declarations_final_entry.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt));raise SystemExit(result.returncode)
