#!/usr/bin/env python3
"""Check source references and PDF geometry; optionally render review sheets.
Requires PyMuPDF and Pillow for rendering. Does not check mathematical proofs.
"""
from pathlib import Path
from collections import Counter
import argparse,json,re
import fitz

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf',type=Path)
    ap.add_argument('--render',type=Path)
    args=ap.parse_args();root=Path(__file__).resolve().parents[1]
    tex=root/'Machine_Societies_v0.6.0.tex';s=tex.read_text()
    labels=re.findall(r'\\label\{([^}]+)\}',s)
    refs=re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',s)
    keys=re.findall(r'\\bibitem\{([^}]+)\}',s)
    cites=[k.strip() for t in re.findall(r'\\cite\{([^}]+)\}',s) for k in t.split(',')]
    inventory={'duplicate_labels':[l for l,c in Counter(labels).items() if c>1], 'missing_refs':sorted(set(refs)-set(labels)), 'missing_cites':sorted(set(cites)-set(keys)), 'unused_bib':sorted(set(keys)-set(cites)), 'bib_entries':len(keys), 'statements':{t:len(re.findall(r'\\begin\{'+t+r'\}',s)) for t in ['theorem','proposition','definition','counterexample']},'figures':s.count('\\begin{figure}')}
    (root/'validation/source_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    pdf=args.pdf or root/'build/Machine_Societies_v0.6.0.pdf';doc=fitz.open(pdf)
    issues=[];pages=[]
    for i,p in enumerate(doc,1):
        words=p.get_text('words');txt=p.get_text()
        bad=[w[:5] for w in words if w[0]<-.2 or w[1]<-.2 or w[2]>p.rect.width+.2 or w[3]>p.rect.height+.2]
        if bad:issues.append({'page':i,'out_of_page_words':bad})
        if '??' in txt or '\ufffd' in txt:issues.append({'page':i,'unresolved_or_replacement_marker':True})
        pages.append({'page':i,'words':len(words)})
        if args.render:
            args.render.mkdir(parents=True,exist_ok=True)
            p.get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False).save(args.render/f'page-{i:02}.png')
    if args.render:
        from PIL import Image,ImageDraw
        for start in range(0,len(doc),12):
            canvas=Image.new('RGB',(1040,1080),'white');draw=ImageDraw.Draw(canvas)
            for j,n in enumerate(range(start,min(start+12,len(doc)))):
                im=Image.open(args.render/f'page-{n+1:02}.png').convert('RGB');im.thumbnail((248,330))
                x=(j%4)*260+(260-im.width)//2;y=(j//4)*360
                canvas.paste(im,(x,y+19));draw.text(((j%4)*260+8,y+3),f'PDF {n+1}',fill='black')
            canvas.save(args.render/f'contact-{start//12+1:02}.png')
    log=root/'build/Machine_Societies_v0.6.0.log'
    diagnostics=[]
    if log.exists():diagnostics=[line for line in log.read_text(errors='replace').splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|Undefined',line)]
    out={'pages':len(doc),'all_pages_rendered':bool(args.render),'page_geometry_and_text_issues':issues,'final_compiler_diagnostics':diagnostics,'page_word_counts':pages,'scope':'Geometry and text checks; visual review and mathematical proof review are separate.'}
    (root/'validation/pdf_preflight.json').write_text(json.dumps(out,indent=2)+'\n')
    failed=any(inventory[k] for k in ('duplicate_labels','missing_refs','missing_cites')) or bool(issues) or bool(diagnostics)
    print(json.dumps({'status':'FAIL' if failed else 'PASS','pages':len(doc),'inventory':inventory,'geometry_issues':len(issues),'compiler_diagnostics':diagnostics},indent=2))
    return int(failed)
if __name__=='__main__':raise SystemExit(main())
