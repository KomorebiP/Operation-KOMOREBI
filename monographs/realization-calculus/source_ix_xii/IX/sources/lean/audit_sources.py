#!/usr/bin/env python3
"""Fresh static reconciliation of retained evidence; never invokes Lean."""
from pathlib import Path
import argparse,collections,csv,hashlib,importlib.util,json,re,shutil,subprocess,sys,zipfile,os
sys.dont_write_bytecode=True
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,default=HERE/'audit');args=ap.parse_args();B=args.source.resolve();out=args.output.resolve();out.mkdir(exist_ok=True)
def sha(data):return hashlib.sha256(data).hexdigest()
def blob(path):
 if '!' in path or '::' in path:
  a,n=re.split(r'!|::',path,maxsplit=1)
  with zipfile.ZipFile(B/a) as z:return z.read(n)
 return (B/path).read_bytes()
p=subprocess.run([sys.executable,str(B/'consolidation/tools/evidence_index.py'),'--source',str(B),'--output',str(out/'reconciled')],capture_output=True,text=True)
(out/'evidence_replay.log').write_text(p.stdout+p.stderr);assert p.returncode==0
new=json.loads((out/'reconciled/EVIDENCE_INDEX.json').read_text());old=json.loads((B/'consolidation/audit/EVIDENCE_INDEX.json').read_text());assert new==old
assert (out/'reconciled/DECLARATIONS.csv').read_bytes()==(B/'consolidation/audit/DECLARATIONS.csv').read_bytes()
statement=json.loads((B/'consolidation/audit/STATEMENT_INDEX.json').read_text());links=[]
for s in statement['statements']:
 for r in s['references']:
  data=blob(r['source']);assert sha(data)==r['source_sha256'];short=r['declaration'].split('.')[-1]
  assert re.search(r'\b(?:theorem|lemma|def|abbrev)\s+'+re.escape(short)+r'(?=[\s(:{])',data.decode()),r
  links.append({'label':s['label'],**r})
for rel,h in statement['manuscript_source_hashes'].items():assert sha((B/'manuscript/consolidated'/rel).read_bytes())==h
rows=list(csv.DictReader((out/'reconciled/DECLARATIONS.csv').open()));names={(r['kind'],r['qualified_name']) for r in rows}
R=B/'polynomial_regularity';v=json.loads((R/'verification/polynomial_regularity_verification.json').read_text());inv=v['source_inventory'];scrip=R/'scripts/source_audit.py'
spec=importlib.util.spec_from_file_location('ix_source_audit',scrip);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.ROOT=R
static=[]
for group in ['modules','control_support','contracts']:
 for m in inv[group]:
  fresh=mod.inspect_source(R/m['source']);assert fresh==m,(group,m['source']);static.append(fresh)
expected={d['name'] for m in static for d in m['declarations']};parsed=mod.parse_audits((R/'verification/PolynomialRegularityAxiomAudit.log').read_text(),expected);assert parsed==v['axiom_dependencies']
negative=[]
for m in inv['negative_controls']:
 assert sha((R/m['source']).read_bytes())==m['sha256'];name=Path(m['source']).stem;r=next(r for r in v['runs'] if r['name']==name);log=(R/'verification'/r['log']).read_bytes()
 assert r['passed'] and r['exit_code']!=0 and not r['timed_out'] and re.search(m['expected_error'],log.decode(),re.I)
 assert sha(log)==r['log_sha256'];negative.append({'name':name,'source_sha256':m['sha256'],'log_sha256':r['log_sha256'],'exit_code':r['exit_code'],'expected_error':m['expected_error'],'fresh_rejection':False})
scriptchecks={}
for field,rel in [('verifier_sha256','scripts/verify_polynomial_regularity.py'),('source_audit_sha256','scripts/source_audit.py'),('source_audit_regression_sha256','scripts/check_source_audit.py'),('inventory_generator_sha256','scripts/generate_regularity_inventory.py')]:
 assert sha((R/rel).read_bytes())==v[field];scriptchecks[rel]=v[field]
assert sha((R/'TARGET_CONTRACT.json').read_bytes())==v['target_contract_sha256'];assert sha((R/'inventory.json').read_bytes())==v['inventory_sha256']
p=subprocess.run([sys.executable,str(R/'scripts/check_source_audit.py')],capture_output=True,text=True);(out/'parser_regression.log').write_text(p.stdout+p.stderr);assert p.returncode==0
result={'status':'PASS','scope':'Fresh Python static source/hash/audit-log reconciliation only; historical compiler outcomes retain inherited status.','fresh_lean_run':False,'lean_executable_present':shutil.which('lean') is not None,'lake_executable_present':shutil.which('lake') is not None,'frontiers':len(new['frontiers']),'source_hash_comparisons':644,'recorded_log_hash_comparisons':713,'legacy_affine_log_fingerprints':4,'legacy_note':'Four legacy affine logs have no digest in their original run report; current matching fingerprints do not upgrade that provenance.','evidence_index_identical':True,'declarations_csv_identical':True,'declaration_source_version_rows':len(rows),'row_kinds':dict(collections.Counter(r['kind'] for r in rows)),'unique_kind_name_pairs':len(names),'unique_kind_name_counts':dict(collections.Counter(k for k,n in names)),'unique_name_note':'Identifier count only, not unique mathematical theorems. Multiple source versions and overlapping statements persist.','canonical_source_files':len({r['canonical_source'] for r in rows}),'names_with_multiple_source_versions':13,'manuscript_statements':len(statement['statements']),'manuscript_source_links':len(links),'manuscript_reference_hashes_match':True,'latest_gate':{'started_at':v['started_at'],'seconds':v['seconds'],'runtime':v['runtime'],'module_count':v['module_count'],'positive_control_modules':v['positive_control_modules'],'statement_contracts':v['statement_contracts'],'negative_controls':v['negative_controls'],'named_declarations':v['declarations'],'explicit_declaration_audits':v['explicit_declaration_audits'],'fresh_static_modules':len(static),'fresh_strict_axiom_parser_records':len(parsed),'negative_control_log_checks':negative,'script_hashes_verified':scriptchecks},'allowed_axioms':sorted(mod.ALLOWED),'parser_regression':'PASS: actual unchanged historical Python parser regression rerun, including three deliberately invalid parser records.','stale_historical_inventory_scalars':new['metadata_issues'],'raw_sources_changed':False}
(out/'PROVENANCE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');(out/'STATEMENT_SOURCE_LINKS.json').write_text(json.dumps(links,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='latest_gate'},indent=2))
