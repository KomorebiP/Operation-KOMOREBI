#!/usr/bin/env python3
"""Render the new pages and generate contact sheets plus geometric checks."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import fitz
from PIL import Image,ImageOps,ImageDraw

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--continuation',type=Path,required=True);ap.add_argument('--map',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
 pages=[];bounds=[]
 for tag,path in [('partIII',a.continuation),('map',a.map)]:
  doc=fitz.open(path)
  for i,p in enumerate(doc):
   name=f'{tag}_{i+1:02}.png';p.get_pixmap(dpi=130,alpha=False).save(out/name);pages.append((tag,i+1,name))
   bad=[]
   for b in p.get_text('dict')['blocks']:
    for line in b.get('lines',[]):
     for s in line['spans']:
      rect=fitz.Rect(s['bbox'])
      if s['text'].strip() and not p.rect.contains(rect):bad.append({'text':s['text'],'bbox':list(rect)})
   bounds.append({'part':tag,'page':i+1,'out_of_page_spans':bad,'replacement_glyph': '\ufffd' in p.get_text()})
 contacts=[]
 for start in range(0,len(pages),4):
  canvas=Image.new('RGB',(1280,1740),'white');draw=ImageDraw.Draw(canvas)
  for j,(tag,n,name) in enumerate(pages[start:start+4]):
   im=Image.open(out/name);im.thumbnail((620,815));x=(j%2)*640+(640-im.width)//2;y=(j//2)*870+32
   canvas.paste(im,(x,y));draw.text(((j%2)*640+20,(j//2)*870+8),f'{tag} / PDF page {n}',fill='black')
  dest=out/f'contact_{start//4+1:02}.png';canvas.save(dest);contacts.append(dest.name)
 result={'status':'passed' if all(not b['out_of_page_spans'] and not b['replacement_glyph'] for b in bounds) else 'failed','new_pages_rendered':len(pages),'dpi':130,'contact_sheets':contacts,'geometry':bounds,'manual_review':'pending'}
 (out/'RENDER_RECORD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='geometry'},indent=2))
if __name__=='__main__':main()
