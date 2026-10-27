#!/usr/bin/env python3
"""Deterministically update correspondence only. Never alter publication statements."""
from pathlib import Path
import json,collections,hashlib
root=Path(__file__).resolve().parents[1]
x=json.loads((root/'predecessor/coverage/COVERAGE_108.json').read_text())
delta=json.loads((root/'coverage/DELTA_108.json').read_text())
old={r['stable_id']:r for r in json.loads(json.dumps(x))['records']}
for d in delta['updates']:
 r=next(r for r in x['records'] if r['stable_id']==d['stable_id'])
 r['status']=d['status'];r['scope_and_remaining_work']=d['scope_and_remaining_work']
 r['mapped_declarations']=list(dict.fromkeys(r['mapped_declarations']+d['add_declarations']))
 r['block05_contribution']=d['add_declarations']
for r in x['records']:
 for k in ('statement','source_proof','current_source'):
  assert r[k]==old[r['stable_id']][k],(r['stable_id'],k)
x['schema']='paper-i-coverage/0.5.0'
x['counts']=dict(collections.Counter(r['status'] for r in x['records']))
x['proved_record_status_counts']=dict(collections.Counter(r['status'] for r in x['records'] if r['kind'] in ['theorem','corollary','lemma','proposition']))
x['block05_statement_identity']={'unchanged_records':len(x['records']),'delta_sha256':hashlib.sha256((root/'coverage/DELTA_108.json').read_bytes()).hexdigest()}
(root/'coverage/COVERAGE_108.json').write_text(json.dumps(x,indent=2)+'\n')
lines=['# Paper I: expanded publication-to-Lean map v0.5.0','',
 '108 records. 69 proof-level records. 18 covered, 31 partial, 20 not mapped.',
 '','The publication text is unchanged. Coverage is reviewed semantic correspondence, not a Lean interpretation of prose. Final declaration acceptance is recorded separately in VERIFICATION.json.','']
for r in x['records']:
 lines += [f"## {r['ordinal']}. {r['stable_id']} — {r['title']}",'',f"**Kind:** {r['kind']}  **Status:** {r['status']}",'',r['scope_and_remaining_work'],'', '**Mapped declarations:**','']
 lines += [f'- `{n}`' for n in r['mapped_declarations']]
 lines += ['', '**Current statement:**','', '```tex',r['statement'],'```','',f"**Source:** `{r['current_source']['file']}`, lines {r['current_source']['statement_start_line']}–{r['current_source']['statement_end_line']}. Statement SHA256 `{r['current_source']['statement_sha256']}`.",'']
(root/'coverage/COVERAGE_108.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(x['proved_record_status_counts']));print('UNCHANGED_STATEMENTS',len(x['records']))
