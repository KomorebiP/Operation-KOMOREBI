#!/usr/bin/env python3
"""Bind cross-reading rows to the traditional volume's actual final PDF labels."""
from pathlib import Path
import argparse,ast,hashlib,json,re
import fitz
from data_helpers import esc
H=Path(__file__).resolve().parent
P=argparse.ArgumentParser(description=__doc__)
P.add_argument('--map',type=Path)
P.add_argument('--traditional',type=Path,default=H.parent/'traditional')
a=P.parse_args();T=a.traditional.resolve(); map_path=(a.map or T/'evidence/FINAL_PAGE_MAP.json').resolve();x=json.loads(map_path.read_text());G=H/'generated'
PDF=T/'Paper_VII_Traditional_Final.pdf';doc=fitz.open(PDF);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(PDF)!=x['pdf_sha256'] or len(doc)!=x['pdf_pages']:raise RuntimeError('Traditional map and PDF identities disagree')
rules=[r for r in doc.get_page_labels() if r.get('style')=='D' and r.get('firstpagenum')==1 and r['startpage']>0]
if not rules:raise RuntimeError('Arabic body page labels required after opening pages')
body_start=max(r['startpage'] for r in rules); page_labels={}
for i,page in enumerate(doc,1):
    if i<=body_start:continue
    label=page.get_label()
    if label in page_labels:raise RuntimeError('Ambiguous body page label '+label)
    page_labels[label]=i

def resolved(row):
    r=dict(row); printed=str(r['printed_page']); actual=page_labels[printed]
    recorded=r.get('physical_pdf_page',r.get('physical_page',r.get('page')))
    if recorded is not None and int(recorded)!=actual:raise RuntimeError('Actual PDF location differs for '+r['label'])
    r.update(printed_page=printed,physical_pdf_page=actual,final_label=r['label'])
    return r

old=ast.parse((H/'historical_assembly/navigation.py').read_text())
relations=next(ast.literal_eval(node.value) for node in old.body if isinstance(node,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='relations' for v in node.targets))
core=[]; strengthened=[]; supplements=[]
for row in x['finite_items']:
    core.append({'ledger_number':row['item'],'title':row['title'],'traditional':resolved(row),'guide_ledger_label':'result:'+row['item'],'formal_status':'inherited-complete-scoped-statement'})
for row in x['records']:
    if row['part']!='strong' or not row.get('proof_required'):continue
    r=resolved(row); relation=relations.get(r['label'],'Additional written statement. No corresponding named endpoint in the current 25-module development.')
    strengthened.append({'title':r['title'],'traditional':r,'relation_to_current_formal_source':relation,'formal_status':'written-result-relation-does-not-enlarge-formal-contract'})
if len(core)!=19 or len(strengthened)!=79:raise RuntimeError('Unexpected cross-reading counts')
notes={
'supp1':'Packet algebra, symmetry and measurements. Corrected resolvent, spacing condition, and finite constraint audit.',
'supp2':'Addressed computational seed, tensor refinement, moving coordinates, canonical connection, and Kraus amplification.',
'supp3':'Actual orbit spaces, sharp seed counts, independently defined Schmidt rank, cyclic characters, and Euclidean exponential.',
'supp4':'Actual-exponential leakage, chart projected curvature, and total orthogonal-syndrome recovery.',
'supp5':'General Gram spectral reduction, actual recovery necessity, density/operator bridge, finite references, and error spans.',
'supp6':'Constructed range local products, smooth transitions, global connection, gauge law, and actual manifold curvature.'}
for prefix in notes:
    sections=[resolved(s) for s in x['sections'] if s['part']==prefix]
    supplements.append({'part':prefix,'summary':notes[prefix],'first':sections[0],'last':sections[-1]})
out=[r'\section{Navigation through the traditional paper}'+'\n'+r'\label{sec:traditional-navigation}'+'\n',
     f'The final traditional volume has {len(doc)} physical PDF pages. Printed pages are the labels in that volume. PDF pages count the cover and Roman opening pages as well. Every location below was resolved from the actual body page label and checked against the source map. A shared subject does not imply identical formal coverage.\n\n',
     r'\subsection{All 19 finite items in the traditional core}'+'\n',
     r'\begin{longtable}{@{}p{.10\linewidth}p{.13\linewidth}p{.49\linewidth}rr@{}}\toprule Item & Number & Core statement & Printed & PDF\\\midrule\endhead'+'\n']
for row in core:
    r=row['traditional'];out.append(r'\hyperref[result:'+row['ledger_number']+']{'+row['ledger_number']+'} & '+esc(r['number'])+' & '+esc(row['title'])+' & '+r['printed_page']+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out += [r'\bottomrule\end{longtable}'+'\n',r'\subsection{Strengthened statements and the endpoint boundary}'+'\n',
        'This index includes all 79 proof-bearing named statements in strengthened Part II. A relation identifies shared ingredients or a shared finite result. It does not claim that the whole stronger statement has a dedicated Lean theorem. Entries without a corresponding named endpoint remain written mathematical statements. They do not enlarge the 19-item ledger or the 323-declaration inventory.\n\n',
        r'{\small\begin{longtable}{@{}p{.13\linewidth}p{.31\linewidth}p{.42\linewidth}r@{}}\toprule Number; printed & Strengthened statement & Relation to the current formal source & PDF\\\midrule\endhead'+'\n']
for row in strengthened:
    r=row['traditional'];title=re.sub(r'\\\((.*?)\\\)',r'\1',r['title'])
    out.append(esc(r['number'])+'; '+r['printed_page']+' & '+esc(title)+' & '+esc(row['relation_to_current_formal_source'])+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out += [r'\bottomrule\end{longtable}}'+'\n',r'\subsection{Retained supplements explain the constructed proofs}'+'\n',
        'Part III retains the mathematical portions of all six formal supplements. Read their historical descriptions in order: later constructions strengthen earlier restricted coverage. The source-bound endpoint map records the current result.\n\n',
        r'{\small\begin{longtable}{@{}p{.14\linewidth}p{.51\linewidth}p{.14\linewidth}p{.12\linewidth}@{}}\toprule Sections & Retained proof material & Printed & PDF\\\midrule\endhead'+'\n']
for row in supplements:
    first,last=row['first'],row['last'];nums=first['number']+'–'+last['number'];pages=first['printed_page']+'–'+last['printed_page'];physical=str(first['physical_pdf_page'])+'–'+str(last['physical_pdf_page'])
    out.append(esc(nums)+' & '+esc(row['summary'])+' & '+esc(pages)+' & '+esc(physical)+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}}'+'\n')
(G/'traditional_navigation.tex').write_text(''.join(out),encoding='utf-8')
provenance={p.relative_to(T).as_posix():sha(p) for p in [map_path,T/'Paper_VII_Traditional_Final.tex']}
for name in ('canonical_label_to_final.json','manuscript_record_to_final.json','SOURCE_RECORDS.json','current_source_records.json','EDITION_RECONCILIATION.json','evidence/ASSEMBLY_MANIFEST.json','evidence/PROOF_BODY_PRESERVATION.json'):
    if (T/name).exists():provenance[name]=sha(T/name)
provenance.update(traditional_pdf_filename=PDF.name,traditional_pdf_sha256=sha(PDF),traditional_pdf_pages=len(doc),physical_location_method='actual unique Arabic body page labels, checked against final source map',arabic_body_first_physical_page=body_start+1)
cross={'core':core,'strengthened':strengthened,'retained_earlier':[],'migration':[],'supplements':supplements,'provenance':provenance}
(G/'traditional_crosswalk.json').write_text(json.dumps(cross,indent=2,ensure_ascii=False)+'\n')
(G/'traditional_page_map.json').write_bytes(map_path.read_bytes())
(G/'traditional_navigation_provenance.json').write_text(json.dumps({'traditional_pdf_sha256':sha(PDF),'traditional_pdf_pages':len(doc),'page_map_sha256':sha(map_path),'finite_items':19,'strong_proof_statements':79,'crosswalk_sha256':sha(G/'traditional_crosswalk.json'),'scope':'actual printed and physical cross-reading navigation. No enlargement of formal coverage.'},indent=2)+'\n')
print(json.dumps({'core':19,'strengthened':79,'supplement_groups':6,'traditional_pdf_pages':len(doc),'traditional_pdf_sha256':sha(PDF)}))
