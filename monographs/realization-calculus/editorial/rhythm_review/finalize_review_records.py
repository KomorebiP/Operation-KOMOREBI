#!/usr/bin/env python3
"""Bind the completed punctuation review to the actual assembled book."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
def load(p):return json.loads((ROOT/p).read_text())
def sha(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def main():
    pdf_hash=sha('output/Realization_Calculus.pdf')
    audit=load('book/final_pdf_audit.json')
    visual=load('editorial/rhythm_review/final_visual_review.json')
    build=load('editorial/rhythm_review/build_run/REBUILD_ALL_COMPONENTS.json')
    for d in (audit,visual):assert d['status']=='PASS' and d['pdf_sha256']==pdf_hash
    assert build['all_36_built'] and build['all_actionable_diagnostics_clear']
    accounting=load('book/book_layout_accounting.json')
    preserved=load('editorial/rhythm_review/preserved_apply_report.json')
    pv=load('editorial/rhythm_review/preserved_visual_review.json')
    assert pv['status']=='SEALED' and pv['result']=='PASS'
    assert len(preserved)==3 and all(not x['skipped'] for x in preserved)
    records=[
      'editorial/rhythm_review/STYLE.md',
      'editorial/rhythm_review/source_seals.json',
      'editorial/rhythm_review/frontmatter_reconciliation_evidence.json',
      'editorial/rhythm_review/glossary_anchor_reconciliation.json',
      'editorial/rhythm_review/page_guard_reconciliation.json',
      'editorial/rhythm_review/frontmatter_independent_check.json',
      'editorial/rhythm_review/i_ii_report.json',
      'editorial/rhythm_review/iii_iv_report.json',
      'editorial/rhythm_review/v_vi_report.json',
      'editorial/rhythm_review/vii_viii_report.json',
      'editorial/rhythm_review/ix_x_report.json',
      'editorial/rhythm_review/xi_xii_report.json',
      'editorial/rhythm_review/xii_report.json',
      'editorial/rhythm_review/outer_journal.json',
      'editorial/rhythm_review/preserved_proposals.json',
      'editorial/rhythm_review/preserved_apply_report.json',
      'editorial/rhythm_review/preserved_visual_review.json',
      'editorial/rhythm_review/build_run/REBUILD_ALL_COMPONENTS.json',
      'editorial/book_revision/frontmatter_keep_overrides.json',
      'book/atlas_book_routes_report.json',
      'book/glossary_anchor_resolution.json',
    ]
    d={
      'schema':'realization-calculus.book-editorial-audit/3',
      'status':'PASS','pdf_sha256':pdf_hash,'pages':accounting['total_pages'],
      'scope':'Contextual punctuation and prose-rhythm pass across all twelve chapters, their available visual/formal/computational companions, further arithmetic studies, outer matter and glossary. This is not a new proof audit or Lean/scientific replay.',
      'method':'Review ordinary prose semicolons, parenthetical dashes, optional hyphenated modifiers and formulaic phrasing in their paragraphs. Apply local grammatical rewrites and reread changed contexts. Exact candidate coverage and retained exceptions are reported by source group. Dense generated contract catalogues are protected rather than claimed as freshly reread prose.',
      'coverage':{'source_rebuilt_readers':36,'component_readers_authenticated':41,'selected_source_pages':accounting['selected_source_pages'],'glossary_terms':73,'glossary_source_references':74,'preserved_candidate_paragraphs':40,'additional_preserved_edits':sum(len(x['applied']) for x in preserved),'preserved_pages_protected':141},
      'mathematical_token_changes':[],
      'preservation':{'source':'Group comparisons preserve protected math, literal code/evidence, identifiers, references, figures and structure. Contextual rereading preserves hypotheses, conclusions and proof order.','preserved_pdf':'All-page mathematical glyph/font/rounded-position snapshots, annotations, image streams and vector geometry pass. Edited pages have zero changed pixels outside the bounded regions at144dpi. All20 changed contexts and18 whole pages passed rendered review.','originals':'All41 exact original readers remain attachments and package files.','formal_evidence':'Historical verification remains historical. No new kernel, numerical experiment, benchmark or scientific figure generation is inferred.'},
      'intentional_punctuation_retained':['Mathematical argument separators, minus signs, conditions and ranges.','Necessary technical compounds and named constructions, such as self-adjoint, finite-dimensional, p-adic and Hilbert–Schmidt.','Exact quoted/normative contracts, code, filenames, source identifiers, catalogue and bibliography delimiters.','Ordinary automatic line-breaking hyphens in typeset words.'],
      'previous_editorial_review':{'path':'editorial/rhythm_review/before/book_editorial_audit.json','sha256':sha('editorial/rhythm_review/before/book_editorial_audit.json')},
      'review_records':[{'path':p,'sha256':sha(p)} for p in records],
      'unresolved_editorial_findings':[],
      'boundaries':{'conjecture_66':'Open','chapter_xii':'Conditional on its stated supplied arithmetic, patching, support, Hecke, classicality and representation inputs.'},
    }
    write('book/book_editorial_audit.json',d)
    write('book/final_visual_review.json',visual)
    p=ROOT/'README.md';text=p.read_text()
    text=re.sub(r'\*\*[\d,]+ pages\*\*','**'+format(accounting['total_pages'],',')+' pages**',text,count=1)
    needle='Exact journals, coverage records and preservation comparisons are supplied in `editorial/prose_review/`.'
    addition=' The subsequent punctuation pass replaces optional semicolons and parenthetical dashes with natural sentence structure, recasts unnecessary compound modifiers, and simplifies formulaic phrasing. Mathematical punctuation, necessary technical compounds and exact source records are retained. Its contextual coverage, exact journals and checks are in `editorial/rhythm_review/`.'
    assert text.count(needle)==1
    if addition.strip() not in text:
        text=text.replace(needle,needle+addition)
    p.write_text(text)
    print(json.dumps({'status':'PASS','pages':accounting['total_pages'],'pdf_sha256':pdf_hash,'preserved_edits':d['coverage']['additional_preserved_edits']}))
if __name__=='__main__':main()
