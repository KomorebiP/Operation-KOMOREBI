from pathlib import Path
import datetime, hashlib, json, os, subprocess
base=Path(__file__).resolve().parent
kit=base/'runtime/Komorebi_Portable_Lean_4.34.0-rc2'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
env=os.environ.copy();env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env['PATH'];env['LD_PRELOAD']=str(kit/'compat/app_path.so')
for key in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:env.pop(key,None)
commands=[]
def run(argv,cwd=kit):
 p=subprocess.run(argv,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
 commands.append({'argv':argv,'cwd':str(cwd),'exit_code':p.returncode,'output':p.stdout})
 assert p.returncode==0,p.stdout
 return p.stdout.strip()
lean=run(['lean','--version']);lake=run(['lake','--version'])
assert '6a10ac8c22beadecabdbb0919c2b50214762f91d' in lean
pins=json.loads((kit/'workspace/lake-manifest.json').read_text())['packages'];actual={}
for p in pins:
 value=run(['git','rev-parse','HEAD'],kit/'workspace/.lake/packages'/p['name']);assert value==p['rev'];actual[p['name']]=value
audit=json.loads((base/'runtime_integrity_audit.json').read_text())
assert len(audit['mismatches'])==9 and all(x['path'].endswith('/.git/index') for x in audit['mismatches'])
log=(base/'runtime_verification.log').read_text();passed=[x[5:] for x in log.splitlines() if x.startswith('PASS ')]
assert len(passed)==16
tracked=['toolchain/bin/lean','toolchain/bin/lake','toolchain/bin/leanchecker','compat/app_path.so','workspace/lake-manifest.json','verification/file-manifest.json']
record={'schema':'komorebi.physics.runtime-recovery.v1','status':'READY_WITH_RECORDED_METADATA_DIFFERENCES','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kit_path':str(kit),'lean_version':lean,'lake_version':lake,'dependency_commits':actual,'combined_archive':{'bytes':2220147424,'sha256':'f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7','verified_by':'runtime_assembly.log'},'exact_file_hashes':{x:sha(kit/x) for x in tracked},'integrity':{'declared_rows':audit['rows'],'checked_regular_file_bytes':audit['checked_bytes'],'all_declared_rows_match':False,'differences':audit['mismatches'],'unstable_during_read':audit['unstable_during_read'],'interpretation':'Only nine dependency Git index files differ from shipped manifest. Every other declared row matched during the scan. This is not an exact inventory check for extra files, a dependency rebuild, or an independent kernel.'},'compiler_checks':{'passed':passed,'count':16,'source':'runtime_verification.log','formal_suite_exit_code':1,'scope':'All 16 compiler/runtime checks passed before optional all-files integrity failed. The original report write then failed for lack of disk space; the empty JSON is retained.'},'commands':commands,'failures':[{'action':'Unadapted direct Lean startup','result':'exit 1: error: failed to locate application','resolution':'Enabled the shipped compat/app_path.so adapter; exact requested compiler then ran.'},{'action':'Optional all-files integrity check','result':'Failed at dependency Cli/.git/index','resolution':'A complete read-only audit recorded nine Git-index mismatches and no other declared-row mismatch; the strict identity failure remains recorded.'},{'action':'First runtime verification JSON write','result':'OSError: [Errno 28] No space left on device','resolution':'Preserved raw passing/failure log and empty output. Removed re-downloadable archive/chunks and stale transfer files; wrote this consolidated receipt.'},{'action':'Optional process-list probe','result':'ps: fatal library error, lookup self','resolution':'No process-list result used as verification evidence.'}],'trust_boundary':'Compiler and precompiled dependencies restored from authenticated compact archive. Runtime checks execute the stored compiler and use the stored cache. They do not independently establish compiler correctness or rebuild dependencies.'}
for n in ['runtime_assembly.log','runtime_extraction.log','runtime_verification.log','runtime_integrity_audit.json','runtime_disk_cleanup.json','runtime_transfer_cleanup.json']:
 record.setdefault('evidence_sha256',{})[n]=sha(base/n)
(base/'runtime_recovery_receipt.json').write_text(json.dumps(record,indent=2)+'\n')
(base/'runtime_environment.sh').write_text('export KOMOREBI_LEAN_KIT='+str(kit)+'\nexport PATH="$KOMOREBI_LEAN_KIT/toolchain/bin:$PATH"\nexport LD_PRELOAD="$KOMOREBI_LEAN_KIT/compat/app_path.so"\nunset LEAN_PATH LEAN_SRC_PATH LEAN_SYSROOT LAKE_HOME\n')
print(json.dumps({'status':record['status'],'receipt':str(base/'runtime_recovery_receipt.json'),'receipt_sha256':sha(base/'runtime_recovery_receipt.json'),'compiler_checks':len(passed),'declared_rows':audit['rows'],'metadata_only_differences':len(audit['mismatches'])},indent=2))
