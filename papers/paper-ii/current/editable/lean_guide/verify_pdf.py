#!/usr/bin/env python3
"""Render every page, make contact sheets, and record publication QA data."""
from pathlib import Path
import json, re, hashlib
import fitz
from PIL import Image, ImageOps, ImageDraw
HERE=Path(__file__).resolve().parent
qa=HERE/'qa';qa.mkdir(exist_ok=True)
pdf=HERE/'Paper_II_Lean_Guide_Final.pdf';doc=fitz.open(pdf)
texts=[]
for i,p in enumerate(doc,1):
    p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(qa/f'page-{i:02}.png')
    texts.append(p.get_text())
for start in range(0,len(doc),9):
    sheet=Image.new('RGB',(930,1320),'#d8e2e2');draw=ImageDraw.Draw(sheet)
    for j,i in enumerate(range(start,min(start+9,len(doc)))):
        im=Image.open(qa/f'page-{i+1:02}.png');im.thumbnail((290,402))
        x=15+(j%3)*310;y=22+(j//3)*440
        sheet.paste(im,(x,y));draw.text((x,y+406),f'PDF page {i+1}',fill='#164c51')
    sheet.save(qa/f'contact-{start//9+1}.png')
log=(HERE/'Paper_II_Lean_Guide_Final.log').read_text(errors='replace')
report={'pages':len(doc),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'a4_pages':all(abs(p.rect.width-595.276)<1 and abs(p.rect.height-841.89)<1 for p in doc),'missing_characters':re.findall(r'Missing character:.*',log),'overfull_boxes':re.findall(r'Overfull \\[hv]box.*',log),'undefined_references':re.findall(r'.*undefined.*',log),'all_pages_rendered':True,'contact_sheets':(len(doc)+8)//9,'text_has_replacement_character':any('\ufffd' in t for t in texts),'lean_compiler_run':False,'visual_inspection':'pending'}
(qa/'pdf_text.txt').write_text('\n\f\n'.join(texts))
(qa/'pdf_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
