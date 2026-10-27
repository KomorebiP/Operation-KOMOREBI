#!/usr/bin/env python3
"""Preserve the original worked layer and attach final locators and Part II examples."""
from pathlib import Path
import argparse,json,hashlib,re
ROOT=Path(__file__).resolve().parent
ANCHORS={
1:['core:section:01','core:section:06','core:section:11','core:section:13'],
2:['tab:notation','sec:formalization'],3:['result:02','result:03'],4:['result:04'],5:['result:05'],6:['result:06'],7:['result:06'],8:['result:07'],9:['result:08'],10:['result:09'],11:['core:section:10'],12:['core:record:22','result:13'],13:['result:14','result:15'],14:['result:14','result:16'],15:['result:10','result:11'],16:['core:section:06','core:section:08'],17:['result:12'],18:['result:12'],19:['core:section:07','core:section:09'],20:['result:17'],21:['core:section:12'],22:['result:18'],23:['result:18','result:19'],24:['result:20'],25:['core:section:14'],26:['sec:formalization','extension:section:15'],
27:['sec:formalization','extension:section:01','extension:section:15'],28:['thm:lattice_polyphase','thm:lattice_refinement','rem:infinity_boundary'],29:['thm:imperfect_reconstruction','thm:frame_perturbation','cor:canonical_noise'],30:['prop:nonunitary_tree_bounds'],31:['thm:higher_order_packet_decomposition','cor:trace_packet_uniqueness'],32:['thm:estimated_packet_reconstruction'],33:['thm:scalar_region_formula','thm:overlap_matrix'],34:['cor:step_location_error','thm:higher_order_location','thm:geometric_packet_bound'],35:['lem:contrast_gap','thm:deterministic_jump_recovery','ex:jump_threshold_certificate'],36:['thm:probability_recovery','cor:repeated_measurements','cor:probability_consistency'],37:['thm:smooth_haar_bound','thm:haar_step_coefficient','cor:haar_scale_separation'],38:['thm:half_shift_guarantee','cor:two_grid_haar_detection'],39:['thm:polynomial_annihilation','prop:difference_noise','cor:robust_breakpoint_bands'],40:['thm:uniform_packet_convergence','thm:estimated_packet_gibbs']}
REPLACEMENTS=[
('This appendix keeps one concrete object in view','This guide keeps one concrete object in view'),
('throughout this appendix.','throughout this guide.'),
('The new example checks all','The supplied suite checks all'),
('The new checks compare every','The supplied suite compares every'),
('In a probabilistic use, the node bounds must hold on one joint event; separate nodewise probabilities do not automatically give its probability.','For ordinary probability, the random node costs and the joint good event must be measurable. Separate nodewise probability bounds do not automatically give the probability of that joint event.'),
('What is established in this appendix','What is established in the original worked layer'),
('No new Lean run is claimed for this appendix.','No fresh Lean run is claimed for this edition. The additional Part II developments remain outside this twenty-result map.'),
('\\textbf{Exact examples.} The new Python suite performs $181$ checks using rational, algebraic, symbolic, and exhaustive finite computations. Seven deliberately false assertions are rejected.','\\textbf{Inherited exact examples.} The saved visual-suite report records $181$ rational, algebraic, symbolic, and exhaustive finite checks. Seven deliberately false assertions were rejected in that run. The SymPy-dependent suite was not rerun in this edition.'),
('\\textbf{Reproducibility.} The source package retains the original manuscript, figures, Python companion, Lean sources, maps, and historical audits unchanged. The new appendix has editable LaTeX, generated TikZ plates, exact models, and isolated rebuild commands. Open \\texttt{START\\_HERE.md}; the root runner verifies file hashes or reruns examples without invoking Lean.',
'\\textbf{Current executions.} The fresh source-release checker passed 20 exact tests containing 305,933 assertions and passed 16 verifier tests, including positive and negative controls. The expanded-source numerical audit passed 11,052 finite checks, mixing exact and numerical calculations. The new extension examples separately passed 38 grouped exact checks and four false controls. These counts measure different operations and are not combined as theorem counts.\\par\n\\textbf{Reproducibility.} The package preserves the original sources and their reports. Run \\texttt{python build.py} here for an isolated PDF build. The new finite checker is \\texttt{checks/verify\\_extension\\_examples.py}; its contract and raw execution manifest are included. The original visual checker requires the listed optional dependencies. PDF assembly does not run Lean or either mathematical checker.'),
("The paper's two edge-recovery problems are not resolved by these examples.","The core's broad edge-recovery problems are not resolved by these finite examples. V--27 introduces the additional separated-jump recovery results and their explicit hypotheses.")]
PAT=r'^\\vpage\{(\d+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}$'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def from_aux(p):
 text=p.read_text();m={}
 for key,num,page,title,anchor in re.findall(r'^\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{([^}]+)\}\{(.*?)\}\{([^}]+)\}\{\}\}',text,re.M):
  if key.endswith('@cref'):continue
  kind={'thm':'theorem','cor':'corollary','lem':'lemma','prop':'proposition','ex':'example','rem':'remark','def':'definition','sec':'section','tab':'table','fig':'figure'}.get(key.split(':')[0],'section' if ':section:' in key else 'statement')
  cm=re.search(r'\\newlabel\{'+re.escape(key)+r'@cref\}\{\{\[([^\]]+)\]',text)
  if cm:kind=cm.group(1)
  if key=='core:record:22':kind='definition'
  if kind=='appendix':kind='section'
  m[key]={'kind':kind,'number':num,'page':int(page),'title':title,'anchor':anchor}
 return m
ap=argparse.ArgumentParser();ap.add_argument('--traditional-aux',type=Path,required=True);ap.add_argument('--traditional-tex',type=Path,required=True);ap.add_argument('--traditional-map',type=Path,required=True);args=ap.parse_args()
original=(ROOT/'source/pages.tex').read_text();core=original
changes=[]
for old,new in REPLACEMENTS:
 assert core.count(old)==1,old
 core=core.replace(old,new);changes.append({'old':old,'new':new})
ext=(ROOT/'source/extensions.tex').read_text()
body=core+'\n'+ext
mapping=from_aux(args.traditional_aux)
canonical=json.loads(args.traditional_map.read_text())
for key in set(k for row in ANCHORS.values() for k in row):
 if key in canonical:
  assert str(mapping[key]['number'])==str(canonical[key]['number']),(key,'number mismatch')
  assert mapping[key]['page']==int(canonical[key]['page']),(key,'page mismatch')
original_headers={int(n):s for n,_,_,s in re.findall(PAT,original,re.M)}
rows=[]
for n,title,kicker,oldsource in re.findall(PAT,body,re.M):
 i=int(n);items=[];locators=[]
 for key in ANCHORS[i]:
  entry=mapping[key];locators.append(f"{entry['kind'].capitalize()} {entry['number']} (p. {entry['page']})");items.append({'canonical_label':key,'final':entry})
 loc='Final traditional paper: '+'; '.join(locators)+'.'
 old=f'\\vpage{{{n}}}{{{title}}}{{{kicker}}}{{{oldsource}}}';new=f'\\vpage{{{n}}}{{{title}}}{{{kicker}}}{{{loc}}}'
 assert body.count(old)==1;body=body.replace(old,new)
 rows.append({'visual_page':i,'part':'core worked layer'if i<=26 else'extended developments','printed_page':i+2,'physical_pdf_page':i+3,'title_tex':title,'original_locator':original_headers.get(i),'final_locator':loc,'anchors':items})
assert len(rows)==40
(ROOT/'source/pages_final.tex').write_text(body)
(ROOT/'VISUAL_CROSSWALK.json').write_text(json.dumps({'edition':'Paper V final visual guide','worked_pages':rows,'traditional_source_sha256':sha(args.traditional_tex),'traditional_aux_sha256':sha(args.traditional_aux),'traditional_map_sha256':sha(args.traditional_map)},indent=2)+'\n')
checks={}
for name,pattern in [('display_math',r'\\\[(.*?)\\\]'),('inline_math',r'(?<!\\)\$(.*?)(?<!\\)\$'),('figure_calls',r'\\vfig(?:\[[^\]]*\])?\{([^}]+)\}')]:
 a=re.findall(pattern,original,re.S);b=re.findall(pattern,core,re.S)
 checks[name]={'original_count':len(a),'final_core_count':len(b),'unchanged':a==b};assert a==b,(name,len(a),len(b))
(ROOT/'MATHEMATICS_PRESERVATION.json').write_text(json.dumps({'scope':'Original V1--V26 mathematical expressions and figure calls only; new extension content reported separately.','original_worked_layer':checks,'new_extension_display_math':len(re.findall(r'\\\[(.*?)\\\]',ext,re.S)),'new_extension_inline_math':len(re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$',ext,re.S)),'new_extension_figure_calls':len(re.findall(r'\\vfig',ext))+len(re.findall(r'\\includegraphics',ext))},indent=2)+'\n')
(ROOT/'EDITORIAL_CHANGES.json').write_text(json.dumps({'original_core_preserved':'source/pages.tex','prose_replacements':changes,'front_matter':'New cover and separate reading routes for core and extended developments.','extension':'Fourteen new worked pages with twelve exact-coordinate TikZ plates and one preserved expanded-source vector figure.','existing_worked_formula_token_changes':[],'mathematical_prose_hypothesis_clarifications':['V14 ordinary probability now explicitly requires measurable random node costs and joint good event, aligned with final traditional audit.'],'source_locators':'All forty worked headers use final traditional statement or section identifiers and printed pages.'},indent=2)+'\n')
print(json.dumps({'worked_pages':len(rows),'locators':sum(len(r['anchors'])for r in rows),'core_math_preserved':checks}))
