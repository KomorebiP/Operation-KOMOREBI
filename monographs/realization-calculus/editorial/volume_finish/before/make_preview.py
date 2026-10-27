#!/usr/bin/env python3
"""Create a bounded book design tour, preserving the full book's printed folios."""
from pathlib import Path
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parent


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def selected_interior(comp, offset=8):
    """Select a real retained page, never infer an index from raw page count."""
    kept = sorted(comp.get('keep_pages', []), key=lambda p: comp['book_pages'][str(p)])
    if not kept:
        return None
    raw = kept[min(offset, len(kept)-1)]
    return comp['book_pages'][str(raw)]


def select_pages(spec):
    leaves = {l['id']: l for l in spec['leaves']}
    components = {c['id']: c for p in spec['parts'] for c in p['components']}
    selected = list(range(spec['front_pages']))
    reasons = {i: ['preliminary matter'] for i in selected}
    def add(index, reason):
        if index is None:
            return
        if index not in reasons:
            selected.append(index); reasons[index] = []
        reasons[index].append(reason)
    for unit in spec['reading_units']:
        leaf = leaves[unit['leaf_id']]
        kind, paper = leaf['kind'], leaf.get('paper')
        if kind in ('chapter', 'study') or (kind == 'formal_companion' and paper in ('I', 'VIII', 'XII')):
            add(leaf['book_index'], leaf['title'])
            retained = [components[cid] for cid in unit['component_ids'] if components[cid].get('keep_pages')]
            retained.sort(key=lambda c: min(c['book_pages'].values()))
            if retained:
                add(selected_interior(retained[0]), leaf['title'] + ': interior')
            if kind == 'formal_companion' and paper == 'I' and len(retained) > 1:
                add(selected_interior(retained[-1], 2), 'Formal companion I: Lean guide')
    for leaf in spec['leaves']:
        if leaf['kind'] in ('studies_division', 'formal_division', 'glossary'):
            add(leaf['book_index'], leaf['title'])
    # Include a normalized retained visual page and a canonical embedded atlas.
    for cid in ('IV_visual', 'VIII_visual', 'XI_research_atlas'):
        if cid in components:
            add(selected_interior(components[cid], 4), cid + ': retained visual page')
    glossary = spec['glossary']
    for offset in (0, glossary['pages']//2, glossary['pages']-1):
        add(glossary['index_start']+offset, 'Glossary')
    # A design tour follows the actual reader sequence even when selections overlap.
    return sorted(selected), reasons


def main():
    spec = json.loads((ROOT/'book/build_spec.json').read_text())
    path = ROOT/'output/Realization_Calculus.pdf'
    source = fitz.open(path)
    selected, reasons = select_pages(spec)
    if any(not 0 <= i < len(source) for i in selected):
        raise ValueError('Preview selection outside assembled book')
    preview = fitz.open()
    for i in selected:
        preview.insert_pdf(source, from_page=i, to_page=i, links=False, annots=False,
                           final=int(i == selected[-1]))
    preview.set_metadata({'title': 'Realization Calculus: Design Preview', 'author': 'Komorebi P.',
        'subject': 'Selected pages with the complete book’s printed folios',
        'creator': 'Realization Calculus publication source'})
    preview.set_toc([[1, 'Book page '+str(p+1)+' / '+source[p].get_label()+': '+reasons[p][0], i+1]
                     for i, p in enumerate(selected)])
    out = ROOT/'output/Realization_Calculus_Design_Preview.pdf'
    preview.save(out, garbage=3, deflate=True)
    report = {'pages': len(preview), 'source_book_pages': [p+1 for p in selected],
        'selections': [{'book_index': p, 'book_page': p+1, 'reasons': reasons[p]} for p in selected],
        'source_sha256': digest(path), 'preview_sha256': digest(out),
        'note': 'A selected-page design tour, not a shortened mathematical edition. Source links omitted in preview.'}
    (ROOT/'book/preview_manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
