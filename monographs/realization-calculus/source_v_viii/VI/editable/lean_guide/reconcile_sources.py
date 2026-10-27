#!/usr/bin/env python3
"""Check guide contracts and exact excerpts against the preserved Lean source.

This is documentation reconciliation. It does not execute Lean, compute proof
semantics, or enlarge the recorded manuscript contract.
"""
from pathlib import Path
import argparse, hashlib, json, re
from data_helpers import active_text
H=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=H.parents[1]/'source/complete/original_snapshot')
parser.add_argument('--output',type=Path,default=H/'generated/static_reconciliation.json')
args=parser.parse_args();S=args.source.resolve();L=S/'formalization/lean';G=H/'generated'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding="utf-8"))
contract=load(S/'verification/source_contract.json');ledger=load(S/'THEOREM_LEDGER.json')
targets=contract['theorem_targets'];names={x['declaration'] for x in targets}
checks={}
checks['source_hashes']=[{'path':p,'sha256':sha(S/p),'match':sha(S/p)==d}
                        for p,d in contract['source_sha256'].items()]
checks['source_hashes_match']=all(x['match'] for x in checks['source_hashes'])
checks['exact_33_record_ledger']=ledger==load(G/'result_ledger.json') and len(ledger)==33
checks['exact_341_theorem_target_catalog']=targets==load(G/'targets.json') and len(targets)==341 and len(names)==341
checks['ledger_endpoint_targets_resolve']=all(n in names for r in ledger for n in r['targets'])
line_checks=[]
for t in targets:
    lines=active_text((L/t['file']).read_text(encoding="utf-8")).splitlines()
    name=t['declaration'].rsplit('.',1)[1]
    text=lines[t['line']-1]
    line_checks.append({'declaration':t['declaration'],'file':t['file'],'line':t['line'],
                        'match':bool(re.match(r'\s*theorem\s+'+re.escape(name)+r'\b',text))})
checks['target_declaration_lines']=line_checks
checks['all_target_lines_match']=all(x['match'] for x in line_checks)
modules=sorted((L/'KomorebiPaperVI').glob('*.lean'))
imports=load(G/'imports.json')
checks['proof_modules']=len(modules)
checks['exact_47_module_inventory']=len(modules)==47 and {p.relative_to(L).as_posix() for p in modules}=={r['file'] for r in imports}
checks['imports_match_source']=all(r['sha256']==sha(L/r['file']) and
 r['imports']==re.findall(r'(?m)^import (\S+)',active_text((L/r['file']).read_text(encoding="utf-8"))) for r in imports)
pins=[{'name':p['name'],'revision':p['rev'],'url':p['url']} for p in load(L/'lake-manifest.json')['packages']]
checks['exact_9_dependency_pins']=len(pins)==9 and pins==load(G/'dependency_pins.json')
audit_source=active_text((L/'KernelAudit.lean').read_text(encoding="utf-8"))
directives=re.findall(r'(?m)^#print axioms (\S+)',audit_source)
checks['341_target_audit_directives_match']=len(directives)==341 and set(directives)==names
raw_audit=(S/'verification/lean_axiom_audit.log').read_text(encoding="utf-8")
audit_records=[{'declaration':n,'axioms':[v.strip() for v in vals.split(',') if v.strip()]}
 for n,vals in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",raw_audit)]
checks['341_inherited_axiom_records_match']=len(audit_records)==341 and {x['declaration'] for x in audit_records}==names and audit_records==load(G/'inherited_axiom_records.json')
checks['inherited_allowed_axioms_match']=all(set(x['axioms'])<={'propext','Classical.choice','Quot.sound'} for x in audit_records)
checks['inherited_namespace_782_record_present']='PAPER_VI_TARGET_AUDIT_PASS: 341 theorem targets; 782 namespace declarations' in raw_audit
excerpts=load(G/'excerpts.json');details=[]
for e in excerpts:
    source=S/e['source_file'];lines=source.read_text(encoding="utf-8").splitlines(keepends=True)
    expected=''.join(lines[e['start_line']-1:e['end_line']])
    raw=H/'excerpts'/f"{e['tag']}.lean.txt"
    details.append({'tag':e['tag'],'source_sha256_match':sha(source)==e['source_sha256'],
      'raw_excerpt_sha256_match':sha(raw)==e['excerpt_sha256'],
      'exact_recorded_source_span':expected==raw.read_text(encoding="utf-8")})
checks['source_excerpts']=details
checks['exact_48_source_excerpts']=len(excerpts)==48 and all(x['source_sha256_match'] and x['raw_excerpt_sha256_match'] and x['exact_recorded_source_span'] for x in details)
flags=[v for k,v in checks.items() if isinstance(v,bool)]
result={'schema':'komorebi.paper_vi.lean_documentation_reconciliation.v1',
 'status':'PASS' if all(flags) else 'FAIL','scope':'static contracts, locations, imports, pins, exact excerpts, inherited transcript reconciliation',
 'fresh_lean_kernel_run':False,'inherited_kernel_timestamp_utc':'2026-09-06T06:00:38.447662+00:00',
 'counts':{'scoped_result_records':33,'theorem_targets':341,'proof_modules':47,
           'source_hash_entries':len(contract['source_sha256']),'source_excerpts':48,'dependency_pins':9,
           'inherited_namespace_declarations':782},'checks':checks}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n', encoding="utf-8")
print(json.dumps({'status':result['status'],'counts':result['counts']}))
raise SystemExit(0 if result['status']=='PASS' else 1)
