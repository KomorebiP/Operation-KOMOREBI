from __future__ import annotations
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
vals=[];i=0
while len(vals)<12:
 d=hashlib.sha256(f'RRCT-v055-overcomplete-edge-2026-08-25:{i}'.encode()).digest()
 v=int.from_bytes(d[:8],'big')%900_000_000+100_000_000
 if v not in vals: vals.append(v)
 i+=1
payload={'schema':'rrct.v055.overcomplete_seed_selection.v1','seeds':vals,'selection_uses_outcomes':False}
(ROOT/'validation/OVERCOMPLETE_SEEDS.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
print(json.dumps(payload,indent=2))
