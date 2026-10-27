#!/usr/bin/env python3
"""Read saved VIII finite-contract identities only; never invokes Lean or writes baseline."""
from pathlib import Path
import hashlib, json, re
from datetime import datetime, timezone

TASK = Path('/dev/shm/komorebi_paper_viii_freeze_fbc994080222')
CORE = TASK/'baseline/core/Komorebi_Paper_VIII_Final_2026-10-10'
SNAP = CORE/'source/complete/Paper_VIII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot'
OUT = TASK/'audit_integrity/FORMAL_STATIC_AUDIT.json'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text())
checks = []
def ck(name, value, detail=None):
    checks.append({'name':name, 'pass':bool(value), 'detail':detail})

receipt_path = SNAP/'verification/sixth_final/SUMMARY.json'
d = load(receipt_path)
inventory = load(SNAP/'verification/theorem_inventory.json')
ledger = load(SNAP/'verification/coverage_ledger.json')
release = load(SNAP/'verification/sixth_release_audit.json')
modules = {m['module']:m for m in d['modules']}
ck('accepted_receipt_complete_and_pass', d['complete'] is True and d['pass'] is True)
ck('exact_formal_counts', len(modules)==40 and sum(m['theorem_declarations'] for m in modules.values())==392 and sum(len(m['construction_audits']) for m in modules.values())==66)
ck('runner_binding', sha(SNAP/'scripts/check_low_memory.py')==d['runner_sha256'])
ck('verifier_binding', sha(SNAP/'scripts/verify.py')==d['verifier_sha256'])
ck('inventory_binding', sha(SNAP/'verification/theorem_inventory.json')==d['inventory_sha256'])
ck('inventory_exact_module_set',set(inventory)==set(modules))
source_failures=[]; log_failures=[]; audit_failures=[]; dep_failures=[]; build_record_failures=[]
allowed=set(d['allowed_axioms'])
for name, m in modules.items():
    src=SNAP/m['source']; log=SNAP/'verification/sixth_final'/m['log']
    if sha(src)!=m['sha256']:source_failures.append(name)
    if sha(log)!=m['log_sha256']:log_failures.append(name)
    parsed={}
    for n, axioms in re.findall(r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)\s*$",log.read_text(),re.M):
        if n in parsed:audit_failures.append(name+':duplicate '+n)
        parsed[n]=[a.strip() for a in axioms.split(',') if a.strip()]
    if parsed!=m['axiom_audits'] or set(parsed)!=set(inventory[name]) or any(not set(v)<=allowed for v in parsed.values()) or m['unexpected_axioms'] or m['forbidden_tokens'] or m['exit_code']!=0 or m['pass'] is not True:
        audit_failures.append(name)
    for dep,h in m['dependency_source_sha256'].items():
        if dep not in modules or sha(SNAP/modules[dep]['source'])!=h:dep_failures.append(name+':'+dep)
    for dep,h in m['dependency_build_sha256'].items():
        if dep not in modules or modules[dep]['build_sha256']!=h:build_record_failures.append(name+':'+dep)
ck('all_40_saved_source_bindings',not source_failures,source_failures)
ck('all_40_saved_log_bindings',not log_failures,log_failures)
ck('raw_axiom_logs_match_inventory_and_saved_audits',not audit_failures,audit_failures)
ck('transitive_dependency_sources_bind',not dep_failures,dep_failures)
ck('dependency_build_record_crosslinks',not build_record_failures,build_record_failures)
negative_failures=[]
for row in d['negative_controls']:
    if sha(SNAP/row['source'])!=row['sha256'] or sha(SNAP/'verification/sixth_final'/row['log'])!=row['log_sha256'] or row['exit_code']!=1 or row['expected_exit_code']!=1 or row['pass'] is not True:
        negative_failures.append(row['name'])
ck('two_recorded_negative_controls_bound_not_rerun',len(d['negative_controls'])==2 and not negative_failures,negative_failures)
ck('release_audit_receipt_binding',release['kernel_report_sha256']==sha(receipt_path) and release['pass'] is True)
ck('release_audit_counts',release['module_count']==40 and release['theorem_count']==392 and release['construction_audit_count']==66)
checked=[x for x in ledger['records'] if x.get('lean_status')=='checked']
external=[x for x in ledger['records'] if x.get('proof')=='external']
ck('ledger_scope',len(ledger['records'])==85 and len(checked)==56 and len(external)==4 and ledger['fully_checked']==56 and ledger['not_fully_checked']==0)
all_names={n for names in inventory.values() for n in names}
missing_coverage_names=[n for x in checked for n in x.get('lean_theorems',[]) if n not in all_names]
ck('all_checked_ledger_names_in_audited_inventory',not missing_coverage_names,missing_coverage_names)
ck('recorded_runtime_revision',d['runtime']['pass'] is True and d['runtime']['manifest_mathlib_revision']==d['runtime']['actual_mathlib_revision']==d['expected_mathlib_revision'])
ck('inherited_scope_flags',d['scope']['manuscript_items_checked']==56 and d['scope']['classical_inputs_tracked_separately']==4 and d['scope']['classical_inputs_independently_reproved_in_full'] is False and d['scope']['general_svd_existence_or_algorithm_formalized'] is False and d['scope']['mathlib_rebuilt_or_independently_rechecked'] is False)
report={
 'schema':'komorebi.paper-viii.freeze-formal-static-audit/1','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','check_count':len(checks),'checks':checks,
 'baseline_read_only':True,'fresh_lean_or_mathlib_execution':False,'scientific_or_control_suites_rerun':False,
 'scope':{'inherited_compilation_utc':d['updated_utc'],'finite_items':56,'theorem_declarations':392,'modules':40,'construction_audits':66,'numbered_records':85,'classical_inputs':[{k:x.get(k) for k in ['number','title','lean_status','formal_scope']} for x in external]},
 'bindings':{'snapshot':str(SNAP.relative_to(CORE)),'receipt':str(receipt_path.relative_to(CORE)),'receipt_sha256':sha(receipt_path),'runner_sha256':d['runner_sha256'],'verifier_sha256':d['verifier_sha256'],'inventory_sha256':d['inventory_sha256'],'module_sources':40,'module_logs':40,'recorded_negative_controls':2,'retained_build_artifact_files':len(list((SNAP/'verification/sixth_final/build').glob('*')))},
 'limitations':[
 'Authenticates saved source, inventory, coverage, runner, verifier, raw axiom logs and record crosslinks; it is not a fresh kernel check or mathematical proof audit.',
 'No sixth_final/build compiled objects are retained; the 200 module output hashes and their dependency references are recorded historical identities rather than independently rehashed retained binaries.',
 'No standalone lake/toolchain configuration is retained in this snapshot; exact runtime/Mathlib identity is recorded in the inherited receipt and verifier constants.',
 'General SVD existence/algorithm, canonical Mathlib singularValues API identification, floating-point QR/SVD certification, four classical inputs, prior-paper rebuilds, Mathlib rebuild and hardware benchmarking are outside the inherited contract.'
 ]}
OUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'report':str(OUT)}))
