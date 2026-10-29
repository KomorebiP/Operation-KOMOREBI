"""Render the retained Paper IV TikZ drawings without regenerating their data.

Run only when updating the checked-in atlas images. The website build verifies
the source and image receipts and does not require a TeX installation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

BASE = 'papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/'
PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage{amsmath,amssymb,tikz}
\usepackage{fontspec,unicode-math}
\setsansfont{texgyreheros-regular.otf}[BoldFont=texgyreheros-bold.otf,Scale=.94]
\setmathfont{latinmodern-math.otf}
\usetikzlibrary{arrows.meta,decorations.pathreplacing,patterns,calc}
\usepackage[active,tightpage]{preview}
\PreviewEnvironment{tikzpicture}
\setlength\PreviewBorder{8pt}
\begin{document}
'''


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--tectonic',type=Path,required=True)
    parser.add_argument('--pdftoppm',type=Path,required=True)
    parser.add_argument('--stage',type=Path,required=True)
    args=parser.parse_args()
    root=args.root.resolve(); stage=args.stage.resolve()
    if stage.exists() and any(stage.iterdir()): raise ValueError('Use an empty staging directory')
    stage.mkdir(parents=True,exist_ok=True)
    source=root/BASE/'visual_graphics'
    names=json.loads((source/'PLATE_INDEX.json').read_bytes())['plates']
    if len(names)!=24 or len(set(names))!=24: raise ValueError('Review the changed figure inventory')
    for name in names:
        shutil.copyfile(source/(name+'.tex'),stage/(name+'.tex'))
    tex=PREAMBLE+'\n'.join(r'\input{'+name+'}' for name in names)+'\n'+r'\end{document}'+'\n'
    (stage/'figures.tex').write_text(tex,encoding='utf-8',newline='\n')
    compiler=args.tectonic.resolve(); renderer=args.pdftoppm.resolve()
    subprocess.run([str(compiler),'-X','compile','--untrusted','--keep-logs','figures.tex'],cwd=stage,check=True)
    log=(stage/'figures.log').read_text(encoding='utf-8',errors='replace')
    if 'Missing character:' in log or 'Undefined control sequence' in log: raise ValueError('Figure glyph or TeX error')
    subprocess.run([str(renderer),'-png','-scale-to-x','1800','-scale-to-y','-1','figures.pdf','drawing'],cwd=stage,check=True)
    images=sorted(stage.glob('drawing-*.png'))
    if len(images)!=len(names): raise ValueError('Unexpected figure page count')
    output=root/'website/assets/atlas/paper-iv'
    output.mkdir(parents=True,exist_ok=True)
    records=[]
    for name,image in zip(names,images):
        dest=output/(name+'.png'); shutil.copyfile(image,dest)
        records.append(dict(name=name,source=BASE+'visual_graphics/'+name+'.tex',
                            source_sha256=digest((source/(name+'.tex')).read_bytes()),
                            image='assets/atlas/paper-iv/'+name+'.png',image_sha256=digest(dest.read_bytes())))
    version=subprocess.run([str(renderer),'-v'],capture_output=True,text=True,check=True)
    report=dict(compiler=subprocess.check_output([str(compiler),'--version'],text=True).strip(),
                renderer=(version.stdout+version.stderr).splitlines()[0],
                recipe_sha256=digest(tex.encode()),figures=records,
                scope='Rendering unchanged TikZ only. No mathematical model, proof or Lean replay.')
    (output/'figures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(figures=len(records),output=str(output))))


if __name__=='__main__': main()
