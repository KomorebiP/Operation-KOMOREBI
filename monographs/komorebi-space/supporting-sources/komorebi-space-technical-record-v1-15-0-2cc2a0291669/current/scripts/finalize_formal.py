"""Integrate only a successful frozen fresh replay into publication metadata."""
from pathlib import Path
import collections
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / 'publication'
RUN = ROOT / 'runs/clean_01'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n')

receipt = json.loads((RUN/'receipt.json').read_text())
assert receipt['status'] == 'PASS'
assert receipt['compile_targets'] == 166
assert receipt['production_modules'] == 162
assert receipt['control_counts'] == {'accept': 18, 'elaboration_reject': 35, 'policy_reject': 3}
assert len(receipt['controls']) == 56 and all(c['passed'] for c in receipt['controls'])
inventory = json.loads((RUN/'declarations.json').read_text())
assert not inventory['rejected']
assert sha(RUN/'declarations.json') == receipt['declarations_sha256']
rows = {r['name']: r for r in inventory['declarations']}
assert len(rows) == inventory['count'] == receipt['exported_declarations']

for proposal in ['book_audit_paragraph_proposal.txt', 'public_docs_proposal.json']:
    p = ROOT/'records'/proposal
    if not p.exists():
        raise FileNotFoundError(p)
    d = json.loads(p.read_text())
    for change in d['replacements']:
        target = PUB/change['file']
        old = target.read_text()
        assert old.count(change['old']) == 1, (proposal, change['file'], change['old'][:80])
        new = change['new'].replace('{{EXPORTED_DECLARATIONS}}', f"{len(rows):,}")
        target.write_text(old.replace(change['old'], new))

p = PUB/'source/Komorebi_Space_Monograph.tex'
s = p.read_text()
old = 'This includes the actual infinite diagonal family and its tail bounds, the sharp asymptotic over all real budgets, and the rounded noisy diagonal rate.'
new = 'This includes the actual infinite diagonal family and its tail bounds, the sharp asymptotic over all real budgets, the rounded noisy and inexact rates, and the concrete nonclosed-range example.'
assert s.count(old) == 1
s = s.replace(old, new)
old = "This edition brings together the accepted foundational source and the verified infinite diagonal extension. Their compilation and audit records are retained separately. Both default entry points built successfully for this edition. Lean's compiler and kernel, its stated standard axioms, and the pinned external dependency cache remain part of the trust boundary. Appendix~\\ref{app:written} gives the exact counts and their interpretation."
new = "The complete source has passed a fresh integrated compilation, declaration audit, and diagnostic-control replay. The earlier records remain available as historical evidence. Lean's compiler and kernel, its stated standard axioms, and the pinned external dependency cache remain part of the trust boundary. The cache is recorded but was not rebuilt by this audit. Appendix~\\ref{app:written} gives the exact counts and their interpretation."
assert s.count(old) == 1
p.write_text(s.replace(old, new))

p = PUB/'source/Komorebi_Space_Lean_Guide.tex'
s = p.read_text()
for old, new in [
    ('The accepted declaration inventories contain', 'The integrated declaration inventory contains'),
    ('The two entrypoints retain the separately verified general and diagonal source interfaces.', 'The two entrypoints expose the general and diagonal source interfaces.'),
    ('The actual infinite diagonal model, its quantitative bounds, its sharp budget asymptotic, and its rounded noisy parameter rate.', 'The actual infinite diagonal model, its quantitative bounds, its sharp budget asymptotic, its rounded noisy and inexact rates, and its range obstruction.')
]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
p.write_text(s)
p = PUB/'README.md'
p.write_text(p.read_text().replace('with new graphics, parameter changes', 'with graphics, parameter changes').replace('uses new worked examples and visual comparisons', 'uses worked examples and visual comparisons'))

mapping = json.loads((PUB/'verification/LEAN_THEOREM_MAP.json').read_text())
checks = []
for entry in mapping['entries']:
    row = rows[entry['declaration']]
    source = PUB/entry['source']
    assert row['module'] == entry['module']
    assert row['kind'] == entry['kind']
    assert sha(source) == entry['source_sha256']
    name = entry['declaration'].split('.')[-1]
    assert re.search(r'\b'+re.escape(name)+r'\b', source.read_text().splitlines()[entry['source_line']-1])
    checks.append({'declaration': entry['declaration'], 'module': row['module'], 'source_hash_and_line_match': True})
assert len(checks) == mapping['entry_count'] == 114

stats = {'EditionProductionModules':'162', 'EditionRoots':'4', 'EditionTargets':'166',
         'EditionTheorems':'1,859', 'EditionDeclarations':f'{len(rows):,}',
         'EditionControls':'56', 'EditionPositiveControls':'18', 'EditionNegativeControls':'35',
         'EditionPolicyControls':'3', 'EditionVerifiedGroups':'16', 'EditionWrittenGroups':'0',
         'EditionPrincipalGroups':'16', 'EditionSelectedMapEntries':'114'}
aliases = {'EditionEntrypoints':'EditionRoots', 'EditionExplicitTheorems':'EditionTheorems',
           'EditionExportedDeclarations':'EditionDeclarations'}
(PUB/'source/edition_stats.tex').write_text('% Fresh integrated verification totals for publication v1.15.0.\n' +
    ''.join('\\newcommand{\\'+key+'}{'+value+'}\n' for key,value in stats.items()) +
    ''.join('\\newcommand{\\'+key+'}{\\'+value+'}\n' for key,value in aliases.items()))

current = PUB/'verification/current'
current.mkdir(parents=True, exist_ok=True)
shutil.copy2(RUN/'receipt.json', current/'INTEGRATED_REPLAY.json')
shutil.copy2(RUN/'declarations.json', current/'DECLARATIONS.json')
save(current/'THEOREM_MAP_CHECK.json', {'status':'PASS', 'method':'Match names, defining modules, declaration kinds, exact source hashes and source lines against the fresh complete Lean environment inventory.', 'entries':checks, 'map_sha256':sha(PUB/'verification/LEAN_THEOREM_MAP.json'), 'inventory_sha256':sha(RUN/'declarations.json')})
save(ROOT/'records/formal_integration.json', {'status':'PASS', 'receipt_sha256':sha(RUN/'receipt.json'), 'exported_declarations':len(rows), 'module_counts':dict(collections.Counter(r['module'] for r in rows.values())), 'applied_proposals':['book_audit_paragraph_proposal.txt','public_docs_proposal.json'], 'additional_edits':['Monograph preface coverage and audit paragraph','edition_stats.tex'], 'theorem_map_entries':len(checks)})
print(json.dumps({'status':'PASS', 'exported_declarations':len(rows),'map_entries':len(checks)}))
