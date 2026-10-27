#!/usr/bin/env python3
"""Check atlas navigation, source routes, assets, and exact data consistency.

These checks supplement, rather than replace, rendered-page review.
"""
from __future__ import annotations
import argparse, ast, hashlib, json
from pathlib import Path
import fitz
from atlas_models import model_data


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output.resolve().is_relative_to(root):
        raise SystemExit('Write the check receipt outside the immutable checkpoint.')
    pdfpath = root/'publication/pdfs/Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf'
    doc = fitz.open(pdfpath)
    catalog = json.loads((root/'evidence/block05/PLATE_CATALOG.json').read_text())['plates']
    errors = []
    def need(condition, message):
        if not condition: errors.append(message)
    need(len(doc)==36, 'atlas must have 36 pages')
    need(len(catalog)==32, 'catalog must have 32 plates')
    counts = {'internal':0, 'companion':0, 'other':0}
    named_destinations = doc.resolve_names()
    named_internal_count = 0
    bounds = []
    for i, page in enumerate(doc):
        for link in page.get_links():
            rect = fitz.Rect(link['from'])
            need(page.rect.contains(rect), f'link rectangle out of bounds on page {i+1}')
            kind = link['kind']
            if kind == fitz.LINK_GOTO or (kind == fitz.LINK_NAMED and 'nameddest' in link):
                counts['internal'] += 1
                if kind == fitz.LINK_NAMED:
                    named_internal_count += 1
                    target = named_destinations.get(link['nameddest'])
                    need(target is not None and target.get('page') == link.get('page'), f'unresolved named destination on page {i+1}')
                need(0<=link.get('page', -1)<len(doc), f'invalid internal destination {i+1}')
            elif kind == fitz.LINK_GOTOR:
                counts['companion'] += 1
                target = pdfpath.parent/link['file']
                need(target.is_file(), f'missing companion file {target.name}')
                if target.is_file():
                    with fitz.open(target) as ref:
                        need(0<=link.get('page', -1)<len(ref), f'invalid companion page {i+1}')
            else:
                counts['other'] += 1
                errors.append(f'unexpected link kind {kind} on page {i+1}')
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    if not page.rect.contains(fitz.Rect(span['bbox'])):
                        bounds.append({'page':i+1, 'text':span['text'], 'box':span['bbox']})
                    need('\ufffd' not in span['text'], f'replacement glyph on page {i+1}')
    need(not bounds, 'text bounds issues')
    need(counts=={'internal':37,'companion':32,'other':0}, f'unexpected navigation counts {counts}')
    tree = ast.parse((root/'tools/test_atlas.py').read_text())
    methods = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
    source_checks = []
    for j, plate in enumerate(catalog, 1):
        hits=[i for i,page in enumerate(doc) if 'WORKED PLATE '+plate['id'] in page.get_text()]
        need(hits==[j+1], f'plate page mismatch: {plate["id"]}')
        p = root/plate['source_file']
        need(p.is_file() and sha(p)==plate['source_sha256'], f'plate source hash mismatch {plate["id"]}')
        for t in plate['tests']:need(t in methods, f'unknown mapped test {t}')
        if hits:
            links=[x for x in doc[hits[0]].get_links() if x['kind']==fitz.LINK_GOTOR]
            need(len(links)==1 and links[0]['file']==plate['source_reader'] and links[0]['page']==plate['pages'][0]-1,
                 f'wrong companion route {plate["id"]}')
        source_checks.append({'plate':plate['id'], 'atlas_page':j+2, 'source_pages':plate['pages'], 'tests':plate['tests']})
    figs = root/'publication/figures'
    manifest = json.loads((figs/'FIGURE_MANIFEST.json').read_text())
    assets=0
    for entry in manifest['figures']:
        need(entry['axes']==1, f'unexpected axes count {entry["plate"]}')
        for ext, digest in entry['outputs'].items():
            p=figs/(entry['plate']+'.'+ext)
            need(p.is_file() and sha(p)==digest, f'figure hash mismatch {p.name}')
            assets+=1
    need(assets==96, 'must have 96 PDF/SVG/PNG figure exports')
    need(json.loads((figs/'ATLAS_MODEL_DATA.json').read_text())==json.loads(json.dumps(model_data())), 'model data mismatch')
    toc=doc.get_toc()
    need(len(toc)==35, 'bookmark count mismatch')
    need(all(1<=row[2]<=len(doc) for row in toc), 'invalid bookmark destination')
    rep={'status':'passed' if not errors else 'failed', 'atlas_pages':len(doc), 'plate_count':len(catalog),
         'bookmark_count':len(toc), 'link_counts':counts, 'named_internal_links_resolved':named_internal_count, 'figure_exports':assets,
         'new_test_methods':len(methods), 'plate_routes':source_checks, 'text_bounds_issues':bounds,
         'errors':errors, 'pdf_sha256':sha(pdfpath),
         'scope':'File and finite-data consistency. Does not certify arithmetic statements or PDF viewer behavior.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep,indent=2))
    return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
