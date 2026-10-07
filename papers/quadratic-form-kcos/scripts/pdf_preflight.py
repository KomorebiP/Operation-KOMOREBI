#!/usr/bin/env python3
"""Inspect final PDF structure and generate compact render contact sheets."""
from pathlib import Path
import argparse
import json
import math
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]

def check(path, out):
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(path)
    issues = []
    images = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if '\ufffd' in text:
            issues.append({'page': i+1, 'issue': 'replacement glyph'})
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    r = fitz.Rect(span['bbox'])
                    if r.x0 < -1 or r.y0 < -1 or r.x1 > page.rect.width+1 or r.y1 > page.rect.height+1:
                        issues.append({'page': i+1, 'issue': 'text outside page', 'text': span['text']})
        pix = page.get_pixmap(matrix=fitz.Matrix(0.58,0.58), alpha=False)
        im = Image.frombytes('RGB', [pix.width,pix.height], pix.samples)
        images.append(im)
    for start in range(0,len(images),12):
        selected = images[start:start+12]
        w,h = max(x.width for x in selected), max(x.height for x in selected)
        sheet = Image.new('RGB', (3*(w+16),4*(h+30)), '#e8ecf0')
        draw = ImageDraw.Draw(sheet)
        for j, im in enumerate(selected):
            x=(j%3)*(w+16)+8; y=(j//3)*(h+30)+22
            sheet.paste(im,(x,y))
            draw.text((x,y-17), f'Page {start+j+1}',fill='black')
        sheet.save(out / f'contact_{start//12+1:02d}.png')
    result={'file':str(path.relative_to(ROOT)),'pages':len(doc),'encrypted':bool(doc.is_encrypted),
            'text_characters':sum(len(p.get_text()) for p in doc),'issues':issues,
            'check_scope':'Structural bounds and complete rendered contact sheets; visual inspection is a separate review.'}
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',choices=['traditional','visual','lean'])
    args=parser.parse_args()
    names={'traditional':'Quadratic_Form_KCOS_Traditional.pdf','visual':'Quadratic_Form_KCOS_Visual_Guide.pdf',
           'lean':'Quadratic_Form_KCOS_Lean_Guide.pdf'}
    report=[]
    for folder,name in names.items():
        if args.only and folder!=args.only:continue
        report.append(check(ROOT/folder/name,ROOT/'verification'/'renders'/folder))
    output=ROOT/'verification'/('PDF_PREFLIGHT_'+args.only+'.json' if args.only else 'PDF_PREFLIGHT.json')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
