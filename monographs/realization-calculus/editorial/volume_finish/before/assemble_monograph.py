#!/usr/bin/env python3
"""Assemble selected scientific pages, editorial leaves and a linked glossary.

All source pages remain addressable through explicit selected-page maps or
redirects. This publication tooling does not execute mathematical or Lean checks.
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


def serial(value):
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, fitz.Rect, fitz.Point)):
        return [serial(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


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


def page_transform(rect, folio, preserved=False, display_normalized=False):
    if preserved and not display_normalized:
        frame = fitz.Rect(24, 55, 588, 741)
        scale = min(frame.width / rect.width, frame.height / rect.height)
        tx = frame.x0 + (frame.width - rect.width * scale) / 2
        ty = frame.y0 + (frame.height - rect.height * scale) / 2
    else:
        if abs(rect.width - W) > .1 or abs(rect.height - H) > .1:
            raise ValueError(f'Full-size component is not letter size: {rect}')
        scale, tx, ty = 1.0, (6.0 if folio % 2 else -6.0), 0.0
    return scale, tx, ty


class TargetResolver:
    """Resolve a raw zero-based source page without inventing a destination."""
    def __init__(self, components, leaves):
        self.components = components
        self.leaves = leaves

    def resolve(self, cid, source_page):
        chain, seen = [], set()
        while True:
            key = (cid, int(source_page))
            if key in seen:
                raise ValueError(f'Redirect cycle: {chain + [list(key)]}')
            seen.add(key)
            if cid not in self.components:
                raise ValueError(f'Unknown target component: {cid}')
            comp = self.components[cid]
            if not 0 <= source_page < comp['pages']:
                raise ValueError(f'Target source page out of range: {cid}:{source_page}')
            chain.append({'component_id': cid, 'source_page': source_page})
            selected = comp.get('book_pages', {})
            if str(source_page) in selected:
                return {'book_index': int(selected[str(source_page)]),
                        'component_id': cid, 'source_page': source_page,
                        'redirected': len(chain) > 1, 'chain': chain}
            redirect = comp.get('redirects', {}).get(str(source_page))
            if redirect is None:
                raise ValueError(f'No explicit route for omitted page: {cid}:{source_page}')
            if 'leaf_id' in redirect:
                lid = redirect['leaf_id']
                if lid not in self.leaves:
                    raise ValueError(f'Unknown redirect leaf: {lid}')
                chain.append({'leaf_id': lid})
                return {'book_index': int(self.leaves[lid]['book_index']),
                        'leaf_id': lid, 'redirected': True, 'chain': chain}
            if 'component_id' not in redirect or 'source_page' not in redirect:
                raise ValueError(f'Invalid redirect: {redirect}')
            cid, source_page = redirect['component_id'], int(redirect['source_page'])


def named_destination(doc, names, name):
    """resolve_names() returns PDF bottom-origin destination coordinates."""
    dest = names.get(name)
    if not dest or not 0 <= dest.get('page', -1) < len(doc):
        raise ValueError(f'Named destination absent: {name}')
    page = dest['page']
    point = dest.get('to', (0, doc[page].rect.height))
    return page, (point[0], doc[page].rect.height - point[1])


def make_toc(spec, documents, original_tocs, override_records=None):
    components = {c['id']: c for p in spec['parts'] for c in p['components']}
    leaves = {l['id']: l for l in spec['leaves']}
    units = {u['leaf_id']: u for u in spec['reading_units']}
    toc = [[1, 'Title', 2], [1, 'Introduction', 3], [1, 'Reading map', 4],
           [1, 'Notation and references', 5], [1, 'Contents', 6],
           [2, 'Chapters VII–XII', 7], [2, 'Further studies and reference', 8],
           [2, 'Formal companions', 9], [1, 'Rights and sources', 10]]
    omitted = []
    if override_records is None:override_records=[]
    for entry in spec['sequence']:
        if entry['kind'] != 'leaf':
            continue
        leaf = leaves[entry['id']]
        kind = leaf['kind']
        paper = leaf.get('paper', '')
        base = 2 if kind in ('formal_companion', 'study') else 1
        prefix = ('Chapter ' + paper + '. ') if kind == 'chapter' else ''
        title = prefix + leaf['title']
        if kind == 'formal_companion' and not title.lower().startswith('formal'):
            title = 'Formal companion ' + paper + '. ' + title
        toc.append([base, title, leaf['book_index'] + 1])
        unit = units.get(leaf['id'])
        if not unit:
            continue
        selected_comps = [components[cid] for cid in unit['component_ids']
                          if components[cid].get('keep_pages')]
        selected_comps.sort(key=lambda c: min(c['book_pages'].values()))
        for comp in selected_comps:
            cid = comp['id']
            start = min(comp['book_pages'].values())
            role = comp.get('role', '')
            label = comp.get('book_title', comp.get('title', cid))
            if role == 'visual':
                label = 'Visual studies'
            toc.append([base + 1, label, start + 1])
            last_level = base + 1
            overrides=comp.get('bookmark_overrides',{})
            used_overrides=set()
            for source_level, source_title, pno in original_tocs[cid]:
                raw = pno - 1
                if source_title in overrides:
                    replacement=overrides[source_title]
                    raw=int(replacement['source_page'] if isinstance(replacement,dict) else replacement)
                    if str(raw) not in comp['book_pages']:
                        raise ValueError(f'Bookmark override must target a selected source page: {cid}:{source_title}')
                    used_overrides.add(source_title)
                    override_records.append({'component_id':cid,'title':source_title,'original_source_index':pno-1,
                        'override_source_index':raw,'book_index':comp['book_pages'][str(raw)],
                        'book_page':comp['book_pages'][str(raw)]+1})
                if str(raw) not in comp['book_pages']:
                    omitted.append({'component_id': cid, 'source_page': raw,
                                    'title': source_title, 'reason': 'source page omitted'})
                    continue
                if re.fullmatch(r'\s*(?:table of )?contents\s*', source_title, re.I):
                    omitted.append({'component_id': cid, 'source_page': raw,
                                    'title': source_title, 'reason': 'local contents bookmark'})
                    continue
                level = min(base + 1 + max(1, source_level), last_level + 1)
                toc.append([level, source_title, comp['book_pages'][str(raw)] + 1])
                last_level = level
            if used_overrides!=set(overrides):
                raise ValueError(f'Bookmark overrides do not match source titles: {cid}: {set(overrides)-used_overrides}')
    return toc, omitted


def main():
    BOOK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    spec = json.loads((BOOK / 'build_spec.json').read_text())
    front_count, parts = spec['front_pages'], spec['parts']
    components = [c for p in parts for c in p['components']]
    component_by_id = {c['id']: c for c in components}
    leaves = {l['id']: l for l in spec['leaves']}
    units = {u['id']: u for u in spec['reading_units']}
    leaf_units = {u['leaf_id']: u for u in spec['reading_units']}
    if front_count != 10 or len(parts) != 12 or len(component_by_id) != len(components):
        raise ValueError('Expected ten prelims, twelve chapters and unique component IDs.')
    if len(leaves) != len(spec['leaves']):
        raise ValueError('Duplicate editorial leaf IDs')
    subprocess.run([sys.executable, str(ROOT / 'render_outer.py')], cwd=ROOT, check=True)
    font_record = register_fonts()
    book = fitz.open()
    front, leaf_pdf = fitz.open(BOOK / 'frontmatter.pdf'), fitz.open(BOOK / 'leaves.pdf')
    leaf_pdf_pages = {l['id']: i for i, l in enumerate(spec['leaves'])}
    if len(front) != front_count or len(leaf_pdf) != len(leaves):
        raise ValueError('Editorial PDF page counts do not match the specification')
    book.insert_pdf(front, links=False)
    documents, names, alias_map, original_tocs = {}, {}, {}, {}
    source_map, source_links, page_records, transforms = {}, {}, {}, {}
    attachment_names = set()
    # Preload all components, including records retained only as original attachments.
    for comp in components:
        cid = comp['id']; path = ROOT / comp['path']; baseline = ROOT / comp['baseline_path']
        if digest(path) != comp['sha256']:
            raise ValueError(f'Component bytes changed after specification: {cid}')
        if digest(baseline) != comp['baseline_sha256']:
            raise ValueError(f'Original source bytes changed: {baseline.name}')
        doc = documents[cid] = fitz.open(path)
        if len(doc) != comp['pages']:
            raise ValueError(f'Raw page count mismatch: {cid}')
        selected = comp.get('keep_pages', [])
        if len(selected) != len(set(selected)) or any(not 0 <= p < len(doc) for p in selected):
            raise ValueError(f'Invalid selected pages: {cid}')
        if set(map(int, comp.get('book_pages', {}))) != set(selected):
            raise ValueError(f'Selected pages and book_pages disagree: {cid}')
        names[cid] = doc.resolve_names(); original_tocs[cid] = doc.get_toc()
        for alias in [baseline.name, path.name] + comp.get('aliases', []):
            alias = Path(unquote(alias).replace('\\', '/')).name
            old = alias_map.setdefault(alias, cid)
            if old != cid:
                raise ValueError(f'Ambiguous component filename {alias}')
        if baseline.name in attachment_names:
            raise ValueError(f'Duplicate original attachment name: {baseline.name}')
        attachment_names.add(baseline.name)
        book.embfile_add(baseline.name, baseline.read_bytes(), filename=baseline.name,
                         ufilename=baseline.name,
                         desc=f'Original reference PDF, Paper {comp["paper"]}: {comp["title"]}')
    resolver = TargetResolver(component_by_id, leaves)
    # Validate every explicitly supplied redirect, even if it receives no live link.
    for comp in components:
        for sp in comp.get('redirects', {}):
            resolver.resolve(comp['id'], int(sp))
    glossary_path = ROOT / spec['glossary']['path']
    glossary = fitz.open(glossary_path)
    if len(glossary) != spec['glossary']['pages']:
        raise ValueError('Glossary page count mismatch')
    seen_leaves, seen_source, glossary_seen = set(), set(), False
    for entry in spec['sequence']:
        if len(book) != entry['book_index']:
            raise ValueError(f'Sequence position mismatch: {entry}, actual {len(book)}')
        kind = entry['kind']
        if kind == 'leaf':
            lid = entry['id']; leaf = leaves[lid]
            if lid in seen_leaves or leaf['book_index'] != len(book):
                raise ValueError(f'Invalid leaf sequence position: {lid}')
            seen_leaves.add(lid); unit = leaf_units.get(lid)
            book.insert_pdf(leaf_pdf, from_page=leaf_pdf_pages[lid], to_page=leaf_pdf_pages[lid], links=False)
            page_records[len(book)-1] = {'kind': 'leaf', 'leaf_id': lid, 'leaf_kind': leaf['kind'],
                'paper': leaf.get('paper'), 'title': leaf['title'], 'divider': True,
                'component': None, 'unit_id': unit['id'] if unit else None}
        elif kind == 'component':
            cid = entry['component_id']; comp = component_by_id[cid]; source = documents[cid]
            unit = units[comp['unit_id']]
            for sp in entry.get('source_pages', comp['keep_pages']):
                if sp not in comp['keep_pages'] or (cid, sp) in seen_source:
                    raise ValueError(f'Duplicate or unselected page in sequence: {cid}:{sp}')
                if comp['book_pages'][str(sp)] != len(book):
                    raise ValueError(f'Authoritative page map mismatch: {cid}:{sp}')
                seen_source.add((cid, sp)); page = source[sp]; index = len(book)
                folio = index-front_count+1
                preserved = comp['build_kind'] == 'preserved_pdf'
                for first, last in comp.get('preserved_page_spans', []):
                    preserved |= first <= sp+1 <= last
                normalized = bool(comp.get('display_normalized', False))
                transform = page_transform(page.rect, folio, preserved, normalized)
                output = book.new_page(width=W, height=H)
                output.show_pdf_page(transformed_rect(page.rect, transform), source, sp, keep_proportion=True)
                source_map[(cid, sp)] = index; source_links[(cid, sp)] = page.get_links()
                transforms[index] = transform
                page_records[index] = {'kind': 'component', 'paper': comp['paper'],
                    'title': comp['title'], 'unit_title': unit['title'], 'unit_kind': unit['kind'],
                    'unit_id': unit['id'], 'divider': False, 'component': cid,
                    'source_page': sp+1, 'source_index': sp, 'source_label': page.get_label(),
                    'preserved_pdf_page': preserved, 'display_normalized': normalized,
                    'transform': list(transform)}
        elif kind == 'glossary':
            if glossary_seen or entry['book_index'] != spec['glossary']['index_start']:
                raise ValueError('Duplicate or misplaced glossary')
            glossary_seen = True
            if entry['pages'] != len(glossary):
                raise ValueError('Glossary sequence count mismatch')
            for sp, page in enumerate(glossary):
                index = len(book); transform = page_transform(page.rect, index-front_count+1)
                output = book.new_page(width=W, height=H)
                output.show_pdf_page(transformed_rect(page.rect, transform), glossary, sp, keep_proportion=True)
                transforms[index] = transform
                page_records[index] = {'kind': 'glossary', 'paper': None, 'title': 'Glossary',
                    'divider': False, 'component': None, 'source_page': sp+1,
                    'source_index': sp, 'source_label': page.get_label(), 'transform': list(transform)}
        else:
            raise ValueError(f'Unknown sequence entry kind: {kind}')
    expected_source = {(c['id'], sp) for c in components for sp in c['keep_pages']}
    if seen_source != expected_source or seen_leaves != set(leaves) or not glossary_seen:
        raise ValueError('Sequence omitted selected scientific or editorial pages')
    if set(page_records) != set(range(front_count, len(book))):
        raise ValueError('Page map does not cover the whole body')
    for comp in components:
        if comp['keep_pages'] and comp['index_start'] != min(comp['book_pages'].values()):
            raise ValueError(f'Component start mismatch: {comp["id"]}')
    bookmark_overrides=[]
    toc, omitted_bookmarks = make_toc(spec, documents, original_tocs, bookmark_overrides)

    # Source interiors and normalized retained pages leave these margins clear.
    furniture_path = BOOK / 'running_furniture.pdf'
    c = canvas.Canvas(str(furniture_path), pagesize=(W, H), pageCompression=1)
    return_links = []
    for index in range(front_count, len(book)):
        rec = page_records[index]; folio = index-front_count+1; odd = folio % 2
        dx = 6 if odd else -6; left, right = LEFT+dx, W-LEFT+dx
        if not rec['divider']:
            if rec['kind'] == 'glossary':
                tag, heading, contents_page = 'GLOSSARY', 'Glossary', 7
            else:
                unit = units[rec['unit_id']]
                leaf_kind = leaves[unit['leaf_id']]['kind']
                tag = ('FORMAL / ' + rec['paper']) if leaf_kind == 'formal_companion' else (
                    'FURTHER STUDIES' if leaf_kind == 'study' else 'CHAPTER ' + rec['paper'])
                heading, contents_page = unit['title'], unit['contents_page']
            c.setFillColor(HexColor(MUTED)); c.setFont('BookSans', 7.2)
            label = heading if odd else 'Realization Calculus'
            available = WIDTH - pdfmetrics.stringWidth(tag, 'BookSans', 7.2) - 24
            original_label = label
            while pdfmetrics.stringWidth(label, 'BookSans', 7.2) > available:
                label = label[:-2]
            if label != original_label:
                label = label.rstrip() + '...'
            if odd:
                c.drawRightString(right, 756, label)
                c.setFillColor(HexColor(MULBERRY)); c.drawString(left, 756, tag)
            else:
                c.drawString(left, 756, label)
                c.setFillColor(HexColor(MULBERRY)); c.drawRightString(right, 756, tag)
            c.setStrokeColor(HexColor(RULE)); c.setLineWidth(.35); c.line(left, 746, right, 746)
            return_links.append({'page': index, 'rect': [left, 23, right, 50],
                                 'target': contents_page, 'kind': 'running_header_return'})
        c.setFillColor(HexColor(INK)); c.setFont('BookSerif', 10.5)
        if odd: c.drawRightString(right, 27, str(folio))
        else: c.drawString(left, 27, str(folio))
        c.showPage()
    c.save(); overlay = fitz.open(furniture_path)
    for index in range(front_count, len(book)):
        book[index].show_pdf_page(book[index].rect, overlay, index-front_count, overlay=True)

    counters = collections.Counter(); unresolved = []; resolved = []; embedded_routes = []
    def add_target(src_index, box, cid, target_page, point, original, source_kind='source'):
        try:
            route = resolver.resolve(cid, target_page)
            target = route['book_index']
            if not front_count <= target < len(book):
                raise ValueError(f'Resolved target outside book: {route}')
            if route['redirected']:
                to = fitz.Point(0, 0)
            else:
                to = transformed_point(point, transforms[target])
            to = fitz.Point(max(0, min(W, to.x)), max(0, min(H, to.y)))
            book[src_index].insert_link({'kind': fitz.LINK_GOTO, 'from': box, 'page': target, 'to': to})
            resolved.append({'kind': source_kind, 'book_page': src_index+1,
                'source_book_index': src_index, 'rect': list(box), 'original': serial(original),
                'target_book_page': target+1, 'target_book_index': target, 'target_point': list(to),
                'target_component': route.get('component_id'),
                'target_component_page': route.get('source_page', -1)+1 if 'component_id' in route else None,
                'resolution': route})
            counters['glossary_reference_links' if source_kind == 'glossary_reference' else 'source_links_internalized'] += 1
        except (ValueError, KeyError, IndexError) as exc:
            unresolved.append({'book_page': src_index+1, 'reason': str(exc), 'target_component': cid,
                               'target_page': target_page+1, 'original': serial(original)})

    def remote_target(raw):
        raw = unquote(raw or '').replace('\\', '/')
        filename, _, fragment = raw.partition('#')
        return alias_map.get(Path(filename).name), parse_qs(fragment)

    def add_frozen_target(src_index, box, target_cid, target_page, original):
        comp = component_by_id[target_cid]
        if not 0 <= target_page < comp['baseline_pages']:
            unresolved.append({'book_page': src_index+1, 'reason': 'original target page absent',
                               'target_component': target_cid, 'target_page': target_page+1})
            return
        filename = Path(comp['baseline_path']).name
        marker = 'urn:komorebi:embedded:' + str(len(embedded_routes))
        page = book[src_index]; page.insert_link({'kind': fitz.LINK_URI, 'from': box, 'uri': marker})
        page = book.reload_page(page)
        created = [x for x in page.get_links() if x.get('uri') == marker]
        if len(created) != 1:
            raise ValueError('Could not identify embedded PDF annotation')
        action = ('<< /S /GoToE /D [' + str(target_page) + ' /Fit] /NewWindow true '
                  '/T << /R /C /N ' + fitz.get_pdf_str(filename) + ' >> >>')
        book.xref_set_key(created[0]['xref'], 'A', action)
        route = {'kind': 'original_pdf_reference', 'book_page': src_index+1,
                 'source_book_index': src_index, 'rect': list(box), 'attachment': filename,
                 'target_page': target_page+1, 'target_component': target_cid,
                 'original': serial(original), 'annotation_xref_before_save': created[0]['xref']}
        embedded_routes.append(route); resolved.append(route)
        counters['frozen_edition_embedded_links'] += 1

    for (cid, sp), links in source_links.items():
        src_index = source_map[(cid, sp)]
        for link in links:
            kind = link['kind']; counters['source_links_total'] += 1
            original = {**serial(link), 'component_id': cid, 'source_page': sp}
            box = transformed_rect(link['from'], transforms[src_index])
            try:
                if kind in (fitz.LINK_GOTO, fitz.LINK_NAMED) and link.get('page', -1) >= 0:
                    target_page, point = link['page'], link.get('to', (0, 0))
                    if kind == fitz.LINK_NAMED:
                        name = link.get('nameddest', '')
                        if name:
                            target_page, point = named_destination(documents[cid], names[cid], name)
                        else:
                            point = (point[0], documents[cid][target_page].rect.height-point[1])
                    add_target(src_index, box, cid, target_page, point, original)
                    continue
                if kind == fitz.LINK_NAMED and link.get('nameddest'):
                    target_page, point = named_destination(documents[cid], names[cid], link['nameddest'])
                    add_target(src_index, box, cid, target_page, point, original)
                    continue
                raw = link.get('file', '')
                if kind == fitz.LINK_URI:
                    raw = link.get('uri', '')
                    if urlsplit(raw).scheme.lower() in ('https', 'http', 'mailto'):
                        book[src_index].insert_link({'kind': fitz.LINK_URI, 'from': box, 'uri': raw})
                        resolved.append({'kind': 'external_uri', 'book_page': src_index+1,
                            'source_book_index': src_index, 'rect': list(box), 'uri': raw, 'original': original})
                        counters['external_uri_links'] += 1
                        continue
                target_cid, fragment = remote_target(raw)
                if target_cid:
                    destname = (fragment.get('nameddest') or [None])[0]
                    point = (0, 0); target_page = link.get('page', -1)
                    numeric = not destname and not isinstance(link.get('to'), str)
                    if 'page' in fragment:
                        target_page = int(fragment['page'][0])-1
                    if numeric and target_page >= 0 and component_by_id[cid]['numeric_remotes_edition'] == 'frozen':
                        add_frozen_target(src_index, box, target_cid, target_page, original)
                        continue
                    if destname or isinstance(link.get('to'), str):
                        target_page, point = named_destination(documents[target_cid], names[target_cid], destname or link['to'])
                    if target_page >= 0:
                        add_target(src_index, box, target_cid, target_page, point, original)
                        continue
                if kind == fitz.LINK_NONE:
                    counters['empty_source_links'] += 1
                    resolved.append({'kind': 'empty_source_link', 'book_page': src_index+1, 'original': original})
                    continue
                raise ValueError('Unresolved source link')
            except (ValueError, KeyError, IndexError) as exc:
                unresolved.append({'book_page': src_index+1, 'reason': str(exc),
                                   'component': cid, 'source_page': sp+1, 'original': original})

    def editorial_link(link, source_kind):
        source, target = int(link['page']), int(link['target'])
        if not 0 <= source < len(book) or not 0 <= target < len(book):
            raise ValueError(f'Editorial navigation outside book: {link}')
        box = fitz.Rect(link['rect']); point = fitz.Point(link.get('point', (0, 0)))
        book[source].insert_link({'kind': fitz.LINK_GOTO, 'from': box, 'page': target, 'to': point})
        resolved.append({'kind': source_kind, 'book_page': source+1, 'source_book_index': source,
                         'rect': list(box), 'target_book_page': target+1,
                         'target_book_index': target, 'target_point': list(point), 'original': link})
        counters[source_kind] += 1

    for link in json.loads((BOOK / 'outer_links.json').read_text()) + return_links:
        editorial_link(link, 'editorial_navigation_links')
    glossary_start = spec['glossary']['index_start']
    for link in json.loads((BOOK / 'glossary_links.json').read_text()):
        src = glossary_start + link['page']; box = transformed_rect(link['rect'], transforms[src])
        if link['kind'] == 'glossary_reference':
            add_target(src, box, link['component_id'], int(link['local_page'])-1, (0, 0), link, 'glossary_reference')
        elif link['kind'] == 'glossary_see_also':
            target = glossary_start + link['target_glossary_page']
            point = transformed_point(link['target_point'], transforms[target])
            point = fitz.Point(max(0, min(W, point.x)), max(0, min(H, point.y)))
            editorial_link({'page': src, 'rect': list(box), 'target': target, 'point': list(point),
                            'original': link}, 'glossary_related_links')
        else:
            raise ValueError(f'Unknown glossary link kind: {link["kind"]}')
    book.set_toc(toc, collapse=2)
    book.set_page_labels([{'startpage': 0, 'prefix': 'Cover', 'style': '', 'firstpagenum': 1},
                         {'startpage': 1, 'prefix': '', 'style': 'r', 'firstpagenum': 1},
                         {'startpage': front_count, 'prefix': '', 'style': 'D', 'firstpagenum': 1}])
    book.set_metadata({'title': 'Realization Calculus: Projectors, Transfer and Arithmetic',
                       'author': 'Komorebi P.', 'subject': 'Chapters I–XII with formal companions and glossary',
                       'keywords': 'Komorebi, realization calculus, projectors, packets, transfer, arithmetic',
                       'creator': 'Realization Calculus publication source',
                       'producer': 'Source-built components and vector PDF assembly'})
    book.xref_set_key(book.pdf_catalog(), 'Lang', '(en-US)')
    book.xref_set_key(book.pdf_catalog(), 'PageMode', '/UseOutlines')
    book.xref_set_key(book.pdf_catalog(), 'ViewerPreferences', '<< /DisplayDocTitle true >>')
    target = OUT / 'Realization_Calculus.pdf'
    book.save(target, garbage=2, deflate=True)
    record = {'pages': len(book), 'front_pages': front_count, 'parts': len(parts),
              'components': len(components), 'selected_source_pages': len(seen_source),
              'raw_source_pages': sum(c['pages'] for c in components),
              'editorial_leaves': len(leaves), 'glossary_pages': len(glossary),
              'reading_units': len(units), 'bookmarks': len(toc), 'links': dict(counters),
              'unresolved_source_links': unresolved, 'sha256': digest(target),
              'embedded_frozen_editions': book.embfile_count(),
              'font_files': font_record, 'boundary': 'Publication assembly, not mathematical verification.'}
    dump(BOOK/'assembly_validation.json', record)
    dump(BOOK/'page_map.json', {'pages': page_records})
    dump(BOOK/'resolved_link_map.json', resolved)
    dump(BOOK/'embedded_reference_links.json', embedded_routes)
    dump(BOOK/'omitted_bookmarks.json', omitted_bookmarks)
    dump(BOOK/'bookmark_target_overrides.json', bookmark_overrides)
    print(json.dumps(record, indent=2))
    if unresolved:
        raise SystemExit('Source links require resolution before delivery.')


if __name__ == '__main__':
    main()
