#!/usr/bin/env python3
"""Fail-closed evidence collector for AVOC v0.37.0."""
from pathlib import Path
import hashlib,json,re,sys,time
ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.37.0'
start=time.time()

def readj(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
counts=readj(RD/'source_counts.json')
assert counts['inherited_theorems']==1860 and counts['new_theorems']==60 and counts['total_theorems']==1920
assert counts['non_audit_modules']==174
ax=readj(RD/'axiom_audit_summary.json')
assert ax['expected']==ax['reports']==ax['unique_reports']==1920
assert not ax['missing'] and not ax['extra'] and ax['duplicates']==0 and ax['allowed_only']
assert ax['axiom_union']==['Classical.choice','Quot.sound','propext']
scan=readj(RD/'source_scan.json'); assert scan['hits']==[]
neg=readj(RD/'negative_all/summary.json'); assert neg['total']==neg['substantive_rejections']==103
inherit=readj(RD/'inherited_module_comparison.json'); assert inherit['baseline_modules']==inherit['byte_identical']==171 and not inherit['changed']
build=(RD/'aggregate_build.log').read_text(); assert 'Build completed successfully (1965 jobs).' in build
for stem in ['LazyStagedControl','LazyStagedRecovery','LazyStagedExamples','LazyStagedCodec','LazyStagedMain']:
    logs=list(RD.glob(f'werror_{stem}.json'))
    assert len(logs)==1,(stem,logs)
    r=readj(logs[0]); assert r['returncode']==0 and not r['timed_out'] and r['source_unchanged']
runtime=readj(RD/'runtime/final/summary.json')
assert runtime['passed']==4
byname={x['case']:x for x in runtime['cases']}
assert byname['warm']['result']['warm_calls']==1 and byname['warm']['result']['cold_calls']==0
assert byname['cold']['result']['cold_calls']==1 and byname['cold']['result']['warm_calls']==0
assert byname['crash']['final']['warm_calls']==1 and byname['crash']['final']['recovery_rechecks']==1
assert len(byname['invalid']['rejected'])==3
summary={
  'version':'0.37.0','status':'PASS','toolchain':'Lean 4.34.0-rc2',
  'mathlib':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
  'theorem_declarations':1920,'new_theorem_declarations':60,
  'non_audit_modules':174,'lean_source_lines':counts['source_lines'],
  'aggregate_build_jobs':1965,'axiom_reports':1920,
  'axiom_union':ax['axiom_union'],'negative_rejections':103,
  'inherited_modules_byte_identical':171,'runtime_regression_groups':4,
  'source_scan_hits':0,
  'evidence_sha256':{
    'axiom_audit':sha(RD/'axiom_audit_summary.json'),
    'negative_summary':sha(RD/'negative_all/summary.json'),
    'runtime_summary':sha(RD/'runtime/final/summary.json'),
    'source_scan':sha(RD/'source_scan.json'),
    'verification_record':sha(ROOT/'results/VERIFICATION_v0.37.0.md'),
  },
  'collector_seconds':round(time.time()-start,3),
  'limitations':['pinned external caches retained','Python/SQLite adapter tested, not universally refined','v0.36 source artifact unavailable; reconstructed from v0.35 plus retained specification']
}
(RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
