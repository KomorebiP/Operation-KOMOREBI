# Current verification record: v0.51.0

The centered free-field extension is accepted with status **PASS_SCOPED_CENTERED_EXTENSION**. Its exact receipt is `formal/continuum/verification/block51/current/receipt.json` (SHA-256 `f530e4bb0c55204fe3d7d55c9cf71c60781f5db949541bfc9b3c649241799d11`).

The result covers the bounded self-adjoint centered operator for nonzero signed spacing, graph convergence on the complete maximal domain, constructed continuum and centered resolvents with both inverse identities at every nonreal spectral parameter, strong resolvent convergence, and quadratic generator/propagator bounds under an actual summable third-order Fourier moment. The physical-space results use the existing Fourier isometry. Compact-time envelopes explicitly require `T >= 0`.

The accepted run records 26 local target compiles and 64 commands; 209 audited environment declarations (162 new and 47 unchanged generator); five module kernel replays; and 21 controls (8 positive, 12 elaboration rejections, 1 custom-axiom policy rejection). The new source contains 74 theorems, 15 definitions and 11 abbreviations. Only `propext`, `Classical.choice` and `Quot.sound` occur as axiom dependencies. Source, object and relevant runtime identities remained stable.

## Trust boundary

The exact portable Lean 4.34.0-rc2 runtime and external compiled dependencies are pinned and reused. Kernel replays use the same Lean kernel and imported environment. This is not a compiler bootstrap, full Mathlib source rebuild, independent proof-assistant verification, or cumulative audit of every historical physics module. The runtime is not bundled in the source ZIP. Follow `formal/continuum/README.md` for a fresh replay into a new directory. Failed development and gate attempts remain separate from accepted records.

## Publication checks

The full book has 572 pages and 574 bookmarks. Five affected components were rebuilt with three TeX passes; the full book was assembled and every page rendered. Final PDF/log/navigation checks and visual-review records are in `audit/continuum_publication_qa.json`.

All 107 original proof bodies are unchanged. Two original theorem-like statements explicitly add `T >= 0`; other original mathematical statements and displayed equations are preserved. All 157 source data files and all numerical image assets are byte-identical. Only the verification-scope schematic changed among 196 image assets. Status prose and technical declaration correspondence were updated without redesigning the five visual atlases.

An initial assembly failed because this runtime lacked the declared TeX Gyre Type 1 dependency. The dependency was restored and assembly rerun successfully; failure and restoration logs remain in the publication audit notes. A sparse intermediate generator layout was corrected by shortening status prose. Neither issue altered scientific data or proof bodies.

The five numerical suites were rerun at the preceding v0.50.0-g1 checkpoint, not during this extension. The retained atlas script references an original-tree `evidence/figure_checks.json` absent from this publication copy. Earlier numerical logs and the production-energy obstruction remain explicit. No new empirical or production-mechanism claim is made.

## Remaining work

- Abstract unbounded spectral-functional-calculus API identification.
- Sampling, interpolation, aliasing and domain comparison with a changing finite spatial grid.
- Background gauge operator domains and coupled dynamical gauge or gravitational evolution.
- Resolution of the retained production-energy obstruction by a controlled physical mechanism.
- Full historical cumulative/gauge evidence audit beyond the exact replayed targets.
- Independent specialist review of the complete mathematical and physical manuscript.

The prior README, release report and manifest are preserved under `history/publication_v0.50.0-g1_metadata/`. Current source-preservation review is `audit/source_preservation_centered.json`; the detailed restart ledger is `formal/continuum/PROGRESS_LEDGER_v0.51.0.md`.
