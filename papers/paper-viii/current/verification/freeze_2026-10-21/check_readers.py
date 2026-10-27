from pathlib import Path
import json,hashlib,sys,subprocess,concurrent.futures
import fitz
from PIL import Image,ImageDraw,ImageFont

TASK=Path('/dev/shm/komorebi_paper_viii_freeze_fbc994080222')
ROOT=TASK/'baseline/core/Komorebi_Paper_VIII_Final_2026-10-10'
OUT=TASK/'audit_readers'
MANIFEST=json.loads((ROOT/'publication/CURRENT_PUBLICATION_MANIFEST.json').read_text())
EDITION=json.loads((ROOT/'EDITION.json').read_text())
CLOSURE=json.loads((ROOT/'verification/RELEASE_CLOSURE.json').read_text())
REPLAY=json.loads((ROOT/'verification/closure_2026-10-10/REBUILD_REPLAY.json').read_text())
SELECTED={'traditional':[1,2,24,60,80,86,90,118,124],'visual_guide':[1,2,4,13,20,28,30,31,34],'lean_guide':[1,2,12,21,35,40,42,50,94]}
DETAILS={'traditional':[80,90],'visual_guide':[13,30],'lean_guide':[35,42]}
def sha(b):return hashlib.sha256(b).hexdigest()
def one(role):
 record=next(x for x in MANIFEST['documents'] if x['role']==role);p=ROOT/record['path'];raw=p.read_bytes();digest=sha(raw);doc=fitz.open(p)
 data={'role':role,'path':record['path'],'sha256':digest,'bytes':len(raw),'pages':len(doc),'matches_current_manifest':digest==record['sha256'] and len(doc)==record['pages'],'receipt_bindings':{},'active_named_copies':[],'encrypted':bool(doc.is_encrypted),'out_of_page_text_blocks':[],'empty_text_pages':[],'unicode_replacement_character_pages':[],'double_question_mark_pages':[],'invalid_internal_links':[],'internal_link_count':0,'link_kind_counts':{},'bookmarks':len(doc.get_toc()),'invalid_bookmark_pages':[],'selected_rendered_pages':SELECTED[role],'detail_pages':DETAILS[role]}
 for label,receipt in [('EDITION',EDITION),('RELEASE_CLOSURE',CLOSURE)]:
  row=next(x for x in receipt['documents'] if x['role']==role);data['receipt_bindings'][label]=digest==row['sha256'] and len(doc)==row['pages']
 replay=next(x for x in REPLAY['documents'] if x['document']==p.stem)
 data['receipt_bindings']['ACCEPTED_REBUILD_REPLAY']=digest==replay['shipped_pdf_sha256']==replay['pdf_sha256'] and len(doc)==replay['pages'] and replay['pdf_byte_identical']
 source=ROOT/record['source_entry_point'];data['source_entry_point']=record['source_entry_point'];data['source_entry_point_sha256']=sha(source.read_bytes())
 for parent in ['papers','publication/pdfs','editable/'+{'traditional':'traditional','visual_guide':'visual_guide','lean_guide':'lean_guide'}[role]]:
  copy=ROOT/parent/p.name;data['active_named_copies'].append({'path':copy.relative_to(ROOT).as_posix(),'sha256':sha(copy.read_bytes()),'matches_current':sha(copy.read_bytes())==digest})
 selected_images=[]
 for number,page in enumerate(doc,1):
  text=page.get_text();rect=page.rect
  if not text.strip():data['empty_text_pages'].append(number)
  if '\ufffd' in text:data['unicode_replacement_character_pages'].append(number)
  if '??' in text:data['double_question_mark_pages'].append(number)
  for b in page.get_text('blocks'):
   if b[6]!=0:continue
   x0,y0,x1,y1=b[:4]
   if x0 < -0.5 or y0 < -0.5 or x1 > rect.width+0.5 or y1 > rect.height+0.5:data['out_of_page_text_blocks'].append({'page':number,'bbox':list(b[:4]),'text':b[4][:100]})
  for link in page.get_links():
   k=str(link.get('kind'));data['link_kind_counts'][k]=data['link_kind_counts'].get(k,0)+1
   if link.get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED):
    data['internal_link_count']+=1
    if not 0<=link.get('page',-1)<len(doc):data['invalid_internal_links'].append({'page':number,'target':link.get('page',-1),'name':link.get('nameddest')})
  if number in SELECTED[role]:
   pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);selected_images.append((number,Image.frombytes('RGB',[pix.width,pix.height],pix.samples)))
  if number in DETAILS[role]:page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False).save(OUT/f'{role}_detail_{number:03d}.png')
 for i,item in enumerate(doc.get_toc(simple=False),1):
  if item[3].get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED) and not 1<=item[2]<=len(doc):data['invalid_bookmark_pages'].append({'index':i,'title':item[1],'page':item[2]})
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17);w=340;h=475;cols=3;rows=(len(selected_images)+cols-1)//cols
 sheet=Image.new('RGB',(w*cols,h*rows),'#d8dce0');draw=ImageDraw.Draw(sheet)
 for j,(n,im) in enumerate(selected_images):
  im.thumbnail((w-14,h-36));x=(j%cols)*w+(w-im.width)//2;y=(j//cols)*h+30;sheet.paste(im,(x,y));draw.text(((j%cols)*w+8,(j//cols)*h+7),f'{role} PDF page {n}',font=font,fill='black')
 sheet.save(OUT/f'{role}_contact.png')
 (OUT/f'{role}_check.json').write_text(json.dumps(data,indent=2)+'\n')
 print(role,len(doc),digest,'copies',len(data['active_named_copies']),flush=True)

if len(sys.argv)>1:one(sys.argv[1])
else:
 def run(role):
  r=subprocess.run([sys.executable,'-B',__file__,role],capture_output=True,text=True)
  if r.returncode:raise RuntimeError(role+' '+r.stderr)
  print(r.stdout.strip(),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,SELECTED))
 docs={k:json.loads((OUT/f'{k}_check.json').read_text()) for k in SELECTED}
 result={'status':'PENDING_VISUAL_REVIEW','scope':'Read-only exact archive PDF binding, all-nine-copy reconciliation, all-page structural/link/bookmark checks and selected fresh render review. No new build, Lean execution, scientific replay or mathematical proof audit.','documents':docs,'distinct_reader_pages':sum(x['pages'] for x in docs.values()),'selected_body_edition':'October9, release closure October10','inherited_replay_boundary':'Initial Lean-guide replay page-text comparison failed because16pages reflowed; accepted second replay records all three final PDFs byte-identical. Neither build was rerun in this freeze audit.'}
 (OUT/'reader_check.json').write_text(json.dumps(result,indent=2)+'\n')
