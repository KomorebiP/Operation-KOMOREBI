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
    ('three_views', 1, [60, 196, 552, 365]),
    ('clock', 3, [60, 244, 552, 433]),
    ('generator_modes', 4, [60, 247, 552, 426]),
    ('lumpability', 5, [60, 220, 552, 400]),
    ('defect_budget', 6, [60, 218, 552, 402]),
    ('weighted_projection', 7, [90, 261, 509, 411]),
    ('variance', 8, [100, 220, 509, 387]),
    ('evidence', 9, [97, 235, 503, 385]),
    ('insufficiency', 10, [93, 198, 509, 350]),
    ('loss_vector', 11, [110, 227, 503, 360]),
    ('odds', 12, [83, 223, 510, 377]),
    ('filter_order', 13, [97, 192, 503, 342]),
    ('beta', 14, [89, 218, 505, 370]),
    ('fractional', 15, [100, 221, 512, 384]),
    ('gap', 16, [78, 236, 511, 388]),
    ('random_clock', 17, [78, 223, 531, 381]),
    ('green', 18, [74, 284, 486, 434]),
    ('mesh', 19, [89, 252, 533, 399]),
    ('paths', 20, [97, 243, 512, 409]),
    ('resolvent', 21, [89, 277, 522, 428]),
    ('memory', 22, [83, 307, 524, 458]),
    ('jordan', 23, [83, 265, 517, 416]),
    ('survival', 24, [83, 290, 516, 440]),
    ('naturality', 25, [103, 286, 512, 413]),
    ('integrated_filter', 26, [90, 248, 516, 400]),
    ('summability', 27, [89, 244, 516, 392]),
    ('ext_paths', 29, [78, 266, 529, 412]),
    ('ext_closure', 30, [84, 231, 530, 360]),
    ('ext_tails', 31, [84, 251, 523, 438]),
    ('ext_obstruction', 32, [78, 259, 530, 428]),
    ('ext_hermite', 33, [85, 207, 527, 364]),
    ('ext_profiles', 34, [78, 279, 524, 431]),
    ('ext_information', 35, [78, 196, 523, 331]),
    ('ext_cumulants', 36, [78, 205, 523, 405]),
    ('ext_selection', 37, [84, 252, 524, 388]),
    ('ext_trajectory', 38, [83, 237, 530, 398]),
    ('ext_auxiliary', 39, [78, 244, 523, 414]),
    ('ext_risks', 40, [78, 212, 529, 352]),
    ('ext_substitution', 41, [78, 233, 530, 372]),
    ('ext_evidence', 42, [78, 128, 530, 246]),
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
