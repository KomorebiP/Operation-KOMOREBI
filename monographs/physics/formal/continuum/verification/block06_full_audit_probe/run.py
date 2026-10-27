import subprocess,time,json,hashlib
from pathlib import Path
R=Path('/mnt/data/Komorebi_Physics_Lean_v0.6.0')
O=Path('/mnt/data/block06_full_audit_probe')
t=time.monotonic()
cmd=['bash','/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2/run.sh','lake','env','lean','-j1','-DwarningAsError=true','Audit.lean']
r={'status':'INCOMPLETE','argv':cmd}
try:
 p=subprocess.run(cmd,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
 (O/'audit.log').write_text(p.stdout)
 r.update(status='PASS' if p.returncode==0 else 'FAIL',returncode=p.returncode)
except subprocess.TimeoutExpired as e:
 r['status']='TIMEOUT'
 text=e.stdout or ''
 if isinstance(text,bytes):text=text.decode(errors='replace')
 (O/'audit.log').write_text(text)
r['seconds']=time.monotonic()-t
(O/'report.json').write_text(json.dumps(r,indent=2))
