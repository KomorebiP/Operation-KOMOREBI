from pathlib import Path
import json,re,subprocess,time,hashlib
R=Path('/mnt/data/Komorebi_Physics_Lean_v0.6.0')
O=Path('/mnt/data/block06_negative_batch_probe');O.mkdir(exist_ok=True)
source=(R/'scripts/verify.py').read_text();a=source.index('        controls = '); b=source.index('        control_files = ',a)
controls=eval(source[a+len('        controls = '):b].strip())
imports=set();bodies={}
for name in controls:
 lines=(R/'negative_controls'/f'{name}.lean').read_text().splitlines()
 imports.update(x for x in lines if x.startswith('import '))
 bodies[name]=[x for x in lines if not x.startswith('import ')]
lines=sorted(imports)+[''];records=[]
for name in controls:
 lines+=['namespace NegativeBatch_'+name]
 start=len(lines)+1
 lines+=bodies[name]
 records.append({'name':name,'start_line':start,'end_line':len(lines),'diagnostic':controls[name]})
 lines+=['end NegativeBatch_'+name,'']
p=O/'negative_batch.lean';p.write_text('\n'.join(lines)+'\n')
t=time.monotonic();cmd=['bash','/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2/run.sh','lake','env','lean','-j1','-DwarningAsError=true',str(p)]
try:
 r=subprocess.run(cmd,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
 text=r.stdout;(O/'negative_batch.log').write_text(text)
 matches=list(re.finditer(r'^.*?:(\d+):\d+: (?:error(?:\([^\n]*?\))?|warning):',text,re.M))
 messages=[(int(m[1]),text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)]) for i,m in enumerate(matches)]
 for rec in records:
  rec['messages']=[msg for line,msg in messages if rec['start_line']<=line<=rec['end_line']]
  rec['status']='PASS' if any(rec['diagnostic'] in msg for msg in rec['messages']) else 'FAIL'
 unassigned=[line for line,_ in messages if not any(q['start_line']<=line<=q['end_line'] for q in records)]
 status='PASS' if r.returncode!=0 and all(q['status']=='PASS' for q in records) and not unassigned else 'FAIL'
 report={'status':status,'returncode':r.returncode,'controls':records,'unassigned':unassigned,'seconds':time.monotonic()-t,'messages':len(messages),'argv':cmd,'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
except subprocess.TimeoutExpired:
 report={'status':'TIMEOUT','seconds':time.monotonic()-t,'argv':cmd}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],report['seconds'])
