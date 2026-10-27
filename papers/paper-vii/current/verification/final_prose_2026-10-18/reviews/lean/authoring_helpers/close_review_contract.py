from pathlib import Path
import json,hashlib,difflib,shutil,re

ROOT=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18')
H=ROOT/'editable/lean_guide'
BASE=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Complete_Proofread_2026-10-18/editable/lean_guide')
OUT=Path('/workspace/scratch/be33f0b6c391/tmp/p7_final_lean_prose')
E=H/'prose_review_2026-10-18'
changes=json.loads((OUT/'REPLACEMENTS.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for name,edits in changes.items():
    baseline=BASE/name;current=H/name
    expected=baseline.read_text()
    for e in edits:
        assert expected.count(e['before'])==e['exact_occurrences']==1,(name,e['before'])
        expected=expected.replace(e['before'],e['after'],1)
    assert expected.encode()==current.read_bytes(),name
    bp=E/'baseline'/name;bp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(baseline,bp)
    records.append({'path':name,'baseline_path':bp.relative_to(H).as_posix(),'baseline_sha256':sha(bp),'reviewed_sha256':sha(current),'replacements':edits})
ledger={'schema':1,'date':'2026-10-18','scope':'Closed editorial substitutions against the accepted preceding proofreading edition. All mathematical spans, formal source files and source-exact excerpts are independently preserved. No Lean compilation.','required_files':sorted(changes),'files':records}
(E/'REVIEWED_REPLACEMENTS.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')

p=H/'static_check.py'
original=p.read_text()
arch=ROOT/'provenance/pre_final_prose_2026-10-18/editable/lean_guide/static_check.py'
arch.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,arch)
before="math=re.compile(r'(?s)"
position=original.index(before)
new='''# The user authorized a new prose pass. Protect it with an exact reviewed
# baseline and a closed sequence of substitutions, while separately retaining
# the original mathematical-span and source-excerpt checks.
review_path=H/'prose_review_2026-10-18/REVIEWED_REPLACEMENTS.json'
review=json.loads(review_path.read_text())
required={'Paper_VII_Lean_Guide_Final.tex','assemble.py','navigation.py'}|{
    p.relative_to(H).as_posix() for p in (H/'chapters').glob('*.tex')}
reviewed={}; expected_text={}
for record in review['files']:
    name=record['path']; baseline=H/record['baseline_path']; current=H/name
    text=baseline.read_text(); substitutions=[]
    for change in record['replacements']:
        unique=text.count(change['before'])==change['exact_occurrences']==1
        substitutions.append(unique)
        if unique:text=text.replace(change['before'],change['after'],1)
    checks={'baseline_sha256':sha(baseline)==record['baseline_sha256'],
            'every_substitution_unique':all(substitutions),
            'reviewed_sha256':sha(current)==record['reviewed_sha256'],
            'complete_file_equals_reviewed_substitutions':current.read_bytes()==text.encode()}
    reviewed[name]={'checks':checks,'replacements':len(substitutions),
                    'baseline_sha256':sha(baseline),'reviewed_sha256':sha(current)}
    expected_text[name]=text
review_checks={'exact_file_inventory':set(reviewed)==set(review['required_files'])==required,
               'no_duplicate_file_records':len(reviewed)==len(review['files']),
               'all_files_match_closed_review':all(all(x['checks'].values()) for x in reviewed.values())}
prose={'status':'PASS' if all(review_checks.values()) else 'FAIL',
       'scope':'Every authored chapter, opening wrapper and narrative generator equals the preserved baseline plus only the explicitly reviewed substitutions.',
       'checks':review_checks,'files':reviewed,
       'review_ledger_sha256':sha(review_path),'fresh_lean_compilation':False}
dump(G/'prose_review_preservation.json',prose)
'''
modified=original[:position]+new+original[position:]
old="""    records.append({'chapter':p.name,'delimited_mathematical_spans':len(left),'all_mathematical_spans_byte_identical':left==right,'contract_and_proof_walk_paragraphs':len(contracts),'all_contract_and_proof_walk_paragraphs_byte_identical':contracts==current})
mp={'status':'PASS' if all(r['all_mathematical_spans_byte_identical'] and r['all_contract_and_proof_walk_paragraphs_byte_identical'] for r in records) else 'FAIL','scope':'All six teaching chapters, excluding the revised evidence/replay chapter. Protects every delimited mathematical span and complete one-line contract/proof-walk paragraph. This is editorial preservation, not proof validation.','total_delimited_mathematical_spans':sum(r['delimited_mathematical_spans'] for r in records),'total_contract_and_proof_walk_paragraphs':sum(r['contract_and_proof_walk_paragraphs'] for r in records),'chapters':records}"""
rep="""    key=p.relative_to(H).as_posix()
    expected_contracts=re.findall(r'(?m)^\\\\(?:contract|walk)\\{.*$',expected_text.get(key,''))
    records.append({'chapter':p.name,'delimited_mathematical_spans':len(left),'all_mathematical_spans_byte_identical':left==right,'contract_and_proof_walk_paragraphs':len(contracts),'all_contract_and_proof_walk_paragraphs_byte_identical_to_historical':contracts==current,'all_contract_and_proof_walk_paragraphs_equal_reviewed_prose':current==expected_contracts,'complete_chapter_equals_closed_review':all(reviewed.get(key,{'checks':{'missing':False}})['checks'].values())})
mp={'status':'PASS' if prose['status']=='PASS' and all(r['all_mathematical_spans_byte_identical'] and r['all_contract_and_proof_walk_paragraphs_equal_reviewed_prose'] and r['complete_chapter_equals_closed_review'] for r in records) else 'FAIL','scope':'All six teaching chapters retain every delimited mathematical span from the retrieved edition. Complete chapters, including every contract and proof explanation, must equal the preserved prose baseline plus the exact reviewed substitutions. The replay chapter is also protected by the closed prose review. This is editorial preservation, not proof validation.','total_delimited_mathematical_spans':sum(r['delimited_mathematical_spans'] for r in records),'total_contract_and_proof_walk_paragraphs':sum(r['contract_and_proof_walk_paragraphs'] for r in records),'chapters':records}"""
assert modified.count(old)==1
modified=modified.replace(old,rep)
modified=modified.replace("'span_count':mp['total_delimited_mathematical_spans']","'span_count':mp['total_delimited_mathematical_spans'],'closed_prose_review':prose['status']")
modified=modified.replace("(static,pr,mp)","(static,pr,mp,prose)")
p.write_text(modified)
(OUT/'STATIC_CHECKER_REVISION.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),modified.splitlines(True),fromfile='before/static_check.py',tofile='after/static_check.py')))
print(json.dumps({'reviewed_files':len(records),'reviewed_replacements':sum(len(r['replacements']) for r in records),'closed_ledger':str(E/'REVIEWED_REPLACEMENTS.json')}))
