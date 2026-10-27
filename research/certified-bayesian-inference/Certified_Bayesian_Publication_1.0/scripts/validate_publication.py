"""Inspect PDF bounds, links, and text; produce page previews for visual QA."""
from pathlib import Path
import hashlib
import json
import re
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    preview = ROOT / 'tmp' / 'pdf_review'
    preview.mkdir(parents=True, exist_ok=True)
    records = []
    for path in sorted((ROOT / 'output').glob('*.pdf')):
        for pattern in (f'{path.stem}_page_*.png', f'{path.stem}_contact_*.png'):
            for stale in preview.glob(pattern):
                stale.unlink()
        doc = fitz.open(path)
        outside = []
        bad_links = []
        text_parts = []
        thumbnails = []
        for i, page in enumerate(doc):
            text_parts.append(page.get_text())
            for block in page.get_text('dict')['blocks']:
                if block.get('type') != 0:
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        x0,y0,x1,y1 = span['bbox']
                        if x0 < 3 or y0 < 3 or x1 > page.rect.width-3 or y1 > page.rect.height-3:
                            outside.append({'page':i+1,'bbox':span['bbox'],'text':span['text']})
            for link in page.get_links():
                if link.get('kind') == fitz.LINK_GOTO and not 0 <= link.get('page', -1) < len(doc):
                    bad_links.append({'page':i+1, 'link':link})
            pix = page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
            image = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            image.save(preview / f'{path.stem}_page_{i+1:03}.png')
            image.thumbnail((260,370))
            tile = Image.new('RGB',(284,405),'#e4ebee')
            tile.paste(image,((284-image.width)//2,8))
            ImageDraw.Draw(tile).text((10,385),f'{path.stem} | {i+1}',fill='#17354a')
            thumbnails.append(tile)
        for start in range(0,len(thumbnails),12):
            sheet = Image.new('RGB',(284*4,405*3),'white')
            for j,tile in enumerate(thumbnails[start:start+12]):
                sheet.paste(tile,((j%4)*284,(j//4)*405))
            sheet.save(preview / f'{path.stem}_contact_{start//12+1:02}.png')
        text='\n'.join(text_parts)
        result={'file':path.name,'pages':len(doc),'bytes':path.stat().st_size,
                'sha256':sha(path),'characters':len(text),'out_of_page_text':outside,
                'broken_internal_links':bad_links,'replacement_characters':text.count('\ufffd'),
                'image_blocks':sum(sum(b.get('type')==1 for b in p.get_text('dict')['blocks']) for p in doc)}
        records.append(result)
        (preview / f'{path.stem}.txt').write_text(text)
        print(path.name,len(doc),'pages',len(outside),'out-of-page spans',len(bad_links),'broken links')
    (ROOT / 'reviews' / 'pdf_validation.json').write_text(json.dumps(records,indent=2)+'\n')
    if any(r['out_of_page_text'] or r['broken_internal_links'] or r['replacement_characters'] for r in records):
        raise SystemExit('PDF structural defect detected')

if __name__ == '__main__':
    main()
