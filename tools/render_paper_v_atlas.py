"""Render reviewed Paper V drawing crops from the unchanged guide PDF.

Requires pypdfium2 only for regeneration; ordinary site builds check the
committed images and source identities without rendering PDFs or running TeX.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASE = 'papers/paper-v/current/editable/traditional/'
PDF = 'papers/paper-v/current/papers/Paper_V_Visual_Guide_Final.pdf'
PDF_SHA256 = 'f3a84216d2fb02169d026cbfafb62a623a87b95e88c7cad35c85160a41739bca'
# Top-left PDF point coordinates, reviewed against the complete guide pages.
CROPS = [
    ('three_worlds',1,[65,170,548,334]),
    ('addresses',3,[65,160,548,344]),
    ('refinement',4,[65,177,548,368]),
    ('fir_transfer',5,[65,160,548,385]),
    ('sample_delay',6,[65,155,548,352]),
    ('perfect_reconstruction',7,[65,191,548,371]),
    ('haar_alignment',8,[65,194,548,382]),
    ('lifting_geometry',9,[65,153,548,400]),
    ('depth_two',10,[65,157,548,382]),
    ('sparse_tail',11,[65,158,548,345]),
    ('complete_cuts',12,[65,167,548,359]),
    ('dynamic_program',13,[65,180,548,420]),
    ('selector_margin',14,[65,182,548,373]),
    ('known_edge',15,[65,193,548,385]),
    ('fourier_jump',16,[65,233,548,425]),
    ('mask_translation',17,[65,195,548,387]),
    ('error_budget',18,[65,157,548,349]),
    ('mask_geometry',19,[65,182,548,368]),
    ('product_conventions',20,[65,158,548,357]),
    ('nonlinear_shift',21,[65,194,548,398]),
    ('cayley_orbit',22,[65,200,548,461]),
    ('projective_poles',23,[65,220,548,404]),
    ('crt_refinement',24,[65,176,548,359]),
    ('sensitivity',25,[65,216,548,404]),
    ('ext_lattice',28,[65,194,548,444]),
    ('ext_frame',29,[65,206,548,354]),
    ('ext_tree',30,[65,155,548,330]),
    ('ext_trace',31,[65,205,548,420]),
    ('ext_amplification',32,[65,205,548,298]),
    ('ext_overlap',33,[65,229,548,359]),
    ('ext_location',34,[65,197,548,384]),
    ('ext_threshold',35,[65,218,548,344]),
    ('ext_repetition',36,[65,240,548,396]),
    ('ext_haar_margin',37,[65,232,548,330]),
    ('ext_two_grids',38,[65,183,548,375]),
    ('ext_differences',39,[65,177,548,304]),
    ('annals_gibbs_comparison',40,[65,234,548,470]),
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def build(root, pdf):
    import pypdfium2 as pdfium
    from importlib.metadata import version
    raw=pdf.read_bytes()
    if digest(raw)!=PDF_SHA256:
        raise ValueError('Paper V guide differs from the retained PDF')
    output=root/'website/assets/atlas/paper-v'
    output.mkdir(parents=True,exist_ok=True)
    records=[]
    with pdfium.PdfDocument(raw) as document:
        for name,number,bounds in CROPS:
            page=document[number+2]
            try:
                bitmap=page.render(scale=3)
                image=bitmap.to_pil().convert('RGB')
                image=image.crop(tuple(int(x*3) for x in bounds))
                target=output/(name+'.png');image.save(target)
                bitmap.close()
            finally:
                page.close()
            source=BASE+'visual_graphics/'+name+('.pdf' if name=='annals_gibbs_comparison' else '.tex')
            records.append(dict(name=name,plate=number,source=source,
                source_sha256=digest((root/source).read_bytes()),
                image=target.relative_to(root/'website').as_posix(),
                image_sha256=digest(target.read_bytes()),pdf_page=number+3,crop_pdf_points=bounds))
    receipt=dict(source_pdf=PDF,source_pdf_sha256=PDF_SHA256,
        renderer='pypdfium2 '+version('pypdfium2'),dpi=216,figures=records,
        scope='Original PDF drawings; no TeX rebuild, example execution, proof audit or Lean replay.')
    (output/'figures.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Rendered',len(records),'Paper V drawings')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--pdf',type=Path)
    args=parser.parse_args()
    build(args.root.resolve(),args.pdf or args.root/PDF)
