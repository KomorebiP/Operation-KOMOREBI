"""Reproduce Paper I drawings from the retained monograph PDF (pypdfium2)."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

BASE='papers/paper-i/current/editable/traditional/'
PDF='papers/paper-i/current/papers/Paper_I_Traditional_Final.pdf'
PDF_SHA256='35f0f7511ed0fbeffac16977ec50028c0e93e5da57c1e6c7748cee89c70a5183'
PDF_PAGE_OFFSET=82
# Top-left PDF point coordinates, reviewed against the complete source pages.
CROPS=[
 ('grammar_budget',1,[55,289,557,487]),
 ('linked_chains',3,[55,248,557,426]),
 ('quotient_heads',4,[55,242,557,393]),
 ('left_ideal',5,[55,358,557,510]),
 ('typed_spaces',6,[55,290,557,412]),
 ('oblique_vectors',7,[55,240,557,453]),
 ('block_square',8,[55,193,557,385]),
 ('cancelled_paths',9,[55,246,557,448]),
 ('support_closure',10,[55,203,557,346]),
 ('transported_packets',11,[55,192,557,417]),
 ('shared_independent',12,[55,192,557,355]),
 ('row_budget',13,[55,236,557,355]),
 ('primary_krylov',14,[55,221,557,437]),
 ('path_walks',15,[55,217,557,487]),
 ('cycle_multiplicity',16,[55,190,557,358]),
 ('normal_form',17,[55,228,557,411]),
 ('shift_tail',18,[55,235,557,447]),
 ('residue_carry',19,[55,222,557,395]),
 ('hull_iteration',20,[55,253,557,481]),
 ('tensor_rectangle',21,[55,278,557,414]),
]


def digest(raw):return hashlib.sha256(raw).hexdigest()


def build(root,pdf):
    import pypdfium2 as pdfium
    raw=pdf.read_bytes()
    if digest(raw)!=PDF_SHA256:raise ValueError('Changed Paper I monograph PDF')
    output=root/'website/assets/atlas/paper-i';output.mkdir(parents=True,exist_ok=True)
    records=[]
    with pdfium.PdfDocument(raw) as document:
        for name,number,bounds in CROPS:
            page=document[number+PDF_PAGE_OFFSET-1]
            try:
                bitmap=page.render(scale=3)
                image=bitmap.to_pil().convert('RGB').crop(tuple(x*3 for x in bounds))
                target=output/(name+'.png');image.save(target);bitmap.close()
            finally:page.close()
            source=BASE+'visual_graphics/'+name+'.tex'
            records.append(dict(name=name,plate=number,source=source,
                source_sha256=digest((root/source).read_bytes()),
                image=target.relative_to(root/'website').as_posix(),image_sha256=digest(target.read_bytes()),
                pdf_page=number+PDF_PAGE_OFFSET,crop_pdf_points=bounds))
    receipt=dict(source_pdf=PDF,source_pdf_sha256=PDF_SHA256,renderer='pypdfium2 '+version('pypdfium2'),
        dpi=216,figures=records,scope='Original monograph drawings; no TeX rebuild, example execution, proof audit or Lean replay.')
    (output/'figures.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Rendered',len(records),'Paper I drawings')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--pdf',type=Path)
    args=parser.parse_args();build(args.root,args.pdf or args.root/PDF)
