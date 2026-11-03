"""Render the retained standalone atlas diagrams without rebuilding the PDF."""
import hashlib
import json
from pathlib import Path


def render(root):
    import pypdfium2 as pdfium
    from large_signal_atlas import BASE, FIGURE_MAP, RECEIPTS, metadata
    destination = root/'website'/Path(RECEIPTS).parent
    destination.mkdir(parents=True,exist_ok=True)
    source_map = json.loads((root/FIGURE_MAP).read_bytes())
    if hashlib.sha256((root/FIGURE_MAP).read_bytes()).hexdigest()!=metadata()['inputs'][FIGURE_MAP]:
        raise ValueError('Review changed source figure manifest')
    figures = []
    for original in source_map['figures']:
        path = BASE+original['file']; raw = (root/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=original['sha256']:
            raise ValueError('Retained atlas diagram differs: '+path)
        document = pdfium.PdfDocument(raw)
        if len(document)!=1:
            raise ValueError('Expected a single-page atlas diagram')
        name = Path(path).stem+'.png'
        document[0].render(scale=2).to_pil().save(destination/name,optimize=True)
        document.close()
        image = (destination/name).read_bytes()
        figures.append(dict(source=path,source_sha256=original['sha256'],
            image=Path(RECEIPTS).parent.as_posix()+'/'+name,image_sha256=hashlib.sha256(image).hexdigest(),
            interpretation=original['interpretation'],scale=2))
    receipt = dict(schema=1,rendering='PDFium, scale 2; original standalone vector diagrams',
        source_manifest=FIGURE_MAP,source_manifest_sha256=metadata()['inputs'][FIGURE_MAP],figures=figures)
    (root/'website'/RECEIPTS).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(figures=len(figures),png_bytes=sum((destination/Path(r['image']).name).stat().st_size for r in figures))))


if __name__=='__main__':
    render(Path(__file__).resolve().parents[1])
