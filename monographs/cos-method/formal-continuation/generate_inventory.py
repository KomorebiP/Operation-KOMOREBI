from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent
rows=[]
for p in sorted((ROOT/'lean/KomorebiQCOS').glob('*.lean')):
 for m in re.finditer(r'(?m)^(?:@\[[^\]]*\]\s+)?(?:noncomputable\s+)?(theorem|lemma|def|instance)\s+([A-Za-z_][A-Za-z_0-9]*)',p.read_text()):
  rows.append({'name':'KomorebiQCOS.'+m[2],'kind':m[1],'file':str(p.relative_to(ROOT)),'line':p.read_text()[:m.start()].count('\n')+1})
controls=[]
for p in [ROOT/'lean/Controls/Positive.lean',ROOT/'lean/Controls/RecordedTilted.lean']:
 ns=re.search(r'(?m)^namespace (\w+)',p.read_text())[1]
 controls.extend(ns+'.'+m[1] for m in re.finditer(r'(?m)^theorem (\w+)',p.read_text()))
d=dict(theorems=sum(x['kind'] in ['theorem','lemma'] for x in rows),definitions=sum(x['kind']=='def' for x in rows),instances=sum(x['kind']=='instance' for x in rows),declarations=rows,controls=controls)
(ROOT/'docs/DECLARATIONS.json').write_text(json.dumps(d,indent=2)+'\n')
print({k:v for k,v in d.items() if k not in ['declarations','controls']},'audited',len(rows),'controls',len(controls))
