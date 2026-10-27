#!/usr/bin/env python3
"""Source-fidelity, extracted-name and geometric PDF checks; no Lean execution."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
import fitz
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path);args=ap.parse_args()
pdf=HERE/'Paper_VII_Lean_Guide_Final.pdf';qa=HERE/'qa';qa.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
doc=fitz.open(pdf);texts=[p.get_text()for p in doc];flat=re.sub(r'\s+','',''.join(texts))
targets=json.loads((HERE/'generated/targets.json').read_text());missing=[r['declaration']for r in targets if r['declaration']not in flat]
log=(HERE/'Paper_VII_Lean_Guide_Final.log').read_text()
checks={'pdf_sha256':sha(pdf),'pages':len(doc),'all_323_theorem_names_extract':not missing,'missing_theorems':missing,'blank_pages':[],'out_of_page_spans':[],'invalid_internal_links':[],'unicode_replacement_characters':''.join(texts).count('\ufffd'),'overfull_boxes':len(re.findall('Overfull',log)),'missing_glyphs':len(re.findall('Missing character',log)),'unresolved_references':bool(re.search(r'undefined|multiply defined|There were undefined',log)),'excerpts':[],'fresh_kernel_execution':False}
for i,(page,txt)in enumerate(zip(doc,texts),1):
    if len(txt.strip())<25:checks['blank_pages'].append(i)
    for b in page.get_text('dict')['blocks']:
        if b['type']!=0:continue
        for l in b['lines']:
            for s in l['spans']:
                x0,y0,x1,y1=s['bbox']
                if x0<0 or y0<0 or x1>page.rect.width+.5 or y1>page.rect.height+.5:checks['out_of_page_spans'].append({'page':i,'text':s['text'],'bbox':s['bbox']})
    for l in page.get_links():
        if l['kind']==fitz.LINK_GOTO and not 0<=l['page']<len(doc):checks['invalid_internal_links'].append({'page':i,'link':str(l)})
for e in json.loads((HERE/'generated/excerpts.json').read_text()):
    raw=HERE/'excerpts'/f"{e['tag']}.lean.txt"
    row={'tag':e['tag'],'raw_hash_matches':sha(raw)==e['excerpt_sha256'],'name_extracts':e['name']in flat}
    if args.source:
        p=args.source/e['source_file'];source=p.read_text().splitlines(keepends=True)
        actual=''.join(source[e['start_line']-1:e['end_line']])
        row['exact_contiguous_source_bytes']=actual.encode()==raw.read_bytes()
        row['source_hash_matches']=sha(p)==e['source_sha256']
    checks['excerpts'].append(row)
checks['status']='PASS' if not missing and not any(checks[k]for k in ('blank_pages','out_of_page_spans','invalid_internal_links','unicode_replacement_characters','overfull_boxes','missing_glyphs','unresolved_references')) and all(all(v for k,v in e.items()if k!='tag')for e in checks['excerpts']) else 'FAIL'
(qa/'pdf_checks.json').write_text(json.dumps(checks,indent=2)+'\n');(qa/'pdf_text.txt').write_text('\n\f\n'.join(texts))
subprocess.run(['pdffonts',str(pdf)],stdout=(qa/'fonts.txt').open('w'),check=True)
thumbs=[]
for page in doc:
    pix=page.get_pixmap(matrix=fitz.Matrix(.42,.42),alpha=False)
    thumbs.append(Image.frombytes('RGB',[pix.width,pix.height],pix.samples))
for start in range(0,len(doc),12):
    w=max(i.width for i in thumbs)+16;h=max(i.height for i in thumbs)+32
    sheet=Image.new('RGB',(w*4,h*3),'#d7dddf');draw=ImageDraw.Draw(sheet)
    for j,im in enumerate(thumbs[start:start+12]):
        px=(j%4)*w+8;py=(j//4)*h+24;sheet.paste(im,(px,py));draw.text((px,py-18),str(start+j+1),fill='black')
    sheet.save(qa/f'contact_{start+1:03d}_{min(start+12,len(doc)):03d}.png')
print(json.dumps({k:v for k,v in checks.items()if k!='excerpts'},indent=2))
if checks['status']!='PASS':raise SystemExit(1)
