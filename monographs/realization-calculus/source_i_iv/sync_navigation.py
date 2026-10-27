from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parent;changes=[];checks=[]
for roman in ['II','III','IV']:
 aux=next((ROOT/'compiled'/roman/'traditional').glob('*.aux'));text=aux.read_text();labels={};bykind={}
 for line in text.splitlines():
  m=re.match(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',line)
  if not m or '@cref' in m[1]:continue
  labels[m[1]]={'number':m[2],'page':m[3]}
  dest=re.search(r'\{(section|theorem|proposition|lemma|corollary|definition|roadmap)\.[^{}]+\}\{\}\}$',line)
  if dest:
   kind={'roadmap':'Formalization target'}.get(dest[1],dest[1].title());key=(kind,m[2]);prev=bykind.get(key)
   if prev and prev!=m[3]:raise ValueError(('ambiguous',roman,key,prev,m[3]))
   bykind[key]=m[3]
 maps=list((ROOT/roman).glob('**/canonical_label_to_final.json'));cross=json.loads(maps[0].read_text()) if maps else {}
 files=[]
 for p in (ROOT/roman).rglob('*.tex'):
  if '/publication/' in str(p) and '/publication_baseline/' not in str(p):continue
  if roman=='IV' and '/visual_guide/' in str(p):continue
  if p.name in ['traditional_crosswalk.tex','current_traditional_crosswalk.tex','visual_atlas.tex','pages_final.tex','reading_bridge.tex','atlas-pages.tex']:files.append(p)
 for p in files:
  s=p.read_text();old=s
  def loc(m):
   key=(m[1],m[2]);pg=bykind.get(key)
   if pg is None:return m[0]
   if pg!=m[3]:changes.append({'file':str(p.relative_to(ROOT)),'kind':m[1],'number':m[2],'old_page':m[3],'new_page':pg})
   checks.append({'file':str(p.relative_to(ROOT)),'kind':m[1],'number':m[2],'page':pg})
   return m[1]+' '+m[2]+' (p. '+pg+')'
  s=re.sub(r'(Formalization target|Definition|Lemma|Theorem|Proposition|Corollary|Section)\s+(\d+(?:\.\d+)?)\s+\(p\.\s*([ivxlcdm0-9]+)\)',loc,s)
  lines=[]
  for ln in s.splitlines(True):
   m=re.search(r'\\code\{([^}]+)\}.*?p\.~([ivxlcdm0-9]+)',ln)
   if m:
    label=cross.get(m[1],{}).get('final_label',m[1]);v=labels.get(label)
    if v:
     pg=v['page'];ln=ln[:m.start(2)]+pg+ln[m.end(2):]
     checks.append({'file':str(p.relative_to(ROOT)),'label':label,'page':pg})
     if pg!=m[2]:changes.append({'file':str(p.relative_to(ROOT)),'label':label,'old_page':m[2],'new_page':pg})
   lines.append(ln)
  s=''.join(lines)
  if s!=old:
   b=ROOT/'before'/p.relative_to(ROOT);b.parent.mkdir(parents=True,exist_ok=True)
   if not b.exists():b.write_bytes(p.read_bytes())
   p.write_text(s)
report={'scope':'page locator refresh only; statement identifiers and mathematical text retained','changes':changes,'checked_locators':len(checks),'checks':checks}
path=ROOT/'navigation_updates.json'
if path.exists():
 prev=json.loads(path.read_text());report['earlier_changes']=prev.get('earlier_changes',[])+prev['changes']
path.write_text(json.dumps(report,indent=2));print(json.dumps({'changes':len(changes),'checked':len(checks)}))
