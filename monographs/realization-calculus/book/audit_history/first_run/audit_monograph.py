#!/usr/bin/env python3
"""Independent structural/content audit of the assembled core monograph.

Read-only with respect to PDFs and assembler source. This verifies publication
assembly, not mathematical correctness or a fresh formal replay.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import sys
import unicodedata

import fitz

ROOT = Path(__file__).resolve().parent
TOL = 0.75


def sha(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def normalized(text):
    text = unicodedata.normalize('NFKC', text)
    return ''.join(c for c in text if not c.isspace() and c not in '\u00ad\u200b\ufeff')


def subsequence(needle, haystack):
    """Ignore only inserted material; never reorder the source characters."""
    j = 0
    for c in haystack:
        if j < len(needle) and c == needle[j]:
            j += 1
    return j == len(needle)


def transform_rect(box, transform):
    scale, tx, ty = transform
    r = fitz.Rect(box)
    return fitz.Rect(r.x0 * scale + tx, r.y0 * scale + ty,
                     r.x1 * scale + tx, r.y1 * scale + ty)


def within(box, page, tol=TOL):
    r, p = fitz.Rect(box), fitz.Rect(page)
    return r.x0 >= p.x0-tol and r.y0 >= p.y0-tol and r.x1 <= p.x1+tol and r.y1 <= p.y1+tol


def spans(page):
    result = []
    for block in page.get_text('dict')['blocks']:
        if block.get('type') != 0:
            continue
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                if span.get('text', '').strip():
                    result.append(span)
    return result


def annotation_xrefs(doc, page):
    kind, value = doc.xref_get_key(page.xref, 'Annots')
    if kind == 'xref':
        ref = int(value.split()[0])
        value = doc.xref_object(ref, compressed=True)
    return [int(x) for x in re.findall(r'(\d+)\s+\d+\s+R', value)] if kind != 'null' else []


def inspect_action(doc, xref):
    kind, value = doc.xref_get_key(xref, 'A')
    if kind == 'xref':
        action = int(value.split()[0])
        prefix = ''
    elif kind == 'dict':
        action = xref
        prefix = 'A/'
    else:
        return None
    def get(key):
        return doc.xref_get_key(action, prefix + key)
    return get


def audit(root=ROOT):
    spec_path = root/'book/build_spec.json'
    map_path = root/'book/page_map.json'
    pdf_path = root/'output/Komorebi_Core_Papers.pdf'
    for path in (spec_path, map_path, pdf_path):
        if not path.is_file():
            raise FileNotFoundError('Required final input absent: ' + str(path))
    spec = json.loads(spec_path.read_text())
    page_map = json.loads(map_path.read_text())['pages']
    page_map = {int(k): v for k, v in page_map.items()}
    parts = spec['parts']
    components = [c for p in parts for c in p['components']]
    comp_by_id = {c['id']: c for c in components}
    book = fitz.open(pdf_path)
    errors, warnings = [], []
    stats = collections.Counter()
    def error(code, **detail):
        errors.append({'code': code, **detail})
    def warn(code, **detail):
        warnings.append({'code': code, **detail})
    if len(parts) != 12:
        error('part_count', actual=len(parts), expected=12)
    if len(components) != 41 or len(comp_by_id) != 41:
        error('component_count_or_unique_ids', actual=len(components), unique=len(comp_by_id), expected=41)
    expected_count = spec['front_pages'] + len(parts) + sum(c['pages'] for c in components)
    if len(book) != expected_count:
        error('page_count', actual=len(book), expected=expected_count)
    expected_map_keys = set(range(spec['front_pages'], len(book)))
    if set(page_map) != expected_map_keys:
        error('page_map_membership', missing=sorted(expected_map_keys-set(page_map)), extra=sorted(set(page_map)-expected_map_keys))

    # Independently authenticate all attachment bytes against baseline files.
    attachments = {}
    embedded_names = book.embfile_names()
    expected_names = [Path(c['baseline_path']).name for c in components]
    if len(set(expected_names)) != len(expected_names):
        error('duplicate_expected_attachment_name')
    if set(embedded_names) != set(expected_names) or len(embedded_names) != 41:
        error('embedded_attachment_membership', expected=sorted(expected_names), actual=sorted(embedded_names))
    attachment_checks = []
    for comp in components:
        baseline = root/comp['baseline_path']
        name = baseline.name
        row = {'component': comp['id'], 'name': name, 'expected_sha256': comp['baseline_sha256']}
        if not baseline.is_file():
            error('baseline_file_missing', component=comp['id'], path=str(baseline))
            row['passed'] = False
            attachment_checks.append(row)
            continue
        baseline_sha = sha(baseline)
        row['baseline_sha256'] = baseline_sha
        with fitz.open(baseline) as original:
            baseline_pages = len(original)
        row['baseline_pages'] = baseline_pages
        if baseline_sha != comp['baseline_sha256']:
            error('baseline_hash_mismatch', component=comp['id'])
        if baseline_pages != comp['baseline_pages']:
            error('baseline_page_count_mismatch', component=comp['id'], actual=baseline_pages, expected=comp['baseline_pages'])
        attachments[name] = baseline_pages
        if name in embedded_names:
            blob = book.embfile_get(name)
            embedded_sha = hashlib.sha256(blob).hexdigest()
            row['embedded_sha256'] = embedded_sha
            row['embedded_bytes'] = len(blob)
            row['passed'] = embedded_sha == baseline_sha == comp['baseline_sha256']
            if not row['passed']:
                error('embedded_attachment_hash_mismatch', component=comp['id'], name=name)
        else:
            row['passed'] = False
        attachment_checks.append(row)

    docs = {}
    component_checks = []
    expected_index = spec['front_pages']
    for part in parts:
        if part['divider_index'] != expected_index:
            error('divider_index', paper=part['paper'], actual=part['divider_index'], expected=expected_index)
        divider_record = page_map.get(expected_index, {})
        if not divider_record.get('divider') or divider_record.get('paper') != part['paper']:
            error('divider_map', paper=part['paper'], page=expected_index+1)
        expected_index += 1
        for comp in part['components']:
            path = root/comp['path']
            if comp['index_start'] != expected_index:
                error('component_start', component=comp['id'], actual=comp['index_start'], expected=expected_index)
            if not path.is_file():
                error('component_file_missing', component=comp['id'], path=str(path))
                expected_index += comp['pages']
                continue
            source = docs[comp['id']] = fitz.open(path)
            source_sha = sha(path)
            ok = source_sha == comp['sha256'] and len(source) == comp['pages']
            if not ok:
                error('component_source_identity', component=comp['id'], actual_sha256=source_sha, actual_pages=len(source), expected_sha256=comp['sha256'], expected_pages=comp['pages'])
            for sp in range(comp['pages']):
                rec = page_map.get(expected_index + sp, {})
                if rec.get('component') != comp['id'] or rec.get('source_page') != sp+1 or rec.get('paper') != part['paper'] or rec.get('divider'):
                    error('component_page_mapping', component=comp['id'], source_page=sp+1, book_page=expected_index+sp+1, map_record=rec)
            component_checks.append({'component': comp['id'], 'source_sha256': source_sha, 'source_pages': len(source), 'mapped_pages': comp['pages'], 'first_book_page': expected_index+1, 'last_book_page': expected_index+comp['pages'], 'source_identity_passed': ok})
            expected_index += comp['pages']
    if expected_index != len(book):
        error('component_mapping_total', mapped=expected_index, actual=len(book))

    # Bounds and page destinations are checked from the actual finished PDF.
    toc = book.get_toc(simple=False)
    for j, item in enumerate(toc):
        if len(item) < 3 or not isinstance(item[2], int) or not 1 <= item[2] <= len(book):
            error('bookmark_destination', bookmark_index=j, value=str(item))
        if j and item[0] > toc[j-1][0]+1:
            error('bookmark_hierarchy_jump', bookmark_index=j, value=str(item))
    stats['bookmarks'] = len(toc)
    page_xrefs = {book.page_xref(i): i for i in range(len(book))}
    embedded_actions, page_checks = [], []
    for index, page in enumerate(book):
        if abs(page.rect.width-612) > .02 or abs(page.rect.height-792) > .02:
            error('page_size', page=index+1, rect=list(page.rect))
        stats['pages_checked'] += 1
        text = page.get_text('text', sort=False)
        if not text.strip():
            error('empty_page_text', page=index+1)
        record = page_map.get(index, {})
        cid = record.get('component')
        row = {'book_page': index+1, 'page_size': [page.rect.width, page.rect.height], 'characters': len(text), 'component': cid}
        inherited_outside = []
        source_spans = []
        if cid and cid in docs:
            sp = record['source_page']-1
            source = docs[cid][sp]
            transform = record.get('transform')
            if not isinstance(transform, list) or len(transform) != 3 or transform[0] <= 0:
                error('invalid_transform', page=index+1, transform=transform)
                continue
            source_text = source.get_text('text', sort=False)
            sn, bn = normalized(source_text), normalized(text)
            if not sn:
                error('empty_component_page_text', component=cid, source_page=sp+1, book_page=index+1)
            exact_block = sn in bn
            ordered = exact_block or subsequence(sn, bn)
            row.update({'source_page': sp+1, 'source_characters_normalized': len(sn), 'source_text_is_contiguous': exact_block, 'source_text_is_ordered_subsequence': ordered, 'preserved_pdf_page': bool(record.get('preserved_pdf_page'))})
            stats['component_pages_checked'] += 1
            stats['contiguous_text_matches' if exact_block else 'ordered_text_matches' if ordered else 'text_mismatches'] += 1
            if not ordered:
                error('source_text_not_preserved', component=cid, source_page=sp+1, book_page=index+1, source_characters=len(sn), book_characters=len(bn))
            source_spans = spans(source)
            for ss in source_spans:
                target = transform_rect(ss['bbox'], transform)
                source_inside = within(ss['bbox'], source.rect)
                if not source_inside:
                    inherited_outside.append({'source_bbox': list(ss['bbox']), 'text': ss['text'][:120]})
                elif not within(target, page.rect):
                    error('assembly_text_crop', component=cid, source_page=sp+1, book_page=index+1, source_bbox=list(ss['bbox']), transformed_bbox=list(target), text=ss['text'][:120])
            if inherited_outside:
                warn('source_component_text_bounds', component=cid, source_page=sp+1, book_page=index+1, spans=inherited_outside, meaning='Present in the input component before final PDF assembly; not introduced by the assembler.')
            if record.get('preserved_pdf_page'):
                target_page = transform_rect(source.rect, transform)
                if not within(target_page, page.rect):
                    error('preserved_page_geometry_crop', component=cid, source_page=sp+1, book_page=index+1, target_rect=list(target_page))
                else:
                    stats['full_preserved_page_frames_within_output'] += 1
            # Imported vector operations precede editorial furniture. Compare
            # every source operation's kind and transformed bbox independently.
            sb, bb = source.get_bboxlog(), page.get_bboxlog()
            geom_ok = len(bb) >= len(sb)
            max_delta = 0.0
            if geom_ok:
                for a, b in zip(sb, bb):
                    if a[0] != b[0]:
                        geom_ok = False
                        break
                    predicted = transform_rect(a[1], transform)
                    delta = max(abs(x-y) for x,y in zip(predicted,b[1]))
                    max_delta = max(max_delta, delta)
                    if delta > TOL:
                        geom_ok = False
                        break
            row.update({'source_graphic_operations': len(sb), 'source_graphic_prefix_matches': geom_ok, 'graphic_bbox_max_delta_pt': round(max_delta,6)})
            if geom_ok:
                stats['graphic_geometry_matches'] += 1
            else:
                warn('graphic_bbox_prefix_difference', component=cid, source_page=sp+1, book_page=index+1, source_ops=len(sb), output_ops=len(bb), max_delta_pt=max_delta, meaning='A text or vector bbox prefix differed; source text and full preserved-page frame checks are independent. Inspect before accepting if unexplained.')
        # Source bounds are distinguished from new editorial/assembly bounds.
        outside = [s for s in spans(page) if not within(s['bbox'], page.rect)]
        for s in outside:
            text_norm = normalized(s['text'])
            known_inherited = any(text_norm == normalized(a['text']) for a in inherited_outside)
            if known_inherited:
                stats['inherited_offpage_spans'] += 1
            else:
                error('output_offpage_text', page=index+1, bbox=list(s['bbox']), text=s['text'][:140])
        row['offpage_text_spans'] = len(outside)
        for link in page.get_links():
            stats['pymupdf_link_records'] += 1
            if link['kind'] == fitz.LINK_GOTO:
                stats['internal_links'] += 1
                if not 0 <= link.get('page', -1) < len(book):
                    error('internal_link_page', source_page=index+1, link=str(link))
                point = link.get('to')
                if isinstance(point, fitz.Point) and (not -TOL <= point.x <= 612+TOL or not -TOL <= point.y <= 792+TOL):
                    warn('internal_link_point_outside_page', source_page=index+1, target_page=link['page']+1, point=list(point), meaning='Page destination is valid; the inherited destination point may lie outside the page.')
            if link.get('from') and not within(link['from'], page.rect):
                warn('link_rectangle_outside_page', page=index+1, rectangle=list(link['from']))
        for xref in annotation_xrefs(book, page):
            action = inspect_action(book, xref)
            if action is None:
                continue
            subtype = action('S')[1]
            stats['annotation_action_'+subtype.strip('/')] += 1
            if subtype == '/GoToE':
                nk, name = action('T/N')
                dk, dest = action('D')
                route_kind = action('T/R')[1]
                match = re.match(r'\[\s*(\d+)\s+/', dest) if dk == 'array' else None
                destpage = int(match.group(1)) if match else None
                rec = {'source_book_page': index+1, 'annotation_xref': xref, 'attachment': name, 'target_page_zero_based': destpage, 'target_relation': route_kind}
                embedded_actions.append(rec)
                if nk != 'string' or name not in attachments:
                    error('embedded_link_attachment', **rec)
                elif destpage is None or not 0 <= destpage < attachments[name]:
                    error('embedded_link_page', **rec)
                if route_kind != '/C':
                    error('embedded_link_relation', **rec)
            elif subtype == '/GoToR':
                error('remaining_external_pdf_action', page=index+1, annotation_xref=xref, target=action('F')[1])
            elif subtype == '/GoTo':
                dk, dest = action('D')
                m = re.match(r'\[\s*(\d+)\s+\d+\s+R', dest) if dk == 'array' else None
                if m and int(m.group(1)) not in page_xrefs:
                    error('internal_link_page_object', page=index+1, annotation_xref=xref, destination=dest)
        page_checks.append(row)
    stats['embedded_links_checked'] = len(embedded_actions)
    # Compare counts to emitted assembler records only after inspecting the PDF.
    record_path = root/'book/embedded_reference_links.json'
    if record_path.is_file():
        declared = json.loads(record_path.read_text())
        actual_keys = collections.Counter((r['source_book_page'],r['attachment'],r['target_page_zero_based']+1) for r in embedded_actions if r['target_page_zero_based'] is not None)
        declared_keys = collections.Counter((r['book_page'],r['attachment'],r['target_page']) for r in declared)
        if actual_keys != declared_keys:
            error('embedded_action_record_mismatch', actual_count=len(embedded_actions), declared_count=len(declared))
    summary = {
        'schema':'komorebi.core-monograph.independent-final-pdf-audit/1',
        'status':'PASS' if not errors else 'FAIL',
        'pdf':str(pdf_path.relative_to(root)), 'pdf_sha256':sha(pdf_path),
        'build_spec_sha256':sha(spec_path), 'page_map_sha256':sha(map_path),
        'scope':'Finished PDF structure, attachment identity, source-page mapping, ordered text survival and imported vector geometry; not mathematical verification.',
        'normalization':'NFKC; remove whitespace, soft hyphen, zero-width space and BOM only. Source characters must survive as a contiguous block or ordered subsequence in extraction order.',
        'geometry_tolerance_pt':TOL,
        'statistics':dict(stats),
        'errors':errors, 'warnings':warnings,
        'attachment_checks':attachment_checks,
        'component_checks':component_checks,
        'embedded_actions':embedded_actions,
        'page_checks':page_checks,
    }
    output = root/'book/final_pdf_audit.json'
    output.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    brief = {'status':summary['status'],'pages':len(book),'components':len(components),'attachments':len(embedded_names),'errors':len(errors),'warnings':len(warnings),'statistics':dict(stats),'output':str(output)}
    (root/'book/final_pdf_audit_summary.txt').write_text(json.dumps(brief,indent=2)+'\n')
    for doc in docs.values():doc.close()
    book.close()
    return brief


def render_samples(root=ROOT):
    from PIL import Image, ImageOps, ImageDraw
    spec = json.loads((root/'book/build_spec.json').read_text())
    book = fitz.open(root/'output/Komorebi_Core_Papers.pdf')
    dest = root/'book/final_visual_samples';dest.mkdir(parents=True,exist_ok=True)
    selected = {}
    def add(index, reason):
        if 0 <= index < len(book):selected.setdefault(index, []).append(reason)
    for n in [0,1,2,3,4,5,spec['front_pages']-1]:add(n,'front matter')
    for part in spec['parts']:
        add(part['divider_index'],'part '+part['paper']+' divider')
        for comp in part['components']:
            # One representative interior from each of the 41 components.
            offset = min(comp['pages']-1, max(1, comp['pages']//2))
            add(comp['index_start']+offset, comp['id']+' interior')
    rendered=[];thumbs=[]
    for index, reason in sorted(selected.items()):
        page=book[index]
        path=dest/f'page_{index+1:04d}.png'
        pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
        pix.save(path)
        image=Image.open(path).convert('RGB')
        thumb=ImageOps.contain(image,(235,304))
        tile=Image.new('RGB',(251,338),'#e9e5e8')
        tile.paste(thumb,((251-thumb.width)//2,5))
        draw=ImageDraw.Draw(tile);draw.text((8,312),f'PDF page {index+1}: '+reason[0][:28],fill='black')
        thumbs.append(tile)
        rendered.append({'page':index+1,'reasons':reason,'image':str(path.relative_to(root))})
    sheets=[]
    for start in range(0,len(thumbs),16):
        sheet=Image.new('RGB',(4*251,4*338),'white')
        for j,tile in enumerate(thumbs[start:start+16]):sheet.paste(tile,((j%4)*251,(j//4)*338))
        path=dest/f'contact_sheet_{start//16+1:02d}.png';sheet.save(path)
        sheets.append(str(path.relative_to(root)))
    report={'sample_count':len(rendered),'selection':'Seven front-matter pages, twelve part dividers and one representative interior from every component. Contact sheets are navigation aids; use individual page PNGs for close inspection.','pages':rendered,'contact_sheets':sheets,'manual_visual_review_performed_by_this_script':False}
    (dest/'sample_index.json').write_text(json.dumps(report,indent=2)+'\n')
    book.close()
    return {'sample_count':len(rendered),'contact_sheets':sheets}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--render-samples',action='store_true',help='Render the bounded sixty-page visual sample after auditing.')
    parser.add_argument('--samples-only',action='store_true',help='Only create the visual samples; does not certify a structural audit.')
    args=parser.parse_args()
    result={}
    if not args.samples_only:result['audit']=audit()
    if args.render_samples or args.samples_only:result['visual_samples']=render_samples()
    print(json.dumps(result,indent=2))
    if result.get('audit',{}).get('status')=='FAIL':raise SystemExit(1)


if __name__=='__main__':main()
