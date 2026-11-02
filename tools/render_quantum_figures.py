"""Render the twenty retained arithmetic figure PDFs and their source receipts."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
BASE='monographs/quantum-and-circuits/volume/'
OUTPUT='assets/figures/quantum-arithmetic/'


def main():
    import pypdfium2 as pdfium
    from readable_chapters import group
    text=(ROOT/BASE/'generated/q_visual.tex').read_text(encoding='utf-8')
    records=[]
    for match in re.finditer(r'\\fig\{([^{}]+)\}',text):
        _,end=group(text,match.end());caption,end=group(text,end)
        source=BASE+'assets/q_'+match[1]+'.pdf';raw=(ROOT/source).read_bytes()
        document=pdfium.PdfDocument(raw)
        if len(document)!=1:raise ValueError('Arithmetic figures must have one page: '+source)
        bitmap=document[0].render(scale=2.5)
        image=bitmap.to_pil();target=ROOT/'website'/OUTPUT/('q_'+match[1]+'.png')
        target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
        records.append(dict(source=source,source_sha256=hashlib.sha256(raw).hexdigest(),
            image=OUTPUT+target.name,image_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            width=image.width,height=image.height,scale=2.5,caption=caption))
        bitmap.close();document.close()
    if len(records)!=20 or len({r['source'] for r in records})!=20:
        raise ValueError('Review arithmetic figure inventory')
    (ROOT/'website'/OUTPUT/'figures.json').write_text(json.dumps(dict(figures=records),indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print('Rendered 20 original arithmetic figures.')


if __name__=='__main__':main()
