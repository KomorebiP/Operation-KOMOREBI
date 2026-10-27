#!/usr/bin/env python3
"""Refresh traditional-paper navigation from its actual final PDF page labels."""
from pathlib import Path
import argparse, hashlib, json
import fitz
from data_helpers import esc
H = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--traditional', type=Path, default=H.parent/'traditional')
args = parser.parse_args()
T = args.traditional.resolve()
records = json.loads((T/'manuscript_record_to_final.json').read_text(encoding="utf-8"))
labels = json.loads((T/'canonical_label_to_final.json').read_text(encoding="utf-8"))
earlier = json.loads((T/'EARLIER_RESULT_DESTINATIONS.json').read_text(encoding="utf-8"))
ledger = json.loads((H/'generated/result_ledger.json').read_text(encoding="utf-8"))
pdf = T/'Paper_VI_Traditional_Final.pdf'
doc = fitz.open(pdf)
page_labels = {}
body_rules = [r for r in doc.get_page_labels() if r.get('style') == 'D'
              and r.get('firstpagenum') == 1 and r['startpage'] > 0]
if not body_rules:
    raise RuntimeError('Expected a labeled Arabic body after the unnumbered cover')
body_start = max(r['startpage'] for r in body_rules)
for index, page in enumerate(doc, 1):
    if index <= body_start:
        continue
    label = page.get_label()
    if label in page_labels:
        raise RuntimeError('Ambiguous PDF page label: '+label)
    page_labels[label] = index

def resolved(record):
    row = dict(record)
    printed = str(row['printed_page'])
    if printed not in page_labels:
        raise RuntimeError('Printed page is absent from PDF labels: '+printed)
    actual = page_labels[printed]
    if int(row['physical_pdf_page']) != actual:
        raise RuntimeError('Traditional map and actual page label disagree for '+str(row.get('final_label')))
    row['physical_pdf_page'] = actual
    return row

cross = []
for row in ledger:
    r = resolved(records[row['number']])
    if r['formal_scope'] != 'released-core-result':
        raise RuntimeError('Core scope mismatch')
    cross.append({'ledger_number':row['number'], 'title':row['title'],
                  'traditional':r, 'guide_ledger_label':'result:'+row['number'],
                  'formal_status':'inherited-complete-scoped-statement'})
retained = []
for source_label, row in earlier.items():
    if row['status'] == 'complete-statement-and-proof-retained-in-Part-III':
        r = resolved(labels[row['final_label']])
        retained.append({'source_label':source_label,'title_tex':row['title_tex'],
                         'traditional':r,'formal_status':'retained-written-result-no-new-formal-contract'})
if len(retained) != 24:
    raise RuntimeError('Unexpected retained earlier count')
migrations = [resolved(r) for k,r in labels.items()
              if k.startswith('migration:') and r.get('kind') in
              ('theorem','proposition','lemma','corollary')]
migrations = list({r['number']:r for r in migrations}.values())
if len(migrations) != 1:
    raise RuntimeError('Expected one migrated reciprocal proposition')
out = [f'Printed pages are the labels in the traditional volume. PDF pages count every physical page, including its cover and Roman opening pages. These locations refer to the final {len(doc)}-page monograph. Every physical location was resolved from the actual PDF page label and checked against the final source map.\n\n',
       r'\textbf{All 33 formal-core endpoints.}'+'\n',
       r'\begin{longtable}{@{}p{.12\linewidth}p{.61\linewidth}rr@{}}\toprule Core & Result & Printed & PDF\\\midrule\endhead'+'\n']
for row in cross:
    r = row['traditional']
    out.append(esc(row['ledger_number'])+' & '+esc(row['title'])+' & '+r['printed_page']+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n')
out.append(r'\textbf{The 24 earlier results retained in Part III.} These have written proofs. This list creates no additional Lean completion claim.'+'\n')
out.append(r'\begin{longtable}{@{}p{.12\linewidth}p{.61\linewidth}rr@{}}\toprule Final & Result & Printed & PDF\\\midrule\endhead'+'\n')
for row in retained:
    r = row['traditional']
    out.append(esc(r['number'])+' & '+row['title_tex']+' & '+r['printed_page']+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n')
r = migrations[0]
out.append('The migrated bounded Banach reciprocal proposition is '+esc(r['number'])+', printed page '+r['printed_page']+' (PDF page '+str(r['physical_pdf_page'])+'). Its scope remains outside the 33-result contract.\n')
(H/'generated/traditional_navigation.tex').write_text(''.join(out), encoding="utf-8")
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
provenance = {name:sha(T/name) for name in
              ['canonical_label_to_final.json','manuscript_record_to_final.json',
               'EARLIER_RESULT_DESTINATIONS.json','EDITION_RECONCILIATION.json',
               'Paper_VI_Traditional_Final.tex']}
if (T/'SOURCE_RECORDS.json').exists():
    provenance['SOURCE_RECORDS.json'] = sha(T/'SOURCE_RECORDS.json')
provenance.update(traditional_pdf_filename=pdf.name,
                  traditional_pdf_sha256=sha(pdf),traditional_pdf_pages=len(doc),
                  physical_location_method='actual unique Arabic body page labels, checked against final source map',
                  arabic_body_first_physical_page=body_start+1)
(H/'generated/traditional_crosswalk.json').write_text(json.dumps(
    {'core':cross,'retained_earlier':retained,'migration':migrations,'provenance':provenance},
    indent=2,ensure_ascii=False)+'\n', encoding="utf-8")
print(json.dumps({'core':len(cross),'retained_earlier':len(retained),
                  'migration':len(migrations),'traditional_pdf_pages':len(doc)}))
