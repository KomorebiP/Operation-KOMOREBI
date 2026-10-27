from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
import fitz, json
root=Path('/mnt/data/komorebi_v080')
imgs=sorted((root/'renders').glob('page-*.png'))
for offset in range(0,len(imgs),15):
    batch=imgs[offset:offset+15]
    w,h=306,440
    sheet=Image.new('RGB',(5*w,3*h),'#e4e4e4')
    d=ImageDraw.Draw(sheet)
    for k,p in enumerate(batch):
        im=Image.open(p).convert('RGB'); im.thumbnail((w-12,h-24))
        x=(k%5)*w+(w-im.width)//2; y=(k//5)*h+20
        sheet.paste(im,(x,y)); d.text(((k%5)*w+8,(k//5)*h+3),p.stem,fill='black')
    sheet.save(root/'renders'/f'contact-{offset//15+1:02}.png')
doc=fitz.open(root/'build'/'Komorebi_Seeded_Two_Axis_Calculus_v0.8.0.pdf')
phrases=['Nonidentity arithmetic','Completion defects','Effective arithmetic lattice','Version ledger','Audit and verification record for v0.8','Theorem ledger']
locs={s:[] for s in phrases}; outside=[]; replacement=[]
for i,p in enumerate(doc):
    txt=p.get_text()
    for s in phrases:
        if s.lower() in txt.lower():locs[s].append(i+1)
    for b in p.get_text('dict')['blocks']:
        for ln in b.get('lines',[]):
            for sp in ln['spans']:
                rect=fitz.Rect(sp['bbox'])
                if sp['text'].strip() and (rect.x0<0 or rect.y0<0 or rect.x1>p.rect.width+0.1 or rect.y1>p.rect.height+0.1):outside.append({'page':i+1,'text':sp['text'],'bbox':list(rect)})
                if '\ufffd' in sp['text']:replacement.append({'page':i+1,'text':sp['text']})
report={'page_count':len(doc),'located_headings':locs,'outside_page_bounds':outside,'replacement_character_spans':replacement,'note':'Geometric/text scan only; visual review recorded separately.'}
(root/'Komorebi_Seeded_Two_Axis_Calculus_v0.8.0'/'audit'/'pdf_layout_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
