#!/usr/bin/env python3
"""Check PDF structure and render review sheets. Requires PyMuPDF and Pillow."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import fitz
from PIL import Image,ImageDraw

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pdf',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
 doc=fitz.open(a.pdf);rows=[];images=[];bad=[]
 for n,p in enumerate(doc):
  links=p.get_links();invalid=[x for x in links if x.get('page',0)>=len(doc) or (x['kind'] in (1,4) and x.get('page',-1)<0)]
  outside=[]
  for b in p.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for span in line['spans']:
     r=fitz.Rect(span['bbox'])
     if span['text'].strip() and (r.x0< -1 or r.y0< -1 or r.x1>p.rect.width+1 or r.y1>p.rect.height+1):outside.append(span['text'])
  text=p.get_text();row={'page':n+1,'links':len(links),'invalid_links':len(invalid),'out_of_page_text':outside,'replacement_character':'\ufffd' in text}
  rows.append(row)
  if invalid or outside or row['replacement_character']:bad.append(n+1)
  pix=p.get_pixmap(dpi=90);image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);image.save(out/f'page_{n+1:03d}.png');images.append(image)
  if n+1 in [2,4,6,8,10,13,14,16,18,20,23]:p.get_pixmap(dpi=160).save(out/f'detail_{n+1:03d}.png')
 for first in range(0,len(images),9):
  sheet=Image.new('RGB',(1008,1398),'#d9d9d9');draw=ImageDraw.Draw(sheet)
  for k,im in enumerate(images[first:first+9]):
   im=im.copy();im.thumbnail((320,425));x=(k%3)*336+8;y=(k//3)*466+23;sheet.paste(im,(x,y));draw.text((x,y-17),f'PDF page {first+k+1}',fill='black')
  sheet.save(out/f'contact_{first//9+1:02d}.png')
 report={'status':'passed' if not bad else 'failed','pdf':a.pdf.name,'sha256':hashlib.sha256(a.pdf.read_bytes()).hexdigest(),'pages':len(doc),'bookmarks':len(doc.get_toc()),'links':sum(x['links'] for x in rows),'bad_pages':bad,'per_page':rows,'visual_review':'requires human/model inspection of the rendered sheets; automated checks do not certify aesthetics'}
 (out/'PDF_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='per_page'})
 if bad:raise SystemExit(1)
if __name__=='__main__':main()
