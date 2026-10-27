# Verification summary — Sufficient Resolution v0.5.0

**Passed. 13 September 2026.**

| Check | Actual result |
|---|---|
| Fresh v0.4.0 source rebuild, axiom audit and same-kernel replay | Pass: 272 theorems, 357 names, 22 modules |
| Preserved v0.4.0 production proof files | All 22 byte-identical |
| Current clean source compilation, warnings as errors | Pass: all 30 modules and the import root |
| Current theorem/lemma declarations | 369, including 97 additions |
| Explicitly named declarations audited | 469, including 112 additions |
| Transitive axiom allowlist | Only propext, Classical.choice, Quot.sound |
| Same-kernel leanchecker replay | Pass: all 30 production modules |
| Deliberately false proof | Rejected |
| Deliberate placeholder | Rejected |
| Deliberate custom axiom | Detected and rejected by allowlist |
| New exact rational assertions | 2,127 pass in 32 systems and exact examples |
| New corrupted/invalid finite inputs | 15 rejected |
| Earlier exact example controls | All five pass |
| Earlier discrete memory controls | 1,307 assertions pass across 20 systems |
| Earlier observable-model controls | 1,657 assertions pass across 30 systems, 10 invalid inputs rejected |
| Earlier approximate-bound controls | 7,509 assertions pass across 30 systems and 370 words, 10 invalid inputs rejected |
| Extracted source-only package rebuild and axiom audit | Pass again: 369 theorems, 469 audited names |
| Extracted-source same-kernel replay | Pass again: all 30 modules |
| Identical execution inputs across both new runs | All 44 source/script/configuration files |
| Inputs unchanged during each run | Pass |
| Project-local v1 manifest validation | Both runs pass structure, result-hash and supplementary source-hash checks |

## What the finite controls test

`check_continuous_memory.py` uses fractions.Fraction with seed 20260913, visible and
hidden dimensions 0–3, Taylor coefficients through degree eight and mixed-time
degrees 0–4 in each variable. It compares the actual full-generator power coefficients
with a polynomial-antiderivative implementation of the Volterra convolution. It
includes arbitrary hidden initialization, zero-dimensional cases, finite moment
certificates, corrupted Taylor prefixes and the exact delayed-return example.
No floating exponential is called, no sampled flow is declared exactly equal, and
no universal statement is inferred from the finite tests.

## Formal trust boundary

Lean/Lake: 4.34.0-rc2. Lean commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib HEAD aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency HEADs
match lake-manifest.json. Imported compiled artifacts are reused, not independently
reconstructed. The project files are rebuilt and replayed with the same Lean kernel,
not an independently implemented checker or a comparator challenge.

Production proof sources contain no sorry, admit, custom axioms, unsafe declarations
or native_decide. Negative-control files deliberately contain rejected constructs
and are not production sources. Counts concern explicitly named declarations and
include supporting lemmas/examples, not independent discoveries.

The verifier runs one Lean thread, serial commands and a 180-second per-command
wall limit. No separate hard memory cap was imposed. Both manifests use the retained
version-1 provenance schema with supplementary before/after hashes. Validation uses
the preserved project-local validator, not a claim of upstream schema-v2 evidence.

## Evidence

`verification/release/report.json` and `verification/roundtrip/report.json` contain
actual command arrays, exit statuses, timings, source hashes and log paths.
`verification/ROUNDTRIP_SOURCE_MATCH_v0.5.0.json` records the 44 identical inputs.
`verification/PREDECESSOR_PRESERVATION_v0.5.0.json` records the 22 unchanged proof files.
`verification/PRINCIPAL_SIGNATURES_v0.5.0.log` prints actual major contracts.
`verification/CONTRACT_REVIEW_v0.5.0.md` explains what those contracts do and do not mean.
`verification/new_declarations_v0.5.0.json` and DECLARATION_INDEX_v0.5.0.csv give inventories.

The source checkpoint was extracted without .lake build objects. Its sources were
rebuilt and replayed. The final archive adds the resulting evidence and completed
documentation. Executed proof/test/configuration inputs remain byte-identical.
Final ZIP CRC and member SHA256 checks are recorded separately in the sibling
ARCHIVE_CHECK.json, so archive integrity is not confused with theorem verification.

## Failures and corrections

Drafts failed on targeted imports/API namespaces, a rational normed-algebra instance,
CLM/linear-map coercions, hidden-space instance unfolding, a scalar chain-rule
argument and product-derivative/extensionality syntax. These were corrected with
explicit type-correct constructions, without weakening intended theorem hypotheses
or disabling warning checks. A signature-printing option was unsupported and was
removed. Initial runtime-restoration invocation issues and a documentation string
quoting issue were corrected. Development diagnostics are retained.

No unresolved production compilation, axiom-audit, kernel-replay or rational-control
failure remains. The exact delayed-return counterexample is an intended mathematical
boundary result, not a failed implementation.

## Scope still open

Unbounded operators and domains, time-varying/nonlinear/stochastic dynamics,
continuous-time quantitative approximation, constrained realizability and arithmetic
existence remain outside this block. The derived Volterra equation holds for the
constructed full trajectory. Converse reconstruction of arbitrary Volterra solutions
is not separately formalized. Finite continuous certificates test exact derivatives
or generator moments, not sampled-time equality.
