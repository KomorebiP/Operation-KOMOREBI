#!/usr/bin/env python3
"""Refresh traditional-paper navigation from its final generated maps."""
from pathlib import Path
import argparse, hashlib, json
from data_helpers import esc
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--traditional',type=Path,default=H.parent/'traditional');a=p.parse_args();T=a.traditional.resolve()
records=json.loads((T/'manuscript_record_to_final.json').read_text())
labels=json.loads((T/'canonical_label_to_final.json').read_text())
earlier=json.loads((T/'EARLIER_RESULT_DESTINATIONS.json').read_text())
ledger=json.loads((H/'generated/result_ledger.json').read_text())
cross=[]
for row in ledger:
 r=records[row['number']]
 if r['formal_scope']!='released-core-result':raise RuntimeError('Core scope mismatch')
 cross.append({'ledger_number':row['number'],'title':row['title'],'traditional':r,'guide_ledger_label':'result:'+row['number'],'formal_status':'inherited-complete-scoped-statement'})
retained=[]
for source_label,row in earlier.items():
 if row['status']=='complete-statement-and-proof-retained-in-Part-III':
  r=labels[row['final_label']]
  retained.append({'source_label':source_label,'title_tex':row['title_tex'],'traditional':r,'formal_status':'retained-written-result-no-new-formal-contract'})
if len(retained)!=24:raise RuntimeError('Unexpected retained earlier count')
migrations=[r for k,r in labels.items() if k.startswith('migration:') and r.get('kind') in ('theorem','proposition','lemma','corollary')]
unique={r['number']:r for r in migrations};migrations=list(unique.values())
if len(migrations)!=1:raise RuntimeError('Expected one migrated reciprocal proposition')
out=['Printed pages are the numbers on the traditional paper; PDF pages count the cover. These locations refer to its final 104-page edition. The source maps and PDF hash are pinned in the editable crosswalk.\n\n',r'\textbf{All 33 formal-core endpoints.}'+'\n',r'\begin{longtable}{@{}p{.12\linewidth}p{.61\linewidth}rr@{}}\toprule Core & Result & Printed & PDF\\\midrule\endhead'+'\n']
for row in cross:
 r=row['traditional'];out.append(esc(row['ledger_number'])+' & '+esc(row['title'])+' & '+r['printed_page']+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n')
out.append(r'\textbf{The 24 earlier results retained in Part III.} These have written proofs; this list creates no additional Lean completion claim.'+'\n')
out.append(r'\begin{longtable}{@{}p{.12\linewidth}p{.61\linewidth}rr@{}}\toprule Final & Result & Printed & PDF\\\midrule\endhead'+'\n')
for row in retained:
 r=row['traditional'];out.append(esc(r['number'])+' & '+row['title_tex']+' & '+r['printed_page']+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n')
r=migrations[0]
out.append('The migrated bounded Banach reciprocal proposition is '+esc(r['number'])+', printed page '+r['printed_page']+' (PDF page '+str(r['physical_pdf_page'])+'). Its scope remains outside the 33-result contract.\n')
(H/'generated/traditional_navigation.tex').write_text(''.join(out))
pdf=T/'Paper_VI_Traditional_Final.pdf'
if not pdf.exists():
 candidates=list(T.glob('*.pdf'))
 if len(candidates)!=1:raise RuntimeError('Ambiguous traditional PDF')
 pdf=candidates[0]
provenance={name:hashlib.sha256((T/name).read_bytes()).hexdigest() for name in ['canonical_label_to_final.json','manuscript_record_to_final.json','EARLIER_RESULT_DESTINATIONS.json','EDITION_RECONCILIATION.json']}
provenance['traditional_pdf_filename']=pdf.name;provenance['traditional_pdf_sha256']=hashlib.sha256(pdf.read_bytes()).hexdigest();provenance['traditional_pdf_pages']=104
(H/'generated/traditional_crosswalk.json').write_text(json.dumps({'core':cross,'retained_earlier':retained,'migration':migrations,'provenance':provenance},indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'core':len(cross),'retained_earlier':len(retained),'migration':len(migrations),'traditional_pdf':pdf.name}))
