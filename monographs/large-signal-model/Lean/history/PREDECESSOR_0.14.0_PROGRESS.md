# Large Signal Model Lean 0.14.0

Komorebi P. — 2026-10-15. Frozen theory 1.0.0; PR-LASM production software 2.3.0 unchanged.

P32 is complete in its stated finite-table scope. This block constructs the leading singular subspace, proves singular-value perturbation and the exact observed residual, and proves the ordinary matrix inverse decoder and its conditioning. It adds 54 named Lean theorems (47 supporting and seven examples), nine definitions, ten proof modules and two rejection controls. Coverage is now 39/87 complete, zero partial and 48 not formalized.

PASS: 282 cumulative stages; 84 metadata/tooling checks. Exact delivered-ZIP replay is recorded separately in the external verification JSON.

## Source map

| Module | Contribution |
|---|---|
| SpectralSubspaces | Retained right spans, dimensions, coordinate support and two spectral bounds. |
| SpectralTail | Constructed left subspace, dimension, residual identity and exact tail norm. |
| SingularPerturbation | Dimension intersection; all-index absolute singular-value perturbation; noisy lower and upper bounds. |
| LeftSingularModes | Normalized left modes, orthonormality, left Gram eigenvector relation and span equality. |
| NoisySpectralSubspace | Data-selected subspace, derived rank/dimension/tail and full spectral/projection endpoint; rectangular maximum-rank convention. |
| BasisCoordinates | Cross matrix, coordinate maps, actual minimum-singular-value bound and injectivity. |
| BasisDecoder | Ordinary inverse matrix, explicit decoder, both inverse laws, true-range membership and norm bound. |
| DecoderMatrixFormula | Ambient basis columns, literal transpose product and matrix decoder formula. |
| FiniteTableP32 | Unified basis-conditioning and decoder endpoint with only P32's noise hypotheses. |
| Block14Examples | Seven exact checks, including sharp perturbation, retained/discarded scalar modes and the rectangular zero-tail boundary. |

## Continuation

No P32 implication remains open in the stated finite-table theorem. The broader program has 48 unformalized propositions; see ROADMAP_1.0.json for the exhaustive disjoint list.

Next bounded target: P31, missing-intervention nonidentifiability, in frozen Foundations §32. The exact manuscript construction uses one hidden state and two observations. Both models give (1/2,1/2) under action a; they give (1,0) and (0,1) under b. Formalize actual stochastic models, prove every a-only word has common probability 2^(-length), and exhibit the one-step b disagreement. Existing instrument and word-probability APIs should supply the construction. P31 is not counted as proved by this handoff.

P35's reset-experiment probability certificate and P37's conditional observation-based completion remain further parts of the learning chain. P32 does not silently supply their statistical or coverage assumptions.

## Preserved development record

There were 22 recorded tool invocations: 10 succeeded and 12 failed. Of these, 21 invoked Lean and one diagnostic tracing attempt was blocked before Lean ran. Every attempted source snapshot and its output is retained in `verification/development_block14/`.

Nine failures were ordinary Lean proof or warnings-as-errors diagnostics: an incorrect namespace and a deprecated Fin accessor; coercion/type inference around a finite span's dimension; unfolding a Gram eigenbasis and normalizing inverse arithmetic; function versus finitely supported function coercions; unused finite-dimensional section assumptions; subtype equality and continuous/linear-map coercions; and explicit scalar operator-norm simplification. Typed intermediate facts, the pinned API and explicit coercions resolved them. The stated mathematical target was not weakened.

Two tail-module runs reached output-file creation and failed while disk space was critically low. Already-saved duplicate extraction/build trees were removed, and the unchanged tail source then compiled. A `strace` diagnostic was rejected by process tracing permissions; no bypass was attempted. These are environment failures, not rejected mathematical claims. The logs are preserved and the cumulative verifier rebuilds all project objects from scratch.

The first metadata pass also failed because an inherited roadmap check still required 49 unfinished propositions. The check was updated to 48 after P32 completion, while retaining exact set equality and disjoint coverage of all 87 propositions. This diagnostic is recorded separately in BLOCK14_METADATA_DEVELOPMENT.json.
