from pathlib import Path
import json,sys,hashlib,subprocess,concurrent.futures
import fitz
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('/workspace/scratch/fbc994080222/paper_vii_freeze/baseline/Komorebi_Paper_VII_Final_2026-10-18')
INPUTS=Path('/workspace/scratch/fbc994080222/paper_vii_freeze/inputs')
OUT=Path(__file__).resolve().parent
MANIFEST=json.loads((ROOT/'publication/CURRENT_PUBLICATION_MANIFEST.json').read_text())
EDITION=json.loads((ROOT/'EDITION.json').read_text())
VALIDATION=json.loads((ROOT/'verification/final_prose_2026-10-18/RELEASE_VALIDATION.json').read_text())
PREFLIGHT=json.loads((ROOT/'verification/final_prose_2026-10-18/PDF_PREFLIGHT.json').read_text())
REVIEW=json.loads((ROOT/'verification/final_prose_2026-10-18/FINAL_PDF_REVIEW.json').read_text())
SELECTED={'traditional':[1,2,20,37,41,65,95,145,159],'visual_guide':[1,2,20,27,28,30,33,40,42],'lean_guide':[1,2,6,20,40,50,60,80,85]}
DETAILS={'traditional':[37,41],'visual_guide':[20,30,42],'lean_guide':[20,50]}
def sha(b):return hashlib.sha256(b).hexdigest()
def one(role,standalone=False):
 record=next(x for x in MANIFEST['documents'] if x['role']==role);name=Path(record['path']).name;p=(INPUTS/name) if standalone else ROOT/record['path']
 raw=p.read_bytes();digest=sha(raw);doc=fitz.open(p)
 data={'role':role,'variant':'unselected_standalone_original' if standalone else 'accepted_archive_reader','path':str(p) if standalone else record['path'],'bytes':len(raw),'pages':len(doc),'sha256':digest,'matches_archive_current_hash':digest==record['sha256'],'matches_archive_current_pages':len(doc)==record['pages'],'encrypted':bool(doc.is_encrypted),'metadata':doc.metadata,'out_of_page_text_blocks':[],'empty_text_pages':[],'unicode_replacement_character_pages':[],'double_question_mark_pages':[],'invalid_internal_links':[],'internal_link_count':0,'link_kind_counts':{},'bookmarks':len(doc.get_toc()),'invalid_bookmark_pages':[],'page_data':[]}
 if not standalone:
  data['receipt_bindings']={}
  for label,receipt in [('EDITION',EDITION),('RELEASE_VALIDATION',VALIDATION),('PDF_PREFLIGHT',PREFLIGHT),('FINAL_PDF_REVIEW',REVIEW)]:
   row=next(x for x in receipt['documents'] if x['role']==role);data['receipt_bindings'][label]=digest==row['sha256'] and len(doc)==row['pages']
  source=ROOT/record['source_entry_point'];data['source_entry_point']=record['source_entry_point'];data['source_entry_point_sha256']=sha(source.read_bytes())
  data['active_named_copies']=[]
  for parent in ['papers','publication/pdfs','editable/'+{'traditional':'traditional','visual_guide':'visual_guide','lean_guide':'lean_guide'}[role]]:
   copy=ROOT/parent/name;data['active_named_copies'].append({'path':copy.relative_to(ROOT).as_posix(),'sha256':sha(copy.read_bytes()),'matches_current':sha(copy.read_bytes())==digest})
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
  pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  streams=b''.join(doc.xref_stream(x) for x in page.get_contents())
  data['page_data'].append({'number':number,'text_sha256':sha(text.encode()),'pixel_sha256':sha(pix.samples),'pixels':[pix.width,pix.height],'decoded_page_content_sha256':sha(streams)})
  if not standalone and number in SELECTED[role]:
   im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);selected_images.append((number,im.copy()))
  if not standalone and number in DETAILS[role]:page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False).save(OUT/f'{role}_detail_{number:03d}.png')
 for i,item in enumerate(doc.get_toc(simple=False),1):
  if item[3].get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED) and not 1<=item[2]<=len(doc):data['invalid_bookmark_pages'].append({'index':i,'title':item[1],'page':item[2]})
 if not standalone:
  data['selected_rendered_pages']=SELECTED[role];data['detail_pages']=DETAILS[role]
  font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17);w=340;h=475;cols=3;rows=(len(selected_images)+cols-1)//cols
  sheet=Image.new('RGB',(w*cols,h*rows),'#d8dce0');draw=ImageDraw.Draw(sheet)
  for j,(n,im) in enumerate(selected_images):
   im.thumbnail((w-14,h-36));x=(j%cols)*w+(w-im.width)//2;y=(j//cols)*h+30;sheet.paste(im,(x,y));draw.text(((j%cols)*w+8,(j//cols)*h+7),f'{role} PDF page {n}',font=font,fill='black')
  sheet.save(OUT/f'{role}_contact.png')
 (OUT/f'{role}{"_standalone" if standalone else ""}_check.json').write_text(json.dumps(data,indent=2)+'\n')
 print(role,'standalone' if standalone else 'archive',len(doc),digest,flush=True)

if len(sys.argv)>1:one(sys.argv[1],len(sys.argv)>2)
else:
 jobs=[(r,s) for r in SELECTED for s in [False,True]]
 def run(job):
  role,standalone=job;r=subprocess.run([sys.executable,__file__,role]+(['standalone'] if standalone else []),capture_output=True,text=True)
  if r.returncode:raise RuntimeError(str(job)+' '+r.stderr)
  print(r.stdout.strip(),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,jobs))
 current={k:json.loads((OUT/f'{k}_check.json').read_text()) for k in SELECTED};standalone={k:json.loads((OUT/f'{k}_standalone_check.json').read_text()) for k in SELECTED};comparisons=[]
 for role in SELECTED:
  a=current[role];b=standalone[role];diff_text=[];diff_pixels=[];diff_contents=[]
  for before,after in zip(a['page_data'],b['page_data']):
   if before['text_sha256']!=after['text_sha256']:diff_text.append(before['number'])
   if before['pixel_sha256']!=after['pixel_sha256'] or before['pixels']!=after['pixels']:diff_pixels.append(before['number'])
   if before['decoded_page_content_sha256']!=after['decoded_page_content_sha256']:diff_contents.append(before['number'])
  comparisons.append({'role':role,'archive_sha256':a['sha256'],'standalone_sha256':b['sha256'],'exact_pdf_bytes_equal':a['sha256']==b['sha256'],'page_counts_equal':a['pages']==b['pages'],'different_extracted_text_pages':diff_text,'different_72dpi_pixel_pages':diff_pixels,'different_decoded_page_content_stream_pages':diff_contents,'selection':'Accepted source-bound final-prose archive reader retained; standalone original is not substituted.'})
 result={'status':'PENDING_VISUAL_REVIEW','scope':'Read-only accepted archive PDF binding, active-copy reconciliation, all-page structural checks, full standalone-original comparison and selected fresh render QA. No source/PDF edits, rebuild or mathematical audit.','documents':current,'unselected_standalone_documents':standalone,'standalone_comparisons':comparisons,'distinct_selected_reader_pages':sum(d['pages'] for d in current.values()),'selected_edition':'October18 final-prose source-bound archive','raw_dot_product_extraction_qualification':REVIEW['text_extraction_qualification']}
 (OUT/'reader_check.json').write_text(json.dumps(result,indent=2)+'\n')
