"""Extract unchanged Paper VII drawings from its frozen monograph PDF.

Requires Poppler pdftoppm. This renders PDF regions; it does not rebuild TeX
or execute any mathematical examples. --pdf can name a verified cached copy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

BASE = 'papers/paper-vii/current/editable/traditional/'
PDF = 'papers/paper-vii/current/papers/Paper_VII_Traditional_Final.pdf'
PDF_SHA256 = 'a4648faa8a1e6d3c15233eae64db2d1f7205ff2330a0dd861125313ea680d19e'
# PDF points, in top-left coordinates. Bounds preserve the whole drawing,
# including tick labels and legends, while excluding surrounding atlas prose.
CROPS = [
    ('three_objects', 1, [78, 244, 531, 423]),
    ('addresses', 3, [78, 204, 531, 384]),
    ('local_orbits', 4, [78, 196, 531, 377]),
    ('seed_rank', 5, [78, 222, 531, 402]),
    ('cyclic_four', 6, [78, 212, 531, 392]),
    ('parity', 7, [78, 218, 531, 398]),
    ('bell_circuit', 8, [78, 211, 531, 391]),
    ('interference', 9, [78, 205, 531, 385]),
    ('hamiltonian', 10, [78, 203, 531, 383]),
    ('leakage', 11, [78, 197, 531, 377]),
    ('moving_frame', 12, [78, 197, 531, 377]),
    ('connection', 13, [78, 197, 531, 377]),
    ('range_atlas', 14, [78, 208, 531, 390]),
    ('bloch_curvature', 15, [78, 239, 531, 419]),
    ('dephasing', 16, [78, 171, 531, 349]),
    ('damping', 17, [76, 210, 531, 390]),
    ('complete_positivity', 18, [78, 172, 531, 352]),
    ('syndromes', 19, [78, 172, 531, 352]),
    ('logical_error', 20, [78, 207, 531, 386]),
    ('feshbach', 21, [78, 218, 531, 397]),
    ('memory', 22, [78, 204, 531, 384]),
    ('euclidean', 23, [78, 210, 531, 390]),
    ('spectral_dimension', 24, [78, 210, 531, 389]),
    ('dispersion', 25, [78, 208, 531, 388]),
    ('constraints', 26, [78, 224, 531, 402]),
    ('perfect_transfer', 27, [78, 190, 531, 371]),
    ('s3', 29, [92, 249, 517, 371]),
    ('polar', 30, [92, 251, 517, 373]),
    ('choi', 31, [92, 202, 517, 325]),
    ('gram', 32, [92, 280, 517, 404]),
    ('defect', 33, [92, 292, 517, 414]),
    ('stability', 34, [92, 230, 517, 352]),
    ('memory_positive', 35, [92, 245, 517, 368]),
    ('transfer_ground', 36, [92, 235, 517, 358]),
    ('heat_limits', 37, [92, 252, 517, 375]),
    ('constraint_image', 38, [92, 197, 517, 320]),
    ('tower_tail', 39, [92, 210, 517, 333]),
    ('trace_topology', 40, [92, 220, 517, 343]),
]



def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def build(root, pdf, renderer):
    if digest(pdf.read_bytes()) != PDF_SHA256:
        raise ValueError('Paper VII monograph PDF differs from the frozen edition')
    output = root / 'website/assets/atlas/paper-vii'
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for name, number, bounds in CROPS:
        x0,y0,x1,y1 = bounds
        target = output / name
        # Three pixels per PDF point, with integral crop coordinates.
        subprocess.run([renderer,'-png','-singlefile','-f',str(number+117),'-l',str(number+117),
                        '-r','216','-x',str(x0*3),'-y',str(y0*3),
                        '-W',str((x1-x0)*3),'-H',str((y1-y0)*3),
                        str(pdf),str(target)],check=True)
        image = target.with_suffix('.png')
        source = BASE+('visual_graphics/' if number<=28 else 'visual_graphics_extended/')+name+'.tex'
        records.append(dict(name=name,plate=number,source=source,
                            source_sha256=digest((root/source).read_bytes()),
                            image=image.relative_to(root/'website').as_posix(),
                            image_sha256=digest(image.read_bytes()),
                            pdf_page=number+117,crop_pdf_points=bounds))
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
