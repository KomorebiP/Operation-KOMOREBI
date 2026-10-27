"""Pin the final raw sources and evidence of the independent quadratic audit."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
KIT = Path(sys.argv[1]).resolve()
MATHLIB = KIT / 'workspace/.lake/packages/mathlib'
NEW = ['QuadraticAlgebra', 'QuadraticCharacters', 'QuadraticRootCompletion',
       'QuadraticPacketBoundary', 'QuadraticGalois', 'QuadraticGaloisPackets',
       'QuadraticArithmeticCompletion']
REVIEWED = ['ArithmeticCertificateExample', 'CompletionExamples', 'Reconstruction', 'Compactness']
PRIMARY = [
    'Mathlib/RingTheory/AdjoinRoot.lean',
    'Mathlib/RingTheory/AdicCompletion/RingHom.lean',
    'Mathlib/Algebra/Group/Subgroup/Basic.lean',
    'Mathlib/FieldTheory/AbsoluteGaloisGroup.lean',
    'Mathlib/FieldTheory/Galois/Infinite.lean',
    'Mathlib/FieldTheory/KrullTopology.lean',
    'Mathlib/Algebra/Ring/Commute.lean',
    'Mathlib/NumberTheory/Padics/RingHoms.lean',
    'Mathlib/NumberTheory/Padics/PadicIntegers.lean',
    'Mathlib/RingTheory/Ideal/Quotient/Index.lean',
]

def record(path, base):
    return {'path': str(path.relative_to(base)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes': path.stat().st_size}

closure = set()
def visit(module):
    if module in closure:
        return
    closure.add(module)
    source = ROOT / 'lean/PaperX' / (module + '.lean')
    for dependency in re.findall(r'^import PaperX\.(\w+)', source.read_text(), re.M):
        visit(dependency)

for module in NEW:
    visit(module)
compiled = json.loads((ROOT / 'checks/quadratic_audit/compile.json').read_text())
assert compiled['passed'], 'No accepted independent compiler replay'
hashes = {x['module']: x['source_sha256'] for x in compiled['compilations']}
for module in NEW:
    assert hashes[module] == record(ROOT / 'lean/PaperX' / (module + '.lean'), ROOT)['sha256']
result = {
    'primary_verdict': 'proved as written',
    'scope': 'The seven explicit Block 21 quadratic-ring, fixed-kernel Galois-character, reduction, completion, and boundary statements. No full Paper X arithmetic claim is certified.',
    'new_production_sources': [record(ROOT / 'lean/PaperX' / (m + '.lean'), ROOT) for m in sorted(NEW)],
    'reviewed_predecessor_definition_sources': [record(ROOT / 'lean/PaperX' / (m + '.lean'), ROOT) for m in REVIEWED],
    'internal_dependency_source_closure': [record(ROOT / 'lean/PaperX' / (m + '.lean'), ROOT) for m in sorted(closure)],
    'primary_mathlib_source_files': [record(MATHLIB / p, MATHLIB) for p in PRIMARY],
    'mathlib_revision': 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
    'lean_binary_sha256': hashlib.sha256((KIT / 'toolchain/bin/lean').read_bytes()).hexdigest(),
    'evidence': [record(ROOT / p, ROOT) for p in [
        'checks/quadratic_audit/run.py', 'checks/quadratic_audit/source_manifest.py',
        'checks/quadratic_audit/compile.json', 'checks/quadratic_audit/BoundaryApplications.lean',
        'checks/quadratic_audit/BoundaryApplications.log',
        'checks/quadratic_audit/edge_development_attempt1.log', 'QUADRATIC_PROOF_AUDIT.md']],
    'source_stability': 'All seven production hashes match the accepted isolated compiler replay, which compared source hashes before and after execution.',
    'limitations': [
        'The internal dependency closure is pinned, but not every predecessor theorem is reaudited.',
        'Only the listed primary Mathlib definitions and decisive lemmas were inspected; the full library is pinned by revision.',
        'Independent exact computation is a separate audit; it is not a proof leaf of these Lean theorems.',
        'Temporary independent proof objects are discarded; the accepted replay log and source hashes are preserved.',
    ],
}
(ROOT / 'QUADRATIC_PROOF_AUDIT_SOURCES.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'new_modules': len(NEW), 'internal_closure': len(closure), 'source_hash_match': True}))
