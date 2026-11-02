"""Regenerate the retained book figure previews (requires pypdfium2).

Run from a complete collection checkout. Normal website builds verify the
committed assets and do not require the rendering dependency.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def checked(path,expected):
    raw=(ROOT/path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Changed figure source: '+path)
    return raw

def main():
    import pypdfium2 as pdfium
    for work in ('komorebi-space','realization-boundaries'):
        path=ROOT/'website/assets/figures'/work/'figures.json'
        receipt=json.loads(path.read_bytes())
        for record in receipt['figures']:
            checked(record['source'],record['source_sha256'])
            output=ROOT/'website'/record['image']
            if record.get('render_image'):
                output.write_bytes(checked(record['render_image'],record['render_image_sha256']))
            else:
                pdf=pdfium.PdfDocument(checked(record['render_source'],record['render_source_sha256']))
                image=pdf[record['page']-1].render(scale=2.5).to_pil().convert('RGB')
                if record['crop_points']:image=image.crop(tuple(round(x*2.5) for x in record['crop_points']))
                image.save(output)
            record['image_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
        path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        print(work,len(receipt['figures']))

if __name__=='__main__':main()
