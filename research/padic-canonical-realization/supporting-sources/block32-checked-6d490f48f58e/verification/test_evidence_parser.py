from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_release import parse_declared_axioms
text="""'A' depends on axioms: []
'B' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'C' does not depend on any axioms
'D' depends on axioms: [Quot.sound]
"""
assert parse_declared_axioms(text)=={'A':set(),'B':{'propext','Classical.choice','Quot.sound'},'C':set(),'D':{'Quot.sound'}}
try:
    parse_declared_axioms("'A' depends on axioms: []\n'A' depends on axioms: []\n")
except ValueError:pass
else:raise AssertionError('duplicate accepted')
assert parse_declared_axioms("'A' depends on axioms: [propext\n'B' depends on axioms: []\n")=={'B':set()}
root=Path(__file__).resolve().parents[1]
record=parse_declared_axioms((root/'results/final_declared_axioms.log').read_text())
expected=json.loads((root/'verification/theorem_inventory.json').read_text())['names']
assert set(record)==set(expected)
print(f'PASS: wrapping, empty lists, axiom-free records, duplicates, truncation, full {len(expected)} declaration coverage')
