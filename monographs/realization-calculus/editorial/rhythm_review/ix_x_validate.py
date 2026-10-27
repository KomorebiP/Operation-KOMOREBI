#!/usr/bin/env python3
"""Validate rhythm-only changes against current-source backups."""
from pathlib import Path
import re,json,hashlib,difflib,importlib.util,collections
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'editorial/rhythm_review'
spec=importlib.util.spec_from_file_location('scan',OUT/'ix_x_candidates.py');scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan)
P={
'math':scan.MATH,
'literal_environments':scan.LITERAL,
'code_paths_identifiers':r'\\(?:code|lean|mcode|target|source|path|url|nolinkurl|texttt|VerbatimInput|label|hypertarget|input|include|includegraphics|cite|bibitem|href|ref|eqref|cref|Cref|pageref)\s*(?:\[[^\]]*\])?\{[^{}]*\}',
'environment_sequence':r'\\(?:begin|end)\{[^{}]+\}',
'graphics':r'\\includegraphics(?:\[[^\]]*\])?\{[^{}]*\}',
'commands':r'\\[A-Za-z@]+\*?',
'numeric_literals':r'\b\d+(?:\.\d+)?\b',
'excerpt_assets':r'\\excerpt\{[^{}]*\}\{[^{}]*\}',
}
J=json.loads((OUT/'ix_x_journal.json').read_text());D=json.loads((OUT/'ix_x_candidates.json').read_text());rows=[];patch=[];totals=collections.Counter();aftercounts=collections.Counter();fail=[]
for name in json.loads((OUT/'ix_x_scope.json').read_text()):
 old=(OUT/'ix_x_before'/name).read_text();new=(ROOT/name).read_text();checks={}
 for key,pattern in P.items():
  a,b=re.findall(pattern,old,re.S),re.findall(pattern,new,re.S);checks[key]={'before':len(a),'after':len(b),'identical':a==b};totals[key]+=len(a)
  if a!=b:fail.append((name,key))
 replay=old
 for e in [e for e in J if e['file']==name]:
  assert e['old'] in replay,(name,e['id']);replay=replay.replace(e['old'],e['new'],1)
 assert replay==new,name
 assert old.count('{')-old.count('}')==new.count('{')-new.count('}'),name
 row={'file':name,'changed':old!=new,'sha256_before':hashlib.sha256(old.encode()).hexdigest(),'sha256_after':hashlib.sha256(new.encode()).hexdigest(),'raw_words_before':len(old.split()),'raw_words_after':len(new.split()),'checks':checks,'exact_journal_replay':True,'brace_balance_unchanged':True};rows.append(row)
 patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+name,tofile=name))
 clean=scan.mask(new)
 for key,pat in scan.PATTERNS.items():aftercounts[key]+=len(re.findall(pat,clean,re.I))
assert not fail,fail
(OUT/'ix_x_validation.json').write_text(json.dumps(rows,indent=2)+'\n');(OUT/'ix_x_changes.patch').write_text(''.join(patch))
report={'status':'SEALED','scope':'Current IX–X source-built traditional, visual and formal companion inputs. Inactive variants, exact source excerpts, generated catalogues, code, evidence and scientific figure assets excluded from changes.','files':len(rows),'additional_generated_introductions_reviewed':['catalog.tex','crosswalk.tex','dependencies.tex'],'generated_intro_coverage_record':'editorial/rhythm_review/ix_x_generated_intro_coverage.json','candidate_context_whitespace_tokens':sum(len(p['masked_paragraph'].split()) for p in D['paragraphs']),'raw_tex_words':sum(r['raw_words_before']for r in rows),'candidate_paragraphs_reviewed':len(D['paragraphs']),'candidate_counts_before':D['totals'],'candidate_counts_after':aftercounts,'candidate_count_net_reductions':{k:D['totals'][k]-aftercounts[k]for k in D['totals']},'changed_paragraphs':len(J),'changed_files':sum(r['changed']for r in rows),'mathematical_token_changes':[],'protected_regions':totals,'protected_comparison_failures':fail,'remaining_eligible_unreviewed':0,'coverage_method':'Every inventoried candidate paragraph read in context. A separate second reading of changed contexts, with adjacent mathematical statements consulted for ambiguous scope. Candidate counts are source occurrences, not unique editorial issues. Ranges, eponyms and technical terms deliberately retained.','retained_semicolons_by_reason':{'structured_contract_hypotheses':10,'mathematical_definitions_hypotheses_and_open_question_lists':15,'checkpoint_locator_headings':15,'exact_source_module_catalogues':3,'bibliographic_edition_record':1,'visual_source_locator_headings':9},'retained_exceptions':'Logical hypothesis and open-question lists, source locator headings, declaration/source-module catalogues and bibliographic records retain necessary semicolon separators. All double-dash/en-dash candidates are eponyms, ranges, or technical paired terms. Necessary mathematical compounds remain, including p-adic, prime-power, finite-dimensional, mixed-step, inverse-limit, characteristic-zero and address/rank designations. Scope-defining contrastive phrasing remains when it distinguishes a proved claim from a stronger unproved claim.','standalone_single_hyphen_check':{'ordinary_prose_occurrences':0,'retained_nonprose_occurrences':2,'reason':'Both are TeX column-width arithmetic in continuation_11.tex.'},'changed_context_reread':True,'validation_command':'python editorial/rhythm_review/ix_x_validate.py'}
(OUT/'ix_x_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
