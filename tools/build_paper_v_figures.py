"""Render unchanged Paper V figure PDFs for the HTML reader.

Run only to regenerate the checked-in PNGs. Normal website builds verify the
source and image digests and need no PDF rendering installation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from paper_v_chapters import BOOK,CHAPTERS,MAIN
from reader_figure_assets import candidates

def digest(raw): return hashlib.sha256(raw).hexdigest()

def build(root,renderer):
    text=(root/MAIN).read_text(encoding='utf-8-sig')
    receipt=json.loads((root/'manifests/source-imports/paper-v.json').read_bytes())
    owned={'papers/paper-v/current/'+f['path']:f for f in receipt['files']}
    output=root/'website/assets/figures/paper-v'
    output.mkdir(parents=True,exist_ok=True)
    records=[]
    for match in re.finditer(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',text):
        line=text.count('\n',0,match.start())+1
        spec=next(c for c in CHAPTERS if c['start_line']<=line<=c['end_line'])
        found=[p for p in candidates(BOOK,spec,match[1]) if p in owned]
        if len(found)!=1: raise ValueError('Ambiguous figure source')
        source=found[0]; raw=(root/source).read_bytes()
        if digest(raw)!=owned[source]['sha256']: raise ValueError('Source figure differs')
        info=subprocess.run([str(renderer.with_name('pdfinfo'+renderer.suffix)),str(root/source)],
                            text=True,capture_output=True,check=True)
        if not re.search(r'^Pages:\s+1\s*$',info.stdout,re.M):
            raise ValueError('Figure PDF must have exactly one page: '+source)
        name=Path(source).stem
        prefix=output/name
        subprocess.run([str(renderer),'-singlefile','-png','-scale-to-x','1800','-scale-to-y','-1',
                        str(root/source),str(prefix)],check=True)
        image='assets/figures/paper-v/'+name+'.png'
        records.append(dict(source=source,source_sha256=digest(raw),image=image,
                            image_sha256=digest((root/'website'/image).read_bytes())))
    if len(records)!=35 or len({r['image'] for r in records})!=35:
        raise ValueError('Review changed Paper V figure inventory')
    version=subprocess.run([str(renderer),'-v'],text=True,capture_output=True,check=True)
    report=dict(renderer=(version.stdout+version.stderr).splitlines()[0],
                recipe='pdftoppm -singlefile -png -scale-to-x 1800 -scale-to-y -1',
                scope='Render retained PDFs only. No mathematical example, proof review or Lean execution.',
                figures=records)
    (output/'figures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--pdftoppm',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(dict(figures=len(build(args.root.resolve(),args.pdftoppm.resolve())['figures']))))
