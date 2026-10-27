#!/usr/bin/env python3
"""Check exact preservation of predecessor theorem/proof text and reference algorithms."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'lineage'/'v0.1.0'

def pairs(text):
    rx=r'\\begin\{(theorem|proposition)\}\[([^]]+)\]\\label\{([^}]+)\}(.*?)\\end\{\1\}\s*\\begin\{proof\}(.*?)\\end\{proof\}'
    return {m[2]:(m[0],m[1],m[3],m[4]) for m in re.findall(rx,text,re.S)}
a=pairs((OLD/'Self_Improving_Intelligence_v0.1.0.tex').read_text())
b=pairs((ROOT/'Self_Improving_Intelligence_v0.2.0.tex').read_text())
changed=[label for label in a if label not in b or a[label]!=b[label]]
code={name:(OLD/'code'/name).read_bytes()==(ROOT/'code'/name).read_bytes()
      for name in ('repair_calculus.py','check_finite_models.py','demo.py')}
result={'status':'PASS' if not changed and all(code.values()) else 'FAIL',
        'predecessor_statement_proof_pairs':len(a),'current_statement_proof_pairs':len(b),
        'unchanged_pairs':len(a)-len(changed),'changed_or_missing':changed,
        'unchanged_reference_code':code,
        'predecessor_source_sha256':hashlib.sha256((OLD/'Self_Improving_Intelligence_v0.1.0.tex').read_bytes()).hexdigest(),
        'non_claim':'Text preservation is not independent mathematical verification.'}
(ROOT/'validation'/'preservation_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],result['unchanged_pairs'],'predecessor statement/proof pairs and three reference programs unchanged.')
if result['status']!='PASS':raise SystemExit(1)
