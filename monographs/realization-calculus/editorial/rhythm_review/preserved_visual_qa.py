from pathlib import Path
import json,fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'editorial/rhythm_review/preserved_visual_qa';OUT.mkdir(exist_ok=True)
p=json.loads((ROOT/'editorial/rhythm_review/preserved_proposals.json').read_text())
a=json.loads((ROOT/'editorial/rhythm_review/preserved_apply_report.json').read_text())
lookup={r['component_id']:r for r in a};opened={};cards=[];pages=[]
for comp,r in lookup.items():
 opened[comp]=fitz.open(ROOT/r['output_pdf'])
 for pg in r['pages']:pages.append((comp,pg['page_1based']))
for i,e in enumerate(p['edits']):
 comp=e['component_id'];pg=e['page_1based'];page=opened[comp][pg-1]
 b=fitz.Rect(e['bbox_optional']);b=fitz.Rect(max(0,b.x0-15),max(0,b.y0-12),page.rect.width-25,min(page.rect.height,b.y1+16))
 pm=page.get_pixmap(matrix=fitz.Matrix(2.0,2.0),clip=b,alpha=False)
 im=Image.frombytes('RGB',[pm.width,pm.height],pm.samples)
 im.save(OUT/f'edit_{i:02}_{comp}_p{pg:02}.png')
 card=Image.new('RGB',(1100,im.height+40),'white');ImageDraw.Draw(card).text((5,5),f'Edit {i}: {comp}, physical p{pg}',fill='black');card.paste(im,(0,30));cards.append(card)
for j in range(0,len(cards),4):
 cs=cards[j:j+4];sheet=Image.new('RGB',(1100,sum(c.height for c in cs)+12*len(cs)),(220,220,220));y=0
 for c in cs:sheet.paste(c,(0,y));y+=c.height+12
 sheet.save(OUT/f'crop_sheet_{j//4+1}.png')
for j in range(0,len(pages),6):
 ps=pages[j:j+6];sheet=Image.new('RGB',(1500,1420),(210,210,210))
 for k,(comp,pg) in enumerate(ps):
  page=opened[comp][pg-1];pm=page.get_pixmap(matrix=fitz.Matrix(.82,.82),alpha=False);im=Image.frombytes('RGB',[pm.width,pm.height],pm.samples);im.thumbnail((490,670))
  x=(k%3)*500;y=(k//3)*710;sheet.paste(im,(x,y+30));ImageDraw.Draw(sheet).text((x+4,y+4),f'{comp} p{pg}',fill='black')
 sheet.save(OUT/f'page_sheet_{j//6+1}.png')
print('changed pages',len(pages),'edits',len(cards));print(OUT)
