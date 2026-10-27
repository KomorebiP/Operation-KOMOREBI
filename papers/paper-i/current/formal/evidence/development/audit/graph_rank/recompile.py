from pathlib import Path
import concurrent.futures,datetime,hashlib,json,subprocess,time
root=Path.cwd();out=root/'release_work/audit/graph_rank';(out/'objects').mkdir(exist_ok=True)
names=['BoundedStar','GraphSources','GraphPropagation','GraphSourceProjection','GraphSourceCount','PacketCorners','PacketPureRank','PacketLocalRank','PacketSourceLower','PacketSourceUpper','PacketSourceRank','GraphSourceBoundary','PacketPureBoundaryTests']
def run(name):
 p=root/'release_work/formal/PaperIRelease'/f'{name}.lean';s=hashlib.sha256(p.read_bytes()).hexdigest();t=time.monotonic();cmd=['bash',str(root/'release_work/runtime/run_lean.sh'),'-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-o',str(out/'objects'/f'{name}.olean'),str(p)]
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(out/f'{name}.log').write_text(r.stdout)
 return {'module':'PaperIRelease.'+name,'source_sha256':s,'post_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'exit_code':r.returncode,'elapsed_seconds':round(time.monotonic()-t,3),'log':str(out/f'{name}.log'),'command':cmd}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 results=list(ex.map(run,names))
(out/'compile_receipt.json').write_text(json.dumps({'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'note':'Independent strict source compilation; imports use authenticated session development objects. Final release closure is separately rebuilt and kernel-replayed by root.'},indent=2)+'\n')
print(json.dumps([{'module':r['module'],'exit_code':r['exit_code'],'stable':r['source_sha256']==r['post_sha256']} for r in results],indent=2))
