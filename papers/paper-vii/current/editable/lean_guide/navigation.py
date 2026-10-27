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
# Preserve the historical map while expressing the current navigation in prose.
reviewed_relations={
    'strong:theorem:001':'Item 2.1 gives the same orbit dimension result.',
    'strong:theorem:002':'Item 2.2 gives the same sharp minimum number of seeds.',
    'strong:corollary:001':'Item 2.3 relates the local orbit to reduced support.',
    'strong:proposition:001':'Item 2.4 constructs the basis by addressed local X gates.',
    'strong:corollary:002':'Item 3.1 formalizes the cyclic specialization.',
    'strong:theorem:006':'Item 3.2 formalizes finite grouping of tensor packets.',
    'strong:theorem:007':'Item 4.1 covers every finite circuit depth.',
    'strong:theorem:008':'Item 4.2 gives both operator unitarity identities.',
    'strong:corollary:005':'Item 4.2 gives the operator identity. The probability corollary is proved in the traditional text.',
    'strong:theorem:010':'Item 5.1 proves packet invariance for the exponential of a fixed generator.',
    'strong:theorem:011':'Item 5.2 gives the commutator leakage bound. The norm equality for the off-diagonal corner is proved in the traditional text.',
    'strong:theorem:012':'Item 6.3 gives the canonical connection identities along a curve.',
    'strong:theorem:014':'Item 6.1 proves the differentiated equation in moving coordinates.',
    'strong:theorem:018':'Item 6.4 gives projected manifold curvature and gauge gluing. The local formulas in orthonormal frames are proved in the traditional text.',
    'strong:corollary:008':'Item 7.1 proves trace invariance for block diagonal observables.',
    'strong:standardfact:001':'Item 7.2 proves complete positivity and trace preservation for finite Kraus channels. The Choi equivalence is proved in the traditional text.',
    'strong:theorem:026':'Item 8.1 gives the criterion for unnormalized error families and recovery on their span. The traditional text also uses a quotient formulation.',
    'strong:theorem:027':'Item 8.1 reduces general positive Gram data by spectral diagonalization.',
    'strong:theorem:028':'Item 8.1 uses one total recovery for normalized channels in the error span.',
    'strong:corollary:011':'The identities for syndrome cross errors support item 8.1. The traditional text supplies the measurement interpretation.',
    'strong:theorem:029':'Item 9.1 gives the projected resolvent with both required invertibility hypotheses.',
    'strong:theorem:030':'Item 9.1 relates invertibility of the full matrix and its Schur complement. The traditional text adds spectral and eigenvector formulations.',
    'strong:theorem:036':'Item 10.1 constructs the shifted exponential and proves its positivity and spectral bounds under the stated hypotheses.',
    'strong:theorem:039':'Item 11.1 gives the scalar bound in one dimension. The traditional text proves the summed result in d dimensions.',
    'strong:proposition:011':'ConstraintAudit formalizes finite compression to the common kernel.'}
if set(reviewed_relations)!=set(relations):
    raise RuntimeError('Historical relation inventory changed')
relations=reviewed_relations
core=[]; strengthened=[]; supplements=[]
for row in x['finite_items']:
    core.append({'ledger_number':row['item'],'title':row['title'],'traditional':resolved(row),'guide_ledger_label':'result:'+row['item'],'formal_status':'inherited-complete-scoped-statement'})
for row in x['records']:
    if row['part']!='strong' or not row.get('proof_required'):continue
    r=resolved(row); relation=relations.get(r['label'],'The traditional statement has no corresponding named endpoint among the current 25 modules.')
    strengthened.append({'title':r['title'],'traditional':r,'relation_to_current_formal_source':relation,'formal_status':'written-result-relation-does-not-enlarge-formal-contract'})
if len(core)!=19 or len(strengthened)!=79:raise RuntimeError('Unexpected cross-reading counts')
notes={
'supp1':'This supplement develops packet algebra, symmetry and measurements. It states the corrected resolvent and spacing hypotheses and audits finite constraints.',
'supp2':'This supplement constructs an addressed computational seed, tensor refinements, moving coordinates, the canonical connection and Kraus amplification.',
'supp3':'This supplement derives orbit spaces and sharp seed counts. It defines Schmidt rank independently and develops cyclic characters and the Euclidean exponential.',
'supp4':'This supplement proves leakage for the exponential, projected curvature in a chart and total recovery from orthogonal syndromes.',
'supp5':'This supplement proves spectral reduction for general Gram data, necessity from recovery, the bridge from states to operators, and correction with finite references and error spans.',
'supp6':'This supplement constructs local products for the range, smooth transitions and the global connection. It proves the gauge law and manifold curvature formula.'}
for prefix in notes:
    sections=[resolved(s) for s in x['sections'] if s['part']==prefix]
    supplements.append({'part':prefix,'summary':notes[prefix],'first':sections[0],'last':sections[-1]})
out=[r'\section{Navigation through the traditional paper}'+'\n'+r'\label{sec:traditional-navigation}'+'\n',
     f'The final traditional volume has {len(doc)} physical PDF pages. Printed pages are the labels in that volume. PDF pages count the cover and Roman opening pages as well. Every location below was resolved from the actual body page label and checked against the source map. A shared subject does not imply identical formal coverage.\n\n',
     r'\subsection{All 19 finite items in the traditional core}'+'\n',
     r'\begin{longtable}{@{}p{.10\linewidth}p{.13\linewidth}p{.49\linewidth}rr@{}}\toprule Item & Number & Core statement & Printed & PDF\\\midrule\endhead'+'\n']
for row in core:
    r=row['traditional'];out.append(r'\hyperref[result:'+row['ledger_number']+']{'+row['ledger_number']+'} & '+esc(r['number'])+' & '+esc(row['title'])+' & '+r['printed_page']+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out += [r'\bottomrule\end{longtable}'+'\n',r'\subsection{Strengthened statements and their formal counterparts}'+'\n',
        'This index includes all 79 named statements with proofs in strengthened Part II. A relation identifies shared ingredients or a shared finite result. It does not claim that the whole stronger statement has a dedicated Lean theorem. Entries without a corresponding named endpoint remain written mathematical statements. The formal ledger still contains 19 items, and the declaration inventory still contains 323 entries.\n\n',
        r'{\small\begin{longtable}{@{}p{.13\linewidth}p{.31\linewidth}p{.42\linewidth}r@{}}\toprule Number (page) & Strengthened statement & Relation to the current formal source & PDF\\\midrule\endhead'+'\n']
for row in strengthened:
    r=row['traditional'];title=re.sub(r'\\\((.*?)\\\)',r'\1',r['title'])
    out.append(esc(r['number'])+' ('+r['printed_page']+') & '+esc(title)+' & '+esc(row['relation_to_current_formal_source'])+' & '+str(r['physical_pdf_page'])+r'\\'+'\n')
out += [r'\bottomrule\end{longtable}}'+'\n',r'\subsection{Retained supplements explain the constructed proofs}'+'\n',
        'Part III retains the mathematical portions of all six formal supplements. Read their historical descriptions in order: later constructions strengthen earlier restricted coverage. The endpoint map ties each current result to its source.\n\n',
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
