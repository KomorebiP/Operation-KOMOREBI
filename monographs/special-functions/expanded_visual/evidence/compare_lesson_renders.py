"""Compare inherited lesson bodies between independently rendered editions.

Usage: python evidence/compare_lesson_renders.py OLD_PNG_DIR NEW_PNG_DIR
Requires 110-dpi page-XX.png files from Poppler and the current lesson index.
The shared edition header lies above 40 points; every lesson body and footer
must be exactly pixel-identical for the inherited visual inspection to apply.
"""
from pathlib import Path
import json
import hashlib
import sys
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]

def page_image(directory, physical_page):
    candidates = list(directory.glob(f'page-*{physical_page}.png'))
    exact = [p for p in candidates if int(p.stem.split('-')[-1]) == physical_page]
    if len(exact) != 1:
        raise ValueError((directory, physical_page, exact))
    return exact[0]

def main():
    old_dir, new_dir = map(Path, sys.argv[1:3])
    old = json.loads((ROOT/'evidence/edition_v0.2/lesson_index.json').read_text())
    new = json.loads((ROOT/'evidence/lesson_index.json').read_text())
    assert len(old) == 110 and len(new) == 158
    records = []
    for a, b in zip(old, new[:110]):
        assert a['title'] == b['title'] and a['figure'] == b['figure']
        pa = page_image(old_dir, a['physical_page'])
        pb = page_image(new_dir, b['physical_page'])
        with Image.open(pa) as xa, Image.open(pb) as xb:
            ia, ib = xa.convert('RGB'), xb.convert('RGB')
        assert ia.size == ib.size
        top = 62  # ceil(40pt * 110dpi / 72pt per inch)
        box = (0, top, ia.width, ia.height)
        diff = ImageChops.difference(ia.crop(box), ib.crop(box))
        identical = diff.getbbox() is None
        records.append({'lesson':a['lesson'], 'old_physical_page':a['physical_page'],
                        'new_physical_page':b['physical_page'],
                        'body_and_footer_pixel_identical':identical,
                        'final_png_sha256':hashlib.sha256(pb.read_bytes()).hexdigest()})
    mismatches = [r['lesson'] for r in records if not r['body_and_footer_pixel_identical']]
    report = {'status':'PASS' if not mismatches else 'NEEDS_REVIEW', 'render_dpi':110,
              'inherited_lessons':110, 'header_crop_top_pixels':62,
              'scope':'All inherited lesson content and footers; edition header is separately inspected.',
              'mismatched_lessons':mismatches, 'lessons':records}
    (ROOT/'evidence/INHERITED_LESSON_RENDER_BRIDGE.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='lessons'}))

if __name__ == '__main__':
    main()
