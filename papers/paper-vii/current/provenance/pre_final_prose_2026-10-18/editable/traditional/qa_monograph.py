#!/usr/bin/env python3
"""Render all monograph pages and scan text bounding boxes. Human review remains separate."""
from pathlib import Path
import re,json
import fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;O=R/'qa/monograph';O.mkdir(parents=True,exist_ok=True)
d=fitz.open(R/'Paper_VII_Traditional_Final.pdf');out=[];sparse=[]
for pi,p in enumerate(d,1):
 if len(p.get_text().strip())<60:sparse.append(pi)
 for b in p.get_text('dict')['blocks']:
  if b['type']!=0:continue
  for line in b['lines']:
   for sp in line['spans']:
    box=sp['bbox']
    if box[0]<-1 or box[1]<-1 or box[2]>p.rect.width+1 or box[3]>p.rect.height+1:out.append({'page':pi,'bbox':box,'text':sp['text']})
for batch in range((len(d)+19)//20):
 sheet=Image.new('RGB',(1500,1980),'#dce2e4');draw=ImageDraw.Draw(sheet)
 for i in range(20):
  idx=batch*20+i
  if idx>=len(d):break
  p=d[idx];pix=p.get_pixmap(matrix=fitz.Matrix(.58,.58),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((288,365));x=(i%5)*300;y=(i//5)*495;sheet.paste(im,(x+(300-im.width)//2,y+12));draw.text((x+8,y+390),f'Physical {idx+1} / printed {p.get_label()}',fill='black')
 sheet.save(O/f'contact_{batch+1}.jpg',quality=92)
log=(R/'Paper_VII_Traditional_Final.log').read_text(errors='replace');warnings=[x for x in log.splitlines() if any(k in x for k in ['Overfull','Missing character','undefined references','undefined citations','undefined on input'])]
summary={'status':'PASS' if not out and not warnings and not sparse else 'REVIEW','pdf_pages':len(d),'out_of_page_text':out,'blank_or_sparse':sparse,'layout_warnings':warnings,'page_labels':d.get_page_labels(),'all_page_contacts_reviewed':False}
(O/'layout_scan.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
