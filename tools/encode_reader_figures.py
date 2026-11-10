"""Losslessly encode selected generated PNGs for the static reader website.

python -B tools/encode_reader_figures.py --apply
python -B tools/encode_reader_figures.py --check

Original PNG bytes move to verification/reader-figure-encoding/original and
remain available for every CI pixel comparison. Source PDFs remain unchanged.
"""
import argparse
import io
import json
from pathlib import Path, PurePosixPath

from PIL import Image, __version__ as pillow_version
from reader_figure_assets import digest, validate_encoding

ROOT=Path(__file__).resolve().parents[1]
GROUPS=('paper-v','komorebi-space','quantum-catalytic','quantum-arithmetic','quantum-symmetry')


def apply(root=ROOT):
    results=[]
    for name in GROUPS:
        directory='assets/figures/'+name
        receipt_path=root/'website'/directory/'figures.json'
        receipt=json.loads(receipt_path.read_bytes())
        for row in receipt['figures']:
            stem=PurePosixPath(row['source']).stem
            target_image=directory+'/'+stem+'.webp'
            png_image=directory+'/'+stem+'.png'
            if row['image']==target_image:
                validate_encoding(root,row,directory)
                continue
            if row['image']!=png_image:
                raise ValueError('Unexpected generated figure path')
            png_path=(root/'website'/png_image).resolve()
            if not png_path.is_relative_to((root/'website/assets/figures').resolve()):
                raise ValueError('Original figure outside intended asset directory')
            original=png_path.read_bytes()
            if digest(original)!=row['image_sha256']:
                raise ValueError('Original generated PNG hash differs: '+png_image)
            with Image.open(io.BytesIO(original)) as image:
                if image.format!='PNG' or getattr(image,'n_frames',1)!=1:
                    raise ValueError('Expected one static original PNG')
                rgba=image.convert('RGBA')
                buffer=io.BytesIO();rgba.save(buffer,format='WEBP',lossless=True,method=6,exact=True)
                encoded=buffer.getvalue()
                with Image.open(io.BytesIO(encoded)) as decoded:
                    if decoded.size!=rgba.size or decoded.convert('RGBA').tobytes()!=rgba.tobytes():
                        raise ValueError('Lossless conversion changed pixels')
                row.update(original_png='verification/reader-figure-encoding/original/'+name+'/'+stem+'.png',
                    original_png_sha256=digest(original),source_rgba_sha256=digest(rgba.tobytes()),
                    image=target_image,image_sha256=digest(encoded),width=rgba.width,height=rgba.height)
            archived=(root/row['original_png']).resolve()
            if not archived.is_relative_to((root/'verification/reader-figure-encoding/original').resolve()):
                raise ValueError('Original PNG archive outside intended directory')
            archived.parent.mkdir(parents=True,exist_ok=True)
            if archived.exists() and archived.read_bytes()!=original:
                raise ValueError('An archived original differs')
            archived.write_bytes(original)
            output=root/'website'/target_image
            output.write_bytes(encoded)
            validate_encoding(root,row,directory)
            # The verified original is archived byte-for-byte before removing the
            # published duplicate. Both paths have fixed, checked parent roots.
            png_path.unlink()
        receipt['browser_encoding']=dict(format='lossless WebP',pillow=pillow_version,
            pixel_contract='Each original PNG and WebP decode to identical RGBA bytes.',
            original_location='verification/reader-figure-encoding/original/'+name,
            command='python -B tools/encode_reader_figures.py --check')
        receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        results.append(summary(root,name,receipt))
    return results


def summary(root,name,receipt):
    original=sum((root/r['original_png']).stat().st_size for r in receipt['figures'])
    encoded=sum((root/'website'/r['image']).stat().st_size for r in receipt['figures'])
    return dict(group=name,figures=len(receipt['figures']),original_bytes=original,
                encoded_bytes=encoded,saved_bytes=original-encoded)


def check(root=ROOT):
    results=[]
    for name in GROUPS:
        directory='assets/figures/'+name
        receipt=json.loads((root/'website'/directory/'figures.json').read_bytes())
        for row in receipt['figures']:
            if PurePosixPath(row['image']).suffix!='.webp':
                raise ValueError('Selected figure still uses PNG')
            validate_encoding(root,row,directory)
            if (root/'website'/directory/(PurePosixPath(row['source']).stem+'.png')).exists():
                raise ValueError('Published duplicate original PNG remains')
        results.append(summary(root,name,receipt))
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--apply',action='store_true');action.add_argument('--check',action='store_true')
    args=parser.parse_args()
    groups=apply() if args.apply else check()
    print(json.dumps(dict(groups=groups,figures=sum(r['figures'] for r in groups),
        original_bytes=sum(r['original_bytes'] for r in groups),encoded_bytes=sum(r['encoded_bytes'] for r in groups),
        saved_bytes=sum(r['saved_bytes'] for r in groups),all_rgba_pixels_identical=True),indent=2))
