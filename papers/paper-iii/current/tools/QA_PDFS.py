#!/usr/bin/env python3
"""Render components and verify links/page preservation; record visual review separately."""
from pathlib import Path
import hashlib,json,math
import fitz
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/qa';OUT.mkdir(parents=True,exist_ok=True)
layout=json.loads((ROOT/'evidence/INTEGRATED_READER_LAYOUT.json').read_text())
merged=fitz.open(ROOT/'publication/Paper_III_Complete_Reading_Edition_v1.0.0.pdf')
report={'status':'PASS','scope':'Programmatic page, link, render-preservation and text-bounds checks; visual inspection is separately recorded.','components':[],'errors':[]}
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
for part in layout['parts']:
 path=ROOT/part['source'];doc=fitz.open(path);offset=part['start_page']-1
 record={'file':path.name,'pages':len(doc),'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'page_records':[],'contacts':[]};thumbs=[]
 for i,page in enumerate(doc):
  link_errors=[]
  for li in page.get_links():
   if li['kind'] in [fitz.LINK_GOTO,fitz.LINK_NAMED] and not 0<=li.get('page',-1)<len(doc):link_errors.append(li.get('nameddest',str(li)))
  text=page.get_text();bounds=[]
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     if not span['text'].strip():continue
     b=fitz.Rect(span['bbox'])
     if b.x0<5 or b.y0<5 or b.x1>page.rect.width-5 or b.y1>page.rect.height-5:bounds.append({'text':span['text'][:100],'bbox':list(b)})
  pix=page.get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False)
  other=merged[offset+i].get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False)
  same=(pix.width==other.width and pix.height==other.height and pix.samples==other.samples)
  rec={'physical_page':i+1,'printed_label':page.get_label(),'characters':len(text),'near_page_boundary':bounds,'unresolved_internal_links':link_errors,'merged_render_identical':same,'render_sha256':hashlib.sha256(pix.samples).hexdigest()};record['page_records'].append(rec)
  if link_errors or not same or not text.strip():report['errors'].append({'file':path.name,'page':i+1,'link_errors':link_errors,'merged_render_identical':same,'empty_text':not text.strip()})
  if 'Final_v1.0.0' not in path.name:
   im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((320,455));thumbs.append((i+1,im))
 for k in range(0,len(thumbs),12):
  chunk=thumbs[k:k+12];sheet=Image.new('RGB',(1002,math.ceil(len(chunk)/3)*481),'#dce3e1');draw=ImageDraw.Draw(sheet)
  for j,(num,im) in enumerate(chunk):
   x=(j%3)*334+7;y=(j//3)*481+7;sheet.paste(im,(x,y));draw.text((x,y+458),f'{path.stem} / {num}',font=font,fill='#1b373c')
  target=OUT/f'{path.stem}_contact_{k//12+1:02}.png';sheet.save(target);record['contacts'].append(str(target.relative_to(ROOT)))
 report['components'].append(record)
actual_links=sum(len(p.get_links()) for p in merged)
report.update(combined_pages=len(merged),combined_links=actual_links,combined_bookmarks=len(merged.get_toc()),expected_links=sum(p['source_links'] for p in layout['parts']))
if actual_links!=report['expected_links']:report['errors'].append({'link_count_mismatch':True})
for i,page in enumerate(merged):
 for li in page.get_links():
  if li['kind']==fitz.LINK_GOTO and not 0<=li.get('page',-1)<len(merged):report['errors'].append({'bad_merged_link_page':i+1})
for item in merged.get_toc():
 if not 1<=item[2]<=len(merged):report['errors'].append({'bad_bookmark':item})
report['status']='PASS' if not report['errors'] else 'FAIL'
(OUT/'PDF_PROGRAMMATIC_QA.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'pages':report['combined_pages'],'links':actual_links,'bookmarks':report['combined_bookmarks'],'errors':report['errors'],'boundary_flags':sum(len(pg['near_page_boundary']) for c in report['components'] for pg in c['page_records']),'contacts':[p for c in report['components'] for p in c['contacts']]},indent=2))
