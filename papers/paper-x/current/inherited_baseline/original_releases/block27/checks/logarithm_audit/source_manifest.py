"""Record exact source revisions used by the independent algebraic proof audit."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
KIT = Path(sys.argv[1]).resolve()
MATHLIB = KIT/'workspace/.lake/packages/mathlib'

def record(path, base):
    return {'path':str(path.relative_to(base)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes':path.stat().st_size}

new = json.loads((ROOT/'provenance.json').read_text())['new_modules']
reviewed = ['NilpotentExponential', 'WeilData', 'MonodromyReconstruction',
            'ReconstructionRecovery', 'WeilMorphisms', 'SpecialMonodromy',
            'ReconstructionBoundary', 'ReconstructionExamples', 'AffineMonodromy', 'WeilSpecialChain']
primary_mathlib = [
 'Mathlib/RingTheory/Nilpotent/Defs.lean',
 'Mathlib/RingTheory/Nilpotent/Exp.lean',
 'Mathlib/RingTheory/PowerSeries/Log.lean',
 'Mathlib/RingTheory/PowerSeries/Substitution.lean',
 'Mathlib/RingTheory/Adjoin/Polynomial/Basic.lean',
 'Mathlib/Algebra/Algebra/Rat.lean',
 'Mathlib/GroupTheory/OrderOfElement.lean',
 'Mathlib/RepresentationTheory/Basic.lean']
closure = set()

def visit(m):
    if m in closure:
        return
    closure.add(m)
    path=ROOT/'lean/PaperX'/f'{m}.lean'
    for dep in re.findall(r'^import PaperX\.(\w+)',path.read_text(), re.M):
        visit(dep)

for m in new:
    visit(m)
compiled = json.loads((ROOT/'checks/logarithm_audit/compile.json').read_text())
assert compiled['passed'], 'No successful independent compile'
compiled_hashes = {x['module']:x['source_sha256'] for x in compiled['compilations']}
for m in new:
    assert compiled_hashes[m] == record(ROOT/'lean/PaperX'/f'{m}.lean',ROOT)['sha256']
result = {
 'primary_verdict':'proved as written',
 'scope':'Formal algebraic statements of the listed Block 20 modules under their explicit hypotheses; no full arithmetic theorem certification.',
 'new_production_sources':[record(ROOT/'lean/PaperX'/f'{m}.lean',ROOT) for m in sorted(new)],
 'reviewed_predecessor_definition_sources':[record(ROOT/'lean/PaperX'/f'{m}.lean',ROOT) for m in reviewed],
 'internal_dependency_source_closure':[record(ROOT/'lean/PaperX'/f'{m}.lean',ROOT) for m in sorted(closure)],
 'primary_mathlib_source_files':[record(MATHLIB/p,MATHLIB) for p in primary_mathlib],
 'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
 'lean_binary_sha256':hashlib.sha256((KIT/'toolchain/bin/lean').read_bytes()).hexdigest(),
 'evidence':[record(ROOT/p,ROOT) for p in ['checks/logarithm_audit/BoundaryApplications.lean',
    'checks/logarithm_audit/run.py','checks/logarithm_audit/compile.json',
    'checks/logarithm_audit/compile_attempt1.json','checks/logarithm_audit/import_path_failure.log',
    'checks/logarithm_audit/attempt2_failure.json',
    'checks/logarithm_audit/source_manifest.py','LOGARITHM_PROOF_AUDIT.md']],
 'source_stability':'All new source hashes match the completed independent isolated compilation records.',
 'limitations':['The entire Mathlib transitive source tree is pinned by its project revision, not individually reread.',
               'The internal source closure is hashed for provenance; not every predecessor proof was reaudited.',
               'Computation evidence is audited separately and is not a proof leaf of the Lean theorems.']}
(ROOT/'LOGARITHM_PROOF_AUDIT_SOURCES.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'new_modules':len(new),'internal_closure':len(closure),'source_hash_match':True}))
