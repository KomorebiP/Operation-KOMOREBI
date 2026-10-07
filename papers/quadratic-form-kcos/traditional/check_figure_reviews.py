#!/usr/bin/env python3
"""Associate prior native-resolution review only with identical output bytes.

A regenerated figure with a different hash requires a new visual review.
This helper never treats a successful plotting run as visual inspection.
"""
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
evidence_path = BASE / 'FIGURE_INDEPENDENT_REVIEW.json'
if not evidence_path.exists():
    print('No retained native-resolution review evidence is available.')
    raise SystemExit(0)
evidence = json.loads(evidence_path.read_text())
reviews = {Path(r['path']).name: r for r in evidence['figures']}
evidence_hash = hashlib.sha256(evidence_path.read_bytes()).hexdigest()

def verified(name):
    entry = reviews.get(name)
    if entry is None:
        return False
    path = BASE / entry['path']
    return (path.exists() and entry['native_review'] == 'PASS'
            and hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'])

for report_name in ['FIGURE_RELAYOUT_EARLY.json', 'FIGURE_RELAYOUT_LATE.json']:
    path = BASE / report_name
    report = json.loads(path.read_text())
    results = []
    for item in report['figures']:
        name = item.get('file', item.get('figure'))
        match = verified(name)
        item['independent_visual_review'] = 'PASS' if match else 'requires new review'
        item['independent_reviewed_output_sha256'] = reviews.get(name, {}).get('sha256')
        results.append(match)
    report['independent_review_evidence'] = evidence_path.name
    report['independent_review_evidence_sha256'] = evidence_hash
    report['all_current_outputs_match_independently_reviewed_hashes'] = all(results)
    path.write_text(json.dumps(report, indent=2) + '\n')
count = sum(verified(name) for name in reviews)
print(f'{count}/{len(reviews)} current figures match independently reviewed bytes.')
