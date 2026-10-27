#!/usr/bin/env python3
"""Check complete final PDFs and render every page for release inspection."""
from pathlib import Path
import argparse,hashlib,json
import fitz
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'audits/pdf_preflight';OUT.mkdir(parents=True,exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('--roles',nargs='+',choices=['Main','Visual','Lean']);args=ap.parse_args()
previous=OUT/'PREFLIGHT.json'
reports=json.loads(previous.read_text()).get('documents',[]) if previous.exists() and args.roles else []
for path in sorted((ROOT/'output/pdf').glob('*.pdf')):
 if args.roles and not any('_'+role+'_' in path.stem for role in args.roles):continue
 before=hashlib.sha256(path.read_bytes()).hexdigest()
 reports=[r for r in reports if r['file']!=str(path.relative_to(ROOT))]
 role=path.stem;dest=OUT/role;dest.mkdir(parents=True,exist_ok=True)
 pdf=fitz.open(path);page_stats=[];thumbs=[];text=[];issues=[]
 for i,page in enumerate(pdf):
  raw=page.get_text();text.append(raw)
  if not raw.strip():issues.append({'page':i+1,'issue':'no extractable text'})
  if '\ufffd' in raw:issues.append({'page':i+1,'issue':'replacement character'})
  words=page.get_text('words')
  outside=[w for w in words if w[0]<-1 or w[1]<-1 or w[2]>page.rect.width+1 or w[3]>page.rect.height+1]
  if outside:issues.append({'page':i+1,'issue':'out-of-page words','count':len(outside)})
  pix=page.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False)
  png=dest/f'page_{i+1:03}.png';pix.save(png)
  thumb=Image.open(png).convert('RGB');thumb.thumbnail((220,312))
  tile=Image.new('RGB',(234,340),'#e9efec');tile.paste(thumb,((234-thumb.width)//2,22));ImageDraw.Draw(tile).text((7,5),f'PDF page {i+1}',fill='#185b58');thumbs.append(tile)
  page_stats.append({'page':i+1,'words':len(words),'out_of_page_words':len(outside)})
 for base in range(0,len(thumbs),20):
  group=thumbs[base:base+20];sheet=Image.new('RGB',(234*5,340*((len(group)+4)//5)),'white')
  for q,img in enumerate(group):sheet.paste(img,((q%5)*234,(q//5)*340))
  sheet.save(dest/f'contact_{base+1:03}_{base+len(group):03}.png')
 (dest/'extracted_text.txt').write_text('\n\f\n'.join(text))
 if hashlib.sha256(path.read_bytes()).hexdigest()!=before:raise SystemExit('PDF changed during rendering: '+str(path))
 reports.append({'file':str(path.relative_to(ROOT)),'pages':len(pdf),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'issues':issues,'page_checks':page_stats,'all_pages_rendered':True})
result={'status':'PASS' if all(not r['issues'] for r in reports) else 'ISSUES','scope':'Complete PDF rendering and text-boundary checks; visual inspection and mathematical proof review are separate','documents':reports}
(OUT/'PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'documents':[{k:r[k] for k in ['file','pages','issues']} for r in reports]},indent=2))
