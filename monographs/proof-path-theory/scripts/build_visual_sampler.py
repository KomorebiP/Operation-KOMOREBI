"""Extract a checked eight-page sampler from the current monograph."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
PAGES = (1, 3, 16, 23, 32, 34, 36, 37)


def main() -> None:
    source = ROOT / 'docs/Proof_Path_Theory.pdf'
    target = ROOT / 'docs/Proof_Path_Theory_Visual_Sampler.pdf'
    with fitz.open(source) as doc:
        if len(doc) != 76 or 'Monograph edition 1.8.0' not in doc[0].get_text():
            raise RuntimeError('Unexpected source edition or pagination; update the sample explicitly')
        selected_text = [doc[p-1].get_text() for p in PAGES]
        with fitz.open() as sample:
            for p in PAGES:
                sample.insert_pdf(doc, from_page=p-1, to_page=p-1, links=False)
            sample.set_metadata({'title':'Proof Path Theory — visual sampler 1.8.0',
                                 'author':'Komorebi P.',
                                 'subject':'Eight selected pages from monograph 1.8.0'})
            sample.save(target, garbage=4, deflate=True)
    with fitz.open(target) as sample:
        if [p.get_text() for p in sample] != selected_text:
            raise RuntimeError('Sampler text differs from the chosen source pages')
    receipt = {'edition':'1.8.0','status':'PASS','source_pages':PAGES,
               'source_pdf_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
               'sampler_pdf_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
               'check':'Exact extracted text matches on all eight chosen pages.'}
    (ROOT/'data/visual_sampler_1.8.0.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
