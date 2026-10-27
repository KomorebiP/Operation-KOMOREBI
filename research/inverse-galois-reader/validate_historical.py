"""Confirm the four recovered source inputs remain byte-identical."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parent
inputs=json.loads((ROOT/'evidence/HISTORICAL_INPUTS.json').read_text())['files']
for row in inputs:
    p=ROOT/'historical'/row['name']
    assert p.stat().st_size==row['bytes']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
report={'status':'passed','files':inputs,'scope':'The four recovered original source inputs are byte-identical. Extracted source interpretation is reviewed separately.'}
(ROOT/'evidence/HISTORICAL_PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'passed','files':len(inputs)}))
