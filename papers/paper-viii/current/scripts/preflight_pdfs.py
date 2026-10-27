#!/usr/bin/env python3
"""Read-only PDF checks and contact-sheet generation for the three final companions."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import fitz
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--roles', nargs='+', choices=('traditional', 'visual_guide', 'lean_guide'),
                    default=('traditional', 'visual_guide', 'lean_guide'))
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
records = []
for role in args.roles:
    name = {'traditional': 'Traditional', 'visual_guide': 'Visual_Guide',
            'lean_guide': 'Lean_Guide'}[role]
    path = args.root / 'papers' / f'Paper_VIII_{name}_Final.pdf'
    output = args.out / role
    output.mkdir(parents=True, exist_ok=True)
    with fitz.open(path) as doc:
        pages = []
        thumbnails = []
        names = doc.resolve_names()
        link_count = 0
        named_link_count = 0
        for index, page in enumerate(doc):
            text = page.get_text()
            outside = []
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    for span in line['spans']:
                        if not span['text'].strip():
                            continue
                        x0, y0, x1, y1 = span['bbox']
                        if x0 < -0.5 or y0 < -0.5 or x1 > page.rect.width + 0.5 or y1 > page.rect.height + 0.5:
                            outside.append({'text': span['text'], 'bbox': span['bbox']})
            invalid = []
            for link in page.get_links():
                link_count += 1
                destination = link.get('nameddest')
                if destination:
                    named_link_count += 1
                    target = names.get(destination)
                    if target is None or not 0 <= target.get('page', -1) < len(doc) or link.get('page') != target.get('page'):
                        invalid.append({'xref': link.get('xref'), 'nameddest': destination,
                                        'page': link.get('page'), 'problem': 'named destination mismatch'})
                elif link['kind'] == fitz.LINK_GOTO and not 0 <= link.get('page', -1) < len(doc):
                    invalid.append({'xref': link.get('xref'), 'page': link.get('page'),
                                    'problem': 'internal page outside document'})
            pixels = page.get_pixmap(matrix=fitz.Matrix(0.30, 0.30), alpha=False)
            thumb = Image.frombytes('RGB', (pixels.width, pixels.height), pixels.samples)
            thumbnails.append(thumb)
            pages.append({'page': index + 1, 'dimensions_pt': list(page.rect)[2:],
                          'text_words': len(text.split()), 'empty_text': not bool(text.strip()),
                          'outside_physical_page': outside,
                          'replacement_character': '\ufffd' in text,
                          'invalid_internal_links': invalid,
                          'raster_objects': len(page.get_images(full=True))})
        columns, rows, width, height = 5, 5, 194, 265
        for offset in range(0, len(thumbnails), columns * rows):
            canvas = Image.new('RGB', (columns * width, rows * height), '#e8edf2')
            draw = ImageDraw.Draw(canvas)
            for j, thumb in enumerate(thumbnails[offset:offset + columns * rows]):
                x, y = (j % columns) * width, (j // columns) * height
                canvas.paste(thumb, (x + 5, y + 20))
                draw.text((x + 5, y + 3), f'{role}: PDF page {offset+j+1}', fill='#1d2b38')
            canvas.save(output / f'contact_{offset+1:03d}_{min(offset+25,len(doc)):03d}.png')
        (output / 'EXTRACTED_TEXT.txt').write_text('\n\f\n'.join(p.get_text() for p in doc))
        faults = [p['page'] for p in pages if p['empty_text'] or p['outside_physical_page']
                  or p['replacement_character'] or p['invalid_internal_links']]
        record = {'role': role, 'path': str(path), 'pages': len(doc),
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                  'bookmark_count': len(doc.get_toc()), 'fault_pages': faults,
                  'annotations_checked': link_count, 'named_internal_links_checked': named_link_count,
                  'named_destinations': len(names),
                  'page_checks': pages,
                  'scope': 'PDF structure, text extents, text presence, internal-link destinations and rendered thumbnails. This does not establish mathematical correctness.'}
        records.append(record)
report = {'status': 'PASS' if not any(r['fault_pages'] for r in records) else 'REVIEW_REQUIRED',
          'documents': records}
(args.out / 'PREFLIGHT.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'],
                  'documents': [{k: r[k] for k in ('role', 'pages', 'fault_pages', 'sha256')}
                                for r in records]}, indent=2))
if report['status'] != 'PASS':
    raise SystemExit(1)
