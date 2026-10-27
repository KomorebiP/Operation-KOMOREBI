from pathlib import Path
import re,json,hashlib,collections
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222');ED=ROOT/'editorial/prose_review';BACK=ED/'xi_xii_before'
parent=json.loads((ED/'xi_xii_parent_journal.json').read_text());child=json.loads((ED/'xi_traditional_exact_journal.json').read_text());journal=parent+child
for e in parent:e['source_journal']='xi_xii_parent_journal.json'
for e in child:e['source_journal']='xi_traditional_exact_journal.json'
(ED/'xi_xii_journal.json').write_text(json.dumps(journal,indent=2)+'\n')
math=re.compile(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath|math|eqnarray\*?)\}.*?\\end\{\1\}|(?<!\\)\\\[.*?(?<!\\)\\\]|\\\(.*?\\\)|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$',re.S)
literals=re.compile(r'\\begin\{(Verbatim|verbatim|lstlisting|minted|alltt|quote)\}.*?\\end\{\1\}',re.S)
refs=re.compile(r'\\(?:label|ref|eqref|cref|Cref|pageref|cite|citep|citet|input|include|includegraphics|bibliography|bibliographystyle)(?:\[[^\]]*\])?\{[^}]*\}')
macro=re.compile(r'\\(?:code|leanname|path|url|nolinkurl|texttt|module|href|hyperlink|hypertarget|VerbatimInput|excerpt|plate)\b')
def args(s):
 out=[]
 for m in macro.finditer(s):
  pos=m.end()
  while pos<len(s) and s[pos].isspace():pos+=1
  if pos<len(s) and s[pos]=='[':
   end=s.find(']',pos);pos=end+1 if end!=-1 else pos
  while pos<len(s) and s[pos].isspace():pos+=1
  if pos>=len(s) or s[pos]!='{':continue
  depth=0;end=pos
  while end<len(s):
   c=s[end]
   if c in '{}':
    n=0;k=end-1
    while k>=0 and s[k]=='\\':n+=1;k-=1
    if n%2==0:
     depth+=1 if c=='{' else -1
     if depth==0:end+=1;break
   end+=1
  out.append(s[m.start():end])
 return out
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
rows=[];group=collections.defaultdict(list)
for e in journal:group[e['file']].append(e)
for f,es in sorted(group.items()):
 a=(BACK/f).read_text();b=(ROOT/f).read_text();s=a
 for e in es:
  assert e['old'] in s,(f,e['old']);s=s.replace(e['old'],e['new'],e.get('occurrences',1))
 assert s==b,('journal replay',f)
 data={
  'math':[m.group(0) for m in math.finditer(a)],
  'literal_code_paths_and_quotes':[m.group(0) for m in literals.finditer(a)]+args(a),
  'labels_references_citations_inputs_graphics':refs.findall(a),
  'environment_sequence':re.findall(r'\\(?:begin|end)\{[^}]+\}',a),
  'numeric_tokens':re.findall(r'\d+',a)}
 later={
  'math':[m.group(0) for m in math.finditer(b)],
  'literal_code_paths_and_quotes':[m.group(0) for m in literals.finditer(b)]+args(b),
  'labels_references_citations_inputs_graphics':refs.findall(b),
  'environment_sequence':re.findall(r'\\(?:begin|end)\{[^}]+\}',b),
  'numeric_tokens':re.findall(r'\d+',b)}
 checks={k:{'count_before':len(v),'count_after':len(later[k]),'before_sha256':sha(json.dumps(v)),'after_sha256':sha(json.dumps(later[k])),'identical':v==later[k]} for k,v in data.items()}
 
 if not all(v['identical'] for v in checks.values()):
  print('DIFFERENCE',f,[k for k,v in checks.items() if not v['identical']])
  for k,v in data.items():
   if v!=later[k]:
    for av,bv in zip(v,later[k]):
     if av!=bv:print(k,repr(av[:400]),repr(bv[:400]));break
  assert all(v['identical'] for v in checks.values()),f
 if '/XII/' in f:
  pat=re.compile(r'\\begin\{(theorem|definition|proposition|corollary|lemma|standardfact)\}.*?\\end\{\1\}',re.S)
  va=[m.group(0) for m in pat.finditer(a)];vb=[m.group(0) for m in pat.finditer(b)]
  checks['xii_statement_and_hypothesis_environments']={'count_before':len(va),'count_after':len(vb),'before_sha256':sha(json.dumps(va)),'after_sha256':sha(json.dumps(vb)),'identical':va==vb};assert va==vb,f
 rows.append({'file':f,'before_sha256':sha(a),'after_sha256':sha(b),'checks':checks,'journal_replay_exact':True})
# Guard the open endpoint's actual statements in the parent's two edited readers.
conj=[]
for f,marker in [('source_ix_xii/XI/publication/source/visual_guide/Paper_XI_Visual_Guide_Final.tex','\\textbf{Conjecture 66 (arithmetic packet realization).}'),('source_ix_xii/XI/publication/source/lean_guide/Paper_XI_Lean_Guide_Final.tex','Fix the declared class \\(\\mathcal A\\) of wild atoms')]:
 a=(BACK/f).read_text();b=(ROOT/f).read_text()
 def paragraph(s):
  start=s.index(marker);end=s.find('\n\n',start);return s[start:end]
 av=paragraph(a);bv=paragraph(b);assert av==bv,f
 conj.append({'file':f,'statement_paragraph_identical':True,'sha256':sha(av)})
(ED/'xi_xii_preservation.json').write_text(json.dumps({'status':'PASS','changed_file_count':len(rows),'files':rows,'xi_parent_conjecture_66_statement_checks':conj,'xi_traditional_conjecture_check':'PASS in xi_traditional_preservation_check.json; full conjecture environment byte-identical.','no_build_or_formal_execution':True},indent=2)+'\n')
# Ranges read are reported separately from exact catalog/literal material excluded from copyediting.
scope=[
 ('source_ix_xii/XI/publication/source/visual_guide/Paper_XI_Visual_Guide_Final.tex',None),
 ('source_ix_xii/XI/publication/source/visual_guide/reader_route.tex',None),
 ('source_ix_xii/XI/publication/source/lean_guide/Paper_XI_Lean_Guide_Final.tex',[(1,543),(14434,14435)]),
 ('source_ix_xii/XI/publication/source/lean_guide/current_verification.tex',None),
 ('source_ix_xii/XI/publication/source/lean_guide/reader_route.tex',None),
 ('source_ix_xii/XII/publication/source/traditional/Paper_XII_Traditional_Final.tex',[(159,1846)]),
 ('source_ix_xii/XII/publication/source/traditional/reading_route.tex',None),
 ('source_ix_xii/XII/publication/source/visual_guide/Paper_XII_Visual_Guide_Final.tex',None),
 ('source_ix_xii/XII/publication/source/visual_guide/source/pages.tex',None),
 ('source_ix_xii/XII/publication/source/lean_guide/Paper_XII_Lean_Guide_Final.tex',None),
 ('source_ix_xii/XII/publication/source/lean_guide/reading_route.tex',None)]
coverage=[]
for f,ranges in scope:
 s=(BACK/f).read_text() if (BACK/f).exists() else (ROOT/f).read_text();lines=s.splitlines()
 actual=ranges or [(1,len(lines))];selected='\n'.join('\n'.join(lines[a-1:b]) for a,b in actual)
 coverage.append({'file':f,'source_ranges_read':actual,'raw_tex_whitespace_tokens_in_ranges':len(selected.split()),'review':'Continuous nonliteral reader prose read in context, including adjacent display integration and captions; math/literal bodies preserved and not audited. Exact generated catalogs and appendix tables excluded.'})
(ED/'xi_xii_parent_coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
cr=json.loads((ED/'xi_traditional_subreport.json').read_text())
report={'status':'SEALED','scope':'Six canonical editable XI/XII core reader components. XI traditional and active appendices delegated to existing IV child; XI visual/formal and all XII read by parent. Preserved XI research PDFs excluded.','authority':['component_builds.json','source_ix_xii/rebuild_xi_xii.py','source_ix_xii/XI/tools/build_readers.py','source_ix_xii/XII/tools/build_readers.py'],'canonical_roots':['source_ix_xii/XI/publication/source','source_ix_xii/XII/publication/source'],'changed_files':sorted(group),'changed_file_count':len(group),'journal':'editorial/prose_review/xi_xii_journal.json','journal_entry_count':len(journal),'parent_journal_entries':len(parent),'xi_traditional_journal_entries':len(child),'preservation':'editorial/prose_review/xi_xii_preservation.json','parent_coverage':'editorial/prose_review/xi_xii_parent_coverage.json','parent_prose_source_files_read':len(coverage),'parent_raw_tex_whitespace_tokens_in_read_ranges':sum(x['raw_tex_whitespace_tokens_in_ranges'] for x in coverage),'word_count_limit':'Parent counts are exact whitespace-separated source tokens in stated ranges, including LaTeX/inline math/metadata; not a prose-only word count. Child uses separately documented estimated lexical prose words. These are not added as if they were one metric.','xi_traditional_report':'editorial/prose_review/xi_traditional_subreport.json','xi_traditional_estimated_prose_words':sum(x.get('estimated_prose_words',0) for x in cr['coverage']),'first_pass':'Read authored nonliteral prose continuously through active entry points and inputs, with neighboring formulas, theorem hypotheses, formal scope, captions and navigation. Literal proof excerpts, generated declaration catalog content, figure code and bibliography records excluded from copyediting.','second_pass':'Reread every changed passage in contextual diffs; checked Chapter/formal-companion terminology, captions, display sentences, US spelling, quotations, stable plate identifiers, and protected endpoint/scope text. Child separately completed its contextual second pass over main/15 appendices and 16 captions.','mathematical_token_changes':[],'xii_hypotheses':'PASS: all theorem/definition/proposition/corollary/lemma/standard-fact environments in edited XII entry are byte-identical. Explicit continuity, topology, local-map, finite occupancy, frame, compatible-point and degree-range hypotheses retained.','conjecture_66':'PASS: full traditional conjecture environment and visual/formal statement paragraphs byte-identical; open status and conditional H5 boundary retained.','unresolved_substantive_issues':cr.get('unresolved_issues',cr.get('suspected_substantive_issues',[])),'layout_watch':'XII visual Plate18 first-column labels now use XII.n under an explicit Plate heading, including ranges XII.6--XII.7, XII.12--XII.13, XII.15--XII.16. Check widths during coordinated rebuild. No layout dimensions changed.','historical_exceptions':'Exact quoted historical summary, namespace/project identifiers, original titles/filenames, and Conjecture66 normalization wording remain unchanged.','build':'Not run; coordinated by root after sealing. No PDFs, builders or root map edited.'}
# Preserve the child's flagged substantive item under its actual field name.
report['xi_traditional_findings']= {k:v for k,v in cr.items() if 'unresolved' in k or 'substant' in k or 'issue' in k}
(ED/'xi_xii_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','changed_file_count','journal_entry_count','parent_raw_tex_whitespace_tokens_in_read_ranges','xi_traditional_estimated_prose_words']}))
