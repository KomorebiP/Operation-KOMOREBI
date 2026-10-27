#!/usr/bin/env python3
"""Check source references, preservation of base proofs, and test provenance."""
from pathlib import Path
import collections, hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
s=(ROOT/'Komorebi_Seeded_Two_Axis_Calculus_v0.9.0.tex').read_text()
b=(ROOT/'previous/Komorebi_Seeded_Two_Axis_Calculus_v0.8.0.tex').read_text()
labels=re.findall(r'\\label\{([^}]+)\}',s)
refs=[x.strip() for term in re.findall(r'\\(?:c|C|eq)?ref\{([^}]+)\}',s) for x in term.split(',')]
cites=[x.strip() for term in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',s) for x in term.split(',')]
keys=re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}',s)
pattern=r'\\begin\{(theorem|lemma|proposition|corollary|proof)\}[\s\S]*?\\end\{\1\}'
blocks=[m.group(0) for m in re.finditer(pattern,b)]
base=json.loads((ROOT/'audit/base_sha256.json').read_text())
base_ok={name:sha(ROOT/'previous'/name)==digest for name,digest in base.items()}
reports=[]
for script,out in [('check_models.py','base_regression_results.json'),('check_interactions.py','interaction_results.json'),('check_resolution_towers.py','resolution_results.json'),('check_intrinsic_exchange.py','intrinsic_results.json')]:
    d=json.loads((ROOT/'checks'/out).read_text())
    reports.append({'script':script,'status':d.get('status'),
                    'hash_matches':d.get('script_sha256',d.get('input_sha256',{}).get(script))==sha(ROOT/'checks'/script)})
log=(ROOT/'audit/latex_final.log').read_text(errors='replace')
log_flags=[line for line in log.splitlines() if re.search(r'Warning|Overfull|Underfull|undefined|^! ',line)]
result={'duplicate_labels':[x for x,n in collections.Counter(labels).items() if n>1],
        'missing_references':sorted(set(refs)-set(labels)),
        'missing_citations':sorted(set(cites)-set(keys)),
        'inherited_theorem_and_proof_blocks':len(blocks),
        'missing_or_changed_inherited_blocks':[i for i,x in enumerate(blocks) if x not in s],
        'base_hashes_match':base_ok,'regression_provenance':reports,
        'latex_log_flags':log_flags,
        'new_ledger_entries':re.findall(r'^K(5[3-9]|6[01]) &',s,re.M)}
okay=not any(result[k] for k in ['duplicate_labels','missing_references','missing_citations','missing_or_changed_inherited_blocks','latex_log_flags']) and all(base_ok.values()) and all(x['status']=='PASS' and x['hash_matches'] for x in reports)
result['status']='PASS' if okay else 'FAIL'
(ROOT/'audit/static_source_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if okay else 1)
