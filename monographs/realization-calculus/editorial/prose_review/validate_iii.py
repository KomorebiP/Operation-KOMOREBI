from pathlib import Path
import json,re,hashlib,difflib
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
ED=ROOT/'editorial/prose_review'
j=json.loads((ED/'iii_journal.json').read_text())
changed=sorted({x['file'] for x in j})
math_re=re.compile(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath|math|eqnarray\*?)\}.*?\\end\{\1\}|\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$',re.S)
lit_re=re.compile(r'\\begin\{(Verbatim|verbatim|lstlisting|minted|alltt)\}.*?\\end\{\1\}',re.S)
refs_re=re.compile(r'\\(?:label|ref|eqref|cref|Cref|pageref|cite|citep|citet|input|include|includegraphics|bibliography|bibliographystyle)(?:\[[^\]]*\])?\{[^}]*\}')
macro_re=re.compile(r'\\(?:code|leanname|path|url|nolinkurl|texttt|href|hyperlink|hypertarget|VerbatimInput)\b')
def args(s):
 out=[]
 for m in macro_re.finditer(s):
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
rows=[]
for f in changed:
 old=(ED/'iii_iv_before'/f).read_text();new=(ROOT/f).read_text()
 math_old=[m.group(0) for m in math_re.finditer(old)];math_new=[m.group(0) for m in math_re.finditer(new)]
 literal_old=[m.group(0) for m in lit_re.finditer(old)]+args(old);literal_new=[m.group(0) for m in lit_re.finditer(new)]+args(new)
 refs_old=refs_re.findall(old);refs_new=refs_re.findall(new)
 env_old=re.findall(r'\\(?:begin|end)\{[^}]+\}',old);env_new=re.findall(r'\\(?:begin|end)\{[^}]+\}',new)
 rows.append({'file':f,'before_sha256':sha(old),'after_sha256':sha(new),'math_regions':len(math_old),'math_before_sha256':sha(json.dumps(math_old)),'math_after_sha256':sha(json.dumps(math_new)),'math_regions_identical':math_old==math_new,'literal_regions_and_arguments':len(literal_old),'literal_before_sha256':sha(json.dumps(literal_old)),'literal_after_sha256':sha(json.dumps(literal_new)),'literal_regions_and_arguments_identical':literal_old==literal_new,'labels_refs_citations_inputs_graphics_identical':refs_old==refs_new,'environment_sequence_identical':env_old==env_new})
 assert all(row[k] for row in [rows[-1]] for k in ['math_regions_identical','literal_regions_and_arguments_identical','labels_refs_citations_inputs_graphics_identical','environment_sequence_identical']), f
(ED/'iii_preservation.json').write_text(json.dumps({'status':'PASS','scope':'Changed files compared byte-for-byte by protected region extraction against pre-edit backups; no TeX or Lean rebuild performed.','files':rows},indent=2)+'\n')
# Exact authored prose files read; generated appendices were read for prose headings/status and preserved as evidence.
files=[
 'source_i_iv/III/manuscript/Paper_III_Traditional_Final.tex',
 *[f'source_i_iv/III/manuscript/chapters/{f}' for f in ['01_finite_coordinates.tex','02_connections_obstructions.tex','03_nonlinear_coordinates.tex','04_correction_transport.tex']],
 'source_i_iv/III/manuscript/visual_atlas.tex',
 'source_i_iv/III/guides/visual/Paper_III_Visual_Guide_Final.tex','source_i_iv/III/guides/visual/source/reading_bridge.tex','source_i_iv/III/guides/visual/source/pages_final.tex',
 'source_i_iv/III/guides/lean/Paper_III_Lean_Guide_Final.tex',
 *[f'source_i_iv/III/guides/lean/chapters/{f}' for f in ['00_current_release.tex','01_orientation.tex','02_edges.tex','03_heterogeneous.tex','04_connections.tex','05_gauges.tex','06_nonlinear.tex','07_replay.tex']],
 'source_i_iv/III/docs/Paper_III_Section17_Analytic_Closeout.tex']
generated=[f'source_i_iv/III/guides/lean/generated/{f}.tex' for f in ['current_receipts','traditional_crosswalk','theorem_map','pins','inherited','imports']]
coverage=[]
for f in files+generated:
 s=(ED/'iii_iv_before'/f).read_text() if (ED/'iii_iv_before'/f).exists() else (ROOT/f).read_text()
 # Retain an honest reproducible count: raw TeX whitespace tokens, not a claim about prose-only words.
 coverage.append({'file':f,'review':'authored prose read in local context' if f in files else 'generated prose headings/status and navigation tables reviewed; exact evidence preserved','source_lines':len(s.splitlines()),'raw_tex_whitespace_tokens':len(s.split()),'changed':f in changed})
report={'status':'SEALED','chapters':'III','entry_points_confirmed_from':['component_builds.json','source_i_iv/selected_sources.json','source_i_iv/build_components.py'],'skill':'mathbox:proofread-math, SKILL.md and references/checklist.md read','style':'editorial/prose_review/STYLE.md','edited_files':changed,'exact_replacement_count':len(j),'journal':'editorial/prose_review/iii_journal.json','preservation':'editorial/prose_review/iii_preservation.json','coverage':coverage,'authored_prose_files_read':len(files),'generated_tables_reviewed':len(generated),'raw_tex_whitespace_tokens_in_authored_sources':sum(x['raw_tex_whitespace_tokens'] for x in coverage if x['file'] in files),'raw_tex_whitespace_tokens_in_generated_tables':sum(x['raw_tex_whitespace_tokens'] for x in coverage if x['file'] in generated),'word_count_limitation':'Counts are exact whitespace-separated source tokens including LaTeX/math and repeated atlas text, not prose-only word counts; both active atlas copies were byte-identical before editing and received matching edits.','first_pass':'Read all authored reader prose in the listed active input closures with adjacent displays, theorem/definition context, tables, captions, and formal scope distinctions. No archive or dormant source/pages.tex edited.','second_pass':'Reread changed sentences with neighboring sentences/displays; checked Chapter terminology, adjective compounds, display integration, captions and repeated shared atlas wording. Generated evidence tables and code excerpts were preserved.','correction_categories':['missing article and noun in analytic prose','dangling modifier and sentence fragment in analytic derivative proof','duplicated clause in Plate III.17','singular author possessive','American spelling','necessary technical compound hyphens','Chapter and mathematical text/formal companion terminology','historical compilation wording without time-relative freshly'],'mathematical_token_changes':[],'unresolved_substantive_issues':[],'excluded':['preserved III release-record PDF','preserved IV visual and verification-addendum PDFs (root-owned)','archived formal source, exact Lean excerpts, figure code and figures (not proofread as mathematical code)','dormant visual source/pages.tex and archives/backups/evidence logs'],'validation':{'math_regions_identical':True,'literal_regions_and_arguments_identical':True,'labels_refs_citations_inputs_graphics_identical':True,'environment_sequences_identical':True,'build':'Not run: source rebuilds coordinated by root after sealing.'}}
(ED/'iii_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','authored_prose_files_read','generated_tables_reviewed','raw_tex_whitespace_tokens_in_authored_sources','raw_tex_whitespace_tokens_in_generated_tables','exact_replacement_count']}))
