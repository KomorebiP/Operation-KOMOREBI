#!/usr/bin/env python3
"""Inventory named source declarations and generate an exact-membership axiom audit."""
import json, re
from release_common_v040 import ROOT, RD, AUDITS, masked_lean, sha, write_json

def collect():
    entries = []
    rx = re.compile(r'^\s*(?:@\[[^\]]+\]\s*)*(?:(namespace)\s+(\S+)|(section)(?:[ \t]+(\S+))?|(end)(?:[ \t]+(\S+))?|((?:(?:private|protected|noncomputable|unsafe)\s+)*)(theorem|lemma)\s+([^\s(:]+))', re.M)
    old = json.loads((ROOT/'results/v0.39.0/declaration_inventory.json').read_text())
    old_private = {(r['module'], r['name']):r['qualified_name'] for r in old if r['private']}
    for path in sorted((ROOT/'AVOC').rglob('*.lean')):
        relative = path.relative_to(ROOT).as_posix()
        if relative in AUDITS: continue
        text = masked_lean(path.read_text()); stack = []; namespace = ''; matched = []
        for match in rx.finditer(text):
            if match.group(1):
                stack.append(namespace); namespace = '.'.join(filter(None, [namespace, match.group(2)]))
            elif match.group(3): stack.append(namespace)
            elif match.group(5):
                if stack: namespace = stack.pop()
            else:
                private = 'private' in match.group(7).split()
                qualified = '.'.join(filter(None, [namespace, match.group(9)]))
                if private:
                    module = str(path.relative_to(ROOT).with_suffix('')).replace('/', '.')
                    qualified = old_private.get((relative, match.group(9)), f'_private.{module}.0.{qualified}')
                token_position = text.find(match.group(8), match.start(), match.end())
                matched.append(token_position)
                entries.append(dict(module=relative, line=text[:token_position].count('\n')+1,
                                    kind=match.group(8), name=match.group(9), qualified_name=qualified, private=private))
        declared = [match.start() for match in re.finditer(r'\b(?:theorem|lemma)\b', text)]
        if declared != matched: raise RuntimeError(f'Unrecognized theorem/lemma source syntax in {relative}: {set(declared)-set(matched)}')
    names = [r['qualified_name'] for r in entries]
    if len(names) != len(set(names)): raise RuntimeError('Duplicate declaration inventory names')
    if set(r['qualified_name'] for r in old)-set(names): raise RuntimeError('Inherited named declarations are missing')
    return entries, old

def main():
    entries, old = collect(); old_names = {r['qualified_name'] for r in old}
    new = [r for r in entries if r['qualified_name'] not in old_names]
    write_json(RD/'declaration_inventory.json', entries); write_json(RD/'new_inventory_entries.json', new)
    audit = 'import AVOC\n\n' + ''.join('#print axioms ' + r['qualified_name'] + '\n' for r in entries if not r['private'])
    private_names = [r['qualified_name'] for r in entries if r['private']]
    audit += '\nopen Lean Elab Command\nrun_cmd do\n  let env ← getEnv\n  let names : List String := ' + json.dumps(private_names)
    audit += '\n  let mut found := 0\n  for (name, _) in env.constants.toList do\n    if names.contains name.toString then\n      found := found + 1\n      let axioms ← collectAxioms name\n      logInfo m!"\'{name.toString}\' depends on axioms: {axioms.qsort Name.lt |>.map MessageData.ofConstName |>.toList}"\n  unless found = ' + str(len(private_names)) + ' do throwError "private declaration inventory mismatch"\n'
    (ROOT/'AVOC/FullAudit.lean').write_text(audit)
    lines = ['# AVOC v0.40.0 theorem index', '', f'{len(entries)} named theorem/lemma declarations, including explicit private helpers.',
             'These are source declarations, not a count of independent mathematical discoveries.', '']
    last = None
    for record in entries:
        if record['module'] != last: last=record['module']; lines += ['', '## '+last, '']
        lines.append(f"- `{record['qualified_name']}` (source line {record['line']})")
    (ROOT/'THEOREM_INDEX.md').write_text('\n'.join(lines)+'\n')
    sources = sorted({r['module'] for r in entries})
    summary = dict(total_named_theorems=len(entries), old_reported_inventory=len(old),
                   new_theorems=len(new), new_private_helpers=sum(r['private'] for r in new),
                   non_audit_modules=len([p for p in (ROOT/'AVOC').rglob('*.lean') if p.relative_to(ROOT).as_posix() not in AUDITS]),
                   source_sha256={source:sha(ROOT/source) for source in sources})
    write_json(RD/'source_counts.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='source_sha256'}, indent=2))
if __name__ == '__main__': main()
