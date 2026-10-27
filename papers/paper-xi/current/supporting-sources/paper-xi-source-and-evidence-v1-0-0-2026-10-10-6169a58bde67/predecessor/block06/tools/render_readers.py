#!/usr/bin/env python3
"""Render the three revised readers and labeled contact sheets outside the checkpoint."""
from pathlib import Path
import argparse,json
import fitz
from PIL import Image,ImageDraw

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--kind',choices=['Traditional','Visual_Guide','Lean_Guide']);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=a.output.resolve()
 if out.is_relative_to(root):raise SystemExit('Output must be outside checkpoint')
 out.mkdir(parents=True,exist_ok=True);records=[]
 for f in sorted((root/'publication/pdfs').glob('*Synchronized*.pdf')):
  short=f.name.split('_Synchronized')[0]
  if a.kind and short != 'Paper_XI_'+a.kind:continue
  folder=out/short;folder.mkdir(exist_ok=True)
  d=fitz.open(f)
  for i,p in enumerate(d):
   p.get_pixmap(matrix=fitz.Matrix(85/72,85/72),alpha=False).save(folder/f'page_{i+1:03}.png')
  contacts=[]
  for start in range(0,len(d),20):
   canvas=Image.new('RGB',(1240,2070),'white');draw=ImageDraw.Draw(canvas)
   for j in range(start,min(start+20,len(d))):
    im=Image.open(folder/f'page_{j+1:03}.png');im.thumbnail((300,388))
    x=((j-start)%4)*310+5;y=((j-start)//4)*414+18
    canvas.paste(im,(x,y));draw.text((x+3,y-15),str(j+1),fill='black')
   path=out/f'{short}_contact_{start//20+1:02}.jpg';canvas.save(path,quality=88);contacts.append(str(path))
  records.append({'file':f.name,'pages':len(d),'dpi':85,'contact_sheets':contacts})
 (out/('RENDER_INVENTORY_'+(a.kind or 'all')+'.json')).write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
if __name__=='__main__':main()
