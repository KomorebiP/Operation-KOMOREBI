# Proof Path Theory 1.2.0

**Komorebi P. — Operation Komorebi**

Certificates, compression, discovery fields, and mathematical memory.

A proof field retains a certified derivation together with recorded alternatives,
failed routes, examples, provenance, and candidate bridges. Retaining a failed
route does not certify that the target theorem is false or unprovable.

## This release

The complete manuscript is `docs/Proof_Path_Theory.pdf`. It preserves the previous
finite theory and adds a checked construction of local proof-field models as a
contravariant view system, an explicit equivalence with coherent realizations,
and a whole-justification-support gluing theorem. Pairwise dependency coverage is
shown insufficient for conjunctive proof steps.

General Lean results also cover protected linear realization, normalized dual
obstructions, affine-fiber classification, exact finite-field observation counts,
and the distinction between information-losing compression and lossless recoding.
A native Lean command exports the actual dependency metadata of five compiled
declarations. Their unexpanded dependencies remain explicit external leaves.

**Scope:** the Lean bridge is not a formalization of all 33 manuscript result
groups. The checked cardinality identity supports a written uniform-entropy
corollary. Semantic interpretations of arbitrary theorem labels, correctness of
all Python code, and correctness of the native exporter as a general metaprogram
are not claimed from these checks. The native export does not recover discovery
history or failed attempts.

## Read first

- `docs/Proof_Path_Theory.pdf`: complete revised manuscript.
- `docs/LEAN_GUIDE.md`: precise formal interfaces, trust boundaries and reproduction.
- `data/claim_ledger.csv`: all 33 result groups with verification categories.
- `evidence/lean/verification.json`: fresh builds, own-kernel replays, axiom audit,
  negative controls, source hashes and compiler/dependency pins.
- `data/release_verification.json`: full software, formal and publication checks.
- `data/bridge_verification.json`: exhaustive binary checks and native export audit.
- `PROGRESS_LEDGER_v1.2.0.md`: completed work, limits and restart point.

## Reproduce

Python requires version 3.10 or later and NumPy. Tests require pytest. Figure
regeneration requires matplotlib and networkx. The paper build requires a working
LaTeX installation and `pdfinfo`. Install these dependencies before an offline run.

```bash
python -m pip install -e . --no-build-isolation
python -m pytest
python examples/ambient_realization.py
python scripts/verify_release.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The full verifier never silently substitutes old evidence for a skipped Lean or
paper build. It rebuilds all eight project modules into an empty temporary
object directory, checks all nine dependency revisions, and runs the negative
controls. The supplied runtime must contain `toolchain/bin/lean`,
`toolchain/bin/leanchecker`, and the pinned cached workspace. It is distributed
separately and is not embedded in this source archive. The recorded formal run is
Linux x86-64. WSL is the intended Windows route; native Windows Lean replay was
not tested here.

For formal checks alone:

```bash
python scripts/verify_lean.py --runtime /path/to/portable-kit
```

For package construction without accessing a package index:

```bash
python scripts/build_release.py
```

The script uses a PEP 517 build without isolation when the frontend is installed,
otherwise the local setuptools fallback. The wheel includes the Python library
and schemas. The complete ZIP additionally includes the paper, Lean source,
examples, tests and evidence. The sdist omits the final package-verification
report because that report hashes the sdist itself; the complete ZIP carries it.

## Small executable bridge

```python
from proof_path_theory import load_proof_field, ProofFieldViews

field = load_proof_field("examples/and_dag.json")
views = ProofFieldViews(field)
assert views.least_model() == field.derive()

# A missing node in this closure concerns the declared rule system only.
for target in field.targets:
    assert views.countermodel(target) is None
```

`ProofFieldViews.to_view_system` can enumerate finite local models and build
literal inclusion restrictions. It enforces size caps. `glue` requires coverage
of each complete certified justification support and agreement on both true and
false overlap values. Those requirements cannot be replaced by author identity,
a vote, a positive certification string, or successful pairwise comparisons.

## Corrections in this edition

Information sufficiency for every predicate requires injectivity, not a verbatim
uncompressed file. Audit and discovery equivalence are not ordered unless their
task families are nested. JSON certification fields must be actual booleans:
`"false"` is rejected rather than treated as true. Binary arithmetic rejects
floating inputs before elimination. Empty view diagrams and empty fibers have
different, mathematically correct behavior.

The bundled hosted CI fragment runs Python and paper checks only. It does not
claim a fresh Lean run without the separately supplied runtime.

## License

No redistribution license has been selected by the author. `LICENSE_NOTICE.md`
retains this unresolved decision. Availability of the source is not described as
an unrestricted open-source license. Historical documents are preserved under
`historical/`; their old counts and limitations do not replace this release's
machine-readable records.
