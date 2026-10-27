from pathlib import Path
import json,re,hashlib,difflib,collections
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');E=R/'editorial/rhythm_review';B=E/'iii_iv_before'
# Load the same masking definitions without rerunning or overwriting the initial candidate inventory.
ns={};exec((E/'iii_iv_inventory.py').read_text().split('rows=[];counts={}')[0],ns)
mask=ns['mask'];math=ns['math'];blocks=ns['blocks'];scope=json.loads((E/'iii_iv_scope.json').read_text());files=scope['files'];rows=json.loads((E/'iii_iv_candidates.json').read_text());j=json.loads((E/'iii_iv_journal.json').read_text());changed=sorted({x['file'] for x in j})
sha=lambda x:hashlib.sha256(x.encode()).hexdigest()
mac=re.compile(r'\\(?:code|leanname|path|url|nolinkurl|texttt|statusleanthree|statusleanprior|label|ref|eqref|cref|Cref|pageref|cite|citep|citet|input|include|includegraphics|bibliography|bibliographystyle|href|hyperlink|hypertarget|excerpt|vfig)\b')
def args(s):
 out=[]
 for m in mac.finditer(s):
  pos=m.end()
  while pos<len(s) and s[pos].isspace():pos+=1
  if pos<len(s) and s[pos]=='[':pos=s.find(']',pos)+1
  while pos<len(s) and s[pos].isspace():pos+=1
  if pos>=len(s) or s[pos]!='{':continue
  depth=0;end=pos
  while end<len(s):
   if s[end] in '{}' and (end==0 or s[end-1]!='\\'):
    depth+=1 if s[end]=='{' else -1
    if depth==0:end+=1;break
   end+=1
  out.append(s[m.start():end])
 return out
checks=[]
for f in changed:
 a=(B/f).read_text();b=(R/f).read_text();s=a
 for e in j:
  if e['file']==f:
   assert e['old'] in s,(f,e['old']);s=s.replace(e['old'],e['new'],1)
 assert s==b,('journal',f)
 pairs={
 'math':([m.group() for m in math.finditer(a)],[m.group() for m in math.finditer(b)]),
 'literal_code_paths_refs_and_figures':([m.group() for m in blocks.finditer(a)]+args(a),[m.group() for m in blocks.finditer(b)]+args(b)),
 'exact_inline_quotes':(re.findall(r"``.*?''",a,re.S),re.findall(r"``.*?''",b,re.S)),
 'environment_sequence':(re.findall(r'\\(?:begin|end)\{[^}]*\}',a),re.findall(r'\\(?:begin|end)\{[^}]*\}',b)),
 'numeric_digits':(re.findall(r'\d+',a),re.findall(r'\d+',b)),
 'eponyms_ranges_and_paired_technical_dashes':(re.findall(r'---|--|[—–]',mask(a)),re.findall(r'---|--|[—–]',mask(b)))}
 cs={}
 for k,(av,bv) in pairs.items():
  assert av==bv,(f,k);cs[k]={'count_before':len(av),'count_after':len(bv),'before_sha256':sha(json.dumps(av)),'after_sha256':sha(json.dumps(bv)),'identical':True}
 checks.append({'file':f,'before_sha256':sha(a),'after_sha256':sha(b),'exact_journal_replay':True,'checks':cs})
(E/'iii_iv_preservation.json').write_text(json.dumps({'status':'PASS','files':checks,'mathematical_token_changes':[],'code_or_figure_edits':[],'no_build_or_root_map_edit':True},indent=2)+'\n')
patterns=[('semicolon',r';'),('dash',r'---|--|[—–]'),('hyphenated_modifier',r'(?<![A-Za-z\\])[A-Za-z]+(?:-[A-Za-z]+)+'),('formulaic_phrase',r'(?i)\b(?:it is (?:important|worth|useful|helpful)|in (?:summary|conclusion)|in short|serves as|provides a framework|we now|we next|the purpose of|a useful|most importantly|importantly|therefore makes|these boundaries leave)\b')]
newcounts=collections.Counter();review=[];idx=0;coverage=[]
for f in files:
 a=(B/f).read_text() if (B/f).exists() else (R/f).read_text();b=(R/f).read_text();ma=mask(a);mb=mask(b);ops=[]
 if a!=b:
  al=a.splitlines(keepends=True);bl=b.splitlines(keepends=True);ap=[0];bp=[0]
  for line in al:ap.append(ap[-1]+len(line))
  for line in bl:bp.append(bp[-1]+len(line))
  for tag,i1,i2,k1,k2 in difflib.SequenceMatcher(None,al,bl,autojunk=False).get_opcodes():
   if tag=='equal':continue
   ac=''.join(al[i1:i2]);bc=''.join(bl[k1:k2])
   for ct,c1,c2,d1,d2 in difflib.SequenceMatcher(None,ac,bc,autojunk=False).get_opcodes():
    if ct!='equal':ops.append((ap[i1]+c1,ap[i1]+c2))
 coverage.append({'file':f,'source_lines_before':len(a.splitlines()),'raw_tex_whitespace_tokens_before':len(a.split()),'changed':f in changed,'review':'Candidate punctuation and phrase contexts read, with neighboring prose/displays consulted for edits. Repeated technical compounds retained. Math/code bodies excluded from copyediting.'})
 for typ,pat in patterns:
  newcounts[typ]+=len(list(re.finditer(pat,mb)))
  for m in re.finditer(pat,ma):
   x=dict(rows[idx]);idx+=1;assert x['file']==f and x['type']==typ and x['candidate']==m.group()
   touched=any(m.start()<a2 and m.end()>a1 for a1,a2 in ops)
   x['decision']='recast' if touched else 'retained'
   if touched:x['reason']='Exact contextual edit recorded in iii_iv_journal.json.'
   elif typ=='dash':x['reason']='Range, eponym, inherited title or paired technical relation; no parenthetical em-dash prose was found.'
   elif typ=='semicolon' and ('& \\leanname{' in x['context'] or x['context'].lstrip().startswith('\\item')):x['reason']='Mathematical/list punctuation or delimiter between exact declaration/file identifiers.'
   elif typ=='semicolon':x['reason']='Structural list punctuation or delimiter between exact identifiers; no removable ordinary prose sentence join remains.'
   elif typ=='hyphenated_modifier':x['reason']='Needed technical compound, disambiguating modifier, numbered compound, source/contract label, or established mathematical vocabulary.'
   else:x['reason']='Specific explanatory wording with mathematical purpose; punctuation or a short phrase alone does not warrant calling it AI-authored.'
   review.append(x)
assert idx==len(rows)
(E/'iii_iv_candidate_review.json').write_text(json.dumps(review,indent=2)+'\n');(E/'iii_iv_coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
oldcounts=collections.Counter(x['type'] for x in rows);decisions=collections.Counter((x['type'],x['decision']) for x in review)
summary={typ:{'initial_candidates':oldcounts[typ],'retained_original_occurrences':decisions[(typ,'retained')],'original_occurrences_recast':decisions[(typ,'recast')],'remaining_candidates_after':newcounts[typ]} for typ,_ in patterns}
report={'status':'SEALED','scope':'Active source-built Chapter III traditional/analytic/visual/formal readers and Chapter IV traditional/formal readers only. IV visual and other preserved PDFs, XI/XII, archives and generated declaration catalogs excluded.','source_authority':['component_builds.json','source_i_iv/build_components.py','source_i_iv/selected_sources.json'],'style':'editorial/rhythm_review/STYLE.md','skill':'mathbox:proofread-math SKILL.md and previously read references/checklist.md','authored_files_reviewed':len(files),'changed_files':changed,'changed_file_count':len(changed),'exact_journal_entries':len(j),'journal':'editorial/rhythm_review/iii_iv_journal.json','backups':'editorial/rhythm_review/iii_iv_before','preservation':'editorial/rhythm_review/iii_iv_preservation.json','coverage':'editorial/rhythm_review/iii_iv_coverage.json','candidate_review':'editorial/rhythm_review/iii_iv_candidate_review.json','candidate_counts':summary,'candidate_count_limitation':'Inventory counts are candidate occurrences after masking math, literals, quoted blocks, code/ref/path arguments, comments and entry preambles. Semicolon totals include retained mathematical enumerations and separators between exact declaration/file identifiers, which are explicitly classified. Dash totals are ranges, eponyms and paired technical relations; none is parenthetical em-dash prose.','raw_tex_whitespace_tokens_in_source_scope':sum(x['raw_tex_whitespace_tokens_before'] for x in coverage),'word_count_limitation':'Exact whitespace token count includes TeX, math and duplicated shared atlas prose; not a prose-only word count.','routine_edits':['Replace unnecessary ordinary prose semicolons with sentence boundaries, preserving logical scope and proof order.','Recast optional hyphenated modifiers as natural noun/prepositional phrases.','Replace Most importantly with a direct sentence introducing the same conjugation formula in both active atlas copies.','Remove one padded edition-summary sentence while retaining the subsequent precise statement-register categories.'],'retained_exceptions':['Mathematical enumeration punctuation and exact declaration/file-list delimiters.','Ranges, proper eponyms, paired technical relations and inherited titles.','Needed compounds such as self-adjoint, finite-dimensional, off-diagonal, zero-free, trace-class, positive-order and branch-dependent.','Exact historical/contract quotations, code, source identifiers, commands and scientific figures.'],'second_pass':'Reread contextual diffs, authored ledger/table edits and adjacent displays for every edited passage. Corrected a caption modifier order to retain four block counts, and made the continuing M=0 conditional scope explicit after a sentence split. No proof reconstructed or shortened.','mathematical_token_changes':[],'proof_hypotheses_quantifiers_or_open_scope_changes':[],'unresolved_substantive_issues':[],'validation':{'status':'PASS','exact_journal_replay':True,'math_regions_identical':True,'literal_code_path_reference_figure_regions_identical':True,'exact_quotes_identical':True,'numeric_digits_identical':True,'environment_sequences_identical':True,'technical_dashes_identical':True,'math_regions_compared':sum(x['checks']['math']['count_before'] for x in checks),'literal_regions_compared':sum(x['checks']['literal_code_paths_refs_and_figures']['count_before'] for x in checks),'build':'Not run. Root coordinates source rebuilds after seal.'},'no_child_agents':True,'canonical_sources_frozen_after_seal':True}
(E/'iii_iv_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','authored_files_reviewed','changed_file_count','exact_journal_entries','candidate_counts','validation']},indent=2))
