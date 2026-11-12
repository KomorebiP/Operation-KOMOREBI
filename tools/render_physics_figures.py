"""Render the retained foundations PDFs with source and image identity receipts."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'monographs/physics/source/monographs/'
OUTPUT = 'assets/figures/physics-foundations/'


def main():
    import pypdfium2 as pdfium
    from readable_chapters import group
    records = []
    for name in ('orientation', 'core', 'refinement', 'extensions', 'conclusion', 'references'):
        text = (ROOT/BASE/'foundations'/f'{name}.tex').read_text(encoding='utf-8')
        for match in re.finditer(r'\\foundationfigure(?:\[[^\]]+\])?\{([^{}]+)\}', text):
            caption, _ = group(text, match.end())
            source = BASE+'foundation_figures/'+match[1]+'.pdf'
            raw = (ROOT/source).read_bytes()
            document = pdfium.PdfDocument(raw)
            if len(document) != 1:
                raise ValueError('Physics figures must have one page: '+source)
            page = document[0]
            bitmap = page.render(scale=2.5)
            image = bitmap.to_pil()
            target = ROOT/'website'/OUTPUT/(match[1]+'.png')
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target)
            records.append(dict(source=source,source_sha256=hashlib.sha256(raw).hexdigest(),
                image=OUTPUT+target.name,image_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                width=image.width,height=image.height,scale=2.5,caption=caption))
            image.close(); bitmap.close(); page.close(); document.close()
    if len(records) != 10 or len({r['source'] for r in records}) != 10:
        raise ValueError('Review Physics foundations figure inventory')
    (ROOT/'website'/OUTPUT/'figures.json').write_text(json.dumps(dict(figures=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Rendered ten original Physics foundations figures.')


if __name__ == '__main__':
    main()
