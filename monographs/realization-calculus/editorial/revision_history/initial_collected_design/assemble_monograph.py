#!/usr/bin/env python3
"""Assemble the collected core papers with explicit source-page and link maps.

This is publication tooling. It does not execute mathematical or Lean checks.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit, parse_qs

import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

ROOT = Path(__file__).resolve().parent
BOOK = ROOT / 'book'
OUT = ROOT / 'output'
W, H = 612.0, 792.0
LEFT, WIDTH = 62.64, 486.72
PLUM, MULBERRY, GOLD = '#3C263F', '#7B4165', '#A68A56'
INK, MUTED, RULE = '#22282C', '#615963', '#D9CDD7'


def digest(p):
    with open(p, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(p, obj):
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def register_fonts():
    sources = {}
    for alias, stem in [('BookSerif', 'P052-Roman'), ('BookSans', 'NimbusSans-Regular'),
                        ('BookSansBold', 'NimbusSans-Bold')]:
        afm = Path('/usr/share/fonts/type1/urw-base35') / (stem + '.afm')
        pfb = Path('/usr/share/fonts/X11/Type1') / (stem + '.pfb')
        if not afm.is_file() or not pfb.is_file():
            raise FileNotFoundError(f'Install the explicit URW font: {stem}')
        face = pdfmetrics.EmbeddedType1Face(str(afm), str(pfb))
        pdfmetrics.registerTypeFace(face)
        pdfmetrics.registerFont(pdfmetrics.Font(alias, face.name, 'WinAnsiEncoding'))
        sources[alias] = [{'path': str(p), 'sha256': digest(p)} for p in (afm, pfb)]
    return sources


def transformed_rect(rect, transform):
    scale, tx, ty = transform
    r = fitz.Rect(rect)
    return fitz.Rect(r.x0 * scale + tx, r.y0 * scale + ty,
                     r.x1 * scale + tx, r.y1 * scale + ty)


def transformed_point(point, transform):
    scale, tx, ty = transform
    p = fitz.Point(point)
    return fitz.Point(p.x * scale + tx, p.y * scale + ty)


def page_transform(rect, folio, preserved):
    if preserved:
        # Keep every source pixel, including inherited page furniture. No crop.
        frame = fitz.Rect(24, 55, 588, 741)
        scale = min(frame.width / rect.width, frame.height / rect.height)
        tx = frame.x0 + (frame.width - rect.width * scale) / 2
        ty = frame.y0 + (frame.height - rect.height * scale) / 2
    else:
        if abs(rect.width - W) > .1 or abs(rect.height - H) > .1:
            raise ValueError(f'Retypeset component is not letter size: {rect}')
        scale, tx, ty = 1.0, (6.0 if folio % 2 else -6.0), 0.0
    return scale, tx, ty


def main():
    BOOK.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    spec = json.loads((BOOK / 'build_spec.json').read_text())
    front_count = spec['front_pages']
    parts = spec['parts']
    components = [c for p in parts for c in p['components']]
    if len(parts) != 12 or len({c['id'] for c in components}) != len(components):
        raise ValueError('The book must have twelve parts and unique component IDs.')
    subprocess.run([sys.executable, str(ROOT / 'render_outer.py')], cwd=ROOT, check=True)
    font_record = register_fonts()
    book, front, dividers = fitz.open(), fitz.open(BOOK / 'frontmatter.pdf'), fitz.open(BOOK / 'part_leaves.pdf')
    assert len(front) == front_count and len(dividers) == 12
    book.insert_pdf(front, links=False)
    documents, names, alias_map = {}, {}, {}
    source_map, page_records, transforms = {}, {}, {}
    source_links, original_tocs = {}, {}
    component_by_id = {c['id']: c for c in components}
    for comp in components:
        baseline = ROOT / comp['baseline_path']
        if digest(baseline) != comp['baseline_sha256']:
            raise ValueError(f'Frozen source bytes changed: {baseline.name}')
        book.embfile_add(baseline.name, baseline.read_bytes(), filename=baseline.name,
                         ufilename=baseline.name,
                         desc=f'Frozen reference edition, Paper {comp["paper"]}: {comp["title"]}')
    toc = [[1, 'Title', 2], [1, 'Scope and edition', 3], [1, 'Introduction', 4],
           [1, 'Reading conventions', 5], [1, 'Contents', 6]]
    for i in range(1, 6):
        toc.append([2, f'Parts {parts[2*i]["paper"]}-{parts[2*i+1]["paper"]}', 6+i])
    toc.append([1, 'Rights and sources', 12])
    for part_idx, part in enumerate(parts):
        assert len(book) == part['divider_index']
        book.insert_pdf(dividers, from_page=part_idx, to_page=part_idx, links=False)
        page_records[len(book)-1] = {'paper': part['paper'], 'title': part['title'],
                                     'divider': True, 'component': None}
        toc.append([1, f'{part["paper"]}. {part["title"]}', len(book)])
        for comp in part['components']:
            cid = comp['id']
            path = ROOT / comp['path']
            if digest(path) != comp['sha256']:
                raise ValueError(f'Component bytes changed after specification: {cid}')
            source = documents[cid] = fitz.open(path)
            assert len(source) == comp['pages']
            names[cid] = source.resolve_names()
            for alias in [Path(comp['baseline_path']).name, path.name] + comp.get('aliases', []):
                old = alias_map.setdefault(alias, cid)
                if old != cid:
                    raise ValueError(f'Ambiguous component filename {alias}')
            assert len(book) == comp['index_start'], (cid, len(book), comp['index_start'])
            toc.append([2, comp['title'], len(book)+1])
            original_tocs[cid] = source.get_toc()
            for sp, page in enumerate(source):
                index = len(book)
                folio = index-front_count+1
                preserved = comp['build_kind'] == 'preserved_pdf'
                for first, last in comp.get('preserved_page_spans', []):
                    preserved |= first <= sp+1 <= last
                transform = page_transform(page.rect, folio, preserved)
                output = book.new_page(width=W, height=H)
                target = transformed_rect(page.rect, transform)
                output.show_pdf_page(target, source, sp, keep_proportion=True)
                source_map[(cid, sp)] = index
                source_links[(cid, sp)] = page.get_links()
                transforms[index] = transform
                page_records[index] = {'paper': part['paper'], 'title': comp['title'],
                                       'divider': False, 'component': cid,
                                       'source_page': sp+1, 'source_label': page.get_label(),
                                       'preserved_pdf_page': preserved,
                                       'transform': list(transform)}
            for level, title, pno in original_tocs[cid]:
                if 1 <= pno <= len(source):
                    toc.append([level+2, title, source_map[(cid, pno-1)]+1])
    # Rendering furniture separately preserves the imported vector content.
    furniture_path = BOOK / 'running_furniture.pdf'
    c = canvas.Canvas(str(furniture_path), pagesize=(W, H), pageCompression=1)
    return_links = []
    for index in range(front_count, len(book)):
        rec = page_records[index]
        folio = index-front_count+1
        odd = folio % 2
        dx = 6 if odd else -6
        left, right = LEFT+dx, W-LEFT+dx
        if not rec['divider']:
            c.setFillColor(HexColor(MUTED)); c.setFont('BookSans', 7.2)
            label = rec['title'] if odd else 'Komorebi Core Papers'
            while pdfmetrics.stringWidth(label, 'BookSans', 7.2) > WIDTH-70:
                label = label[:-2]
            if label != (rec['title'] if odd else 'Komorebi Core Papers'):
                label = label.rstrip() + '...'
            if odd:
                c.drawRightString(right, 756, label)
                c.setFillColor(HexColor(MULBERRY)); c.drawString(left, 756, 'PART '+rec['paper'])
            else:
                c.drawString(left, 756, label)
                c.setFillColor(HexColor(MULBERRY)); c.drawRightString(right, 756, 'PART '+rec['paper'])
            c.setStrokeColor(HexColor(RULE)); c.setLineWidth(.35); c.line(left, 746, right, 746)
            c.setFillColor(HexColor(MUTED)); c.setFont('BookSans', 6.5)
            comp = component_by_id[rec['component']]
            local = rec['source_label'] or str(rec['source_page'])
            note = f'{comp["short_role"]} / {local}'
            if rec['preserved_pdf_page']:
                note += ' / preserved edition'
            c.drawCentredString(W/2, 28, note)
            partno = next(j for j, x in enumerate(parts) if x['paper'] == rec['paper'])
            return_links.append({'page': index, 'rect': [left, 23, right, 50],
                                 'target': 5+partno//2})
        c.setFillColor(HexColor(INK)); c.setFont('BookSerif', 10.5)
        if odd: c.drawRightString(right, 27, str(folio))
        else: c.drawString(left, 27, str(folio))
        c.showPage()
    c.save()
    overlay = fitz.open(furniture_path)
    for index in range(front_count, len(book)):
        book[index].show_pdf_page(book[index].rect, overlay, index-front_count, overlay=True)

    # All source internal and adjacent-PDF links are rebuilt against the complete map.
    counters = collections.Counter(); unresolved = []; resolved = []
    embedded_routes = []
    def add_target(src_index, box, cid, target_page, point, original):
        if (cid, target_page) not in source_map:
            unresolved.append({'book_page': src_index+1, 'reason': 'target page absent',
                               'target_component': cid, 'target_page': target_page+1, 'original': str(original)})
            return
        target = source_map[(cid, target_page)]
        to = transformed_point(point, transforms[target])
        # A source page-origin target can move six points outside the page
        # after the mirrored gutter translation. Keep navigation on the page.
        to = fitz.Point(max(0, min(W, to.x)), max(0, min(H, to.y)))
        book[src_index].insert_link({'kind': fitz.LINK_GOTO, 'from': box, 'page': target, 'to': to})
        resolved.append({'book_page': src_index+1, 'target_book_page': target+1,
                         'source_kind': original['kind'], 'target_component': cid,
                         'target_component_page': target_page+1})
        counters['source_links_internalized'] += 1

    def remote_target(raw):
        raw = unquote(raw or '').replace('\\', '/')
        filename, _, fragment = raw.partition('#')
        alias = Path(filename).name
        return alias_map.get(alias), parse_qs(fragment)

    def add_frozen_target(src_index, box, target_cid, target_page, original):
        comp = component_by_id[target_cid]
        if not 0 <= target_page < comp['baseline_pages']:
            unresolved.append({'book_page': src_index+1, 'reason': 'frozen target page absent',
                               'target_component': target_cid, 'target_page': target_page+1})
            return
        filename = Path(comp['baseline_path']).name
        marker = 'urn:komorebi:embedded:' + str(len(embedded_routes))
        page = book[src_index]
        page.insert_link({'kind': fitz.LINK_URI, 'from': box, 'uri': marker})
        page = book.reload_page(page)
        created = [x for x in page.get_links() if x.get('uri') == marker]
        if len(created) != 1: raise ValueError('Could not identify embedded PDF annotation')
        # PDF GoToE: child embedded-file target by its EmbeddedFiles name-tree name.
        action = ('<< /S /GoToE /D [' + str(target_page) + ' /Fit] /NewWindow true '
                  '/T << /R /C /N ' + fitz.get_pdf_str(filename) + ' >> >>')
        book.xref_set_key(created[0]['xref'], 'A', action)
        embedded_routes.append({'book_page': src_index+1, 'attachment': filename,
                                'target_page': target_page+1, 'source_kind': original['kind'],
                                'annotation_xref_before_save': created[0]['xref']})
        counters['frozen_edition_embedded_links'] += 1

    for (cid, sp), links in source_links.items():
        src_index = source_map[(cid, sp)]
        for link in links:
            kind = link['kind']; counters['source_links_total'] += 1
            box = transformed_rect(link['from'], transforms[src_index])
            if kind in (fitz.LINK_GOTO, fitz.LINK_NAMED) and link.get('page', -1) >= 0:
                point = link.get('to', (0, 0))
                target_page = link['page']
                if kind == fitz.LINK_NAMED:
                    dest = names[cid].get(link.get('nameddest', ''))
                    if dest and dest.get('page', -1) >= 0:
                        target_page = dest['page']
                        xy = dest.get('to', (0, documents[cid][target_page].rect.height))
                        point = (xy[0], documents[cid][target_page].rect.height-xy[1])
                    else:
                        point = (point[0], documents[cid][target_page].rect.height-point[1])
                add_target(src_index, box, cid, target_page, point, link)
                continue
            raw = link.get('file', '')
            if kind == fitz.LINK_URI:
                raw = link.get('uri', '')
                if urlsplit(raw).scheme in ('https', 'http', 'mailto'):
                    book[src_index].insert_link({'kind': fitz.LINK_URI, 'from': box, 'uri': raw})
                    counters['external_uri_links'] += 1
                    continue
            target_cid, fragment = remote_target(raw)
            if target_cid:
                destname = (fragment.get('nameddest') or [None])[0]
                to = (0, 0); target_page = link.get('page', -1)
                numeric = not destname and not isinstance(link.get('to'), str)
                if 'page' in fragment: target_page = int(fragment['page'][0])-1
                if numeric and target_page >= 0 and component_by_id[cid]['numeric_remotes_edition'] == 'frozen':
                    add_frozen_target(src_index, box, target_cid, target_page, link)
                    continue
                if destname:
                    dest = names[target_cid].get(destname)
                    if dest and dest.get('page', -1) >= 0:
                        target_page = dest['page']
                        xy = dest.get('to', (0, documents[target_cid][target_page].rect.height))
                        to = (xy[0], documents[target_cid][target_page].rect.height-xy[1])
                    else:
                        unresolved.append({'book_page': src_index+1, 'reason': 'named destination absent',
                                           'target_component': target_cid, 'name': destname})
                        continue
                elif 'page' in fragment:
                    target_page = int(fragment['page'][0])-1
                elif isinstance(link.get('to'), str):
                    dest = names[target_cid].get(link['to'])
                    if dest:
                        target_page = dest['page']
                        xy = dest.get('to', (0, documents[target_cid][target_page].rect.height))
                        to = (xy[0], documents[target_cid][target_page].rect.height-xy[1])
                if target_page >= 0:
                    add_target(src_index, box, target_cid, target_page, to, link)
                    continue
            if kind == fitz.LINK_NONE:
                counters['empty_source_links'] += 1
                continue
            unresolved.append({'book_page': src_index+1, 'reason': 'unresolved source link',
                               'component': cid, 'source_page': sp+1, 'original': str(link)})
    for link in json.loads((BOOK / 'outer_links.json').read_text()) + return_links:
        book[link['page']].insert_link({'kind': fitz.LINK_GOTO, 'from': fitz.Rect(link['rect']),
                                      'page': link['target'], 'to': fitz.Point(0, 0)})
        counters['editorial_navigation_links'] += 1
    book.set_toc(toc, collapse=2)
    book.set_page_labels([{'startpage': 0, 'prefix': 'Cover', 'style': '', 'firstpagenum': 1},
                         {'startpage': 1, 'prefix': '', 'style': 'r', 'firstpagenum': 1},
                         {'startpage': front_count, 'prefix': '', 'style': 'D', 'firstpagenum': 1}])
    book.set_metadata({'title': 'Komorebi Core Papers: Projectors, Transfer and Arithmetic',
                       'author': 'Komorebi P.', 'subject': 'Collected core papers I-XII',
                       'keywords': 'Komorebi, realization calculus, projectors, packets, transfer, arithmetic',
                       'creator': 'Komorebi core monograph publication source',
                       'producer': 'Source-built components and vector PDF assembly'})
    book.xref_set_key(book.pdf_catalog(), 'Lang', '(en-US)')
    book.xref_set_key(book.pdf_catalog(), 'PageMode', '/UseOutlines')
    book.xref_set_key(book.pdf_catalog(), 'ViewerPreferences', '<< /DisplayDocTitle true >>')
    target = OUT / 'Komorebi_Core_Papers.pdf'
    book.save(target, garbage=2, deflate=True)
    record = {'pages': len(book), 'front_pages': front_count, 'parts': len(parts),
              'components': len(components), 'bookmarks': len(toc), 'links': dict(counters),
              'unresolved_source_links': unresolved, 'sha256': digest(target),
              'embedded_frozen_editions': book.embfile_count(),
              'font_files': font_record, 'boundary': 'Publication assembly, not mathematical verification.'}
    dump(BOOK/'assembly_validation.json', record)
    dump(BOOK/'page_map.json', {'pages': page_records})
    dump(BOOK/'resolved_link_map.json', resolved)
    dump(BOOK/'embedded_reference_links.json', embedded_routes)
    print(json.dumps(record, indent=2))
    if unresolved:
        raise SystemExit('Source links require resolution before delivery.')


if __name__ == '__main__':
    main()
