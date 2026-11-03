"""Render retained Paper IX figure PDFs and extract their native labels only."""
import argparse
from importlib.metadata import version
import json
from pathlib import Path
import re
import unicodedata

from paper_ix_atlas import SPEC,RECEIPTS
from reader_atlas import digest


def build(root):
    import pypdfium2 as pdfium
    compact=lambda text:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKC',text).lower())
    raw=(root/SPEC['pdf']).read_bytes()
    if digest(raw)!=SPEC['pdf_sha256']:raise ValueError('Changed Paper IX visual PDF')
    with pdfium.PdfDocument(raw) as document:
        if len(document)!=25:raise ValueError('Changed Paper IX PDF page inventory')
        for section in SPEC['sections']:
            page=document[section['number']+1]
            try:
                textpage=page.get_textpage()
                try:
                    text=compact(textpage.get_text_range())
                    if compact(section['title']) not in text:raise ValueError('Changed Paper IX PDF section title')
                finally:textpage.close()
            finally:page.close()
    records=[];output=root/'website/assets/atlas/paper-ix';output.mkdir(parents=True,exist_ok=True)
    for name,binding in SPEC['figures'].items():
        raw=(root/binding['source']).read_bytes()
        if digest(raw)!=binding['source_sha256']:raise ValueError('Changed Paper IX vector figure')
        with pdfium.PdfDocument(raw) as document:
            if len(document)!=1:raise ValueError('Changed Paper IX figure page count')
            page=document[0]
            try:
                textpage=page.get_textpage()
                try:native=textpage.get_text_range().replace('\r\n','\n')
                finally:textpage.close()
                bitmap=page.render(scale=3)
                try:
                    image=bitmap.to_pil().convert('RGB');target=output/(name.replace('/','-')+'.png');image.save(target)
                    dimensions=list(image.size)
                finally:bitmap.close()
            finally:page.close()
        records.append(dict(name=name,**binding,image=target.relative_to(root/'website').as_posix(),
            image_sha256=digest(target.read_bytes()),dimensions=dimensions,native_text=native))
    receipt=dict(source_pdf=SPEC['pdf'],source_pdf_sha256=SPEC['pdf_sha256'],renderer='pypdfium2 '+version('pypdfium2'),dpi=216,
        checked_visual_pdf_pages=25,figures=records,scope='Original vector figure rendering and native text extraction only; no mathematical generator or TeX execution.')
    (root/'website'/RECEIPTS).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Checked 23 PDF sections; rendered 20 original figures')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    build(parser.parse_args().root)
