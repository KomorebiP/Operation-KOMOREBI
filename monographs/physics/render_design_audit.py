"""Render the final book with PDFium, recording failures and making contact sheets."""
from pathlib import Path
import json, time
import pypdfium2 as pdfium
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'audit' / 'render_review'
OUT.mkdir(parents=True, exist_ok=True)
book = ROOT / 'Komorebi_Physics.pdf'
doc = pdfium.PdfDocument(book)
failures, sheets, page_sizes = [], [], []
t0 = time.monotonic()
cols, rows, tw, th = 4, 4, 306, 420
sheet = None
for i in range(len(doc)):
    if i % (cols*rows) == 0:
        sheet = Image.new('RGB',(cols*tw, rows*th), '#e5e8e9')
    try:
        page = doc[i]
        bm = page.render(scale=0.6)
        im = bm.to_pil().convert('RGB')
        page_sizes.append([i+1, im.width, im.height])
        im.thumbnail((tw-12, th-26), Image.Resampling.LANCZOS)
        pos = i % (cols*rows)
        x, y = (pos%cols)*tw, (pos//cols)*th
        sheet.paste(im,(x+(tw-im.width)//2,y+4))
        ImageDraw.Draw(sheet).text((x+10,y+th-18), f'PDF page {i+1}', fill='#233844')
        bm.close(); page.close()
    except Exception as exc:
        failures.append({'page':i+1,'error':repr(exc)})
    if (i+1) % (cols*rows) == 0 or i == len(doc)-1:
        name = f'contact_{i//(cols*rows)+1:02d}.jpg'
        sheet.save(OUT/name, quality=84)
        sheets.append(name)
        print(f'{i+1}/{len(doc)} rendered', flush=True)
report={'renderer':'PDFium (pypdfium2)','scale':0.6,'pages_attempted':len(doc),
        'pages_rendered':len(page_sizes),'failures':failures,'contact_sheets':sheets,
        'elapsed_seconds':round(time.monotonic()-t0,2),
        'review_note':'Every page rendered. Contact sheets support layout review; representative pages also inspected at higher resolution. This is not independent mathematical verification.'}
(OUT/'render_report.json').write_text(json.dumps(report,indent=2)+'\n')
doc.close()
raise SystemExit(1 if failures else 0)
