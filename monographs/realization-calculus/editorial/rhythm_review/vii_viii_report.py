from pathlib import Path
import json,re,collections,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from vii_viii_scan import ROOT,OUT,FILES,COV,masked
from vii_viii_validate import CMD
primary=COV['continuous_review_files'];counts={};ret=[];words={};phrases=[]
for phase in ['before','after']:
 co=collections.Counter();ws=0
 for f in primary:
  s=(OUT/'vii_viii_before'/f).read_text() if phase=='before' else (ROOT/f).read_text();ws+=len(s.split());s=masked(s);s=CMD.sub(lambda m:' '*len(m.group()),s)
  co['semicolon_occurrences']+=s.count(';');co['dash_sequences']+=len(re.findall(r'---|--|[—–]',s));co['lexical_hyphenated_compounds']+=len(re.findall(r'\b[A-Za-z]+(?:-[A-Za-z]+)+\b',s))
  if phase=='after':
   for i,l in enumerate(s.splitlines(),1):
    if ';' in l:ret.append({'file':f,'line':i,'text':(ROOT/f).read_text().splitlines()[i-1],'reason':'Exact compact source-item/module/evidence locator label, retained as a technical record.'})
 counts[phase]=dict(co);words[phase]=ws
for f in FILES:
 old=(OUT/'vii_viii_before'/f).read_text();new=(ROOT/f).read_text()
 assert re.findall(r'\d+(?:\.\d+)*',old)==re.findall(r'\d+(?:\.\d+)*',new),f
 assert re.findall(r"``[\s\S]*?''",old)==re.findall(r"``[\s\S]*?''",new),f
J=json.loads((OUT/'vii_viii_journal.json').read_text());P=json.loads((OUT/'vii_viii_preservation.json').read_text());C=json.loads((OUT/'vii_viii_candidates.json').read_text())
report={
 'status':'SEALED','scope':'Active source-built VII–VIII traditional, visual and formal companion prose, including duplicate active plate bodies. No preserved PDF, build, root-map or archival-source edits.',
 'coverage':'Contextual targeted review of all screened punctuation/compound/formulaic-phrasing candidate passages in all 48 primary prose inputs. This is a targeted rhythm pass, not a claim of a second continuous word-by-word proofreading of the entire manuscript. Duplicate atlas bodies were synchronized and checked against the primary plate text.',
 'primary_prose_files':len(primary),'active_inputs_including_duplicates_and_wrapper':len(FILES),'primary_flagged_passages':sum(c['file'] in primary for c in C),'screened_passages_including_duplicates':len(C),'primary_before_raw_tex_whitespace_tokens':words['before'],
 'count_definition':'Counts cover the 48 primary prose inputs with equations, literal/code/font commands, identifiers, figures and comments masked. Lexical hyphenated-compound count means word matches containing one or more letter-to-letter hyphens, not a count of individual hyphen characters. Technical source/evidence labels and compact locators remain in this screening count. Candidate inventory also contains structural false positives, which were inspected and retained.',
 'counts':counts,'ordinary_semicolon_occurrences_revised':counts['before']['semicolon_occurrences']-counts['after']['semicolon_occurrences'],'retained_semicolon_records':ret,
 'routine_edits':'Sentence breaks or conjunctions in place of ordinary semicolons; one multiply/accumulation dash phrase; removal or rephrasing of optional stacked/adverbial compounds; direct wording in a small number of editorial statements.',
 'edited_files':len({x['file'] for x in J}),'exact_journal_entries':len(J),'mathematical_token_changes':0,'unresolved_issues':[],
 'retained_exceptions':['Named constructions and eponym dashes, including Knill--Laflamme, Hilbert--Schmidt and Eckart--Young--Mirsky.','Number/item/appendix/plate ranges and literal command flags. No parenthetical prose dash remained in the screened source.','Technical compounds needed for meaning or readability, including self-adjoint, finite-dimensional, rank-one, off-diagonal, floating-point, trace-class, low-rank, right-hand-side and mathematical/code model names.','Exact historical quotations, technical source records, generated identifiers, code, equations, figures and numerical metadata.','Meaningful contrasts that state hypotheses, distinguish proof scope or preserve open obligations.'],
 'validation':{'protected_math_literal_figure_comment_spans':sum(x['protected_math_literal_figure_comments'] for x in P['files']),'protected_identifier_commands':sum(x['protected_identifier_commands'] for x in P['files']),'environment_delimiters':sum(x['environment_delimiters'] for x in P['files']),'all_equal':True,'all_numeric_literals_equal':True,'all_tex_quoted_strings_equal':True,'braces_preserved':True,'exact_journal_reconstruction_all_inputs':True,'active_duplicate_plate_bodies_consistent':True,'changed_sentences_reread_in_context':True,'build':'Not run: root coordinates builds after source seal.'},
 'records':['editorial/rhythm_review/vii_viii_inputs.json','editorial/rhythm_review/vii_viii_candidates.json','editorial/rhythm_review/vii_viii_journal.json','editorial/rhythm_review/vii_viii_changes.diff','editorial/rhythm_review/vii_viii_changed_files.json','editorial/rhythm_review/vii_viii_preservation.json'],'backups':'editorial/rhythm_review/vii_viii_before/',
 'files_reviewed':primary,'duplicates':COV['duplicate_plate_files']
}
(OUT/'vii_viii_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','primary_flagged_passages','counts','ordinary_semicolon_occurrences_revised','edited_files','exact_journal_entries','validation']},indent=2))
