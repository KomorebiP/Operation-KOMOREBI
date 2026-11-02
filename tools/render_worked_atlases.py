"""Reproduce the Paper II/III drawings from their retained PDFs (pypdfium2)."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
from worked_atlas_sources import SOURCES


def digest(raw):return hashlib.sha256(raw).hexdigest()


def build(root,work):
    import pypdfium2 as pdfium
    spec=SOURCES[work];raw=(root/spec['pdf']).read_bytes()
    if digest(raw)!=spec['sha256']:raise ValueError('Changed visual-guide PDF: '+work)
    output=root/'website/assets/atlas'/work;output.mkdir(parents=True,exist_ok=True)
    records=[]
    with pdfium.PdfDocument(raw) as document:
        for name,number,bounds in spec['crops']:
            page=document[number+spec['offset']-1]
            try:
                bitmap=page.render(scale=3)
                image=bitmap.to_pil().convert('RGB').crop(tuple(x*3 for x in bounds))
                target=output/(name+'.png');image.save(target);bitmap.close()
            finally:page.close()
            source=spec['base']+'visual_graphics/'+name+'.tex'
            records.append(dict(name=name,plate=number,source=source,source_sha256=digest((root/source).read_bytes()),
                image=target.relative_to(root/'website').as_posix(),image_sha256=digest(target.read_bytes()),
                pdf_page=number+spec['offset'],crop_pdf_points=bounds))
    receipt=dict(source_pdf=spec['pdf'],source_pdf_sha256=spec['sha256'],renderer='pypdfium2 '+version('pypdfium2'),dpi=216,
        figures=records,scope='Original visual-guide drawings; no TeX rebuild, example execution, proof audit or Lean replay.')
    (output/'figures.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Rendered',len(records),work,'drawings')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--work',choices=list(SOURCES))
    args=parser.parse_args()
    for work in [args.work] if args.work else SOURCES:build(args.root,work)
