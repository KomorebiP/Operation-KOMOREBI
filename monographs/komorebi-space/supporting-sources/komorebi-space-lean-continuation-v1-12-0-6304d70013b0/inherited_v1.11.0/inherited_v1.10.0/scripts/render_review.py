#!/usr/bin/env python3
"""Render every page and record geometry checks; human review is separate."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import fitz

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    label=sys.argv[1]
    out=ROOT/'audit/renders'/label
    out.mkdir(parents=True,exist_ok=False)
    pdf=ROOT/'publication/Komorebi_Space_Monograph.pdf'
    doc=fitz.open(pdf)
    pages=[]
    outside=[]
    unresolved=[]
    for i,p in enumerate(doc,1):
        image=out/f'page_{i:03}.png'
        p.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(image)
        pages.append({'page':i,'png_sha256':sha(image)})
        for w in p.get_text('words'):
            if w[0]<0 or w[1]<0 or w[2]>p.rect.width or w[3]>p.rect.height:
                outside.append({'page':i,'word':w[:5]})
        if '??' in p.get_text(): unresolved.append(i)
    fonts=subprocess.run(['pdffonts',str(pdf)],text=True,capture_output=True,check=True)
    (ROOT/'audit'/f'{label}_fonts.txt').write_text(fonts.stdout)
    result={'pdf_sha256':sha(pdf),'page_count':len(doc),'render_directory':str(out),
            'render_scale':1.4,'page_hashes':pages,'out_of_page_words':outside,
            'literal_unresolved_reference_pages':unresolved,
            'human_visual_review':'pending; consult separate signed coverage record'}
    (ROOT/'audit'/f'{label}_render.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='page_hashes'},indent=2))

if __name__=='__main__': main()
