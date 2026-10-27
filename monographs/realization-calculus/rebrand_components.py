#!/usr/bin/env python3
"""Apply a bounded branding-only treatment to displayed component PDF copies.

The original source PDFs and frozen attachments must be retained separately.
No page is rasterized. Font programs come from the documented installed fonts.
Every changed page is rendered only for validation of the vector PDF edit.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import unicodedata

import fitz
from PIL import Image, ImageChops, ImageDraw

OLD = 'operationkomorebi'
NEW = 'REALIZATION CALCULUS'


def _sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _letters(text):
    return ''.join(c for c in text.lower() if 'a' <= c <= 'z')


def _normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text)
                   if not c.isspace() and c not in '\u00ad\u200b\ufeff')


def _serial(value):
    if isinstance(value, (fitz.Rect, fitz.Point, fitz.Quad, fitz.Matrix)):
        return [_serial(v) for v in value]
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, dict):
        return {k: _serial(v) for k, v in value.items()
                if k not in ('xref', 'id', 'seqno')}
    if isinstance(value, (list, tuple)):
        return [_serial(v) for v in value]
    if isinstance(value, float):
        return round(value, 5)
    return value


def _lines(page):
    result = []
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            spans = line['spans']
            text = ''.join(ch['c'] for sp in spans for ch in sp['chars'])
            result.append({**line, 'text': text})
    return result


def _replace_label(text):
    # Map normalized letters back to exact source character positions.
    positions = [i for i, c in enumerate(text) if 'a' <= c.lower() <= 'z']
    norm = _letters(text)
    if norm.count(OLD) != 1:
        raise ValueError('Expected exactly one old brand in a label: ' + text)
    if norm == OLD + _letters(NEW):
        return NEW  # old brand / already-present new brand
    start = norm.index(OLD)
    lo, hi = positions[start], positions[start + len(OLD) - 1] + 1
    return text[:lo] + NEW + text[hi:]


def _font(font_name):
    if font_name == 'Helvetica':
        return {'resource': 'helv', 'font': fitz.Font('helv'),
                'description': 'PDF standard Helvetica', 'file': None}
    if font_name == 'Helvetica-Bold':
        return {'resource': 'hebo', 'font': fitz.Font('hebo'),
                'description': 'PDF standard Helvetica-Bold', 'file': None}
    if font_name in ('NimbusSans-Regular', 'NimbusSanL-Regu'):
        filename = 'NimbusSans-Regular.otf'
    elif font_name in ('NimbusSans-Bold', 'NimbusSanL-Bold'):
        filename = 'NimbusSans-Bold.otf'
    elif font_name == 'LMRoman10-Bold':
        filename = 'lmroman10-bold.otf'
    else:
        raise ValueError('Unreviewed branding font: ' + font_name)
    located = subprocess.run(['kpsewhich', filename], capture_output=True,
                             text=True, check=True).stdout.strip()
    if not located or not Path(located).is_file():
        raise RuntimeError('Install the required system font: ' + filename)
    font_path = Path(located)
    digest = _sha(font_path)
    return {'resource': 'RCBrand' + digest[:12], 'font': fitz.Font(fontfile=str(font_path)),
            'description': filename, 'file': str(font_path), 'sha256': digest}


def _outside_text(page, boxes):
    pieces = []
    for line in _lines(page):
        for span in line['spans']:
            for char in span['chars']:
                rect = fitz.Rect(char['bbox'])
                if not any(rect.intersects(box) for box in boxes):
                    pieces.append(char['c'])
    return _normalized(''.join(pieces))


def _snapshot(page):
    return {'rect': list(page.rect), 'label': page.get_label(),
            'links': _serial(page.get_links()),
            'drawings': _serial(page.get_drawings()),
            'images': _serial(page.get_image_info(hashes=True))}


def _vector_difference(before, after):
    """Bound harmless PDF-number reserialization; require exact path structure."""
    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        delta = abs(before - after)
        if delta > .0001:
            raise ValueError('Vector coordinate/style changed beyond 0.0001 point: ' + str(delta))
        return delta
    if isinstance(before, dict) and isinstance(after, dict) and before.keys() == after.keys():
        return max((_vector_difference(before[k], after[k]) for k in before), default=0)
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        return max((_vector_difference(a, b) for a, b in zip(before, after)), default=0)
    if before != after:
        raise ValueError('Vector path structure/style changed')
    return 0


def _pixels_outside(before, after, boxes, scale=2):
    a = before.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    b = after.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    if (a.width, a.height, a.n) != (b.width, b.height, b.n):
        raise ValueError('Rendered page geometry changed')
    ia = Image.frombytes('RGB', (a.width, a.height), a.samples)
    ib = Image.frombytes('RGB', (b.width, b.height), b.samples)
    diff = ImageChops.difference(ia, ib)
    mask = ImageDraw.Draw(diff)
    for box in boxes:
        # One point around actual old/new glyph bounds includes antialias edges.
        rect = fitz.Rect(box) + (-1, -1, 1, 1)
        mask.rectangle((math.floor(rect.x0 * scale), math.floor(rect.y0 * scale),
                        math.ceil(rect.x1 * scale), math.ceil(rect.y1 * scale)), fill=(0, 0, 0))
    channels = diff.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    hist = maximum.histogram()
    return {'render_dpi': 72 * scale, 'changed_pixels_outside_branding': sum(hist[1:]),
            'maximum_channel_difference_outside_branding': maximum.getextrema()[1]}


def rebrand_component(path):
    """Atomically replace only reviewed branding in a display PDF copy.

    Returns a JSON-serializable record. Any validation failure leaves path
    untouched and raises an exception. An already rebranded PDF is a no-op.
    """
    path = Path(path)
    before_hash = _sha(path)
    original = fitz.open(path)
    doc = fitz.open(path)
    page_count = len(original)
    before_toc = _serial(original.get_toc(simple=False))
    before_labels = _serial(original.get_page_labels())
    before_named_destinations = _serial(original.resolve_names())
    edits = []
    changed_pages = {}
    fonts = {}
    try:
        for page_number, page in enumerate(doc):
            page_edits = []
            lines = _lines(page)
            for line in lines:
                if OLD not in _letters(line['text']):
                    continue
                rect = fitz.Rect(line['bbox'])
                if not (rect.y1 < 100 or rect.y0 > page.rect.height - 80):
                    raise ValueError('Old branding occurs outside a reviewed cover/header/footer region')
                if tuple(line.get('dir', (1, 0))) != (1.0, 0.0):
                    raise ValueError('Rotated branding requires separate review')
                if len(line['spans']) != 1:
                    raise ValueError('Mixed-style branding requires separate review')
                span = line['spans'][0]
                name = span['font']
                if name not in fonts:
                    fonts[name] = _font(name)
                font = fonts[name]
                new_text = _replace_label(line['text'])
                retained_brand = None
                if _letters(line['text']) == OLD and rect.y1 < 100:
                    existing = [other for other in lines if other is not line
                                and _letters(other['text']) == _letters(NEW)
                                and rect.y1 < other['bbox'][1] < rect.y1 + 45
                                and abs(other['bbox'][0] - rect.x0) < 8]
                    if len(existing) == 1:
                        # These six preserved covers already carry the requested
                        # series name below the old project brand. Keep that
                        # original label and remove only the redundant old line.
                        retained_brand = {'text': existing[0]['text'],
                                          'bbox': list(existing[0]['bbox'])}
                        new_text = ''
                size = span['size']
                width = font['font'].text_length(new_text, fontsize=size)
                origin = fitz.Point(span['origin'])
                alignment = 'left'
                if _letters(line['text']) == OLD and abs((rect.x0 + rect.x1) / 2 - page.rect.width / 2) < 2:
                    origin.x = page.rect.width / 2 - width / 2
                    alignment = 'center'
                predicted = fitz.Rect(origin.x, origin.y - size * font['font'].ascender,
                                      origin.x + width, origin.y - size * font['font'].descender)
                if new_text and not page.rect.contains(predicted):
                    raise ValueError('Replacement branding would leave its page')
                for other in lines:
                    if other is line:
                        continue
                    if new_text and predicted.intersects(fitz.Rect(other['bbox'])):
                        raise ValueError('Replacement branding would overlap other text')
                color = tuple(((span['color'] >> shift) & 255) / 255 for shift in (16, 8, 0))
                edit = {'page_1based': page_number + 1, 'old_text': line['text'], 'new_text': new_text,
                        'old_bbox': list(rect), 'origin': list(origin), 'font_size': size,
                        'old_font': name, 'replacement_font': font['description'],
                        'font_sha256': font.get('sha256'), 'color_rgb': list(color),
                        'alignment': alignment, '_font': font,
                        'action': 'remove_redundant_old_brand' if retained_brand else 'replace_branding_line',
                        'retained_existing_brand': retained_brand}
                page_edits.append(edit)
            if not page_edits:
                continue
            # No fill is added. Existing white/pale backgrounds remain untouched.
            for edit in page_edits:
                page.add_redact_annot(fitz.Rect(edit['old_bbox']), fill=None, cross_out=False)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                  graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                  text=fitz.PDF_REDACT_TEXT_REMOVE)
            for edit in page_edits:
                font = edit.pop('_font')
                if edit['new_text']:
                    page.insert_text(fitz.Point(edit['origin']), edit['new_text'],
                                     fontsize=edit['font_size'], fontname=font['resource'],
                                     fontfile=font['file'], color=tuple(edit['color_rgb']), overlay=True)
            changed_pages[page_number] = page_edits
            edits.extend(page_edits)
        if not edits:
            return {'status': 'unchanged', 'before_sha256': before_hash,
                    'after_sha256': before_hash, 'pages': len(doc), 'edits': [],
                    'scope': 'No Operation Komorebi display branding was present.'}
        handle, temporary_name = tempfile.mkstemp(prefix=path.stem + '_branding_', suffix='.pdf', dir=path.parent)
        os.close(handle)
        temporary = Path(temporary_name)
        try:
            # Compact unused objects without merging unrelated inherited objects.
            doc.save(temporary, garbage=2, deflate=True, no_new_id=True)
            doc.close()
            check = fitz.open(temporary)
            try:
                if len(check) != len(original) or _serial(check.get_page_labels()) != before_labels:
                    raise ValueError('Page count or page labels changed')
                if _serial(check.get_toc(simple=False)) != before_toc:
                    raise ValueError('Component bookmarks changed')
                if _serial(check.resolve_names()) != before_named_destinations:
                    raise ValueError('Component named destinations changed')
                checks = []
                for number, page in enumerate(check):
                    before = original[number]
                    bs, after = _snapshot(before), _snapshot(page)
                    vector_delta = _vector_difference(bs['drawings'], after['drawings'])
                    if any(bs[k] != after[k] for k in bs if k != 'drawings'):
                        differing = [k for k in bs if k != 'drawings' and bs[k] != after[k]]
                        raise ValueError('Non-branding structure changed on page ' + str(number + 1) + ': ' + str(differing))
                    if OLD in _letters(page.get_text()):
                        raise ValueError('Old display branding remains after edit')
                    if number not in changed_pages:
                        if before.get_text() != page.get_text():
                            raise ValueError('Untouched page text changed')
                        continue
                    new_lines = _lines(page)
                    old_boxes = []
                    new_boxes = []
                    for edit in changed_pages[number]:
                        if not edit['new_text']:
                            kept = edit['retained_existing_brand']
                            candidates = [line for line in new_lines if line['text'] == kept['text']
                                          and _serial(line['bbox']) == _serial(kept['bbox'])]
                            if len(candidates) != 1:
                                raise ValueError('Existing series label changed during cover de-duplication')
                            edit['new_bbox'] = None
                            edit['validation_region'] = edit['old_bbox']
                            old_boxes.append(fitz.Rect(edit['old_bbox']))
                            continue
                        candidates = [line for line in new_lines if line['text'] == edit['new_text']
                                      and abs(line['spans'][0]['origin'][1] - edit['origin'][1]) < .05]
                        if len(candidates) != 1:
                            raise ValueError('Replacement label does not extract exactly once: ' + edit['new_text'])
                        box = fitz.Rect(candidates[0]['bbox'])
                        edit['new_bbox'] = list(box)
                        union = box | fitz.Rect(edit['old_bbox'])
                        edit['validation_region'] = list(union)
                        old_boxes.append(fitz.Rect(edit['old_bbox']))
                        new_boxes.append(box)
                    a = _outside_text(before, old_boxes)
                    b = _outside_text(page, new_boxes)
                    if a != b:
                        raise ValueError('Normalized non-branding text changed on page ' + str(number + 1))
                    pixels = _pixels_outside(before, page, [e['validation_region'] for e in changed_pages[number]])
                    if pixels['changed_pixels_outside_branding']:
                        raise ValueError('Pixels outside branding changed on page ' + str(number + 1) + ': ' + str(pixels))
                    checks.append({'page_1based': number + 1, 'nonbranding_text_sha256': hashlib.sha256(a.encode()).hexdigest(),
                                   'nonbranding_text_identical': True, 'images_links_identical': True,
                                   'vector_path_structure_preserved': True,
                                   'maximum_vector_numeric_reserialization_delta': vector_delta, **pixels})
                after_hash = _sha(temporary)
            finally:
                check.close()
            original.close()
            os.replace(temporary, path)
            return {'status': 'rebranded', 'before_sha256': before_hash, 'after_sha256': after_hash,
                    'pages': page_count,
                    'changed_pages': len(changed_pages), 'branding_occurrences': len(edits),
                    'scope': 'Displayed publication branding only; original frozen readers retained separately.',
                    'page_count_labels_links_bookmarks_preserved': True,
                    'named_destinations_preserved': True,
                    'images_and_vector_drawings_preserved': True, 'background_fill_added': False,
                    'vector_numeric_reserialization_tolerance_pt': .0001,
                    'edits': edits, 'page_checks': checks}
        finally:
            temporary.unlink(missing_ok=True)
    finally:
        if not original.is_closed:
            original.close()
        if not doc.is_closed:
            doc.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path, help='Display derivative to edit in place; keep the original separately.')
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    result = rebrand_component(args.pdf)
    if args.record:
        args.record.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
