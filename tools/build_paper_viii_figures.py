"""Regenerate browser PNGs from the unchanged, receipt-bound Paper VIII PDFs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from paper_viii_reading import BOOK, CHAPTERS
from reader_figure_assets import candidates
from readable_chapters import chapter_text


def digest(raw): return hashlib.sha256(raw).hexdigest()


def build(root, renderer):
    receipt=json.loads((root/'manifests/source-imports/paper-viii.json').read_bytes())
    owned={'papers/paper-viii/current/'+f['path']:f for f in receipt['files']}
    output=root/'website/assets/figures/paper-viii'
    output.mkdir(parents=True,exist_ok=True)
    records=[]
    for spec in CHAPTERS:
        text=chapter_text((root/spec['source']).read_text(encoding='utf-8-sig'),spec)
        for match in re.finditer(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',text):
            found=[p for p in candidates(BOOK,spec,match[1]) if p in owned]
            if len(found)!=1: raise ValueError('Ambiguous Paper VIII figure: '+match[1])
            source=found[0]; raw=(root/source).read_bytes()
            if digest(raw)!=owned[source]['sha256']: raise ValueError('Source figure differs: '+source)
            info=subprocess.run([str(renderer.with_name('pdfinfo'+renderer.suffix)),str(root/source)],
                                text=True,capture_output=True,check=True)
            if not re.search(r'^Pages:\s+1\s*$',info.stdout,re.M):
                raise ValueError('Figure PDF must have exactly one page: '+source)
            name=Path(source).stem
            subprocess.run([str(renderer),'-singlefile','-png','-scale-to-x','1800','-scale-to-y','-1',
                            str(root/source),str(output/name)],check=True)
            image='assets/figures/paper-viii/'+name+'.png'
            records.append(dict(source=source,source_sha256=digest(raw),image=image,
                                image_sha256=digest((root/'website'/image).read_bytes())))
    if len(records)!=25 or len({r['image'] for r in records})!=25:
        raise ValueError('Review changed Paper VIII figure inventory')
    version=subprocess.run([str(renderer),'-v'],text=True,capture_output=True,check=True)
    report=dict(renderer=(version.stdout+version.stderr).splitlines()[0],
        recipe='pdftoppm -singlefile -png -scale-to-x 1800 -scale-to-y -1',
        scope='Render retained figure PDFs only. No mathematical program, proof review or Lean execution.',
        figures=records)
    (output/'figures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--pdftoppm',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(dict(figures=len(build(args.root.resolve(),args.pdftoppm.resolve())['figures']))))
