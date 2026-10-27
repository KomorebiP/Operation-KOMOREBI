"""Check register completeness, references, source identity and an acyclic map.

This is a document/code linkage audit, not a proof checker.
"""
from pathlib import Path
import ast, hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    reg=json.loads((ROOT/'PROOF_REGISTER.json').read_text())
    text=(ROOT/'theory/FOUNDATIONS.md').read_text()
    if reg['source_sha256']!=digest(ROOT/'theory/FOUNDATIONS.md'): raise ValueError('Manuscript changed after register generation.')
    spans={int(m.group(1)):m.group(0) for m in re.finditer(r'\*\*Proposition (\d+)\..*?\\square\$',text,re.S)}
    entries={x['id']:x for x in reg['entries']}
    if set(entries)!=set(range(1,88)) or set(spans)!=set(entries) or len(reg['entries'])!=87:
        raise ValueError('The register must cover 87 unique propositions.')
    for i,x in entries.items():
        if x['statement_proof_sha256']!=hashlib.sha256(spans[i].encode()).hexdigest(): raise ValueError(f'P{i} span hash mismatch.')
        deps=x['principal_internal_dependencies']
        if any(d not in entries or d==i for d in deps): raise ValueError(f'P{i} has an invalid dependency.')
        for field in ['related_suite','implementation']:
            item=x[field]
            if item is None:continue
            p=ROOT/item['path']
            if not p.resolve().is_relative_to(ROOT.resolve()) or digest(p)!=item['sha256']:raise ValueError(f'Code link mismatch P{i}')
            if 'symbol' in item:
                matches=[n for n in ast.parse(p.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==item['symbol']]
                if len(matches)!=1 or (matches[0].lineno,matches[0].end_lineno)!=(item['start_line'],item['end_line']):raise ValueError(f'Code symbol mismatch P{i}')
    seen=set(); active=set(); order=[]
    def visit(i):
        if i in active:raise ValueError('Dependency cycle.')
        if i in seen:return
        active.add(i)
        for d in entries[i]['principal_internal_dependencies']:visit(d)
        active.remove(i);seen.add(i);order.append(i)
    for i in entries:visit(i)
    scenarios=json.loads((ROOT/'SCENARIO_REGISTER.json').read_text())
    for scenario in scenarios['scenarios']:
        if any(p not in entries for p in scenario['propositions']):raise ValueError('Invalid scenario reference.')
        for name in scenario.get('programs',[]):
            if not (ROOT/name).is_file():raise ValueError('Missing scenario program: '+name)
    report={'version':'1.0.0','passed':True,'propositions':87,
        'principal_dependency_edges':sum(len(x['principal_internal_dependencies']) for x in entries.values()),
        'implementation_links':sum(x['implementation'] is not None for x in entries.values()),
        'acyclic':True,'topological_order':order,'scenario_count':len(scenarios['scenarios']),
        'proof_kernel_run':False,'complete_formal_proof_graph':False}
    (ROOT/'verification/proof_register_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
