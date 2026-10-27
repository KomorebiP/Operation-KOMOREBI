#!/usr/bin/env python3
"""Assemble the current reading edition, preserving component links and outlines."""
from pathlib import Path
import hashlib
import json
import fitz
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'publication'
STATUS = json.loads((ROOT / 'formal/verification/FINAL_VERIFICATION_SUMMARY.json').read_text())
if STATUS['status'] != 'PASS':
    raise SystemExit('Formal verification summary must be final and passing')
ss = getSampleStyleSheet()
for name, parent, font, size, leading, color in [
    ('KickerK', 'Normal', 'Helvetica-Bold', 9, 13, '#326d6b'),
    ('TitleK', 'Title', 'Times-Bold', 27, 30, '#193139'),
    ('SubK', 'Normal', 'Times-Roman', 15, 20, '#55686a'),
    ('HeadK', 'Heading2', 'Helvetica-Bold', 11, 15, '#193139'),
    ('BodyK', 'BodyText', 'Times-Roman', 10.4, 14.5, '#193139'),
    ('SmallK', 'BodyText', 'Helvetica', 8.8, 12, '#55686a'),
    ('CellK', 'Normal', 'Helvetica', 8.9, 12.2, '#193139')]:
    ss.add(ParagraphStyle(name=name, parent=ss[parent], fontName=font, fontSize=size,
                          leading=leading, textColor=HexColor(color), alignment=0,
                          spaceAfter=9, spaceBefore=5 if name == 'HeadK' else 0))


def p(text, style='BodyK'):
    return Paragraph(text, ss[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(HexColor('#cfd9d6'))
    canvas.line(52, A4[1] - 40, A4[0] - 52, A4[1] - 40)
    canvas.setFillColor(HexColor('#55686a'))
    canvas.setFont('Helvetica', 7.3)
    canvas.drawString(52, 29, 'OPERATION KOMOREBI / PAPER III / RELEASE 1.0.0')
    canvas.drawRightString(A4[0] - 52, 29, str(doc.page))
    canvas.restoreState()


parts = [
    ('Traditional monograph', OUT / 'Paper_III_Final_v1.0.0.pdf'),
    ('Analytic packet supplement', OUT / 'Paper_III_Analytic_Supplement_v1.0.0.pdf'),
    ('Visual guide', OUT / 'Paper_III_Visual_Guide_v1.0.0.pdf'),
    ('Lean and evidence guide', OUT / 'Paper_III_Lean_Guide_v1.0.0.pdf')]
page_counts = {}
for name, path in parts:
    with fitz.open(path) as document:
        page_counts[name] = len(document)
scope = OUT / 'Paper_III_Release_Record_v1.0.0.pdf'
story = [p('OPERATION KOMOREBI · REALIZATION CALCULUS', 'KickerK'),
         p('Projector Resolved<br/>Seed Calculus III', 'TitleK'),
         p('Complete reading edition', 'SubK'),
         p('Version 1.0.0 · 20 October 2026 · Komorebi P.', 'SmallK'),
         p('The completed technical release', 'HeadK'),
         p('This edition integrates the corrected mathematical monograph, its analytic supplement, '
           'the visual guide, and a revised guide to the formal evidence. The main manuscript contains '
           '98 result environments and two classical standard facts. Their proof and verification '
           'status is recorded statement by statement in the source package.'),
         p('Current verification', 'HeadK')]
rows = [
    ('Layer', 'Release evidence'),
    ('Ordinary proofs', 'The finite and nonlinear coordinate arguments, corrected Section 17 analysis, '
     'and all 59 later results plus two classical inputs were reviewed under their stated hypotheses.'),
    ('Fresh Lean verification', f"{STATUS['production_module_count']} production modules compiled. "
     f"The ownership audit recorded {STATUS['owned_declarations']} entries. "
     f"Kernel replay accepted {STATUS['replayed_logical_declarations']} logical declarations, "
     f"with {STATUS['generated_runtime_helpers']} generated runtime helpers separately inventoried. "
     'All designated controls passed.'),
    ('New packet interface', 'Literal continuous range jets, the stronger norm estimate, and the '
     'complete decorated composition and structural support laws are in the accepted Lean source.'),
    ('Exact computation', '18,630 assertions across three coordinate and calculus suites, plus 124 '
     'visual-model checks and four rejected false controls. The audit states the tested ranges and repetitions.')]
table = Table([[p(a, 'CellK'), p(b, 'CellK')] for a, b in rows], colWidths=[112, 379], repeatRows=1)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f0ee')),
    ('LINEBELOW', (0, 0), (-1, -1), .4, HexColor('#cfd9d6')),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8)]))
story += [table, p('Formal scope', 'HeadK'),
          p('The integral Taylor remainder, its estimate, the Stirling count, and the later analytic '
            'and obstruction results retain ordinary proof status. This release does not certify '
            'full Lean coverage of the monograph. The unrecovered larger October 16 formal claim '
            'is preserved only as historical evidence.'), PageBreak(),
          p('READING AND REPRODUCTION', 'KickerK'), p('The paper and its companions', 'TitleK')]
descriptions = [
    ('Traditional monograph', 'The complete mathematical development, corrected Section 17 proofs, '
     '24 worked visual plates, and bibliography. The original theorem numbering is retained.'),
    ('Analytic packet supplement', 'Full range-space, norm, Taylor, composition and support arguments, '
     'including degenerate cases and the exact relation to the accepted formal interface.'),
    ('Visual guide', '24 worked plates and 22 exact model figures, with a current evidence page. '
     'The figures expose map directions, assumptions and finite counterexamples.'),
    ('Lean and evidence guide', 'A new current-release chapter, the complete finite 41-row map, '
     'exact source excerpts, current monograph locators, and reproducible formal commands.')]
for name, description in descriptions:
    story += [p(name + f' · {page_counts[name]} pages', 'HeadK'), p(description)]
story += [p('The reproducible package', 'HeadK'),
          p('The final archive includes editable TeX and figure sources, Lean source and dependency '
            'pins, full verification transcripts, independent mathematical reviews, exact computation '
            'scripts, the statement register, and a SHA-256 manifest. The earlier checkpoint and '
            'release-candidate records remain explicitly archived.'),
          p('Run <font face="Courier">python VERIFY_RELEASE.py</font> from a fresh extraction to '
            'check all packaged bytes. Run <font face="Courier">python BUILD_PDFS.py</font> in a '
            'working copy to rebuild the reading files. The formal README gives the pinned compiler '
            'restore and four-phase replay procedure.'),
          p('Edition and rights', 'HeadK'),
          p('Version 1.0.0 is the final technical manuscript release under its declared mathematical '
            'and formal scope. Public reuse terms remain an author decision. The package retains '
            'the existing copyright notices and assigns no new license.'),
          p('Use the bookmarks to move between the release record and the four documents. '
            'Internal links and component page labels are retained. Printed locators refer to '
            'the relevant standalone companion.', 'SmallK')]
SimpleDocTemplate(str(scope), pagesize=A4, leftMargin=52, rightMargin=52, topMargin=57,
                  bottomMargin=51, title='Paper III release record', author='Komorebi P.').build(
                      story, onFirstPage=footer, onLaterPages=footer)
parts.insert(0, ('Release record', scope))
merged = fitz.open()
toc, layout, labels = [], [], []
for name, path in parts:
    with fitz.open(path) as doc:
        offset = len(merged)
        # insert_pdf deliberately omits named links. Resolve them in their own
        # component before names such as section.1 can collide across documents.
        # resolve_names returns PDF coordinates; convert them to page coordinates.
        merged.insert_pdf(doc, links=False, annots=True)
        names = doc.resolve_names()
        copied_links = 0
        for source_page in doc:
            for link in source_page.get_links():
                kind = link['kind']
                if kind == fitz.LINK_NAMED and link.get('nameddest') in names:
                    destination = names[link['nameddest']]
                    page_number = destination['page']
                    if not 0 <= page_number < len(doc):
                        raise RuntimeError('Unresolved named destination: ' + link['nameddest'])
                    point = fitz.Point(destination.get('to', (0, doc[page_number].rect.height)))
                    point = point * doc[page_number].transformation_matrix
                    item = {'kind': fitz.LINK_GOTO, 'from': link['from'],
                            'page': page_number + offset, 'to': point,
                            'zoom': destination.get('zoom', 0)}
                elif kind == fitz.LINK_GOTO:
                    if not 0 <= link['page'] < len(doc):
                        raise RuntimeError('Invalid component destination page')
                    item = {'kind': kind, 'from': link['from'], 'page': link['page'] + offset,
                            'to': link.get('to', fitz.Point(0, 0)), 'zoom': link.get('zoom', 0)}
                elif kind == fitz.LINK_URI:
                    item = {'kind': kind, 'from': link['from'], 'uri': link['uri']}
                else:
                    raise RuntimeError('Unhandled component link kind: ' + str(kind))
                merged[source_page.number + offset].insert_link(item)
                copied_links += 1
        toc.append([1, name, offset + 1])
        toc.extend([[level + 1, title, page + offset if page > 0 else page]
                    for level, title, page in doc.get_toc()])
        for label in doc.get_page_labels():
            labels.append(dict(label, startpage=label['startpage'] + offset))
        if not doc.get_page_labels():
            labels.append({'startpage': offset, 'prefix': '', 'style': 'D', 'firstpagenum': 1})
        layout.append({'name': name, 'source': str(path.relative_to(ROOT)), 'pages': len(doc),
                       'start_page': offset + 1, 'source_links': sum(len(pg.get_links()) for pg in doc),
                       'copied_links': copied_links,
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
merged.set_toc(toc)
merged.set_page_labels(labels)
merged.set_metadata({'title': 'Projector Resolved Seed Calculus III — Complete Reading Edition',
                     'author': 'Komorebi P.', 'subject': 'Final technical release 1.0.0 with explicit formal scope',
                     'keywords': 'packet calculus, nonlinear coordinates, obstruction theory, Lean'})
output = OUT / 'Paper_III_Complete_Reading_Edition_v1.0.0.pdf'
merged.save(output, garbage=4, deflate=True)
with fitz.open(output) as checked:
    actual_links = sum(len(page.get_links()) for page in checked)
    expected_links = sum(part['source_links'] for part in layout)
    if actual_links != expected_links:
        raise RuntimeError(f'Link loss: expected {expected_links}, found {actual_links}')
(ROOT / 'evidence/INTEGRATED_READER_LAYOUT.json').write_text(json.dumps({
    'status': 'PASS', 'release_version': '1.0.0', 'pages': len(merged),
    'bookmark_count': len(toc), 'parts': layout, 'links_preserved': True,
    'expected_links': expected_links, 'verified_links': actual_links,
    'scope': 'Component named destinations resolved explicitly to page destinations with coordinate conversion; all component outlines are offset and retained.'
}, indent=2) + '\n')
print(f'Complete reader: {len(merged)} pages, {len(toc)} bookmarks')
