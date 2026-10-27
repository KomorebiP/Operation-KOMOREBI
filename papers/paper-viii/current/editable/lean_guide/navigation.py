#!/usr/bin/env python3
"""Resolve guide locations from the final traditional source map and PDF."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import fitz
from data_helpers import esc

HERE = Path(__file__).resolve().parent
PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--traditional', type=Path, default=HERE.parent / 'traditional')
PARSER.add_argument('--map', type=Path)
ARGS = PARSER.parse_args()
TRADITIONAL = ARGS.traditional.resolve()
MAP = (ARGS.map or TRADITIONAL / 'canonical_label_to_final.json').resolve()
PDF = TRADITIONAL / 'Paper_VIII_Traditional_Final.pdf'
GENERATED = HERE / 'generated'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
labels = json.loads(MAP.read_text(encoding='utf-8'))
document = fitz.open(PDF)
destinations = document.resolve_names()
ledger = json.loads((GENERATED / 'coverage_ledger.json').read_text())

def resolve(original):
    label = original['label']
    if label not in labels:
        raise RuntimeError('Missing current traditional label: ' + label)
    row = dict(labels[label])
    printed = str(row.get('printed_page', row.get('page')))
    physical = row.get('physical_pdf_page', row.get('physical_page'))
    if physical is None:
        raise RuntimeError('Missing physical PDF page: ' + label)
    physical = int(physical)
    if not 1 <= physical <= len(document) or document[physical - 1].get_label() != printed:
        raise RuntimeError('Current traditional page label differs: ' + label)
    destination = row.get('destination')
    if destination and destination in destinations:
        actual = destinations[destination]['page'] + 1
        if actual != physical:
            raise RuntimeError('Current PDF destination differs: ' + label)
    row.update(original_label=label, original_item=original.get('number'),
               printed_page=printed, physical_pdf_page=physical)
    return row

rows = []
for original in ledger['records']:
    row = {
        'item': original['number'], 'title': original['title'],
        'lean_status': original['lean_status'],
        'lean_theorems': original.get('lean_theorems', []),
        'formal_scope': original.get('formal_scope'),
        'traditional': resolve(original),
    }
    rows.append(row)
core = [row for row in rows if row['lean_status'] == 'checked']
classical = [row for row in rows if row['lean_status'].startswith('external_input_')]
if len(rows) != 85 or len(core) != 56 or len(classical) != 4:
    raise RuntimeError('Unexpected manuscript/coverage counts: ' + str((len(rows), len(core), len(classical))))

out = [r'\section{Navigation through the traditional volume}' + '\n' +
       r'\label{sec:traditional-navigation}' + '\n',
       f'The traditional volume contains {len(document)} physical PDF pages. Printed pages are its visible page labels. PDF pages count the cover and opening pages as well. The locations below are resolved from the current source map and verified against the actual PDF labels and destinations. Original result numbers remain the correspondence keys.\n\n',
       r'\subsection{All 56 registered finite results}' + '\n',
       'The page map locates each manuscript statement. The formal hypotheses in Section~\\ref{sec:scope} describe its actual finite counterpart. These page locations do not expand the formal contract.\n\n',
       r'{\small\begin{longtable}{@{}p{.10\linewidth}p{.11\linewidth}p{.51\linewidth}rr@{}}\toprule Item & Number & Statement & Printed & PDF\\\midrule\endhead' + '\n']
for row in core:
    location = row['traditional']
    out.append(r'\hyperref[result:' + row['item'] + ']{' + row['item'] + '} & ' +
               esc(location['number']) + ' & ' + esc(row['title']) + ' & ' +
               location['printed_page'] + ' & ' + str(location['physical_pdf_page']) + r'\\' + '\n')
out += [r'\bottomrule\end{longtable}}' + '\n',
        r'\subsection{The four separately supplied classical inputs}' + '\n',
        'These inputs are tracked separately from the 56 finite results. Their exact boundaries are discussed in the replay chapter.\n\n',
        r'{\small\begin{longtable}{@{}p{.10\linewidth}p{.11\linewidth}p{.51\linewidth}rr@{}}\toprule Item & Number & Classical input & Printed & PDF\\\midrule\endhead' + '\n']
for row in classical:
    location = row['traditional']
    out.append(r'\hyperref[result:' + row['item'] + ']{' + row['item'] + '} & ' +
               esc(location['number']) + ' & ' + esc(row['title']) + ' & ' +
               location['printed_page'] + ' & ' + str(location['physical_pdf_page']) + r'\\' + '\n')
out += [r'\bottomrule\end{longtable}}' + '\n',
        r'\subsection{The open research boundary}' + '\n']
boundary = resolve({'label': 'sec:boundaries'})
out += ['The traditional boundary discussion is on printed page ' + boundary['printed_page'] +
        ' (PDF page ' + str(boundary['physical_pdf_page']) + '). It retains the three broader targets: discovery of profitable structure for arbitrary operators, controlled compilation for overlapping decompositions and nonlocal costs, and a communication theorem for a specified packet memory architecture. Their finite special cases do not settle those broader targets.\n']
(GENERATED / 'traditional_navigation.tex').write_text(''.join(out), encoding='utf-8')

result_map = GENERATED / 'result_map.tex'
text = result_map.read_text(encoding='utf-8')
text = re.sub(r'% BEGIN MONOGRAPH LOCATION\n.*?% END MONOGRAPH LOCATION\n', '', text, flags=re.S)
for row in core + classical:
    location = row['traditional']
    anchor = r'\label{result:' + row['item'] + '}\n'
    if text.count(anchor) != 1:
        raise RuntimeError('Missing or duplicate formal correspondence label ' + row['item'])
    note = ('% BEGIN MONOGRAPH LOCATION\n' + r'{\footnotesize\color{muted}Traditional original item ' +
           row['item'] + ', current statement ' + esc(location['number']) + '. Printed page ' +
           location['printed_page'] + ', PDF page ' + str(location['physical_pdf_page']) + r'.}\par' +
           '\n% END MONOGRAPH LOCATION\n')
    text = text.replace(anchor, anchor + note)
result_map.write_text(text, encoding='utf-8')

pins = {}
for name in ('canonical_label_to_final.json', 'current_source_records.json',
             'SOURCE_RECORDS.json', 'EDITION_RECONCILIATION.json',
             'Paper_VIII_Traditional_Final.tex', 'evidence/ASSEMBLY_MANIFEST.json',
             'evidence/PROOF_BODY_PRESERVATION.json', 'evidence/FINAL_PAGE_MAP.json'):
    path = TRADITIONAL / name
    if path.is_file():
        pins[name] = sha(path)
provenance = {'traditional_pdf_filename': PDF.name, 'traditional_pdf_sha256': sha(PDF),
              'traditional_pdf_pages': len(document), 'traditional_source_map_sha256': sha(MAP),
              'source_record_pins': pins,
              'location_method': 'current canonical source label, actual physical PDF page, visible PDF page label and internal named destination',
              'fresh_lean_kernel_run': False}
crosswalk = {'paper': 'VIII', 'edition': '2026-10-09', 'registered_finite_results': core,
             'classical_inputs': classical, 'all_85_original_records': rows,
             'open_boundary': boundary, 'provenance': provenance}
(GENERATED / 'traditional_crosswalk.json').write_text(json.dumps(crosswalk, indent=2, ensure_ascii=False) + '\n')
(GENERATED / 'traditional_navigation_provenance.json').write_text(json.dumps({
    **provenance, 'mapped_finite_results': 56, 'mapped_classical_inputs': 4,
    'mapped_all_original_records': 85,
    'traditional_crosswalk_sha256': sha(GENERATED / 'traditional_crosswalk.json'),
}, indent=2) + '\n')
print(json.dumps({'finite_results': 56, 'classical_inputs': 4, 'all_original_records': 85,
                  'traditional_pdf_pages': len(document), 'traditional_pdf_sha256': sha(PDF)}))
