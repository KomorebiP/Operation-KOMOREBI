#!/usr/bin/env python3
"""Render all manuscripts (or named stems) and make layout contact sheets."""
from pathlib import Path
import subprocess
import json
import tempfile
import shutil
import sys
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / (ROOT.name + '_qa')
OUT.mkdir(exist_ok=True)
previous_report = ROOT/'editorial'/'render_checks.json'
records = json.loads(previous_report.read_text()) if previous_report.exists() else []
requested = {Path(name).stem for name in sys.argv[1:]}
pdfs = sorted((ROOT/'pdfs').glob('Physics_*.pdf'))
if requested:
    missing = requested - {pdf.stem for pdf in pdfs}
    if missing:
        raise FileNotFoundError('Unknown PDF stems: ' + ', '.join(sorted(missing)))
    pdfs = [pdf for pdf in pdfs if pdf.stem in requested]
for pdf in pdfs:
    dest = OUT/pdf.stem
    dest.mkdir(exist_ok=True)
    for pattern in ('page-*.png', 'contact-*.jpg'):
        for previous in dest.glob(pattern):
            previous.unlink()
    with tempfile.TemporaryDirectory(prefix='physics-render-') as staging:
        staging = Path(staging)
        subprocess.run(['pdftoppm','-r','85','-png',str(pdf),str(staging/'page')],check=True)
        pages = []
        for rendered in sorted(staging.glob('page-*.png')):
            target = dest/rendered.name
            shutil.copy2(rendered, target)
            pages.append(target)
    for start in range(0,len(pages),4):
        sheet = Image.new('RGB',(1100,1480),'#e5e8e7')
        draw = ImageDraw.Draw(sheet)
        for j,p in enumerate(pages[start:start+4]):
            im=Image.open(p).convert('RGB');im.thumbnail((530,700))
            x=10+(j%2)*550;y=35+(j//2)*740
            sheet.paste(im,(x,y));draw.text((x,y-22),pdf.stem+' / page '+str(start+j+1),fill='black')
        sheet.save(dest/f'contact-{start//4+1:02}.jpg',quality=92)
    doc=fitz.open(pdf)
    if len(pages) != len(doc):
        raise RuntimeError(f'Incomplete page render: {pdf.name}')
    out_of_page=[]
    for i,page in enumerate(doc):
        for block in page.get_text('blocks'):
            x0,y0,x1,y1=block[:4]
            if x0<10 or y0<10 or x1>page.rect.width-10 or y1>page.rect.height-10:
                out_of_page.append({'page':i+1,'box':[x0,y0,x1,y1],'text':block[4][:70]})
    records = [item for item in records if item['pdf'] != pdf.name]
    records.append({'pdf':pdf.name,'pages':len(doc),'rendered_pages':len(pages),'text_outside_safe_page':out_of_page})
records.sort(key=lambda item:item['pdf'])
(ROOT/'editorial'/'render_checks.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
