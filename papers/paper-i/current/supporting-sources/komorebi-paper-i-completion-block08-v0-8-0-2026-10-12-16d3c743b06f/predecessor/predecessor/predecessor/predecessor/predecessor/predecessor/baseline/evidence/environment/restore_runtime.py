from pathlib import Path
import zipfile,hashlib,json,subprocess,time
base=Path('/mnt/data/runtime_parts'); out=Path('/mnt/data/runtime'); out.mkdir(exist_ok=True)
reference=json.loads((base/'LEAN_RUNTIME_READY.json').read_text())
report={'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'RUNNING','parts':[]}
path=Path('/mnt/data/environment/runtime_restore.json')
def save(): path.write_text(json.dumps(report,indent=2)+'\n')
save()
archive=base/'offline.tar.zst'; overall=hashlib.sha256()
with archive.open('wb') as dst:
 for i in range(1,8):
  p=base/f'Lean_Offline_{i:02}.zip'; h=hashlib.sha256(); count=0
  with zipfile.ZipFile(p) as z:
   ns=z.namelist(); assert len(ns)==1,ns
   with z.open(ns[0]) as src:
    while b:=src.read(4*1024*1024): h.update(b);overall.update(b);dst.write(b);count+=len(b)
  expected=reference['archive']['part_records'][i-1]
  assert count==expected['bytes'] and h.hexdigest()==expected['sha256'],(i,count,h.hexdigest())
  report['parts'].append({'file':p.name,'member':ns[0],'bytes':count,'sha256':h.hexdigest(),'crc_checked_on_read':True}); save(); print('Verified part',i,flush=True)
assert overall.hexdigest()==reference['archive']['verified_sha256']
report['archive_sha256']=overall.hexdigest(); report['archive_bytes']=archive.stat().st_size; save()
start=time.monotonic()
p=subprocess.run(['tar','--zstd','-xf',str(archive),'-C',str(out)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
report['extract_returncode']=p.returncode;report['extract_output']=p.stdout;report['extract_seconds']=time.monotonic()-start
report['status']='PASS' if p.returncode==0 else 'FAIL'; save(); print(json.dumps(report,indent=2),flush=True)
