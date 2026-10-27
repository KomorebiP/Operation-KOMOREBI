#!/usr/bin/env python3
"""Minimal static policy checks. Cannot type-check, elaborate or kernel check Lean."""
from pathlib import Path
import hashlib,json,re,sys
root=Path(__file__).resolve().parents[1]
paths=sorted((root/'formal/drafts').glob('*.lean'))
words=re.compile(r'(?m)^\s*(?:sorry|admit|axiom|unsafe\s+(?:def|theorem)|opaque\b|set_option\s+autoImplicit\s+true)\b')
rows=[];issues=[]
for p in paths:
    s=p.read_text()
    found=[m.group(0).strip() for m in words.finditer(s)]
    main_imports=re.findall(r'^import (.+)$',s,re.M)
    rows.append({'path':str(p.relative_to(root)),'lines':len(s.splitlines()),'sha256':hashlib.sha256(s.encode()).hexdigest(),
                 'local_proof_declarations':len(re.findall(r'^theorem\b|^@\[simp\] theorem\b',s,re.M)),
                 'imports':main_imports,'forbidden':found})
    issues+=['forbidden lexical declaration in '+p.name+': '+x for x in found]
for p in [root/'formal/current/PaperIIIContinuation.lean',root/'formal/current/KomorebiPaperIII.lean']:
    t=p.read_text()
    for draft in paths:
        if draft.stem in t: issues.append('draft imported by production root: '+draft.name)
result={'schema':'paper-iii-section17-static-source/1','status':'PASS_STATIC_ONLY' if not issues else 'FAIL',
        'compiler_executed':False,'kernel_replay_executed':False,'axiom_audit_executed':False,
        'source_files':rows,'errors':issues,
        'limitation':'Lexical tests do not establish Lean syntax, elaboration, logical soundness, semantic correspondence or compiler acceptance.'}
out=root/'evidence/section17/static_lean_source_audit.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2))
print(json.dumps({'status':result['status'],'source_files':len(rows),'errors':issues},indent=2))
sys.exit(bool(issues))
