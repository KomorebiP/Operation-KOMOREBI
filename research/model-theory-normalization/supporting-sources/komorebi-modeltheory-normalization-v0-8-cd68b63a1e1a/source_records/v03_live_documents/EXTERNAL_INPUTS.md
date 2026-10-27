# External and inherited inputs

## Immutable project parents

Both originals are retained verbatim in `history/`. Hashes and source provenance
are recorded in `source_records/PREDECESSORS.json` and `INPUT_LINEAGE.json`.

* Model-Theory Normalization v0.2: tagged state/value language; standard Mathlib
  truth translation; local finite-code certificate and standard definability.
* Representation Calculus v0.4: semiring matrix operations, witnessed row
  certificates, all-state/all-word exact behavior, actual encoded image, Smith
  image certificates and growth witnesses. Four matrix modules are imported here.
  The parent's general arithmetic minimum-coordinate modules are retained in the
  frozen archive but not rebuilt by this new bridge.

The shared RepresentationCore and FiniteCertificates modules were identical in
both parents. Their bytes are preserved, not independently rewritten copies of
semantically similar definitions.

## Pinned upstream proof library

Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

The parent source hashes for Mathlib ModelTheory Basic, Syntax, Semantics,
Complexity, and Definability are checked again before accepted execution.
`evidence/ENVIRONMENT_VERIFIED.json` records the actual runtime identity and limits.

The new proofs use standard FirstOrder.Language terms/formulas, interpretation
of those objects, IsQF, Set.Definable and Set.TermDefinable. They use no external
mathematical result asserting the correctness of the proposed matrix-to-code
bridge. The bridge is constructed from the pinned parent theorems and explicit
matrix certificate hypotheses.

Primary documentation consulted for the meaning of the existing standard APIs:

* https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Definability.html
* https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Semantics.html

Those public pages can change. The build and theorem interpretation are pinned to
the local source revision and hashes, not to an assumed current documentation
version. This is a source/application check, not a historical novelty survey.

## Trust boundary

Lean checks the literal source emitted into each generated file, using the pinned
upstream cache. The source transcription is independently tested against the
expected JSON; this does not prove that an informal real-world problem was
translated to that JSON correctly. The authoring review is self-review, not a
separate referee or independent agent. Standard ingredients and previous project
results are not presented as newly invented here.
