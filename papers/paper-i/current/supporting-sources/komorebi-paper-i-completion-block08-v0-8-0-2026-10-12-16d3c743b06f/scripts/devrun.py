from pathlib import Path
import os,sys,json,time,subprocess,hashlib,shutil,signal
root=Path(__file__).resolve().parents[1]; rel=sys.argv[1]; src=root/'source/extension'/rel
if not src.exists():src=root/rel
stamp=time.strftime('%H%M%S')+'_'+str(time.time_ns()%1000000000); d=root/'evidence/development'/stamp;d.mkdir()
shutil.copy2(src,d/src.name);en=os.environ.copy();base=json.load(open('/mnt/data/lake_env08.json'));en.update(base)
paths=[s for s in en['LEAN_PATH'].split(':') if '/packages/' in s or s.endswith('/toolchain/lib/lean')]
en['LEAN_PATH']=':'.join([str(root/'evidence/dev_objects'),str(root/'evidence/dev_imports'),*paths])
obj=root/'evidence/dev_objects'/Path(rel).with_suffix('.olean');obj.parent.mkdir(parents=True,exist_ok=True)
cmd=['lean','-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3','-o',str(obj),str(src)]
start=time.monotonic()
with (d/'compile.log').open('w') as f:
 p=subprocess.Popen(cmd,env=en,cwd=root/'source/extension' if 'source/extension' in str(src) else src.parent,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=p.wait(timeout=int(os.environ.get("KOMOREBI_DEV_TIMEOUT", "420")))
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
receipt={'source':str(src.relative_to(root)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'command':cmd,'exit':code,'seconds':round(time.monotonic()-start,3)}
(d/'receipt.json').write_text(json.dumps(receipt,indent=2));print(d,code,flush=True);print((d/'compile.log').read_text(),flush=True)

raise SystemExit(code)
