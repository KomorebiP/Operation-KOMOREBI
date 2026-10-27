#!/usr/bin/env python3
"""Apply recorded prose/reference changes to the preserved Paper IV visual pages."""
from pathlib import Path
import argparse,hashlib,json,re
ROOT=Path(__file__).resolve().parent
ANCHORS={
1:['sec:map','sec:reciprocal_powers','sec:zero_geometry','sec:hadamard'],
2:['sec:map','def:reduced_denominator','def:reciprocal_family','def:normalized_section'],
3:['thm:root_filter','prop:covariance'],
4:['thm:cyclic_product'],
5:['thm:signed_cycle','thm:companion_matrix_realization','cor:fundamental_matrix_entries','cor:companion_addition_inversion'],
6:['prop:signed_addition','thm:finite_algebra_exponentials'],
7:['thm:hypergeometric_form'],
8:['def:reduced_denominator','ex:fourth_order_zeros','cor:reduced_zeros'],
9:['thm:parameter_recurrence','thm:logarithmic_newton_recurrence'],
10:['thm:reciprocal_bell','cor:first_reciprocal_polynomials'],
11:['thm:parameter_recurrence','thm:reciprocal_parameter_addition','thm:logarithmic_newton_recurrence'],
12:['prop:tangent_kappa','cor:reciprocal_derivative','thm:higher_riccati'],
13:['sec:map','def:reciprocal_family','cor:reciprocal_derivative'],
14:['def:normalized_section','thm:triangular_inverse','ex:euler_boundaries'],
15:['thm:appell_laws','thm:appell_two_parameter_convolution','prop:appell_operator_form'],
16:['thm:theta_reconstruction','prop:theta_factors','prop:theta_newton_recurrence'],
17:['def:indicator_polygon','thm:indicator_polygon'],
18:['lem:two_term_dominance','thm:large_zero_strings','cor:N3_zero_correction'],
19:['thm:large_zero_strings','thm:first_zero_correction','cor:N3_zero_correction'],
20:['ex:fourth_order_zeros','thm:zero_counting'],
21:['thm:genus_zero_product','thm:trace_class_model'],
22:['thm:newton_sums','cor:mittag_leffler_tangent','cor:tangent_zero_sums','cor:reciprocal_zero_data'],
23:['thm:nearest_circle_expansion','cor:leading_dominant_zero','cor:orbit_reduced_asymptotic','cor:secant_asymptotic'],
24:['thm:zeta_convergence','thm:zeta_continuation','cor:exact_zeta_models'],
25:['cor:first_reciprocal_polynomials','ex:fourth_order_zeros','thm:newton_sums'],
26:['sec:further_questions','sec:formalization_ledger']}
REPLACEMENTS=[
('This appendix follows a concrete analytic family','This guide follows a concrete analytic family'),
('Three routes through the appendix','Three routes through the guide'),
('The original proofread manuscript remains unchanged.','The source package preserves the original proofread manuscript.')]
V26=r'''\vpage{26}{What is evidence, and for what?}{FORMAL AND COMPUTATIONAL BOUNDARIES}{SOURCE_LINE}
This guide accompanies the final traditional edition and the Lean guide. Its twenty-six worked pages preserve the mathematical models of the original visual appendix. Final references and evidence descriptions connect those models to the present edition.

{\small
\begin{tabularx}{\linewidth}{@{}p{.24\linewidth}Y@{}}\toprule
\textbf{Evidence layer} & \textbf{What it supports}\\\midrule
Inherited formal record & The v1.0.0 sources, theorem map, dependency pins, saved axiom reports, and original review retain their own scope. The release reports a 68-result contract. No fresh Lean compilation is claimed here.\\
Exact and symbolic suite & EXACT_TEXT\\
Certified zero brackets & Four rational intervals of width $10^{-20}$ establish local existence and uniqueness only. BRACKET_TEXT\\
Numerical visualization & Sampled analytic curves, finite products, moment shares, and displacement diagnostics have the roles stated on their pages. They are not exact global zero censuses.\\
Figure provenance & FIGURE_TEXT\\
Editorial preservation & The original worked formulas, model code, checker, and vector figure sources are preserved. Updated locators refer to the final traditional edition.\\\bottomrule
\end{tabularx}}

\head{Boundaries that remain in force}
The general family has eventual positivity and simplicity of its reduced zeros, not an assertion that every reduced zero is positive and simple. The paper leaves universal simplicity, positivity of every reduced zero, full displacement expansions, and a zeta functional equation open. The exact order-two and order-four models do not settle those questions for every order.
Imported standard fact 11.1 stays outside the 68-result contract. Fixed logarithms, zero-free domains, multiplicities, and the hypotheses of nearest-pole asymptotics remain explicit. No historical priority is inferred from successful computation or formal verification.

\head{Replay the worked layer}
Run \texttt{python build.py} in this editable guide folder to compile the PDF in an isolated temporary directory. The separate model checker is \texttt{checks/verify\_examples.py}; the plate generator is \texttt{source/generate\_graphics.py}. They require the listed Python dependencies. Run those mathematical tools in a temporary copy to preserve the delivered evidence.

\takeaway{A proof, a finite exact test, a root enclosure, and a sampled curve answer different questions. Keeping their scopes explicit makes the pictures useful mathematical evidence.}
\captiontext{The source package preserves the formal release, proofread review, independent audit, exact certificates, and rebuild instructions. PDF assembly is a separate operation from mathematical verification.}
'''
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--traditional-map',type=Path,required=True)
 ap.add_argument('--traditional-tex',type=Path,required=True)
 ap.add_argument('--evidence',type=Path,required=True)
 args=ap.parse_args()
 original=(ROOT/'source/pages.tex').read_text()
 body=original
 changes=[]
 for old,new in REPLACEMENTS:
  assert body.count(old)==1,old
  body=body.replace(old,new);changes.append({'old':old,'new':new})
 evidence=json.loads(args.evidence.read_text())
 v26=V26.replace('SOURCE_LINE','Final traditional paper: scope and formalization ledger')
 for marker,key in [('EXACT_TEXT','exact_text'),('BRACKET_TEXT','bracket_text'),('FIGURE_TEXT','figure_text')]:
  v26=v26.replace(marker,evidence[key])
 body=body[:body.index(r'\vpage{26}')]+v26
 mapping=json.loads(args.traditional_map.read_text())
 if 'labels' in mapping:mapping=mapping['labels']
 headerpattern=r'^\\vpage\{(\d+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}$'
 originals={int(n):{'title_tex':t,'locator':s} for n,t,_,s in re.findall(headerpattern,original,re.M)}
 crosswalk=[]
 for n,title,kicker,oldsource in re.findall(headerpattern,body,re.M):
  i=int(n);items=[];locators=[]
  for key in ANCHORS[i]:
   entry=mapping[key]
   kind=entry['kind'].capitalize()
   locators.append(f"{kind} {entry['number']} (p. {entry['page']})")
   items.append({'canonical_label':key,'final':entry})
  source='Final traditional paper: '+'; '.join(locators)+'.'
  old=f'\\vpage{{{n}}}{{{title}}}{{{kicker}}}{{{oldsource}}}'
  new=f'\\vpage{{{n}}}{{{title}}}{{{kicker}}}{{{source}}}'
  assert body.count(old)==1
  body=body.replace(old,new)
  crosswalk.append({'visual_page':i,'printed_page':i+1,'physical_pdf_page':i+2,'title_tex':title,'original_locator':originals[i]['locator'],'final_locator':source,'anchors':items})
 assert len(crosswalk)==26
 (ROOT/'source/pages_final.tex').write_text(body)
 (ROOT/'VISUAL_CROSSWALK.json').write_text(json.dumps({'edition':'Paper IV final visual guide','worked_pages':crosswalk,'traditional_source_sha256':digest(args.traditional_tex),'traditional_map_sha256':digest(args.traditional_map)},indent=2)+'\n')
 (ROOT/'EDITORIAL_CHANGES.json').write_text(json.dumps({'preserved_original':'source/pages.tex','unchanged':'All displayed and inline worked mathematical formulas, exact Python model, checker, and 24 TikZ sources.','prose_replacements':changes,'replaced_page_26':'Updated companion context, verification scope, source provenance and replay instructions. Original mathematical boundaries retained.','source_locators':'All 26 page headers now name final traditional statements with printed page numbers.','front_matter':'New cover, contents and reading route.','mathematical_token_changes':[]},indent=2)+'\n')
 checks={}
 for name,pattern in [('display_math',r'\\\[(.*?)\\\]'),('inline_math',r'(?<!\\)\$(.*?)(?<!\\)\$'),('figure_calls',r'\\vfig(?:\[[^\]]*\])?\{([^}]+)\}')]:
  a=re.findall(pattern,original,re.S);b=re.findall(pattern,body,re.S)
  checks[name]={'count':len(a),'unchanged':a==b}
  assert a==b,(name,len(a),len(b))
 (ROOT/'MATHEMATICS_PRESERVATION.json').write_text(json.dumps(checks,indent=2)+'\n')
 print(json.dumps({'worked_pages':len(crosswalk),'locator_occurrences':sum(len(x['anchors']) for x in crosswalk),'mathematics_preserved':checks}))
if __name__=='__main__': main()
