#!/usr/bin/env python3
"""Bind cross-reading tables to the built traditional paper's label/page map."""
from pathlib import Path
import argparse,hashlib,json,re
from data_helpers import esc
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--map',type=Path,default=HERE.parent/'traditional/evidence/FINAL_PAGE_MAP.json');a=ap.parse_args()
x=json.loads(a.map.read_text());g=HERE/'generated'
(g/'traditional_page_map.json').write_text(json.dumps(x,indent=2)+'\n')
relations={
'strong:theorem:001':'Shared orbit-dimension result; item 2.1.',
'strong:theorem:002':'Shared sharp seed-count result; item 2.2.',
'strong:corollary:001':'Shared local-orbit and reduced-support result; item 2.3.',
'strong:proposition:001':'Addressed local-X basis construction; item 2.4.',
'strong:corollary:002':'Cyclic specialization is encoded; item 3.1.',
'strong:theorem:006':'Finite tensor grouping is encoded; item 3.2.',
'strong:theorem:007':'All finite circuit depths are encoded; item 4.1.',
'strong:theorem:008':'Both operator unitarity identities; item 4.2.',
'strong:corollary:005':'Operator identity in item 4.2; state-probability corollary is an additional human statement.',
'strong:theorem:010':'Fixed-generator exponential packet invariance; item 5.1.',
'strong:theorem:011':'Commutator leakage bound in item 5.2; the off-diagonal norm equality is an additional human statement.',
'strong:theorem:012':'Canonical curve connection identities; item 6.3.',
'strong:theorem:014':'Differentiated moving coordinates; item 6.1.',
'strong:theorem:018':'Projected manifold curvature and gauge gluing in item 6.4; local orthonormal-frame formulas are additional human statements.',
'strong:corollary:008':'Block-diagonal trace invariance; item 7.1.',
'strong:standardfact:001':'Finite Kraus CP/TP in item 7.2; the Choi equivalence is an additional human statement.',
'strong:theorem:026':'Unnormalized error-family criterion and span recovery in item 8.1; quotient notation is an additional human formulation.',
'strong:theorem:027':'General positive Gram spectral reduction; item 8.1.',
'strong:theorem:028':'One total recovery and normalized error-span channels; item 8.1.',
'strong:corollary:011':'Syndrome cross-error identities support item 8.1; the measurement interpretation is an additional human statement.',
'strong:theorem:029':'Corrected two-invertibility projected resolvent; item 9.1.',
'strong:theorem:030':'Schur/full invertibility equivalence in item 9.1; spectral and eigenvector formulations extend the endpoint.',
'strong:theorem:036':'Actual shifted exponential, positivity and spectrum in item 10.1; read its exact endpoint.',
'strong:theorem:039':'One-dimensional scalar bound in item 11.1; the d-dimensional summed statement is an additional human result.',
'strong:proposition:011':'Finite common-kernel compression audit is encoded in ConstraintAudit.'}
out=[r'\section{Navigation through the traditional paper}'+'\n'+r'\label{sec:traditional-navigation}'+'\n'+
'The final traditional paper has a core Part I, a broader strengthened Part II, and retained proof supplements in Part III. The tables below use its printed page numbers; physical PDF page indices are different because of the front matter. A shared subject does not by itself imply identical formal coverage. The item links refer to the exact finite-result map in this guide.\n\n'+
r'\subsection{All 19 finite items in the traditional core}'+'\n'+r'\begin{longtable}{@{}p{.10\linewidth}p{.14\linewidth}p{.51\linewidth}p{.17\linewidth}@{}}\toprule Item & Number & Core statement & Printed page\\\midrule\endhead'+'\n']
for r in x['finite_items']:
    title=esc(r['title'].replace('--','–'))
    out.append(r'\hyperref[result:'+r['item']+']{'+r['item']+'} & '+esc(r['number'])+' & '+title+' & '+r['printed_page']+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n'+
r'\subsection{Strengthened statements and the endpoint boundary}'+'\n'+
'This index includes every proof-bearing named statement in strengthened Part II. A relation identifies shared ingredients or a shared finite result, not a claim that the whole stronger statement has a dedicated Lean theorem. Entries with no corresponding named endpoint remain human mathematical statements in the traditional paper. They do not enlarge the 19-item ledger or the 323-declaration inventory. Definitions, examples and remarks can be found through the traditional contents and are not independently classified as theorem endpoints here.\n\n'+
r'\begin{longtable}{@{}p{.13\linewidth}p{.34\linewidth}p{.46\linewidth}@{}}\toprule Number; page & Strengthened statement & Relation to the current formal source\\\midrule\endhead'+'\n')
count=0
for r in x['records']:
    if r['part']!='strong' or not r.get('proof_required'):continue
    title=re.sub(r'\\\((.*?)\\\)',r'\1',r['title'])
    relation=relations.get(r['label'],'Additional human statement; no corresponding named endpoint in the current 25-module development.')
    out.append(esc(r['number'])+'; '+r['printed_page']+' & '+esc(title)+' & '+esc(relation)+r'\\'+'\n');count+=1
out.append(r'\bottomrule\end{longtable}'+'\n'+
r'\subsection{Retained supplements explain the constructed proofs}'+'\n'+
'Part III retains the mathematical portions of all six formal supplements. Their historical wording should be read in order: early restricted coverage is strengthened by later constructions. The source-bound endpoint map records the current result.\n'+
r'\begin{longtable}{@{}p{.17\linewidth}p{.60\linewidth}p{.16\linewidth}@{}}\toprule Sections & Retained proof material & Printed pages\\\midrule\endhead'+'\n')
for prefix in ('supp1','supp2','supp3','supp4','supp5','supp6'):
    ss=[s for s in x['sections']if s['part']==prefix]
    nums=ss[0]['number']+'–'+ss[-1]['number']
    pages=ss[0]['printed_page']+'–'+ss[-1]['printed_page']
    summaries={'supp1':'Packet algebra, symmetry and measurements; corrected resolvent; spacing condition; finite constraint audit.',
    'supp2':'Addressed computational seed, tensor refinement, moving coordinates, canonical connection and Kraus amplification.',
    'supp3':'Actual orbit spaces, sharp seed counts, independently defined Schmidt rank, cyclic characters and Euclidean exponential.',
    'supp4':'Actual-exponential leakage, chart projected curvature and total orthogonal-syndrome recovery.',
    'supp5':'General Gram spectral reduction, actual recovery necessity, density/operator bridge, finite references and error spans.',
    'supp6':'Constructed range local products, smooth transitions, global connection, gauge law and actual manifold curvature.'}
    out.append(esc(nums)+' & '+esc(summaries[prefix])+' & '+esc(pages)+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n')
(g/'traditional_navigation.tex').write_text(''.join(out))
(g/'traditional_navigation_provenance.json').write_text(json.dumps({'traditional_pdf_sha256':x['pdf_sha256'],'traditional_pdf_pages':x['pdf_pages'],'page_map_sha256':hashlib.sha256(a.map.read_bytes()).hexdigest(),'finite_items':len(x['finite_items']),'strong_proof_statements':count,'scope':'source-derived cross-reading navigation; no enlargement of formal coverage'},indent=2)+'\n')
print(json.dumps({'finite_items':len(x['finite_items']),'strengthened_statements':count,'traditional_pdf_sha256':x['pdf_sha256']}))
