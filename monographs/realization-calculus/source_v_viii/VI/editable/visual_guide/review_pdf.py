#!/usr/bin/env python3
"""Render and mechanically inspect every page of the Paper VI visual guide.
Requires PyMuPDF and Pillow; no installed-package changes or network calls.
"""
from pathlib import Path
import hashlib,json,re
import fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
PDF=ROOT/'Paper_VI_Visual_Guide_Final.pdf'
def main():
 qa=ROOT/'qa';qa.mkdir(exist_ok=True)
 d=fitz.open(PDF);assert len(d)==44,len(d)
 assert [x[2] for x in d.get_toc()]==list(range(3,45))
 records=[];invalid=[];links=0
 for i,page in enumerate(d):
  outside=[]
  for b in page.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for s in line['spans']:
     if s['text'].strip() and (s['bbox'][0]<20 or s['bbox'][2]>592 or s['bbox'][1]<10 or s['bbox'][3]>780):outside.append(s['text'])
  assert not outside,(i+1,outside)
  assert not page.get_images(),i+1
  for link in page.get_links():
   if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED):
    links+=1
    if not 0<=link.get('page',-1)<len(d):invalid.append({'page':i+1,'link':link})
  page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(qa/f'page_{i+1:02d}.png')
  records.append({'physical_page':i+1,'visual_page':None if i<2 else i-1,'word_count':len(page.get_text().split()),'raster_images':0,'outside_safe_bounds':outside})
 assert not invalid,invalid
 sheets=[]
 for start in range(0,len(d),12):
  sheet=Image.new('RGB',(1110,2000),(225,225,225));draw=ImageDraw.Draw(sheet)
  for j in range(start,min(start+12,len(d))):
   im=Image.open(qa/f'page_{j+1:02d}.png');im.thumbnail((350,462))
   x=(j-start)%3*370+10;y=(j-start)//3*500+23;sheet.paste(im,(x,y))
   draw.text((x,y-18),f'PDF {j+1}; '+('preliminary' if j<2 else f'V{j-1}'),fill=(0,0,0))
  name=f'contact_{start+1:02d}_{min(start+12,len(d)):02d}.png';sheet.save(qa/name);sheets.append(name)
 log=(ROOT/'Paper_VI_Visual_Guide_Final.log').read_text()
 faults=re.findall(r'Overfull \\[hv]box|Underfull \\[hv]box|undefined references|Missing character:|LaTeX Error',log)
 assert not faults,faults
 report={'status':'PASS','pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'physical_pages':len(d),'preliminary_pages':2,'visual_pages':42,'bookmarks_match_visual_pages':True,'raster_image_objects':0,'valid_internal_links':links,'typesetting_faults':faults,'pages':records,'contact_sheets':sheets,'render_resolution_dpi':90,'manual_visual_review':'Recorded separately in VISUAL_REVIEW.txt; generating contact sheets alone is not manual inspection.'}
 (ROOT/'PDF_QA.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: all 44 pages rendered, geometry and internal destinations valid.')
if __name__=='__main__':main()
