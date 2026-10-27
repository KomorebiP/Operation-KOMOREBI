#!/usr/bin/env python3
"""Read Paper IX's preserved formal identities, without compiler or control runs."""
from pathlib import Path
import collections, csv, hashlib, importlib.util, io, json, os, re, sys, zipfile
from datetime import datetime, timezone
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
TASK=Path('/dev/shm/komorebi_paper_ix_freeze_fbc994080222')
BASE=TASK/'baseline/Paper_IX_Final_Release_v1.0.0'
B=BASE/'preserved/PRSC_IX_Consolidated_Manuscript'
CURRENT=BASE/'verification/2026-10-20/finite/runs/formal_source_reconciliation'
OUT=TASK/'audit_integrity/FORMAL_STATIC_AUDIT.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
archives={}
def blob(loc):
    if '!' in loc or '::' in loc:
        archive,member=re.split(r'!|::',loc,maxsplit=1)
        if archive not in archives:archives[archive]=zipfile.ZipFile(B/archive)
        return archives[archive].read(member)
    return (B/loc).read_bytes()
checks=[]
def ck(name,value,detail=None):checks.append({'name':name,'pass':bool(value),'detail':detail})

index=load(B/'consolidation/audit/EVIDENCE_INDEX.json')
saved=load(CURRENT/'PROVENANCE_AUDIT.json')
ck('current_saved_reconciliation_status',saved['status']=='PASS' and saved['fresh_lean_run'] is False)
ck('current_and_preserved_evidence_index_equal',load(CURRENT/'reconciled/EVIDENCE_INDEX.json')==index)
ck('exact_15_retained_frontiers',len(index['frontiers'])==15)
ck('nested_baseline_archive_hash',sha(blob(index['baseline_nested_archive']['path']))==index['baseline_nested_archive']['sha256'])
ck('index_builder_hash',sha(blob(index['consolidation_checks']['script_path']))==index['consolidation_checks']['script_sha256'])
source_count=log_count=legacy_count=0
source_errors=[];log_errors=[];report_errors=[];inventory_errors=[];axiom_errors=[]
for f in index['frontiers']:
    name=f['frontier'];report=json.loads(blob(f['report']['path']))
    if sha(blob(f['report']['path']))!=f['report']['sha256']:report_errors.append(name+':receipt hash')
    if f['recompiled_during_consolidation'] is not False:report_errors.append(name+':recompile flag')
    for row in f['source_files_validated']:
        source_count+=1
        if sha(blob(row['path']))!=row['sha256']:source_errors.append(row['path'])
    for row in f['logs_validated']:
        if name=='native_affine':legacy_count+=1
        else:log_count+=1
        if sha(blob(row['path']))!=row['sha256']:log_errors.append(row['path'])
    if name=='native_affine':
        if report['pass'] is not True or any(r['pass'] is not True for r in report['results']):report_errors.append(name+':historical pass')
        continue
    inv=json.loads(blob(f['inventory']['path']))
    if sha(blob(f['inventory']['path']))!=f['inventory']['sha256']:inventory_errors.append(name+':inventory hash')
    if report.get('inventory_sha256') and sha(blob(f['inventory']['path']))!=report['inventory_sha256']:inventory_errors.append(name+':report inventory hash')
    if 'source_inventory' in report and inv!=report['source_inventory']:inventory_errors.append(name+':embedded inventory')
    if report['status'] not in ['PASS','LEAN_BUILD_AND_AXIOM_AUDIT_PASS']:report_errors.append(name+':historical status')
    audited=report['axiom_dependencies'];names=set()
    for group in ['modules','control_support','contracts','controls','negative_controls']:
        for m in inv.get(group,[]):
            names.update(d['name'] for d in m.get('declarations',[]))
    if names!=set(audited) or any(not set(v)<={'Classical.choice','Quot.sound','propext'} for v in audited.values()):axiom_errors.append(name)
ck('644_source_hash_bindings',source_count==644 and not source_errors,{'count':source_count,'failures':source_errors})
ck('713_original_digest_log_bindings',log_count==713 and not log_errors,{'recorded_digest_comparisons':log_count,'legacy_fingerprints':legacy_count,'failures':log_errors})
ck('four_legacy_logs_fingerprint_only',legacy_count==4 and all(r['compared_to_historical_log_hash'] is False for f in index['frontiers'] if f['frontier']=='native_affine' for r in f['logs_validated']))
ck('frontier_receipt_bindings',not report_errors,report_errors)
ck('frontier_inventory_bindings',not inventory_errors,inventory_errors)
ck('fourteen_inventory_axiom_sets_and_allowed_axioms',not axiom_errors,axiom_errors)
support_errors=[r['path'] for r in index['supporting_records'] if sha(blob(r['path']))!=r['sha256']]
ck('supporting_record_hashes',not support_errors,support_errors)
csv_bytes=blob('consolidation/audit/DECLARATIONS.csv')
rows=list(csv.DictReader(io.StringIO(csv_bytes.decode())))
ck('saved_declarations_digest_and_current_copy',sha(csv_bytes)==index['declaration_inventory']['sha256'] and csv_bytes==(CURRENT/'reconciled/DECLARATIONS.csv').read_bytes())
versions=collections.defaultdict(set)
for r in rows:versions[(r['kind'],r['qualified_name'])].add(r['source_sha256'])
ck('exact_declaration_source_version_inventory',len(rows)==1876 and len(versions)==1863 and len({r['canonical_source'] for r in rows})==199 and sum(len(v)>1 for v in versions.values())==13)
canonical_errors=[]
for r in rows:
    if sha(blob(r['canonical_source']))!=r['source_sha256']:canonical_errors.append(r['canonical_source'])
ck('all_declaration_canonical_source_hashes',not canonical_errors,canonical_errors)
statement=load(B/'consolidation/audit/STATEMENT_INDEX.json');links=[];link_errors=[]
for s in statement['statements']:
    for r in s['references']:
        data=blob(r['source']);short=r['declaration'].split('.')[-1]
        if sha(data)!=r['source_sha256'] or not re.search(r'\b(?:theorem|lemma|def|abbrev)\s+'+re.escape(short)+r'(?=[\s(:{])',data.decode()):link_errors.append(r)
        links.append({'label':s['label'],**r})
ck('202_statement_source_links_across_62_records',len(statement['statements'])==62 and len(links)==202 and not link_errors and links==load(CURRENT/'STATEMENT_SOURCE_LINKS.json'),{'records':len(statement['statements']),'links':len(links),'failures':link_errors})
ck('consolidated_manuscript_source_pins',all(sha((B/'manuscript/consolidated'/r).read_bytes())==h for r,h in statement['manuscript_source_hashes'].items()))

R=B/'polynomial_regularity';v=load(R/'verification/polynomial_regularity_verification.json');inv=v['source_inventory']
spec=importlib.util.spec_from_file_location('ix_freeze_source_audit',R/'scripts/source_audit.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.ROOT=R
latest_errors=[];static=[]
for group in ['modules','control_support','contracts']:
    for m in inv[group]:
        fresh=mod.inspect_source(R/m['source']);static.append(fresh)
        if fresh!=m:latest_errors.append(m['source'])
expected={d['name'] for m in static for d in m['declarations']}
parsed=mod.parse_audits((R/'verification/PolynomialRegularityAxiomAudit.log').read_text(),expected)
ck('latest_76_static_source_inventories',len(static)==76 and not latest_errors,latest_errors)
ck('latest_515_strict_raw_axiom_records',len(parsed)==515 and parsed==v['axiom_dependencies'])
ck('latest_module_contract_and_declaration_counts',v['status']=='PASS' and v['module_count']==55 and v['positive_control_modules']==8 and v['statement_contracts']==13 and v['negative_controls']==12 and v['declarations']=={'def':92,'abbrev':8,'theorem':415} and v['explicit_declaration_audits']==515)
negative_errors=[]
for m in inv['negative_controls']:
    name=Path(m['source']).stem;r=next(r for r in v['runs'] if r['name']==name);log=(R/'verification'/r['log']).read_bytes()
    if sha((R/m['source']).read_bytes())!=m['sha256'] or sha(log)!=r['log_sha256'] or not r['passed'] or r['exit_code']==0 or r['timed_out'] or not re.search(m['expected_error'],log.decode(),re.I):negative_errors.append(name)
ck('twelve_historical_negative_records_not_rerun',len(inv['negative_controls'])==12 and not negative_errors,negative_errors)
script_fields={'verifier_sha256':'scripts/verify_polynomial_regularity.py','source_audit_sha256':'scripts/source_audit.py','source_audit_regression_sha256':'scripts/check_source_audit.py','inventory_generator_sha256':'scripts/generate_regularity_inventory.py','runner_sha256':'scripts/check_low_memory.py'}
ck('five_latest_tool_source_bindings',all(sha((R/r).read_bytes())==v[f] for f,r in script_fields.items()))
ck('latest_target_and_inventory_bindings',sha((R/'TARGET_CONTRACT.json').read_bytes())==v['target_contract_sha256'] and sha((R/'inventory.json').read_bytes())==v['inventory_sha256'])
parser_run=next(r for r in v['runs'] if r['name']=='SourceAuditParserRegression')
ck('historical_parser_regression_log_bound_not_rerun',parser_run['exit_code']==0 and parser_run['passed'] and sha((R/'verification'/parser_run['log']).read_bytes())==parser_run['log_sha256'])
ck('historical_metadata_limits_retained',len(index['metadata_issues'])==2 and saved['stale_historical_inventory_scalars']==index['metadata_issues'] and index['source_statement_review']['full_primary_source_in_release'] is False and index['source_statement_review']['external_comparison_freshly_repeated'] is False)
report={'schema':'komorebi.paper-ix.freeze-formal-static-audit/1','created_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS' if all(r['pass'] for r in checks) else 'FAIL','check_count':len(checks),'checks':checks,'baseline_read_only':True,'fresh_lean_or_mathlib_execution':False,'scientific_or_control_suites_rerun':False,
 'scope':{'frontiers':15,'source_hash_comparisons':source_count,'recorded_log_hash_comparisons':log_count,'legacy_log_fingerprints':legacy_count,'statement_records':len(statement['statements']),'statement_source_links':len(links),'latest_strict_axiom_records':len(parsed),'latest_static_sources':len(static),'latest_inherited_compilation':v['started_at'],'declaration_source_version_rows':len(rows),'unique_kind_name_pairs':len(versions),'canonical_source_files':len({r['canonical_source'] for r in rows})},
 'receipt_paths':{'consolidated_evidence_index':'preserved/PRSC_IX_Consolidated_Manuscript/consolidation/audit/EVIDENCE_INDEX.json','current_reconciliation':'verification/2026-10-20/finite/runs/formal_source_reconciliation/PROVENANCE_AUDIT.json','latest_inherited_compiler_receipt':'preserved/PRSC_IX_Consolidated_Manuscript/polynomial_regularity/verification/polynomial_regularity_verification.json','latest_receipt_sha256':sha((R/'verification/polynomial_regularity_verification.json').read_bytes())},
 'frontier_receipts':[{ 'frontier':f['frontier'],**f['report'],'source_rows':len(f['source_files_validated']),'log_rows':len(f['logs_validated'])} for f in index['frontiers']],
 'limitations':['Fresh static authentication only. Historical compiler outcomes retain inherited status; no simultaneous clean Lean build or Mathlib rebuild is claimed.','The four native affine logs have current matching fingerprints but no log digests in their original report; this is not upgraded provenance.','The 1876 declaration/source-version rows and 1863 kind/name pairs overlap across versions and roles. Neither is a unique mathematical theorem count. Two stale historical scalar summaries remain preserved with explicit reconciliation.','Latest inherited gate has 55 proof modules, 8 positive-control modules, 13 contracts, 12 recorded rejecting controls and 515 audited declarations. The 380 recorded compiled-output hashes have no retained build directory; external binary/lake-manifest/adapter identities remain recorded runtime provenance.','The full Nishibuchi primary source is not in the release; exact external correspondence is inherited from the preserved source audit, not freshly reverified. Expanded factorial, mixed-step, all-rank and radius results are written/audited/bounded work rather than newly compiled Lean endpoints.','sources/lean/audit_sources.py also reruns a parser regression with deliberately invalid records. It was not executed here; only its static identity logic and historical parser receipt were checked.']}
OUT.write_text(json.dumps(report,indent=2)+'\n')
for z in archives.values():z.close()
print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[r['name'] for r in checks if not r['pass']],'report':str(OUT)}))
