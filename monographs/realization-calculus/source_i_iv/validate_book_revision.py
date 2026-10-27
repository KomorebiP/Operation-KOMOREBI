from pathlib import Path
import fitz,json,re,hashlib,difflib
from PIL import Image,ImageDraw
S=Path(__file__).resolve().parent;E=S.parent/'editorial/book_revision';Q=E/'i_iv_visual_review';Q.mkdir(exist_ok=True)
results=json.loads((S/'build_results.json').read_text());checks=[]
special={('I','traditional'):[1,5,9,75,98,100],('I','lean'):[1,5,6,8,9,44],('I','machine'):[2,7,9,14,15,98],('II','traditional'):[1,5,40,55,57,80],('II','visual'):[1,3,14,23,25,26],('II','lean'):[1,5,8,9,32,50],('III','traditional'):[1,5,41,73,75,98],('III','visual'):[1,3,14,24,25,26],('III','lean'):[1,5,7,8,48,51],('III','analytic'):[1,2,3,4,5,6],('IV','traditional'):[1,5,34,54,76,79],('IV','lean'):[1,7,35,36,38,135]}
for e in results:
 d=fitz.open(e['pdf']);key=(e['paper'],e['role']);nums=[x for x in special[key] if x<=len(d)];sheet=Image.new('RGB',(960,900),'#ccc');dr=ImageDraw.Draw(sheet)
 for k,n in enumerate(nums):
  pix=d[n-1].get_pixmap(matrix=fitz.Matrix(.48,.48),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);x=k%3*320;y=k//3*450;sheet.paste(im,(x+10,y+20));dr.text((x+10,y+5),f'{key[0]} {key[1]} physical {n}',fill='black')
 sheet.save(Q/f'{key[0]}_{key[1]}.png')
 bounds=[];bad=[];total=0;plateheads=[]
 for i,p in enumerate(d):
  for block in p.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for sp in line['spans']:
     r=fitz.Rect(sp['bbox'])
     if r.x0<-.2 or r.y0<-.2 or r.x1>p.rect.width+.2 or r.y1>p.rect.height+.2:bounds.append({'page':i+1,'text':sp['text'],'bbox':list(r)})
  for l in p.get_links():
   total+=1
   if l['kind']==fitz.LINK_GOTO and not 0<=l.get('page',-1)<len(d):bad.append({'page':i+1,'link':str(l)})
  text=p.get_text()
  for m in re.finditer(r'Plate ([IVX]+)\.(\d+)\s*/',text):plateheads.append({'plate':m[1]+'.'+m[2],'page':i+1})
 checks.append({'paper':key[0],'role':key[1],'pdf':e['pdf'],'sha256':hashlib.sha256(Path(e['pdf']).read_bytes()).hexdigest(),'pages':len(d),'selected_visual_pages':nums,'outside_page_text':bounds,'links':total,'invalid_internal_links':bad,'plate_headings':plateheads,'page_labels':d.get_page_labels(),'bookmarks':d.get_toc()})
(E/'i_iv_pdf_checks.json').write_text(json.dumps(checks,indent=2))
# Exact source diffs cover all original backups, including the final navigation-only follow-up.
patch=[];files=[]
for b in sorted((S/'book_revision_before').rglob('*')):
 if not b.is_file():continue
 rel=b.relative_to(S/'book_revision_before');p=S/rel
 if not p.exists():continue
 old=b.read_bytes();new=p.read_bytes();files.append({'path':'source_i_iv/'+str(rel),'backup':'source_i_iv/book_revision_before/'+str(rel),'old_sha256':hashlib.sha256(old).hexdigest(),'sha256':hashlib.sha256(new).hexdigest()})
 if p.suffix in ['.tex','.sty','.bib']:
  patch.extend(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
(E/'i_iv_all_source_changes.diff').write_text(''.join(patch));(E/'i_iv_changed_files.json').write_text(json.dumps(files,indent=2))
print(json.dumps({'components':len(checks),'pages':sum(x['pages'] for x in checks),'bounds':sum(len(x['outside_page_text'])for x in checks),'bad_links':sum(len(x['invalid_internal_links'])for x in checks),'source_files':len(files)}))
