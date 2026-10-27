#!/usr/bin/env python3
"""Render every page and create contact sheets plus objective layout checks."""
from pathlib import Path
import json,re,hashlib
import fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;Q=R/'qa';Q.mkdir(exist_ok=True)
for pattern in ['page-*.png','contact-*.jpg']:
    for old in Q.glob(pattern):old.unlink()
pdf=R/'Paper_VI_Traditional_Final.pdf';d=fitz.open(pdf)
edge=[];replacement=[];images=[]
for i,p in enumerate(d):
    pix=p.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False)
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    im.save(Q/f'page-{i+1:03}.png')
    text=p.get_text()
    if '\ufffd' in text:replacement.append(i+1)
    for block in p.get_text('dict')['blocks']:
        if block.get('type')!=0:continue
        x0,y0,x1,y1=block['bbox']
        if x0<20 or y0<15 or x1>p.rect.width-20 or y1>p.rect.height-15:
            edge.append({'page':i+1,'bbox':list(block['bbox'])})
    thumb=im.copy();thumb.thumbnail((330,467));images.append(thumb)
for start in range(0,len(images),16):
    sheet=Image.new('RGB',(4*350,4*497),'#dbe3e2');draw=ImageDraw.Draw(sheet)
    for j,im in enumerate(images[start:start+16]):
        x=(j%4)*350+10;y=(j//4)*497+25
        sheet.paste(im,(x,y));draw.text((x,y-18),f'PDF page {start+j+1}',fill='black')
    sheet.save(Q/f'contact-{start+1:03}-{min(start+16,len(images)):03}.jpg',quality=90)
log=(R/'Paper_VI_Traditional_Final.log').read_text(errors='replace')
warnings=[l for l in log.splitlines() if any(t in l for t in ['Overfull','LaTeX Warning','Package hyperref Warning','Missing character:','!'])]
summary={'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'page_count':len(d),'rendered_pages':len(images),'warnings':warnings,'text_near_crop_edges':edge,'unicode_replacement_pages':replacement,'manual_visual_review':'Pending review of contact sheets and selected detail pages.'}
(Q/'PDF_LAYOUT_CHECK.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
