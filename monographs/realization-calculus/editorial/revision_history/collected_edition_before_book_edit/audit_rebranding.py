#!/usr/bin/env python3
"""Independent read-only audit of displayed branding and bounded PDF edits.

Run only after the final Realization_Calculus.pdf has been sealed.  Raw component
builds and frozen attachments are inputs, never modified.  This checks editorial
assembly preservation, not mathematical correctness or fresh formal replay.
"""
from pathlib import Path
import collections
import hashlib
import json
import math
import re
import sys
import unicodedata

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent
OLD = 'operationkomorebi'
NEW = 'realizationcalculus'
# These six source pages already carry the desired title beneath the former
# top-level project brand.  The authorized edit removes only that redundant line.
REMOVE_ONLY = {'IV_visual': {1}, 'XI_research_progress': {1, 3, 36, 55},
               'XI_research_atlas': {1}}


def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def alpha(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text).casefold() if c.isalpha())


def lines(page):
    result = []
    for block in page.get_text('rawdict')['blocks']:
        if block.get('type') != 0:
            continue
        for line in block['lines']:
            chars = [c for s in line['spans'] for c in s['chars']]
            text = ''.join(c['c'] for c in chars)
            result.append({'text': text, 'bbox': fitz.Rect(line['bbox']), 'chars': chars})
    return result


def glyphs_outside(page_lines, rects):
    out = []
    for line in page_lines:
        for char in line['chars']:
            # Whitespace may be synthesized differently after content-stream
            # editing.  Actual nonspace glyphs and their placement must survive.
            if char['c'].isspace():
                continue
            box = fitz.Rect(char['bbox'])
            center = (box.tl + box.br) / 2
            if any(r.contains(center) for r in rects):
                continue
            out.append((char['c'], tuple(char['origin']), tuple(box)))
    return out


def same_glyphs(before, after, tol=0.02):
    if len(before) != len(after):
        return False
    return all(a[0] == b[0] and all(abs(x-y) <= tol for x, y in zip(a[1]+a[2], b[1]+b[2]))
               for a, b in zip(before, after))


def clean_links(page):
    return [{k: (tuple(v) if isinstance(v, (fitz.Point, fitz.Rect)) else v)
             for k, v in l.items() if k not in ('xref', 'id')}
            for l in page.get_links()]


def numeric_vector_delta(before, after):
    """Preserve path structure/style, ignoring only display-list sequence IDs."""
    maximum = 0.0
    def check(a, b):
        nonlocal maximum
        if isinstance(a, (fitz.Point, fitz.Rect)):
            a = tuple(a)
        if isinstance(b, (fitz.Point, fitz.Rect)):
            b = tuple(b)
        if isinstance(a, dict) and isinstance(b, dict):
            aa, bb = set(a)-{'seqno'}, set(b)-{'seqno'}
            return aa == bb and all(check(a[k], b[k]) for k in aa)
        if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
            return len(a) == len(b) and all(check(x, y) for x, y in zip(a, b))
        if isinstance(a, (float, int)) and isinstance(b, (float, int)):
            maximum = max(maximum, abs(a-b))
            return abs(a-b) <= 0.0001
        return a == b
    same = check(before.get_drawings(), after.get_drawings())
    return {'structure_and_style_preserved': same, 'maximum_numeric_delta': maximum,
            'numeric_tolerance': 0.0001}


def higher_resolution_pixels(before, after, rects, scale):
    pp = [p.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
          for p in (before, after)]
    images = [Image.frombytes('RGB', (p.width, p.height), p.samples) for p in pp]
    diff = ImageChops.difference(*images)
    draw = ImageDraw.Draw(diff)
    for r in rects:
        draw.rectangle((math.floor((r.x0-2)*scale), math.floor((r.y0-2)*scale),
                        math.ceil((r.x1+2)*scale), math.ceil((r.y1+2)*scale)), fill=(0, 0, 0))
    return diff.getbbox() is None


def main():
    pdf_path = ROOT/'output/Realization_Calculus.pdf'
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise RuntimeError('Final Realization_Calculus.pdf does not exist yet')
    spec = json.loads((ROOT/'book/build_spec.json').read_text())
    builds = json.loads((ROOT/'component_builds.json').read_text())
    if isinstance(builds, dict):
        builds = builds['components']
    raw_by_filename = {b['baseline_filename']: b for b in builds}
    inventory = json.loads((ROOT/'editorial/COMPONENT_BRANDING_SCAN.json').read_text())
    affected = {x['id']: x for x in inventory['affected']}
    errors, warnings, components, edited_pages = [], [], [], []
    count = collections.Counter()
    def fail(code, **details):
        errors.append({'code': code, **details})

    for part in spec['parts']:
        for comp in part['components']:
            current_path = ROOT/comp['path']
            raw_info = raw_by_filename[Path(comp['baseline_path']).name]
            raw_path = Path(raw_info['output_pdf'])
            if not raw_path.is_absolute():
                raw_path = ROOT/raw_path
            raw_sha, current_sha = digest(raw_path), digest(current_path)
            expected_raw_sha = raw_info.get('sha256', raw_info.get('output_sha256'))
            if not expected_raw_sha:
                raise ValueError('Raw build has no recorded PDF hash: '+comp['id'])
            row = {'id': comp['id'], 'raw_path': str(raw_path.relative_to(ROOT)),
                   'display_path': comp['path'], 'raw_sha256': raw_sha,
                   'display_sha256': current_sha, 'expected_raw_sha256': expected_raw_sha}
            if raw_sha != expected_raw_sha:
                fail('raw_build_hash_changed', component=comp['id'])
            if comp['id'] not in affected:
                row['unchanged_bytes'] = raw_sha == current_sha
                count['unaffected_components_byte_identical'] += int(row['unchanged_bytes'])
                if not row['unchanged_bytes']:
                    fail('unexpected_component_change', component=comp['id'])
                components.append(row)
                continue
            before, after = fitz.open(raw_path), fitz.open(current_path)
            if len(before) != len(after):
                fail('component_page_count_changed', component=comp['id'])
            if before.get_toc(simple=False) != after.get_toc(simple=False):
                # Xref numbers are implementation details.  Normalize them before
                # reporting a semantic bookmark change.
                def toc(doc):
                    return [[*entry[:3], {k: tuple(v) if isinstance(v, fitz.Point) else v
                                           for k, v in entry[3].items() if k != 'xref'}]
                            for entry in doc.get_toc(simple=False)]
                if toc(before) != toc(after):
                    fail('component_bookmark_changed', component=comp['id'])
            changed_count = 0
            for n in range(min(len(before), len(after))):
                bp, ap = before[n], after[n]
                bl, al = lines(bp), lines(ap)
                oldlines = [x for x in bl if OLD in alpha(x['text'])]
                if alpha(bp.get_text()).count(OLD) != len(oldlines):
                    fail('old_brand_line_detection_mismatch', component=comp['id'], page=n+1)
                if OLD in alpha(ap.get_text()):
                    fail('old_brand_survives_component', component=comp['id'], page=n+1)
                if bp.rect != ap.rect:
                    fail('component_page_geometry_changed', component=comp['id'], page=n+1)
                if clean_links(bp) != clean_links(ap):
                    fail('component_links_changed', component=comp['id'], page=n+1)
                rects, replacements = [], []
                used = set()
                for old in oldlines:
                    # Find new display line on the same baseline band, without
                    # trusting the adapter's declared allowed rectangle.
                    cy = (old['bbox'].y0 + old['bbox'].y1) / 2
                    candidates = [(i, line) for i, line in enumerate(al)
                                  if NEW in alpha(line['text']) and i not in used
                                  and abs((line['bbox'].y0+line['bbox'].y1)/2-cy) < 5]
                    removal = n+1 in REMOVE_ONLY.get(comp['id'], set())
                    if removal:
                        if candidates or not any(NEW in alpha(x['text']) for x in al):
                            fail('deduplication_rule_not_satisfied', component=comp['id'], page=n+1)
                        new = None
                        rect = fitz.Rect(old['bbox'])
                    elif len(candidates) != 1:
                        fail('replacement_line_ambiguous', component=comp['id'], page=n+1,
                             old_text=old['text'], candidates=len(candidates))
                        continue
                    else:
                        idx, new = candidates[0]
                        used.add(idx)
                        rect = old['bbox'] | new['bbox']
                    rect = fitz.Rect(rect.x0-0.5, rect.y0-0.5, rect.x1+0.5, rect.y1+0.5)
                    rects.append(rect)
                    replacements.append({'old': old['text'], 'new': new['text'] if new else '',
                                         'mode': 'remove_redundant_project_line' if removal else 'replace_display_line',
                                         'allowed_rect': list(rect)})
                    # The independently derived edit band may not consume any
                    # other nonbranding source line.
                    for line in bl:
                        if line is old or OLD in alpha(line['text']) or not line['text'].strip():
                            continue
                        if any(rect.contains((fitz.Rect(c['bbox']).tl+fitz.Rect(c['bbox']).br)/2)
                               for c in line['chars'] if not c['c'].isspace()):
                            fail('edit_band_overlaps_other_source_text', component=comp['id'],
                                 page=n+1, text=line['text'])
                bg, ag = glyphs_outside(bl, rects), glyphs_outside(al, rects)
                glyph_ok = same_glyphs(bg, ag)
                if not glyph_ok:
                    fail('nonbranding_glyph_content_or_position_changed', component=comp['id'],
                         page=n+1, source_glyphs=len(bg), display_glyphs=len(ag))
                count['adapted_component_pages_nonbranding_glyph_match'] += int(glyph_ok)
                # Render only one page pair at a time: bounded RAM, independent
                # preservation check for diagrams/paths as well as text.
                pix1 = bp.get_pixmap(matrix=fitz.Matrix(1, 1), colorspace=fitz.csRGB, alpha=False)
                pix2 = ap.get_pixmap(matrix=fitz.Matrix(1, 1), colorspace=fitz.csRGB, alpha=False)
                im1 = Image.frombytes('RGB', (pix1.width, pix1.height), pix1.samples)
                im2 = Image.frombytes('RGB', (pix2.width, pix2.height), pix2.samples)
                diff = ImageChops.difference(im1, im2)
                mask = ImageDraw.Draw(diff)
                for rect in rects:
                    # Two raster pixels cover glyph antialiasing at clip edges.
                    mask.rectangle((math.floor(rect.x0)-2, math.floor(rect.y0)-2,
                                    math.ceil(rect.x1)+2, math.ceil(rect.y1)+2), fill=(0, 0, 0))
                pixel_ok = diff.getbbox() is None
                pixel_warning = None
                if not pixel_ok:
                    nonzero = [(x, y, diff.getpixel((x, y)))
                               for y in range(diff.getbbox()[1], diff.getbbox()[3])
                               for x in range(diff.getbbox()[0], diff.getbbox()[2])
                               if max(diff.getpixel((x, y)))]
                    maximum = max(max(v) for _, _, v in nonzero)
                    vector = numeric_vector_delta(bp, ap)
                    higher = {str(scale*72): higher_resolution_pixels(bp, ap, rects, scale)
                              for scale in (2, 4)}
                    evidence = {'component': comp['id'], 'page': n+1,
                                'difference_bbox': diff.getbbox(), 'differing_pixels': len(nonzero),
                                'maximum_channel_difference_of_255': maximum,
                                'pixel_channel_differences': [{'xy': [x, y], 'difference': list(v)}
                                                             for x, y, v in nonzero[:10]],
                                'vectors': vector, 'higher_dpi_pixels_exact_outside_same_bands': higher}
                    if (len(nonzero) <= 2 and maximum <= 3 and glyph_ok
                            and vector['structure_and_style_preserved'] and all(higher.values())):
                        pixel_warning = {'code': 'negligible_numeric_reserialization_antialiasing',
                                         **evidence,
                                         'interpretation': 'A tiny vector-coordinate roundtrip changes antialias edge coverage at 72dpi. Text and vector structure/styles survive; 144/288dpi pixels are exact outside the same edit bands. No edit-band expansion was applied.'}
                        warnings.append(pixel_warning)
                        count['adapted_component_pages_negligible_serialization_antialiasing'] += 1
                    else:
                        fail('pixels_changed_outside_branding_bands', **evidence)
                count['adapted_component_pages_pixels_identical_outside_bands'] += int(pixel_ok)
                if oldlines:
                    changed_count += len(oldlines)
                    edited_pages.append({'component': comp['id'], 'page': n+1,
                                         'book_page': comp['index_start']+n+1,
                                         'replacements': replacements,
                                         'nonbranding_glyph_match': glyph_ok,
                                         'pixels_outside_bands_identical': pixel_ok,
                                         'pixel_warning': pixel_warning})
            row['labels_replaced'] = changed_count
            if changed_count != affected[comp['id']]['occurrences']:
                fail('label_count_changed', component=comp['id'], actual=changed_count,
                     expected=affected[comp['id']]['occurrences'])
            count['adapted_components'] += 1
            count['labels_replaced'] += changed_count
            before.close(); after.close()
            components.append(row)

    book = fitz.open(pdf_path)
    old_hits, old_title_hits, new_title_pages = [], [], []
    for n, page in enumerate(book):
        text = page.get_text()
        compact = alpha(text)
        if OLD in compact:
            old_hits.append(n+1)
        if 'komorebicorepapers' in compact:
            old_title_hits.append(n+1)
        if NEW in compact:
            new_title_pages.append(n+1)
    if old_hits:
        fail('old_brand_survives_displayed_book', pages=old_hits)
    if old_title_hits:
        warnings.append({'code': 'old_book_title_text_present', 'pages': old_title_hits})
    if NEW not in alpha(book[0].get_text()) or NEW not in alpha(book.metadata.get('title', '')):
        fail('new_title_missing_from_cover_or_metadata', metadata=book.metadata)
    prohibited = re.compile(r'\b(?:version|release|released|freeze|frozen|closeout|rebuild)\b|\bv\d+\.\d+|\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b', re.I)
    editorial = []
    for n in (0, 1, 2, 3):
        text = book[n].get_text()
        hits = [m.group() for m in prohibited.finditer(text)]
        editorial.append({'page': n+1, 'text': text, 'administrative_terms': hits})
        if hits:
            fail('administrative_wording_in_cover_scope_or_introduction', page=n+1, terms=hits)
    count['displayed_pages_scanned'] = len(book)
    count['edited_component_pages'] = len(edited_pages)
    count['new_title_pages'] = len(new_title_pages)
    if count['labels_replaced'] != 150 or count['edited_component_pages'] != 149:
        fail('total_label_count_mismatch', labels=count['labels_replaced'],
             pages=count['edited_component_pages'])
    report = {'schema': 'realization-calculus.independent-rebranding-audit/1',
              'pdf': str(pdf_path.relative_to(ROOT)), 'pdf_sha256': digest(pdf_path),
              'status': 'PASS' if not errors else 'FAIL', 'stats': dict(count),
              'errors': errors, 'warnings': warnings, 'components': components,
              'edited_pages': edited_pages, 'front_matter': editorial,
              'old_operation_brand_book_pages': old_hits, 'old_book_title_pages': old_title_hits,
              'method': {'text': 'All displayed pages normalized by NFKC, casefold, alphabetic characters only.',
                         'raw_sources': 'Every raw build hash is checked against component_builds.json; 35 unaffected components must be byte-identical.',
                         'edited_sources': 'All 154 pages in six adapted components compared against raw PDFs. Every nonbranding nonspace glyph and position must agree. Page-pair RGB pixels at 72dpi are compared outside independently derived old/new label bands plus two-pixel antialias margins. Deviations remain explicit: at most two pixels with channel delta at most3 can be classified as a warning only if all vector structures/styles agree within0.0001 and 144/288dpi pixels are exact outside the same bands. Larger or unexplained changes fail.',
                         'limitations': 'Raster preservation is 72dpi; exact glyph geometry complements it. Frozen attachment hashes are independently checked by audit_monograph.py. This is an editorial preservation audit, not a mathematical or formal proof audit.'}}
    (ROOT/'book/rebranding_audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    summary = {'status': report['status'], 'pdf_sha256': report['pdf_sha256'],
               'stats': dict(count), 'errors': errors, 'warnings': warnings}
    print(json.dumps(summary, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
