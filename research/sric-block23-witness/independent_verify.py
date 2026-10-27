from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import json
from pathlib import Path

from block23.core import expected_certificate
from block23.receipts import digest

ROOT=Path(__file__).resolve().parent

def main():
    result=json.loads((ROOT/'results'/'block23_final.json').read_text())
    released=result.pop('result_receipt')
    recomputed=digest(result)
    if released!=recomputed:raise SystemExit('result receipt mismatch')
    rows=result['records']
    for row in rows:
        if row['expected_certificate']!=expected_certificate(row['family']):
            raise SystemExit('expected certificate table mismatch')
        if row['certificate']!=row['expected_certificate'] or not row['correct']:
            raise SystemExit(f"certificate failure:{row['episode_id']}")
        if row['family']=='semantic_ambiguity':
            if row['certificate']!='ONTOLOGY_UNDERIDENTIFIED' or row['alternative_semantic_disagreement']<0.75:
                raise SystemExit('semantic ambiguity was overclaimed')
        if row['family']=='destructive_loss':
            if row['collision_count']<48 or row['minimum_protected_consequence_gap']<0.75:
                raise SystemExit('destructive no-go lacks collision witness')
    print('SRIC_BLOCK23_REPLAY_VERIFIED')
    print(f"episodes={len(rows)}")
    print(f"result_receipt={released}")
if __name__=='__main__':main()
