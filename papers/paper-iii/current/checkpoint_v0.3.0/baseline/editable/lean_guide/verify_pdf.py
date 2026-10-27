#!/usr/bin/env python3
"""Render all guide pages and prepare review contact sheets. No Lean execution."""
from pathlib import Path
import fitz, hashlib,json,re
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent; qa=HERE/'qa';qa.mkdir(exist_ok=True)
pdf=HERE/'Paper_III_Lean_Guide_Final.pdf';doc=fitz.open(pdf)
assert len(doc)>0,'No valid PDF pages; build must complete before QA'
rows=[];thumbs=[];outside=[];empty=[]
for i,page in enumerate(doc):
    text=page.get_text()
    if not text.strip():empty.append(i+1)
    for block in page.get_text('dict')['blocks']:
        if 'lines' not in block:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<0 or y0<0 or x1>page.rect.width+.5 or y1>page.rect.height+.5:
                    outside.append({'page':i+1,'text':span['text'],'bbox':span['bbox']})
    pix=page.get_pixmap(matrix=fitz.Matrix(.44,.44),alpha=False)
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    card=Image.new('RGB',(im.width,im.height+26),'#dde7e7');card.paste(im,(0,26));ImageDraw.Draw(card).text((8,6),str(i+1),fill='black');thumbs.append(card)
    rows.append({'physical_page':i+1,'characters':len(text),'words':len(page.get_text('words'))})
    (qa/f'page_{i+1:02d}.txt').write_text(text)
for k in range(0,len(thumbs),12):
    w=thumbs[0].width;h=thumbs[0].height
    sheet=Image.new('RGB',(w*3,h*4),'#e8eeee')
    for j,t in enumerate(thumbs[k:k+12]):sheet.paste(t,((j%3)*w,(j//3)*h))
    sheet.save(qa/f'contact_{k//12+1:02d}.png')
# Details include the first dense edge code, dependent-fiber identity, tree proof, gate, and contract.
for n in [1,4,7,15,20,24,28,31,35,42,46]:
    if n<=len(doc):doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(qa/f'detail_{n:02d}.png')
log=(HERE/'Paper_III_Lean_Guide_Final.log').read_text()
issues=[l for l in log.splitlines() if re.search(r'Warning|Missing character|Overfull|Underfull|Error',l)]
record={'pdf':pdf.name,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':len(doc),'empty_pages':empty,'outside_page_spans':outside,'final_log_issues':issues,'all_pages_rendered_to_contact_sheets':True,'visual_review_status':'pending human/agent contact-sheet inspection','page_statistics':rows}
(qa/'pdf_verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['pages','empty_pages','outside_page_spans','final_log_issues']}))
