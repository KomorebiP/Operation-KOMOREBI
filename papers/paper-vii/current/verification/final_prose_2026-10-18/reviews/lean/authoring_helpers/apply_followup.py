from pathlib import Path
import json,hashlib

H=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18/editable/lean_guide')
OUT=Path('/workspace/scratch/be33f0b6c391/tmp/p7_final_lean_prose')
rp=OUT/'REPLACEMENTS.json';changes=json.loads(rp.read_text())
for file,before,after in [
    ('chapters/channels_recovery.tex','Agreement of two maps that are linear over the complex numbers on pure states therefore forces agreement on every operator.','Two maps that are linear over the complex numbers therefore agree on every operator if they agree on all pure states.'),
    ('chapters/geometry.tex',r'The global development begins with a map taking values in operators $P:M\to\mathcal L_{\mathbb R}(F,F)$.',r'The global development begins with an operator family $P:M\to\mathcal L_{\mathbb R}(F,F)$.')]:
    p=H/file;t=p.read_text();assert t.count(before)==1
    p.write_text(t.replace(before,after,1))
    changes[file].append({'before':before,'after':after,'exact_occurrences':1,'category':'Independent prose review'})
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
print(json.dumps({'files':len(ledger['files']),'replacements':sum(len(r['replacements']) for r in ledger['files'])}))
