"""Render original symmetry figures, recording repeated manuscript uses."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
BASE='monographs/quantum-and-circuits/volume/'
OUTPUT='assets/figures/quantum-symmetry/'


def main():
    import pypdfium2 as pdfium
    from readable_chapters import group
    text=(ROOT/BASE/'generated/s_main.tex').read_text(encoding='utf-8')
    records={}
    for figure in re.finditer(r'\\begin\{figure\}\[H\](.*?)\\end\{figure\}',text,re.S):
        match=re.search(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',figure[1])
        caption_match=re.search(r'\\caption\{',figure[1])
        if not match or not caption_match:raise ValueError('Review original symmetry figure syntax')
        caption,_=group(figure[1],caption_match.end()-1)
        source=BASE+match[1]
        if source in records:
            records[source]['uses']+=1;records[source]['captions'].append(caption);continue
        raw=(ROOT/source).read_bytes();document=pdfium.PdfDocument(raw)
        if len(document)!=1:raise ValueError('Symmetry figures must have one page: '+source)
        bitmap=document[0].render(scale=2.5);image=bitmap.to_pil()
        target=ROOT/'website'/OUTPUT/(Path(source).stem+'.png')
        target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
        records[source]=dict(source=source,source_sha256=hashlib.sha256(raw).hexdigest(),
            image=OUTPUT+target.name,image_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            width=image.width,height=image.height,scale=2.5,uses=1,captions=[caption])
        bitmap.close();document.close()
    if len(records)!=18 or sum(r['uses'] for r in records.values())!=19:
        raise ValueError('Review symmetry figure inventory')
    (ROOT/'website'/OUTPUT/'figures.json').write_text(json.dumps(dict(figures=list(records.values())),indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print('Rendered 18 original symmetry figures for 19 manuscript appearances.')


if __name__=='__main__':main()
