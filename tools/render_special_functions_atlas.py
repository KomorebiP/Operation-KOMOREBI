"""Create lossless browser copies and pin the original visual-guide inputs.

Run deliberately after reviewing source changes:
    python -B tools/render_special_functions_atlas.py

This changes only generated reader metadata/assets. Original source files stay
byte-identical. Every WebP is decoded and compared to its original PNG in RGBA.
"""
import io
import json
from pathlib import Path
import shutil

from PIL import Image, __version__ as pillow_version
from special_functions_atlas import BASE, PDF, SPEC_FILE, RECEIPTS, source_specs, digest

ROOT=Path(__file__).resolve().parents[1]


def main():
    pages,sources=source_specs(lambda p:(ROOT/p).read_text(encoding='utf-8-sig'))
    figures=[]
    directory=ROOT/'website'/Path(RECEIPTS).parent
    directory.mkdir(parents=True,exist_ok=True)
    for page in pages:
        if page['kind']!='lesson':continue
        name=page['figure'];source=BASE+'figures/'+name+'.png';pdf=BASE+'figures/'+name+'.pdf'
        original=Image.open(ROOT/source).convert('RGBA')
        buffer=io.BytesIO();original.save(buffer,format='WEBP',lossless=True,method=6,exact=True)
        raw=buffer.getvalue();converted=Image.open(io.BytesIO(raw)).convert('RGBA')
        if converted.size!=original.size or converted.tobytes()!=original.tobytes():
            raise ValueError('Lossless figure conversion changed pixels: '+name)
        image=Path(RECEIPTS).parent.as_posix()+'/'+name+'.webp'
        (ROOT/'website'/image).write_bytes(raw)
        figures.append(dict(name=name,source=source,source_sha256=digest((ROOT/source).read_bytes()),
            pdf_source=pdf,pdf_sha256=digest((ROOT/pdf).read_bytes()),
            image=image,image_sha256=digest(raw),width=original.width,height=original.height,
            rgba_sha256=digest(original.tobytes()),pixel_identity=True))
    receipt=dict(schema=1,conversion='lossless WebP; original and result decoded to RGBA and compared byte-for-byte',
                 pillow=pillow_version,figures=figures)
    receipt_raw=(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/'website'/RECEIPTS).write_bytes(receipt_raw)
    shutil.copyfile(ROOT/(BASE+'figures/F01_coefficient_addresses.png'),directory/'preview.png')
    descriptors=[{k:v for k,v in p.items() if k not in {'body','equation','description','example','takeaway','scope'}} for p in pages]
    metadata=dict(schema=1,inputs={p:digest((ROOT/p).read_bytes()) for p in sorted(set(sources)|{PDF})},
                  text_sources=sources,pages=descriptors,figure_receipts_sha256=digest(receipt_raw))
    SPEC_FILE.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(reading_pages=len(pages),lessons=len(figures),
        image_bytes=sum((ROOT/'website'/r['image']).stat().st_size for r in figures),
        all_rgba_pixels_identical=True,pillow=pillow_version)))


if __name__=='__main__':main()
