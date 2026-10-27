#!/usr/bin/env python3
"""Static source and Block 11 theorem-preservation audit for Block 12."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

DECL = re.compile(r"^\s*(?:@\[[^\]]+\]\s*)*(?:protected\s+)?(theorem|lemma|def|structure)\s+([A-Za-z0-9_'.]+)", re.MULTILINE)
THEOREM_START = re.compile(r"^\s*(?:@\[[^\]]+\]\s*)*(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)\b")
BAD = {
    'sorry': re.compile(r'\bsorry\b'),
    'admit': re.compile(r'\badmit\b'),
    'axiom': re.compile(r'^\s*axiom\s+', re.MULTILINE),
}
LOCAL_IMPORT = re.compile(r'^import\s+(KomorebiPadic(?:\.[A-Za-z0-9_\']+)?)\s*$', re.MULTILINE)
EXPECTED_NEW = {
    'quotientSearchBound_sub_one',
    'lastRadixBlockQuotient_at_searchBound',
    'lastRadixBlockQuotient_at_searchBound_explicit',
    'lastRadixBlockQuotient_at_searchBound_le',
    'coarseRadixDepth_zero_base',
    'coarseRadixDepth_one_base',
    'maximumLayerCompilerPrimeEnvelopeBound_eq_parameterEnvelopeBound',
    'compilerEnvelopeFromCoarseK_mono',
    'coarseK_le_precision_sub_one',
    'maximumLayerCompilerParameterEnvelopeBound_le_rawPrecisionBound',
    'maximumLayerCompilerTotalTests_le_parameterEnvelopeBound',
    'maximumLayerCompilerTotalTests_le_parameterEnvelopeBound_explicit',
    'maximumLayerCompilerTotalTests_le_rawPrecisionBound',
    'maximumLayerCompilerTotalTests_le_rawPrecisionBound_explicit',
}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def theorem_headers(lean_root: Path) -> dict[str, dict[str, str]]:
    out = {}
    for path in sorted((lean_root / 'KomorebiPadic').glob('*.lean')):
        lines = path.read_text(encoding='utf-8').splitlines()
        i = 0
        while i < len(lines):
            m = THEOREM_START.match(lines[i])
            if not m:
                i += 1; continue
            name = m.group(1); acc = [lines[i]]
            while ':=' not in acc[-1]:
                i += 1
                if i >= len(lines): raise RuntimeError(f'unterminated theorem header {name} in {path}')
                acc.append(lines[i])
            out[name] = {
                'header': ' '.join('\n'.join(acc).split(':=', 1)[0].split()),
                'file': str(path.relative_to(lean_root.parent)),
            }
            i += 1
    return out

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    lean_root = root / 'lean'
    snapshot_path = root / 'predecessor' / 'BLOCK11_THEOREM_HEADERS.json'
    snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
    old_headers = snapshot['headers']
    files = sorted(lean_root.rglob('*.lean'))
    modules = {}
    for path in files:
        rel = path.relative_to(lean_root).with_suffix('')
        modules['.'.join(rel.parts)] = path
    declarations=[]; violations=[]; missing_imports=[]; imports={}
    for module,path in modules.items():
        text=path.read_text(encoding='utf-8')
        for kind,name in DECL.findall(text): declarations.append({'module':module,'kind':kind,'name':name})
        for label,pattern in BAD.items():
            if pattern.search(text): violations.append({'module':module,'kind':label})
        local=LOCAL_IMPORT.findall(text); imports[module]=local
        for imported in local:
            if imported not in modules: missing_imports.append({'module':module,'missing':imported})
    cycles=[]; visiting=[]; visited=set()
    def dfs(module:str)->None:
        if module in visiting:
            i=visiting.index(module); cycles.append(visiting[i:]+[module]); return
        if module in visited: return
        visiting.append(module)
        for dep in imports.get(module,[]):
            if dep in modules: dfs(dep)
        visiting.pop(); visited.add(module)
    for module in modules: dfs(module)
    root_imports=set(imports.get('KomorebiPadic',[]))
    production_modules={m for m in modules if m!='KomorebiPadic'}
    missing_from_root=sorted(production_modules-root_imports)
    by_kind={}
    for d in declarations: by_kind[d['kind']]=by_kind.get(d['kind'],0)+1
    names=[d['name'] for d in declarations]
    duplicate=sorted({n for n in names if names.count(n)>1})
    new_headers=theorem_headers(lean_root)
    missing_old=sorted(set(old_headers)-set(new_headers))
    changed_old=[{'name':n,'predecessor':old_headers[n],'block12':new_headers.get(n)} for n in sorted(set(old_headers)&set(new_headers)) if old_headers[n]['header']!=new_headers[n]['header']]
    added=sorted(set(new_headers)-set(old_headers))
    expected_checks={
        'lean_file_count':len(files)==19,
        'predecessor_theorem_count':len(old_headers)==165,
        'block12_theorem_count':len(new_headers)==179,
        'new_theorems_exact':set(added)==EXPECTED_NEW,
        'new_module_present':'KomorebiPadic.RepresentativeBudgetParameterEnvelope' in modules,
        'new_module_imported':'KomorebiPadic.RepresentativeBudgetParameterEnvelope' in root_imports,
    }
    passed=not(violations or missing_imports or cycles or missing_from_root or duplicate or missing_old or changed_old) and all(expected_checks.values())
    report={
        'schema':'komorebi-padic-block12-static-source-audit-v1',
        'status':'PASS' if passed else 'FAIL',
        'lean_file_count':len(files),'module_count':len(modules),'declaration_counts':by_kind,'declaration_total':len(declarations),
        'placeholder_or_axiom_violations':violations,'missing_local_imports':missing_imports,'local_import_cycles':cycles,'missing_root_imports':missing_from_root,'duplicate_declarations':duplicate,
        'predecessor_theorem_count':len(old_headers),'predecessor_snapshot_sha256':sha256(snapshot_path),'block12_theorem_count':len(new_headers),
        'missing_predecessor_theorems':missing_old,'changed_predecessor_theorem_statements':changed_old,'added_theorems':added,'expected_new_theorems':sorted(EXPECTED_NEW),'expected_checks':expected_checks,
        'files':[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in files],
    }
    out=root/'results'/'static_source_audit_block12.json'; out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2,sort_keys=True))
    return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
