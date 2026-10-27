#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
import fitz
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;pdf=HERE/'Paper_VI_Lean_Guide_Final.pdf';qa=HERE/'qa';qa.mkdir(exist_ok=True)
doc=fitz.open(pdf);texts=[p.get_text() for p in doc];flat=re.sub(r'\s+','', ''.join(texts));targets=json.loads((HERE/'generated/targets.json').read_text(encoding="utf-8"));names=[t['declaration'] for t in targets]
missing=[n for n in names if n not in flat]
checks={'pages':len(doc),'all_341_target_names_present_in_extracted_text':not missing,'missing_targets':missing,'blank_pages':[],'out_of_page_text_spans':[],'unicode_replacement_character_count':''.join(texts).count('\ufffd'),'source_excerpts':[]}
for i,(page,txt) in enumerate(zip(doc,texts),1):
 if len(txt.strip())<20:checks['blank_pages'].append(i)
 for b in page.get_text('dict')['blocks']:
  if b['type']!=0:continue
  for l in b['lines']:
   for s in l['spans']:
    x0,y0,x1,y1=s['bbox']
    if x0<0 or y0<0 or x1>page.rect.width+.5 or y1>page.rect.height+.5:checks['out_of_page_text_spans'].append({'page':i,'text':s['text'],'bbox':s['bbox']})
for e in json.loads((HERE/'generated/excerpts.json').read_text(encoding="utf-8")):
 raw=HERE/'excerpts'/f"{e['tag']}.lean.txt"
 checks['source_excerpts'].append({'tag':e['tag'],'raw_sha256_match':hashlib.sha256(raw.read_bytes()).hexdigest()==e['excerpt_sha256'],'declaration_name_present':e['name'] in flat})
checks['status']='PASS' if not missing and not checks['blank_pages'] and not checks['out_of_page_text_spans'] and not checks['unicode_replacement_character_count'] and all(e['raw_sha256_match'] and e['declaration_name_present'] for e in checks['source_excerpts']) else 'FAIL'
(qa/'pdf_checks.json').write_text(json.dumps(checks,indent=2)+'\n', encoding="utf-8");(qa/'pdf_text.txt').write_text('\n\f\n'.join(texts), encoding="utf-8")
subprocess.run(['pdffonts',str(pdf)],stdout=(qa/'fonts.txt').open('w'),check=True)
# Every page rendered, then assembled in 12-page sheets for visual inspection.
thumbs=[]
for i,page in enumerate(doc):
 pix=page.get_pixmap(matrix=fitz.Matrix(.40,.40),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);thumbs.append(im)
for start in range(0,len(doc),12):
 w=max(i.width for i in thumbs)+16;h=max(i.height for i in thumbs)+32;sheet=Image.new('RGB',(w*4,h*3),'#d7dddf');draw=ImageDraw.Draw(sheet)
 for j,im in enumerate(thumbs[start:start+12]):
  x=(j%4)*w+8;y=(j//4)*h+24;sheet.paste(im,(x,y));draw.text((x,y-18),str(start+j+1),fill='black')
 sheet.save(qa/f'contact_{start+1:03d}_{min(start+12,len(doc)):03d}.png')
print(json.dumps({k:v for k,v in checks.items() if k!='source_excerpts'},indent=2))
