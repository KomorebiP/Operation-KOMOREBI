#!/usr/bin/env python3
"""Render all guide pages and record structural PDF checks for visual review."""
from pathlib import Path
import hashlib
import json
import re
import fitz
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
qa = root / 'qa'
qa.mkdir(exist_ok=True)
pdf = root / 'Paper_IV_Visual_Guide_Final.pdf'
doc = fitz.open(pdf)
assert len(doc) == 28, f'Expected cover + route + 26 worked pages, got {len(doc)}'
page_checks = []
thumbs = []
for i, page in enumerate(doc):
    text = page.get_text()
    blocks = [b[:4] for b in page.get_text('blocks') if len(b) > 4 and b[4].strip()]
    outside = [b for b in blocks if min(b[0], b[1]) < 0 or
        b[2] > page.rect.width+.1 or b[3] > page.rect.height+.1]
    links = page.get_links()
    invalid_links = [a for a in links if a.get('kind') == fitz.LINK_GOTO and
        not 0 <= a.get('page', -1) < len(doc)]
    if i >= 2:
        assert f'V{i-1}\n' in text or f'V{i-1} /' in text, f'Missing worked heading on PDF page {i+1}'
    pix = page.get_pixmap(matrix=fitz.Matrix(.65, .65), alpha=False)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    img.save(qa / f'page_{i+1:02}.png')
    thumbs.append(img)
    page_checks.append({'physical_pdf_page': i+1, 'text_chars': len(text),
        'outside_page_blocks': outside, 'invalid_internal_links': invalid_links})
    assert not outside and not invalid_links, page_checks[-1]
for start in range(0, len(thumbs), 8):
    sheet = Image.new('RGB', (thumbs[0].width*4, (thumbs[0].height+24)*2), '#dddddd')
    draw = ImageDraw.Draw(sheet)
    for j, img in enumerate(thumbs[start:start+8]):
        x, y = (j%4)*img.width, (j//4)*(img.height+24)
        sheet.paste(img, (x, y+24))
        draw.text((x+8, y+4), f'PDF page {start+j+1}', fill='black')
    sheet.save(qa / f'contact_{start+1:02}_{min(start+8,len(thumbs)):02}.png')
for i in (0, 1, 2, 5, 9, 12, 18, 22, 23, 25):
    doc[i].get_pixmap(matrix=fitz.Matrix(1.35, 1.35), alpha=False).save(qa / f'detail_{i+1:02}.png')
log = (root / 'Paper_IV_Visual_Guide_Final.log').read_text()
warnings = [line for line in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character', line)]
assert not warnings, warnings
report = {'status': 'PASS', 'physical_pages': len(doc), 'worked_pages': 26,
    'deterministic_vector_figures': 24, 'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
    'metadata': doc.metadata, 'bookmark_count': len(doc.get_toc()), 'page_checks': page_checks,
    'tex_warnings': warnings, 'raster_review_status': 'Rendered all pages; see REVIEW_NOTES.txt for visual inspection.',
    'scope': 'PDF geometry, navigation, rendering, and TeX checks. No fresh mathematical model execution or Lean compilation.'}
(qa / 'PDF_QA.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k: report[k] for k in ('status', 'physical_pages', 'worked_pages', 'deterministic_vector_figures', 'pdf_sha256')}))
