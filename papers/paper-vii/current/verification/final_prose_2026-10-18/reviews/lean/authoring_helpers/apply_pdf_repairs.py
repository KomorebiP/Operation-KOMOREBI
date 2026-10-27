from pathlib import Path
import json,hashlib,difflib

H=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18/editable/lean_guide')
B=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Complete_Proofread_2026-10-18/editable/lean_guide')
O=Path('/workspace/scratch/be33f0b6c391/tmp/p7_final_lean_prose')
rp=O/'REPLACEMENTS.json';changes=json.loads(rp.read_text())
edits=[
('chapters/reading.tex',r'A theorem with \code{[Nonempty n]} is only available',r'A theorem with \mbox{\code{[Nonempty n]}} is only available','Keep a short type-class token on one line'),
('assemble.py',"for r in imports:out.append(r'\\textbf{'", "for r in imports:out.append(r'\\Needspace{3\\baselineskip}\\textbf{'",'Keep every module label with its source hash')]
for file,before,after,category in edits:
    p=H/file;t=p.read_text();assert t.count(before)==1,(file,before)
    p.write_text(t.replace(before,after,1))
    changes[file].append({'before':before,'after':after,'exact_occurrences':1,'category':category})
rp.write_text(json.dumps(changes,indent=2,ensure_ascii=False)+'\n')
ledger_path=H/'prose_review_2026-10-18/REVIEWED_REPLACEMENTS.json'
ledger=json.loads(ledger_path.read_text())
for rec in ledger['files']:
    rec['replacements']=changes[rec['path']]
    expected=(H/rec['baseline_path']).read_text()
    for e in rec['replacements']:
        assert expected.count(e['before'])==1
        expected=expected.replace(e['before'],e['after'],1)
    assert expected.encode()==(H/rec['path']).read_bytes()
    rec['reviewed_sha256']=hashlib.sha256(expected.encode()).hexdigest()
ledger_path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
report=json.loads((O/'PROSE_REVIEW.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report['exact_replacements']=sum(len(r['replacements']) for r in ledger['files'])
for r in report['coverage']:
    r['sha256']=sha(H/r['path'])
for r in report['files']:
    r['sha256']=sha(H/r['path'])
report['pdf_repairs']={'failed_candidate_sha256':'05b4110b022c07f8af6839298af757e2a6225366d3a5ec020b9875cd0991c8e8','pages':85,'findings':[{'physical_pages':[71,72,73],'issue':'Module names detached from their source hashes across a page break.','examples':['ConstraintAudit','QuantumStateBridge'],'repair':'Needspace guard before every module/hash pair.'},{'physical_pages':[3],'issue':'Short inline [Nonempty n] token broke inside its name.','repair':'Local nonbreaking wrapper retains the exact code token.'}],'status':'SOURCE_REPAIRS_APPLIED_AWAITING_REBUILD'}
(O/'PROSE_REVIEW.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
diffs=[]
for n in sorted(set(ledger['required_files'])|{'static_check.py'}):
    diffs.extend(difflib.unified_diff((B/n).read_text().splitlines(True),(H/n).read_text().splitlines(True),fromfile='before/editable/lean_guide/'+n,tofile='after/editable/lean_guide/'+n))
(O/'PROSE_REVIEW.patch').write_text(''.join(diffs))
print(json.dumps({'reviewed_replacements':report['exact_replacements'],'status':'source repairs applied'}))
