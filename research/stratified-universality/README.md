# Stratified Universality for Resolved Representations

**Author:** Komorebi P.  
**Edition:** Final Publication Edition, 6 October 2026  
**Mathematical base:** Formal Foundations v2.0.0, with the release amendments documented below.

The canonical reading set consists of:

1. `traditional/Stratified_Universality_Traditional.pdf`: the complete traditional manuscript, including the amended 75-component concordance.
2. `visual/Stratified_Universality_Visual_Guide.pdf`: a standalone illustrated companion with checked examples and manuscript-label correspondence.
3. `lean/Stratified_Universality_Lean_Guide.pdf`: inspected Lean source, recorded formalization evidence, coverage boundaries, and an explicit formalization concordance.

The TeX sources, guide Markdown files, figure generators, exact examples, data, validation scripts, review records and inherited Markdown notes are included. The complete unmodified 397-member v2.0.0 source archive, including its 72 Markdown files, is retained in `provenance/`. Extract that archive to inspect the original repository-level documentation, scripts, standalone notes and figures. The `traditional/` directory also supplies the complete manuscript source tree for the amended edition.

## Mathematical scope

The paper develops finite, profiled resolved representations, lane transport, holonomy-compatible sections, task-relative semantic quotients, carrier and observer change, exact loss, admissibility-relative obstruction and doctrine lifting. The preservation profile, continuation grammar, observation family, carrier law and descent hypotheses remain part of each theorem.

The 75 concordance components retain their original status distribution: 52 internally proved, 12 classical imported/reinterpreted, 2 conditional, 3 framework, and 6 conjectural. These are component classifications, not a count of independently new theorems or a completion percentage. The final source gives the corrected hypotheses and proofs; `reviews/MATHEMATICAL_SCOPE_REVIEW.md` identifies the exact release-review coverage.

Five amendment groups distinguish this edition from the frozen mathematical base:

- Nonempty monodromy support is separated from a selector acting nonzero on compatible sections.
- Observer packet updates use finite branches and finite raw-history aggregation, with explicit empty sums and empty convex packets.
- The escape proof uses an attained positive minimum on each compact conditioned sublevel.
- The greatest-fixed-point proof and finite stabilization argument use the correct containment implications.
- Metric statements use positive dimension, explicit determinant normalization, inverse traversal and an explicit spanning-tree construction.

These amendments do not supply unrestricted atlas effectivity, cross-doctrine equivalences or missing enrichment/lifting data. Original sources, result files and status records remain distinguishable from the amended release files.

## Verification

Fresh replay of the three principal exact Python suites completed with zero failures:

| Suite | Assertions |
|---|---:|
| Finite lane transport, Block 15 | 197,099 |
| Holonomy-twisted lane transport, Block 16 | 1,344,823 |
| Semantic extension, Block 17 | 3,022 |
| Total | 1,544,944 |

The scientific JSON outputs match the inherited records byte-for-byte. The computation manifests record inputs, outputs, bounds, seeds, environment and execution times. These are finite implementation regressions. They do not replace the universal written arguments or certify the release amendments through source-label checks.

The Lean guide distinguishes the inspected standalone core source from the historical v0.7 normalization package. The matching archives could not be retrieved because their downloads returned HTTP 502. The included standalone `.lean` source was reconstructed from a complete authoritative text read, with the recorded byte-count check. No fresh Lean compilation or full-monograph Lean certificate is claimed. See the guide and its provenance records for exact coverage and unavailable material.

## Rebuild and replay

To compile the three PDFs with a suitable TeX installation:

```bash
python3 build_release.py
```

The supplied figures are sufficient for compilation. Figure regeneration commands are documented beside the companion sources. TeX dependencies are those imported in each document preamble; the upstream build notes remain available in the frozen source archive.

To replay the exact validators with Python and the listed dependencies:

```bash
python3 -m pip install -r requirements.txt
python3 replay_validators.py
```

The replay script uses isolated frozen implementation inputs and writes a new `user_replays/` directory. It leaves inherited reports unchanged. To check the archived execution hashes without rerunning the suites:

```bash
python3 verification/validate_archived_hashes.py
```

Compilation and Python replay do not run Lean. Archived upstream scripts whose filenames refer to older editions remain provenance; use the root build command for the amended canonical documents.

## Attribution and permissions

Author attribution remains Komorebi P. The original interim license and other upstream notices are preserved in the source archive. This private final-edition handoff does not silently replace those distribution terms or publish a repository.
