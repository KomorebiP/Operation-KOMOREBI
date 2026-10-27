from pathlib import Path
import json,hashlib,fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;qa=ROOT/'qa';qa.mkdir(exist_ok=True)
results=json.loads((ROOT/'build_results.json').read_text());checks=[]
for e in results:
 d=fitz.open(e['pdf']);nums=sorted(set([0,1,2,len(d)//3,len(d)//2,len(d)-1]));sheet=Image.new('RGB',(960,900),'#cccccc');dr=ImageDraw.Draw(sheet)
 for k,p in enumerate(nums):
  pix=d[p].get_pixmap(matrix=fitz.Matrix(.48,.48),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);x=(k%3)*320;y=(k//3)*450;sheet.paste(im,(x+10,y+20));dr.text((x+10,y+5),f"{e['paper']} {e['role']} p{p+1}",fill='black')
 sheet.save(qa/f"{e['paper']}_{e['role']}.png")
 bounds=[];links=0;bad_links=[]
 for i,p in enumerate(d):
  for b in p.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for s in line['spans']:
     box=fitz.Rect(s['bbox'])
     if box.x0<0 or box.y0<0 or box.x1>p.rect.width+.2 or box.y1>p.rect.height+.2:bounds.append({'page':i+1,'text':s['text'][:100],'bbox':list(box)})
  for l in p.get_links():
   links+=1
   if l['kind']==fitz.LINK_GOTO and not 0<=l.get('page',-1)<len(d):bad_links.append({'page':i+1,'link':str(l)})
 checks.append({'paper':e['paper'],'role':e['role'],'pages':len(d),'rendered_selected_pages':[n+1 for n in nums],'outside_page_text':bounds,'links':links,'invalid_internal_links':bad_links})
(ROOT/'qa/structural_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
