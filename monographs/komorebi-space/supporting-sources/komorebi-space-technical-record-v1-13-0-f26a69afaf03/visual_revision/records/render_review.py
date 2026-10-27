#!/usr/bin/env python3
"""Render each guide page and record deterministic visual-review coverage."""
from pathlib import Path
import hashlib
import json
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
pdf = ROOT / 'build/visual_02/visual/Komorebi_Space_Visual_Guide.pdf'
dest = ROOT / 'build/visual_review_final'
dest.mkdir(parents=True, exist_ok=True)
report = {'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
          'pages': 0, 'outside_words': [], 'page_images': []}
with fitz.open(pdf) as doc:
    report['pages'] = len(doc)
    for i, page in enumerate(doc, 1):
        for word in page.get_text('words'):
            if not page.rect.contains(fitz.Rect(word[:4])):
                report['outside_words'].append({'page': i, 'word': word[4], 'bbox': word[:4]})
        target = dest / f'page-{i:02}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.4,1.4), alpha=False).save(target)
        old = ROOT / 'build/visual_review' / target.name
        same = old.is_file() and Image.open(old).tobytes() == Image.open(target).tobytes()
        report['page_images'].append({'physical_page': i, 'file': target.name,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'pixels_identical_to_first_review': same})
    for start in range(1,len(doc)+1,4):
        stop = min(start+3,len(doc))
        sheet = Image.new('RGB', (960,1280), '#dddddd')
        draw = ImageDraw.Draw(sheet)
        for j,i in enumerate(range(start,stop+1)):
            im = Image.open(dest / f'page-{i:02}.png')
            im.thumbnail((465,600))
            x,y = (j%2)*480+7,(j//2)*640+24
            sheet.paste(im,(x,y))
            draw.text((x,y-18),f'Physical page {i}',fill='black')
        sheet.save(dest / f'contact-{start:02}-{stop:02}.png')
(dest / 'render_report.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'pdf_sha256': report['pdf_sha256'], 'pages': report['pages'],
                  'outside_words': len(report['outside_words']),
                  'changed_pages': [p['physical_page'] for p in report['page_images']
                                    if not p['pixels_identical_to_first_review']]},indent=2))
