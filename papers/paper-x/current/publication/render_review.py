#!/usr/bin/env python3
"""Render every reader page into contact sheets and selected larger details."""
from pathlib import Path
import argparse, hashlib, json
import fitz
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
DETAILS = {'traditional':[2,3,36,38,59,60,61,63,92],
           'visual':[2,4,33], 'lean':[4,6,18,22,28,35,36,37]}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf-directory', type=Path, default=ROOT/'publication/pdfs')
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    records = []
    for item in json.loads((ROOT/'publication/documents.json').read_text()):
        path = args.pdf_directory/item['file_name']
        key = item['kind']
        with fitz.open(path) as document:
            row = {'file':item['file_name'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                   'pages':len(document),'contact_sheets':[], 'detail_pages':[]}
            for start in range(0,len(document),12):
                sheet = Image.new('RGB',(1290,2350),'#e6e8e7')
                draw = ImageDraw.Draw(sheet)
                for page in range(start,min(start+12,len(document))):
                    pixmap = document[page].get_pixmap(matrix=fitz.Matrix(.65,.65),alpha=False)
                    bitmap = Image.frombytes('RGB',(pixmap.width,pixmap.height),pixmap.samples)
                    bitmap.thumbnail((405,548))
                    x = 15+(page-start)%3*425
                    y = 30+(page-start)//3*580
                    sheet.paste(bitmap,(x,y))
                    draw.text((x,y-18),f'{key} | PDF page {page+1}',fill='black')
                name = f'{key}_{start//12+1:02}.png'
                sheet.save(args.output_directory/name)
                row['contact_sheets'].append(name)
            for page in DETAILS[key]:
                if page > len(document):
                    raise ValueError('Selected detail lies outside reader')
                name = f'{key}_detail_{page:03}.png'
                document[page-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(args.output_directory/name)
                row['detail_pages'].append({'page':page,'file':name})
            records.append(row)
    (args.output_directory/'RENDER_INPUTS.json').write_text(json.dumps({
        'scope':'Rendered evidence for human layout inspection; not mathematical verification.',
        'pymupdf':fitz.VersionBind,'documents':records},indent=2)+'\n')
    print(json.dumps({'pages':sum(r['pages'] for r in records),
                     'contact_sheets':sum(len(r['contact_sheets']) for r in records),
                     'details':sum(len(r['detail_pages']) for r in records)}))
if __name__ == '__main__':
    main()
