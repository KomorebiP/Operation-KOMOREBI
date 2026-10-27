#!/usr/bin/env python3
"""Reconcile guide selections and source-bound inherited records without Lean."""
from pathlib import Path
import argparse, datetime, hashlib, json, re, shutil
from data_helpers import active_text, inventory
H=Path(__file__).resolve().parent; R=H.parents[1]
P=argparse.ArgumentParser(description=__doc__)
P.add_argument('--source',type=Path,default=R/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot')
a=P.parse_args(); S=a.source.resolve(); G=H/'generated'; F=S/'verification/final_finite_release_run'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
summary=json.loads((F/'SUMMARY.json').read_text()); modules=sorted((S/'formalization').glob('*.lean'))
rows=[r for p in modules for r in inventory(p)]; names={r['declaration'] for r in rows}
saved=json.loads((S/'verification/theorem_inventory.json').read_text()); targets={n for ns in saved.values() for n in ns}
recorded={n:ax for m in summary['modules'] for n,ax in m['axiom_audits'].items()}
allowed={'propext','Classical.choice','Quot.sound'}; findings=[]; module_rows=[]
for p in modules:
    m=next(r for r in summary['modules'] if r['module']==p.stem); log=F/m['log']
    parsed={n:[] if vals is None else [v.strip() for v in vals.split(',') if v.strip()] for n,vals in re.findall(r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)\s*$",log.read_text(),re.M)}
    parsed={k:v for k,v in parsed.items() if k in recorded}
    # Empty captures denote axiom-free records in re.findall.
    controls={'source_hash':sha(p)==m['sha256'],'log_hash':sha(log)==m['log_sha256'],'successful_saved_exit':m['exit_code']==0,'inventory':set(parsed)==set(m['axiom_audits']),'exact_saved_axiom_sets':parsed==m['axiom_audits'],'allowed_axioms':all(set(v)<=allowed for v in parsed.values()),'no_admitted_proof_or_new_axiom':not bool(re.search(r'\b(?:sorry|admit|axiom)\b',active_text(p.read_text()))),'transitive_import_source_hashes':all(sha(S/'formalization'/f'{name}.lean')==value for name,value in m['dependency_source_sha256'].items())}
    if not all(controls.values()):findings.append({'module':p.stem,'checks':controls})
    module_rows.append({'module':p.stem,'source_sha256':sha(p),'log_sha256':sha(log),'theorems':len(parsed),'checks':controls})
extra=json.loads((F/'CONSTRUCTED_OBJECTS_AUDIT.json').read_text()); inv=json.loads((S/'verification/constructed_objects_inventory.json').read_text()); construction_log=F/'constructed_objects.log'
cparsed={n:[v.strip() for v in vals.split(',') if v.strip()] for n,vals in re.findall(r"^'([^']+)' depends on axioms:\s*\[([^\]]*)\]\s*$",construction_log.read_text(),re.M)}
constructed={'six_objects':len(inv)==extra['construction_count']==6,'saved_exit_success':extra['pass'] and extra['exit_code']==0,'source_hash':sha(S/extra['source'])==extra['source_sha256'],'inventory_hash':sha(S/'verification/constructed_objects_inventory.json')==extra['inventory_sha256'],'runner_hash':sha(S/'scripts/check_low_memory.py')==extra['runner_sha256'],'log_hash':sha(construction_log)==extra['log_sha256'],'summary_hash':sha(F/'SUMMARY.json')==extra['cumulative_summary_sha256'],'exact_inventory_and_axiom_sets':set(cparsed)==set(inv) and cparsed==extra['axiom_audits'],'allowed_axioms':all(set(v)<=allowed for v in cparsed.values())}
controls=[]
for c in summary['negative_controls']:
    controls.append({'name':c['name'],'source_hash':sha(S/c['source'])==c['sha256'],'log_hash':sha(F/c['log'])==c['log_sha256'],'inherited_rejected_exit':c['exit_code']==c['expected_exit_code']==1 and c['pass'],'fresh_execution':False})
pins=json.loads((S/'provenance/lake-manifest.json').read_text())['packages']; gpins=json.loads((G/'dependency_pins.json').read_text())
common={'25_modules':len(modules)==25,'323_unique_targets':len(rows)==len(names)==323,'inventory_matches':names==targets==set(recorded),'current_saved_complete_success':summary['pass'] and summary['complete'],'19_scoped_items':len(json.loads((S/'THEOREM_LEDGER.json').read_text()))==19,'five_continuum_targets_open':summary['scope']['continuum_conjectures_not_proved']==5,'runner_hash':sha(S/'scripts/check_low_memory.py')==summary['runner_sha256'],'verifier_hash':sha(S/'scripts/verify.py')==summary['verifier_sha256'],'inventory_hash':sha(S/'verification/theorem_inventory.json')==summary['inventory_sha256'],'nine_exact_dependency_pins':len(pins)==9 and pins==gpins,'pinned_mathlib_revision':next(p['rev'] for p in pins if p['name']=='mathlib')==summary['expected_mathlib_revision']=='aeb72f1e9981b6d35b426b16dca7759be3e7ba06','pinned_compiler_version':summary['expected_lean_version']=='4.34.0-rc2','all_module_checks':not findings,'constructed_object_checks':all(constructed.values()),'two_inherited_negative_records':len(controls)==2 and all(all(v for k,v in c.items() if k not in ('name','fresh_execution')) for c in controls)}
static={'status':'PASS' if all(common.values()) else 'FAIL','scope':'Source identity, imports, active declarations, saved axiom-log correspondence, locked dependencies and excerpt fidelity. No kernel execution.','checks':common,'module_checks':module_rows,'constructed_object_checks':constructed,'inherited_negative_controls':controls,'inherited_release':summary['release'],'inherited_started_utc':summary['started_utc'],'inherited_updated_utc':summary['updated_utc'],'source_modules':25,'theorem_targets':323,'scoped_results':19,'constructed_objects':6,'dependency_pins':9,'open_continuum_conjectures':5,'fresh_lean_compilation':False,'runtime_available':{n:shutil.which(n) for n in ('lean','lake','elan')},'inherited_evidence_sha256':{p.relative_to(S).as_posix():sha(p) for p in (F/'SUMMARY.json',F/'CONSTRUCTED_OBJECTS_AUDIT.json',S/'THEOREM_LEDGER.json',S/'verification/theorem_inventory.json',S/'verification/constructed_objects_inventory.json',S/'provenance/lake-manifest.json')}}
dump(G/'static_reconciliation.json',static)
raw=[]
for e in json.loads((G/'excerpts.json').read_text()):
    p=S/e['source_file']; text=p.read_text().splitlines(keepends=True); expected=''.join(text[e['start_line']-1:e['end_line']]).encode(); actual=H/'excerpts'/f"{e['tag']}.lean.txt"; historical=H/'historical_assembly/excerpts'/actual.name
    raw.append({'tag':e['tag'],'source_sha256_matches':sha(p)==e['source_sha256'],'excerpt_sha256_matches':sha(actual)==e['excerpt_sha256'],'exact_contiguous_source_bytes':expected==actual.read_bytes(),'unchanged_from_retrieved_baseline':historical.read_bytes()==actual.read_bytes()})
pr={'status':'PASS' if len(raw)==67 and all(all(v for k,v in e.items() if k!='tag') for e in raw) else 'FAIL','exact_raw_excerpts':67,'checks':raw,'formal_sources_modified':False,'scope':'Every selected source block is exact raw UTF-8 and byte-identical to the retrieved edition.'}
dump(G/'preservation.json',pr)
math=re.compile(r'(?s)\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$\$.*?\$\$|(?<!\\)\$[^$]*?(?<!\\)\$|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}')
records=[]
for p in sorted((H/'chapters').glob('*.tex')):
    if p.name=='replay.tex':continue
    old=(H/'historical_assembly/chapters'/p.name).read_text(); new=p.read_text(); left=[m.group() for m in math.finditer(old)];right=[m.group() for m in math.finditer(new)]
    contracts=re.findall(r'(?m)^\\(?:contract|walk)\{.*$',old); current=re.findall(r'(?m)^\\(?:contract|walk)\{.*$',new)
    records.append({'chapter':p.name,'delimited_mathematical_spans':len(left),'all_mathematical_spans_byte_identical':left==right,'contract_and_proof_walk_paragraphs':len(contracts),'all_contract_and_proof_walk_paragraphs_byte_identical':contracts==current})
mp={'status':'PASS' if all(r['all_mathematical_spans_byte_identical'] and r['all_contract_and_proof_walk_paragraphs_byte_identical'] for r in records) else 'FAIL','scope':'All six teaching chapters, excluding the revised evidence/replay chapter. Protects every delimited mathematical span and complete one-line contract/proof-walk paragraph. This is editorial preservation, not proof validation.','total_delimited_mathematical_spans':sum(r['delimited_mathematical_spans'] for r in records),'total_contract_and_proof_walk_paragraphs':sum(r['contract_and_proof_walk_paragraphs'] for r in records),'chapters':records}
dump(G/'mathematical_span_preservation.json',mp)
print(json.dumps({'static':static['status'],'source_modules':25,'theorems':323,'constructed_objects':6,'raw_excerpts':pr['status'],'mathematical_spans':mp['status'],'span_count':mp['total_delimited_mathematical_spans']}))
if not all(r['status']=='PASS' for r in (static,pr,mp)):raise SystemExit(1)
