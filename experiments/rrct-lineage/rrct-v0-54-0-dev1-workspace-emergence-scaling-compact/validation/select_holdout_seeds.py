from __future__ import annotations
import hashlib, json, pathlib
NAMESPACE=b'RRCT-v0.54-workspace-emergence-scaling-holdout-2026-08-25'
excluded={54011,54029,54047,109716655,144594564,594133867,558679426}
seeds=[];counter=0
while len(seeds)<4:
    digest=hashlib.sha256(NAMESPACE+counter.to_bytes(8,'big')).digest()
    value=100_000_000 + int.from_bytes(digest[:8],'big')%800_000_000
    if value not in excluded and value not in seeds: seeds.append(value)
    counter+=1
payload={'schema':'rrct.v054.holdout_seed_selection.v1','namespace_sha256':hashlib.sha256(NAMESPACE).hexdigest(),'method':'SHA-256 counter expansion; no model execution','seeds':seeds,'excluded_seeds':sorted(excluded),'candidate_outcomes_inspected':False}
path=pathlib.Path(__file__).with_name('HOLDOUT_SEEDS.json');path.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
print(json.dumps(payload,indent=2))
