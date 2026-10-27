from pathlib import Path
import hashlib,json,io,re,zipfile,datetime
import fitz
from fontTools.ttLib import TTFont
from fontTools.cffLib import CFFFontSet
import matplotlib
W=Path('/dev/shm/komorebi_paper_xi_freeze_fbc994080222');B=W/'baseline/Paper_XI_Complete_v1.1.0';A=W/'audit_licenses'
OLD=Path('/dev/shm/komorebi_paper_x_freeze_fbc994080222/audit_licenses')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(x).hexdigest()
def normname(s):return re.sub(r'^[A-Z]{6}\+','',s or '').removesuffix('-Identity-H')
def psstr(s,start):
 i=start+1;out=[];depth=1
 while i<len(s) and depth:
  c=s[i]
  if c=='\\':
   out.append(c);i+=1
   if i<len(s):out.append(s[i])
  elif c=='(':depth+=1;out.append(c)
  elif c==')':
   depth-=1
   if depth:out.append(c)
  else:out.append(c)
  i+=1
 return ''.join(out)
def unesc(s):
 if s is None:return None
 return re.sub(r'\\([0-7]{1,3})',lambda m:chr(int(m[1],8)),s).replace('\\(','(').replace('\\)',')').replace('\\\\','\\')
def psmeta(data):
 s=data.decode('latin1',errors='replace').split('currentfile eexec')[0]
 r={}
 for key,out in [('FontName','postscript_name'),('version','version'),('FullName','full_name'),('FamilyName','family_name'),('Notice','notice'),('Copyright','copyright')]:
  m=re.search('/'+re.escape(key)+r'\s*(\(|/)',s)
  if m:
   r[out]=psstr(s,m.end()-1) if m[1]=='(' else re.match(r'[^\s\[\]{}()<>/%]+',s[m.end():])[0]
 return r
fields={'version':'version','FullName':'full_name','FamilyName':'family_name','Notice':'notice','Copyright':'copyright'}
def cffmeta(data):
 c=CFFFontSet();c.decompile(io.BytesIO(data),None);t=c.topDictIndex[0]
 return {'postscript_name':str(c.fontNames[0]),**{out:str(getattr(t,k)) for k,out in fields.items() if hasattr(t,k)}}
def ttmeta(data):
 f=TTFont(io.BytesIO(data));t=f['name'];r={out:t.getDebugName(k) for k,out in [(0,'copyright'),(1,'family_name'),(4,'full_name'),(5,'version'),(6,'postscript_name'),(13,'license_description'),(14,'license_url')] if t.getDebugName(k) is not None}
 return r
embedded={};inputs=[];errors=[]
for p in sorted((B/'publication/pdfs').glob('*.pdf')):
 d=fitz.open(p);inputs.append({'path':p.relative_to(B).as_posix(),'pages':len(d),'sha256':sha(p)})
 seen=set()
 for page in range(len(d)):
  for f in d.get_page_fonts(page,full=True):
   if f[0] in seen:continue
   seen.add(f[0]);xref=f[0]
   try:
    name,ext,typ,data=d.extract_font(xref);key=(normname(f[3]),digest(data) if data else 'no-program',typ)
    if key not in embedded:
     meta=(ttmeta(data) if ext in ['ttf','otf'] else cffmeta(data) if ext in ['cff','cid'] else psmeta(data) if ext in ['pfa','pfb'] else {}) if data else {}
     embedded[key]={'resource_font_name':normname(f[3]),'format':ext,'type':typ,'bytes':len(data),'sha256':digest(data) if data else None,'metadata':meta,'occurrences':[]}
    embedded[key]['occurrences'].append({'pdf':p.relative_to(B).as_posix(),'xref':xref,'first_page':page+1,'raw_resource_name':f[3]})
   except Exception as e:errors.append({'pdf':p.relative_to(B).as_posix(),'xref':xref,'font':f[3],'error':str(e)})
old=json.loads((OLD/'EMBEDDED_FONT_METADATA.json').read_text())
paths={Path(c['path']) for c in old['installed_candidates']}
paths|={Path('/usr/share/texmf/fonts/type1/public/lm/lmtt10.pfb'),Path('/usr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/symbols/msam10.pfb')}
M=Path(matplotlib.get_data_path())/'fonts/ttf'
paths|=set(M.glob('*.ttf'))
paths|=set(Path('/usr/share/fonts/opentype/urw-base35').glob('*.otf'))
paths|=set(Path('/usr/share/fonts/truetype/dejavu').glob('*.ttf'))
candidates=[];lookup_errors=[]
for p in sorted(paths):
 if not p.is_file():lookup_errors.append({'path':str(p),'error':'not present'});continue
 try:
  data=p.read_bytes();meta=ttmeta(data) if p.suffix.lower() in ['.ttf','.otf'] else psmeta(data)
  row={'path':str(p),'sha256':sha(p),'metadata':meta}
  if p.suffix.lower()=='.otf':
   ff=TTFont(p)
   if 'CFF ' in ff:
    c=ff['CFF '].cff;t=c.topDictIndex[0];row['CFF_metadata']={'postscript_name':str(c.fontNames[0]),**{o:str(getattr(t,k)) for k,o in fields.items() if hasattr(t,k)}}
  candidates.append(row)
 except Exception as e:lookup_errors.append({'path':str(p),'error':str(e)})
for e in embedded.values():
 n=normname(e['metadata'].get('postscript_name') or e['resource_font_name']);matches=[]
 for c in candidates:
  for layer,m in [('main',c['metadata']),('CFF',c.get('CFF_metadata',{}))]:
   if normname(m.get('postscript_name'))!=n:continue
   keys=sorted(set(e['metadata'])&set(m)-{'postscript_name'})
   matches.append({'path':c['path'],'sha256':c['sha256'],'layer':layer,'equal_fields':[k for k in keys if e['metadata'][k]==m[k]],'equal_after_explicit_PostScript_octal_unescaping':[k for k in keys if e['metadata'][k]!=m[k] and unesc(e['metadata'][k])==unesc(m[k])],'different_fields':[{'field':k,'embedded':e['metadata'][k],'installed':m[k]} for k in keys if unesc(e['metadata'][k])!=unesc(m[k])]})
 e['installed_name_matches']=matches
 e['evidence_status']='PostScript-name candidate plus listed metadata comparisons; no exact whole-font identity inferred' if matches else 'No installed candidate matched; retain explicit origin limitation'
r={'audit':'Paper XI current-reader font metadata and bounded installed-candidate comparison','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Current five readers only; subset metadata does not establish exact whole-font identity. All baseline bytes unchanged.','input_readers':inputs,'unique_resource_font_names':len({e['resource_font_name'] for e in embedded.values()}),'unique_font_program_records':len(embedded),'font_program_metadata_parsed_records':sum(bool(e['metadata']) for e in embedded.values()),'embedded_fonts':list(embedded.values()),'installed_candidates':candidates,'candidate_lookup_errors':lookup_errors,'extraction_errors':errors,'name_only_origin_limits':[{'font':e['resource_font_name'],'type':e['type']} for e in embedded.values() if not e['metadata']],'unmatched_fonts':[{'font':e['resource_font_name'],'metadata':e['metadata']} for e in embedded.values() if not e['installed_name_matches']]}
(A/'EMBEDDED_FONT_METADATA.json').write_text(json.dumps(r,indent=2)+'\n')
pdfs=[]
for p in sorted(B.rglob('*.pdf')):
 try:
  d=fitz.open(p);names={normname(f[3]) for i in range(len(d)) for f in d.get_page_fonts(i,full=True)};pdfs.append({'path':p.relative_to(B).as_posix(),'pages':len(d),'sha256':sha(p),'resource_fonts':sorted(names)})
 except Exception as e:pdfs.append({'path':p.relative_to(B).as_posix(),'error':str(e)})
(A/'PDF_FONT_INVENTORY.json').write_text(json.dumps(pdfs,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ['embedded_fonts','installed_candidates','input_readers']},indent=2))
