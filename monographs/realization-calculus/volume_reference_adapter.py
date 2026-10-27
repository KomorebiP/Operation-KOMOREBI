#!/usr/bin/env python3
"""Separate mixed bibliography pages in a displayed component, in memory.

Original source PDFs are not edited. Reference glyphs retain their fonts and
relative positions. Explicit routes let the book assembler send a destination
inside an original bibliography region to its appended display page.
"""
import copy
import hashlib
import json
import re

import fitz


def _belongs(rect, region):
    rect = fitz.Rect(rect)
    # A zero-width ligature continuation still has a position on the page.
    probe = fitz.Rect(rect)
    if probe.width == 0:
        probe.x1 += .00001
    if probe.height == 0:
        probe.y1 += .00001
    if not probe.intersects(region):
        return False
    if not (region + (-.001, -.001, .001, .001)).contains(probe):
        raise ValueError('Reference split crosses visible content: ' + str(rect))
    return True


def _glyphs(page, region=None, inside=True, offset=0):
    rows = []
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                for char in span['chars']:
                    if region is not None and _belongs(char['bbox'], region) != inside:
                        continue
                    box = list(char['bbox'])
                    origin = list(char['origin'])
                    box[1] += offset
                    box[3] += offset
                    origin[1] += offset
                    rows.append((char['c'], span['font'], round(span['size'], 4),
                                 span.get('flags'),
                                 tuple(box), tuple(origin)))
    return sorted(rows, key=repr)


def _compare_glyphs(expected, actual, label):
    if len(expected) != len(actual):
        raise ValueError('Glyph count changed: ' + label)
    maximum = 0
    for before, after in zip(expected, actual):
        if before[:4] != after[:4]:
            raise ValueError('Glyph or font changed: ' + label)
        delta = max(abs(a - b) for a, b in
                    zip(before[4] + before[5], after[4] + after[5]))
        maximum = max(maximum, delta)
        # MuPDF reserializes PDF decimal operands and uses float32 glyph
        # geometry. This bound permits that harmless numerical roundoff only.
        if delta > .0002:
            raise ValueError('Glyph geometry changed: ' + label + ': ' + str(delta))
    return maximum


def _serial(value, offset=0, key=None):
    if isinstance(value, fitz.Point):
        return [round(value.x, 3), round(value.y + offset, 3)]
    if isinstance(value, fitz.Rect):
        return [round(value.x0, 3), round(value.y0 + offset, 3),
                round(value.x1, 3), round(value.y1 + offset, 3)]
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, dict):
        return {k: _serial(v, offset, k) for k, v in value.items()
                if k not in ('xref', 'number', 'seqno', 'layer')}
    if isinstance(value, (tuple, list)):
        return [_serial(v, offset) for v in value]
    if isinstance(value, float):
        return round(value, 3)
    return value


def _images(page, region=None, inside=True):
    rows = []
    for image in page.get_image_info(hashes=True):
        if region is None or _belongs(image['bbox'], region) == inside:
            rows.append(_serial(image))
    return sorted(rows, key=repr)


def _drawings(page, region=None, inside=True, offset=0):
    rows = []
    for drawing in page.get_drawings():
        if region is None or _belongs(drawing['rect'], region) == inside:
            rows.append(_serial(drawing, offset))
    return sorted(rows, key=repr)


def _links(page):
    doc = page.parent
    return [{'link': copy.deepcopy(link),
             'object': doc.xref_object(link['xref'], compressed=False)}
            for link in page.get_links()]


def _annotation_refs(doc, page):
    kind, value = doc.xref_get_key(page.xref, 'Annots')
    if kind == 'null':
        return []
    if kind == 'xref':
        value = doc.xref_object(int(value.split()[0]), compressed=False)
    refs = re.findall(r'(\d+)\s+\d+\s+R', value)
    remaining = re.sub(r'\d+\s+\d+\s+R', '', value)
    if remaining.strip().strip('[]').strip():
        raise ValueError('Inline annotation requires a reviewed PDF adapter')
    return [int(ref) for ref in refs]


def _restore_links(doc, page, records, offset=0):
    """Copy raw link actions so named destinations keep their exact semantics."""
    current = {link['xref'] for link in page.get_links()}
    refs = [ref for ref in _annotation_refs(doc, page) if ref not in current]
    for record in records:
        link = record['link']
        rect = fitz.Rect(link['from']) + (0, offset, 0, offset)
        raw_rect = rect * ~page.transformation_matrix
        xref = doc.get_new_xref()
        doc.update_object(xref, record['object'])
        doc.xref_set_key(xref, 'P', f'{page.xref} 0 R')
        doc.xref_set_key(xref, 'Rect',
                         '[' + ' '.join(f'{v:.8f}' for v in raw_rect) + ']')
        refs.append(xref)
    doc.xref_set_key(page.xref, 'Annots',
                     '[' + ' '.join(f'{ref} 0 R' for ref in refs) + ']')
    return doc.reload_page(page)


def _link_signature(links, offset=0):
    rows = []
    for item in links:
        link = copy.deepcopy(item['link'] if 'link' in item else item)
        link.pop('xref', None)
        link.pop('id', None)
        link['from'] = fitz.Rect(link['from']) + (0, offset, 0, offset)
        rows.append(_serial(link))
    return sorted(rows, key=repr)


def _independent_contents(doc, page, translate_y=0):
    """Use a fresh stream rather than mutate streams shared by a full copy."""
    data = b'\n'.join(doc.xref_stream(xref) for xref in page.get_contents())
    if translate_y:
        data = (f'q\n1 0 0 1 0 {-translate_y:.8f} cm\n'.encode() +
                data + b'\nQ\n')
    xref = doc.get_new_xref()
    doc.update_object(xref, '<<>>')
    doc.update_stream(xref, data)
    page.set_contents(xref)


def _complement(page_rect, region):
    rectangles = [fitz.Rect(page_rect.x0, page_rect.y0, page_rect.x1, region.y0),
                  fitz.Rect(page_rect.x0, region.y1, page_rect.x1, page_rect.y1),
                  fitz.Rect(page_rect.x0, region.y0, region.x0, region.y1),
                  fitz.Rect(region.x1, region.y0, page_rect.x1, region.y1)]
    return [rect for rect in rectangles if rect.width > 0 and rect.height > 0]


def _redact(page, rectangles):
    for rect in rectangles:
        page.add_redact_annot(rect, fill=None, cross_out=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                          graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False,
                                    sort_keys=True).encode()).hexdigest()


def _destination_snapshot(doc):
    # get_links() may add a redundant "nameddest" member to MuPDF's cached
    # destination value. The dictionary key already is that exact name.
    return {name: _serial({key: value for key, value in destination.items()
                           if key != 'nameddest'})
            for name, destination in doc.resolve_names().items()}


def split_reference_pages(doc, component_id, groups):
    """Append isolated reference pages and return zero-based layout routes.

    ``doc`` is an already adapted in-memory display component. Only its mixed
    bibliography pages are changed. Whole reference pages retain their existing
    indices. A failed preservation check raises before the caller saves a PDF.
    """
    groups = [group for group in groups
              if group.get('component_id', component_id) == component_id]
    original_count = len(doc)
    names_before = _destination_snapshot(doc)
    result = {'reference_groups': [], 'reference_pages': [],
              'reference_routes': [], 'splits': []}
    split_pages = {}
    for group in groups:
        for mixed in group.get('mixed_regions', []):
            source = mixed['source_page_1based'] - 1
            if source in split_pages:
                raise ValueError('Multiple reference splits on one source page')
            if not 0 <= source < original_count:
                raise ValueError('Mixed reference page outside original component')
            original = doc[source]
            region = fitz.Rect(mixed['move_bbox_pdf_top_origin'])
            if not original.rect.contains(region) or region.is_empty:
                raise ValueError('Reference region outside page')
            if original.rotation:
                raise ValueError('Rotated reference page requires separate review')
            expected_main = _glyphs(original, region, inside=False)
            expected_refs = _glyphs(original, region, inside=True)
            if not expected_refs:
                raise ValueError('Empty mixed reference region')
            main_images = _images(original, region, inside=False)
            ref_images = _images(original, region, inside=True)
            # Current reviewed mixed pages have no reference figures. Avoid
            # silently translating image matrices under a weaker text check.
            if ref_images:
                raise ValueError('Reference-region image requires separate review')
            main_drawings = _drawings(original, region, inside=False)
            ref_drawings = _drawings(original, region, inside=True)
            links_before = _links(original)
            main_links = [row for row in links_before
                          if not _belongs(row['link']['from'], region)]
            ref_links = [row for row in links_before
                         if _belongs(row['link']['from'], region)]
            target = len(doc)
            doc.fullcopy_page(source)
            main = doc[source]
            clone = doc[target]
            _independent_contents(doc, main)
            _independent_contents(doc, clone)
            _redact(main, [region])
            _redact(clone, _complement(clone.rect, region))
            # Redaction changes page internals, so reload before setting links.
            main = _restore_links(doc, doc.reload_page(main), main_links)
            clone = _restore_links(doc, doc.reload_page(clone), ref_links)
            dy = 60 - region.y0
            _independent_contents(doc, clone, translate_y=dy)
            clone = _restore_links(doc, doc.reload_page(clone), ref_links, dy)
            main = doc[source]
            clone = doc[target]
            main_delta = _compare_glyphs(expected_main, _glyphs(main),
                                         f'{component_id}:{source + 1}: nonreference')
            ref_delta = _compare_glyphs(expected_refs, _glyphs(clone, offset=-dy),
                                        f'{component_id}:{source + 1}: reference')
            if _images(main) != main_images or _images(clone):
                raise ValueError('Reference split changed nonreference images')
            if _drawings(main) != main_drawings:
                raise ValueError('Reference split changed nonreference vector geometry')
            if _drawings(clone, offset=-dy) != ref_drawings:
                raise ValueError('Reference split changed reference vector geometry')
            if _link_signature(main.get_links()) != _link_signature(main_links):
                raise ValueError('Nonreference link action or geometry changed')
            if _link_signature(clone.get_links(), offset=-dy) != _link_signature(ref_links):
                raise ValueError('Reference link action or geometry changed')
            split_pages[source] = target
            result['reference_routes'].append({
                'source_page': source, 'rect': list(region),
                'target_source_page': target, 'point_offset': [0, dy]})
            result['splits'].append({
                'component_id': component_id, 'source_page': source,
                'target_source_page': target, 'reference_region': list(region),
                'translation': [0, dy],
                'nonreference_glyphs': len(expected_main),
                'reference_glyphs': len(expected_refs),
                'nonreference_glyphs_sha256': _digest(expected_main),
                'reference_glyphs_sha256': _digest(expected_refs),
                'nonreference_glyphs_fonts_positions_identical': True,
                'reference_glyphs_fonts_relative_positions_identical': True,
                'max_nonreference_geometry_reserialization_delta_pt': main_delta,
                'max_reference_geometry_reserialization_delta_pt': ref_delta,
                'geometry_reserialization_tolerance_pt': .0002,
                'nonreference_images_vectors_identical': True,
                'reference_vectors_relative_positions_identical': True,
                'nonreference_links': len(main_links),
                'reference_links': len(ref_links),
                'link_actions_and_geometries_preserved': True})
        pages = []
        for page_1based in group['pages_1based']:
            raw = page_1based - 1
            if not 0 <= raw < original_count:
                raise ValueError('Reference page outside original component')
            pages.append(split_pages.get(raw, raw))
        result['reference_groups'].append({
            'id': group['id'], 'title': group['group_title'], 'pages': pages})
        result['reference_pages'].extend(pages)
    if len(result['reference_pages']) != len(set(result['reference_pages'])):
        raise ValueError('Reference page selected by multiple groups')
    if _destination_snapshot(doc) != names_before:
        raise ValueError('Splitting references changed original named destinations')
    if len(doc) != original_count + len(split_pages):
        raise ValueError('Unexpected split reference page count')
    return result
