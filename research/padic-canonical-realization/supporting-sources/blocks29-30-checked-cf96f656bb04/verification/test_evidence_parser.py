from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from verify_release import parse_kernel_axioms
rows=parse_kernel_axioms('PROJECT_AXIOMS foo | Module | \nPROJECT_AXIOMS bar | Module | propext,Quot.sound\nPROJECT_AXIOMS baz | Module |\n')
assert rows==[('foo','Module',[]),('bar','Module',['propext','Quot.sound']),('baz','Module',[])]
for invalid in ['PROJECT_AXIOMS | Module |','PROJECT_AXIOMS name | |','PROJECT_AXIOMS missing','PROJECT_AXIOMS foo | M |\nPROJECT_AXIOMS foo | M |']:
 try:parse_kernel_axioms(invalid)
 except ValueError:pass
 else:raise AssertionError('Malformed or duplicate inventory was accepted')
p=ROOT/'results_current/final_kernel_inventory.log'
rows=parse_kernel_axioms(p.read_text());expected=set(json.loads((ROOT/'verification/theorem_inventory.json').read_text())['names'])
assert expected<={n for n,m,a in rows}
assert len(rows)==2024
assert set().union(*(set(a) for n,m,a in rows))<={'propext','Classical.choice','Quot.sound'}
print(json.dumps({'status':'PASS','parsed_project_theorem_constants':len(rows),'declared_theorems':len(expected),'empty_axiom_lists':sum(not a for n,m,a in rows)},indent=2))
