# Komorebi Space — Lean progress v1.11.0

Accepted checkpoint: **KS-v1.11.0-WR08-WR09-WR16-complete**. Parent: v1.10.0. Acceptance recorded 2026-10-12T22:48:48.253414+00:00.

## Completed in Lean

| Group | Result |
| --- | --- |
| WR08 | Full regularization alternative: fitted images approach the projection, residual norms approach the floor, weighted penalty vanishes, corrections converge strongly to the constructed unique minimum-norm preimage when attained, and norms tend to infinity otherwise. |
| WR09 | Sharp coefficient proved with a scalar operator, plus convergence for the entire positive noise-level family under the stated parameter rule. |
| WR16 | Strong convergence of inexact proposals, with the full three-term error certificate at every index. |

The three modules add **31 explicit theorems and 33 named public declarations**. They use the full positive real-parameter filter and the existing actual Hilbert norms. No closed-range, finite-dimensionality, separability, injectivity, or zero-floor assumption was added. WR09 includes the scalar sharpness clause; completing only its limiting statement would have left the group incomplete.

## Verification

- Fresh cumulative compilation: **154 targets**, comprising **151 production modules and three roots**, from an empty project object directory.
- Cumulative explicit theorem/lemma count: **1,650**. Complete environment audit: **4,982 declarations**, including **47 new declarations** and every one of the 4,935 inherited identities.
- Only `propext`, `Classical.choice`, and `Quot.sound` occur in the accepted axiom union.
- **39 control files**: 12 positive, 25 intended compiler rejections, and 2 policy rejections. All **231 recorded commands** passed their required outcomes.
- Independent printed/source and complete exported-type review passed, followed by independent terminal evidence reconstruction. Sources, project objects and **130,284 runtime/cache files** passed the recorded endpoint checks.

## Mistakes found and corrected

The mathematical arguments did not need weaker targets. Numbered attempts preserve compiler failures involving deprecated API names, type inference, strict linting, documentation placement, scalar simplification, and triangle-inequality expression order, followed by their corrected successful attempts. Positive controls also exposed simplification and lemma-name mistakes; those were corrected. Two control drafts were strengthened before freezing, including a parameter-choice test that now discharges the exact-data bias limit rather than assuming it.

The initial exporter probe put printer options in the wrong Lean monad and was rejected. The corrected probe succeeded. The new exporter still audits every declaration and fully prints every new type; selected inherited types use readable printing. This removes large inherited proof-term expansion while preserving the complete axiom check and the accepted historical full report. Probes remain explicitly labeled development evidence. The accepted cumulative replay was separate and began with no project objects.

The strong-convergence route uses the accepted energy identity to bound squared correction distance by the squared norm deficit. The frequently-bounded WR01 theorem proves the lower norm limit directly for the full filter. This closes the entire parameter-family statement without an unproved sequential-to-filter step.

## Remaining gaps and restart

**Twelve of sixteen principal WR groups are complete. No group remains partially formalized.** WR10–WR12 and WR15 remain written-only. WR15's invariant coordinate certificate is the proposed next bounded block; WR10–WR12 form the larger infinite-diagonal-model and rate block. Exact obligations are in `NEXT_RESEARCH_BLOCK.md`.

The independent global monograph audit, refinement of executable certificate code, application-specific model identification, and synchronized publication/companion-guide editions remain separate. This is a Lean-focused continuation: the accepted v1.10.0 PDF is preserved as historical material, not relabeled as a new edition.

## Evidence and trust

Formal receipt SHA-256: `1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0`. Postflight SHA-256: `37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d`. `VERIFICATION_SUMMARY.json` binds the source, exports and reviews; `records/EVENTS.jsonl` retains the event history. Every predecessor archive file and every new development attempt are retained in the release package, excluding reproducible compiled objects and runtime binaries.

The Lean compiler/kernel, permitted standard axioms, pinned external caches and supporting runtime remain trusted. Dependencies were not rebuilt from source. Endpoint hashes cannot detect a temporary change restored between checks. The focused audit does not certify every sentence or executable example of the monograph.
