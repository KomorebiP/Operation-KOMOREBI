#!/usr/bin/env python3
"""Bind final publication source, build and raster evidence; no compilation."""
from pathlib import Path
import datetime,difflib,hashlib,json,re,shutil
import fitz

BASE=Path('/workspace/scratch/604befec1954')
ROOT=BASE/'paperxi_release'
BUILD=BASE/'paperxi_build_1_1_published'
EVIDENCE=ROOT/'evidence/release_1_1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

record=json.loads((BUILD/'BUILD_RECORD.json').read_text())
assert record['status']=='passed'
name_map={
 'traditional':('Paper_XI_Traditional_Final','Paper_XI_Traditional_v1.1.0.pdf'),
 'visual_guide':('Paper_XI_Visual_Guide_Final','Paper_XI_Visual_Guide_v1.1.0.pdf'),
 'lean_guide':('Paper_XI_Lean_Guide_Final','Paper_XI_Lean_Guide_v1.1.0.pdf')}
raster=[]
for kind,(stem,name) in name_map.items():
 raw=BUILD/'build'/kind/(stem+'.pdf');final=BUILD/name
 assert sha(raw)==record['records'][kind]['raw_sha256']
 assert sha(final)==record['records'][kind]['sha256']
 a=fitz.open(raw);b=fitz.open(final);assert len(a)==len(b)
 rows=[]
 for i in range(len(a)):
  x=a[i].get_pixmap(dpi=96,alpha=False);y=b[i].get_pixmap(dpi=96,alpha=False)
  assert (x.width,x.height,x.samples)==(y.width,y.height,y.samples),(kind,i+1)
  rows.append({'page':i+1,'rgb_sha256':hashlib.sha256(x.samples).hexdigest()})
 raster.append({'kind':kind,'file':name,'pages':len(a),'raw_pdf_sha256':sha(raw),'assembled_pdf_sha256':sha(final),'all_pages_pixel_identical':True,'page_raster_hashes':rows})
 a.close();b.close()
 old=ROOT/'publication/pdfs'/name.replace('v1.1.0','v1.0.0')
 if old.exists():old.unlink()
 shutil.copy2(final,ROOT/'publication/pdfs'/name)
 out=ROOT/'verification/publication'/kind;out.mkdir(parents=True,exist_ok=True)
 shutil.copy2(BUILD/f'COMPILE_{kind}.json',out/f'COMPILE_{kind}.json')
 for p in (BUILD/'build'/kind).iterdir():
  if p.is_file() and (p.suffix in ['.aux','.log','.bbl','.blg','.fls','.toc','.out'] or p.name=='komorebi-font-paths.tex'):
   shutil.copy2(p,out/p.name)

shutil.copy2(BUILD/'BUILD_RECORD.json',EVIDENCE/'BUILD_RECORD.json')
write_json(EVIDENCE/'ASSEMBLY_RASTER_CHECK.json',{
 'status':'passed','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'renderer':'PyMuPDF '+fitz.VersionBind,'dpi':96,
 'scope':'All pages of the three raw compiled readers compared with their companion-link-assembled final PDFs; RGB sample bytes must be identical. This binds the raw-reader visual reviews to the final delivered PDFs.',
 'records':raster})

oldroot=BASE/'paperxi_work/publication/source';newroot=ROOT/'publication/source'
old={str(p.relative_to(oldroot)):p for p in oldroot.rglob('*') if p.is_file()}
new={str(p.relative_to(newroot)):p for p in newroot.rglob('*') if p.is_file()}
changes=[];patches=[]
for relative in sorted(set(old)|set(new)):
 a=old.get(relative);b=new.get(relative)
 if a and b and a.read_bytes()==b.read_bytes():continue
 changes.append({'path':'publication/source/'+relative,'status':'added' if a is None else 'removed' if b is None else 'modified','before_sha256':sha(a) if a else None,'after_sha256':sha(b) if b else None})
 if Path(relative).suffix in ['.tex','.sty','.bib','.md','.lean']:
  left=a.read_text().splitlines(keepends=True) if a else []
  right=b.read_text().splitlines(keepends=True) if b else []
  patches.extend(difflib.unified_diff(left,right,fromfile='v1.0.0/publication/source/'+relative if a else '/dev/null',tofile='v1.1.0/publication/source/'+relative if b else '/dev/null'))
main='traditional/Paper_XI_Traditional_Final.tex'
before=re.findall(r'\\begin\{proof\}(.*?)\\end\{proof\}',old[main].read_text(),re.S)
after=re.findall(r'\\begin\{proof\}(.*?)\\end\{proof\}',new[main].read_text(),re.S)
assert len(before)==len(after)==68
revised=[i+1 for i,(a,b) in enumerate(zip(before,after)) if a!=b]
assert revised==[30,63,65],revised
index={
 'schema_version':1,'checkpoint':'P11-RELEASE-1.1.0','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'baseline_archive':'historical/Paper_XI_Source_and_Evidence_v1.0.0_2026-10-10.zip',
 'old_file_count':len(old),'new_file_count':len(new),'changes':changes,
 'main_proof_environments':{'before':68,'after':68,'byte_identical_bodies':65,'revised_body_indices_one_based':revised},
 'main_source_sha256':sha(new[main]),
 'scope':'Exact active-source comparison. The main proof-environment census is not a theorem/discovery count or a certification of every historical proof.'}
write_json(EVIDENCE/'SOURCE_CHANGE_INDEX.json',index)
(EVIDENCE/'PUBLICATION_SOURCE.diff').write_text(''.join(patches))
print(json.dumps({'status':'passed','raw_and_assembled_pages_compared':sum(r['pages'] for r in raster),'active_source_changes':len(changes),'main_proof_bodies':index['main_proof_environments']},indent=2))
