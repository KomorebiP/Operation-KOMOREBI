"""Extract unchanged Paper VI drawings from its frozen visual-guide PDF.

Requires Poppler pdftoppm. This renders PDF regions; it does not rebuild TeX
or execute any mathematical examples. --pdf can name a verified cached copy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

BASE = 'papers/paper-vi/current/editable/traditional/'
PDF = 'papers/paper-vi/current/papers/Paper_VI_Visual_Guide_Final.pdf'
PDF_SHA256 = '1c13f03f789d0c6d6ea465fb734b9305ddaaf7f575225932bfaccd1b25cd3a0b'
# PDF points, in top-left coordinates. Bounds preserve the whole drawing,
# including tick labels and legends, while excluding surrounding atlas prose.
CROPS = [
    ('three_views',1,[60,196,552,365]),
    ('clock',3,[60,244,552,433]),
    ('generator_modes',4,[60,247,552,426]),
    ('lumpability',5,[60,220,552,400]),
    ('defect_budget',6,[60,218,552,402]),
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def build(root, pdf, renderer):
    if digest(pdf.read_bytes()) != PDF_SHA256:
        raise ValueError('Paper VI visual-guide PDF differs from the frozen edition')
    output = root / 'website/assets/atlas/paper-vi'
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for name, number, bounds in CROPS:
        x0,y0,x1,y1 = bounds
        target = output / name
        # Three pixels per PDF point, with integral crop coordinates.
        subprocess.run([renderer,'-png','-singlefile','-f',str(number+2),'-l',str(number+2),
                        '-r','216','-x',str(x0*3),'-y',str(y0*3),
                        '-W',str((x1-x0)*3),'-H',str((y1-y0)*3),
                        str(pdf),str(target)],check=True)
        image = target.with_suffix('.png')
        source = BASE+'visual_graphics/'+name+'.tex'
        records.append(dict(name=name,plate=number,source=source,
                            source_sha256=digest((root/source).read_bytes()),
                            image=image.relative_to(root/'website').as_posix(),
                            image_sha256=digest(image.read_bytes()),
                            pdf_page=number+2,crop_pdf_points=bounds))
    version = subprocess.run([renderer,'-v'],capture_output=True,text=True,check=True)
    report = dict(source_pdf=PDF,source_pdf_sha256=PDF_SHA256,
                  renderer=(version.stdout+version.stderr).splitlines()[0],
                  dpi=216,figures=records,
                  scope='Views of the frozen PDF drawings. No TeX rebuild, example execution, proof audit or Lean replay.')
    (output/'figures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--pdf',type=Path)
    parser.add_argument('--pdftoppm',default=shutil.which('pdftoppm'))
    args = parser.parse_args()
    if not args.pdftoppm:
        parser.error('Install Poppler or supply --pdftoppm PATH')
    build(args.root.resolve(),(args.pdf or args.root/PDF).resolve(),args.pdftoppm)
