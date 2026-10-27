# Quantum–Arithmetic formal scope audit

The authoritative formal target is the fixed twelve-dimensional example in the
later five-module `Komorebi_Quantum_Arithmetic_Lean_v0.2.0_Checked(1).zip`
checkpoint. Its central declaration is
`Komorebi.QuantumArithmetic.publication_bridge` in `Publication.lean:68`.
The target uses ordinary complex matrices indexed by `Fin 12`, the positive-sign
normalized Fourier matrix `F`, the coprime-residue selector `D`, the rational
cyclic projector interpreted as `P`, and the separately defined normalized
states `psi` and `chi`.

**Primary verdict: proved as written.** This verdict refers to the exact fixed
`q = 12` statements and their archived fresh-source build and Lean-kernel replay.
This release has checked source/evidence consistency, not repeated the Lean
compiler run. The new runtime transfer failed as recorded below.

## Exact claim and dependency graph

The bundled target asserts `Fᴴ F = I`, `F Fᴴ = I`, `F D Fᴴ = P`, `P² = P`,
`Pᴴ = P`, `F unitState = psi`, `Fᴴ psi = unitState`, normalization of both
states, equality of every initial squared amplitude, their inner product zero,
and transformed coprime mass one for `psi` versus zero for `chi`.

The dependency chain is:

1. `QuantumArithmeticBridge`: rational tables and four-coordinate arithmetic.
2. `FiniteFourier`: finite, normalized matrix and vector certificates in the
   exact coordinates. Universal indices in these claims range over `Fin 12`.
3. `SemanticBridge`: operation-preserving interpretation in ordinary complex
   numbers, actual complex matrix unitarity, projector transport, state actions,
   and probability statements.
4. `Conventions`: positive complex exponential entry formula, real square-root
   normalization, selector and projector algebra.
5. `Publication`: actual complex Ramanujan phase sum, signed/absolute-value
   identification, reconstruction obstructions, and the bundled final theorem.

The exact finite certificates use `decide +kernel`. Semantic transfer uses Lean
proof terms and pinned Mathlib lemmas. The complex interpretation need not be
proved injective to transfer an equality. It is not installed as a general field
instance. No floating-point arithmetic justifies a load-bearing theorem.

## Reconciled counts and source identity

| Checkpoint | Production modules | Named mathematical theorems | Controls |
|---|---:|---:|---|
| Earlier `v0.2.0_CHECKED` | 4 | 59 | 4 checked explicit refutations and 4 rejected source mutations |
| Later `v0.2.0_Checked(1)` | 5 | 96 | 3 rejected negative-control source files |

The original 22 theorem statements survive inside both revisions. They are not
added to 59 or 96. The later count is exactly `22 + 17 + 30 + 17 + 10 = 96`.
There are also 65 top-level definitions, abbreviations, and one structure in
the active source inventory. Neither compilation jobs nor generated compiler
declarations are counted as new theorems. The later checkpoint replaces the
earlier checkpoint as the main source for this publication.

`lean/Lean_Concordance.json` and `.csv` enumerate all 96 names, exact file and
physical line, literal theorem statement, source SHA-256, and per-theorem
archived axiom dependencies. All 96 line locators agree with the archived index.
All five production source hashes and all eleven archived check-log hashes
match the later `verification/final/REPORT.json`: sixteen hash matches in total.

The later source closes the earlier checkpoint's explicitly disclosed missing
cross-representation implications: `F D Fᴴ = P`, normalized state preparation
and recovery, the usual exponential Fourier convention, and the histogram
nonreconstruction theorem. The earlier `PROOF_BOUNDARY.md` remains correct for
its own source revision and is not a current global gap list.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Exact twelve-entry signal equals the primitive-root sum | Passed | `exact_phase_signal_lookup`, `complex_ramanujan_signal` |
| Root has exact order 12 and is the usual positive exponential root | Passed | `root_exact_order`, `root_is_exponential` |
| Standard normalized complex Fourier matrix is unitary on both sides | Passed | `fourier_unitary_left/right`, `fourier_entry_formula` |
| Literal rational projector equals the transported selector | Passed | `exact_projector_matches_rational_table`, `projector_transport` |
| Projector is Hermitian and idempotent | Passed | `projector_selfAdjoint_complex`, `projector_idempotent_complex` |
| Normalized state action and probabilities are actual complex identities | Passed | `state_preparation/recovery`, normalization and probability declarations |
| Same initial histogram, orthogonal states, and mass 1 versus 0 | Passed | `complete_phase_separation`, `publication_bridge` |
| No histogram-only reconstruction function works on both states | Passed | `no_reconstruction_from_initial_probabilities` |
| Projection alone is noninjective but retained plus residual reconstructs | Passed | `projector_not_injective`, `projector_residual_reconstructs` |
| General-modulus Möbius formula and complete divisor-projector family | Out of scope | Prose/exact-computation evidence only in this release |
| General polyphase recombination and alias formulas | Out of scope | No current Lean theorem |
| General quantum measurement/update API or hardware implementation | Out of scope | Matrix algebra and specific probabilities only |
| QA19 continuous relative-phase family | Out of scope | New prose extension, not an inherited Lean declaration |
| QA20 density-matrix dephasing probability | Out of scope | New prose calculation, not an inherited Lean declaration |
| Fresh compiler build and kernel replay in this publication session | Not addressed | Required runtime materialization failed HTTP 502 |

## Trust and freshness boundary

The archived September 21, 2026 receipt records Lean 4.34.0-rc2, compiler commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, and Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Each of the five modules was built
from fresh sources with warnings treated as errors and replayed with
`leanchecker`. All 96 theorem axiom records were printed. Their union is
`propext`, `Classical.choice`, and `Quot.sound`. The active source token audit
finds no `sorry`, `admit`, custom `axiom`, `native_decide`, or `unsafe` declaration.
The source does not claim an axiom-free formalization. `leanchecker` uses Lean's
kernel rather than an independently implemented verifier. The compiler and
imported dependency cache were not rebuilt from their own source.

For this publication session, `lean`, `lake`, and `leanchecker` were absent from
PATH and the explicit runtime locations probed were absent. Both checkpoint
runtime instructions identify five existing Library files
`Lean_Compact_01.zip` through `Lean_Compact_05.zip` as the required pinned runtime.
All five were resolved. Current Library helper materialization of all five,
then part 01 alone, then smaller part 05 alone each failed with
`download failed with HTTP status 502`. No runtime bytes landed and no Lean
process ran. `lean/FRESH_LEAN_STATUS.json` reports **NOT_RUN**, not a proof failure
and not a fresh pass. The exact runtime metadata is retained separately.

## Negative controls and preserved failures

The later control `FalseSignalSign.lean` directly reports a false sign claim.
`AdmittedProof.lean` directly reports `sorry` under warnings as errors.
`FalseFourierMode.lean` is rejected because a `Decidable` reduction gets stuck;
its log is not a direct certificate of the false claim. The runner's broad
`false` diagnostic pattern can match the filename, so that diagnostic alone
cannot distinguish wrong arithmetic from opaque reduction. This does not affect
the positive theorem: `ramanujan_dft_table` separately certifies the mode value
12 rather than zero. The older checkpoint includes explicit proved negations of
its four false variants, retained as older evidence rather than silently merged
with the later controls.

Historical native-decision drafts and unsuccessful attempts remain under
`development/` or `history/`. They are not active imports or present proof
certificates. The numerical Block 17 quantum package is also a distinct program;
its QEC namespace is not a repair of this finite arithmetic bridge.

## Strongest safe statement and remaining work

The fixed `q = 12` arithmetic-to-complex projector and state bridge is fully
covered by the archived later source proofs under their exact definitions.
The new publication can state these conclusions strongly while distinguishing
current static reconciliation from the historical execution receipt.

The remaining formalization work is the arbitrary-modulus family, the general
Möbius/divisor and polyphase results, and a general measurement interface if
desired. The cheapest freshness check is restoring the exact pinned portable
runtime when materialization works, then running the unmodified latest verifier
into a new output directory. That is a reproducibility task, not a missing
implication in the already archived fixed-example proofs.

The current manuscript has twenty claim labels. QA15's up-to-global-phase
strengthening is a prose corollary, and QA19–QA20 are new prose extensions.
QA18's full manuscript bundle uses `publication_bridge` together with separate
checked filter, energy, unit-state normalization, projector-action, and
noninjectivity declarations. The machine concordance records those supporting
results rather than identifying the longer manuscript statement with a shorter
single declaration.
