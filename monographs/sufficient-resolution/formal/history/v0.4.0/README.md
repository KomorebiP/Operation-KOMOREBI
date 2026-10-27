# Komorebi Sufficient Resolution — Lean v0.4.0

**Komorebi P. · 13 September 2026**

A cumulative formalization of exact resolution, compression defects, linear
globalization obstructions, discrete memory, finite observable-state minimality,
and quantitative approximate behavioral sufficiency.

**272 theorem/lemma declarations in 22 proof modules; 357 explicitly named declarations.**
This block adds **82 theorems in six modules**. All 16 predecessor production proof
sources are unchanged. Counts include supporting lemmas and examples; they are not
independent discoveries and do not modify the Papers I–XII theorem census.

## Main new result

Let q represent true states, T_i be the true operations, U_i the approximate reduced
operations, and O,V the two readouts. Assume whole-map operator bounds

    ||T_i|| ≤ a,   ||U_i|| ≤ b,
    ||q T_i − U_i q|| ≤ ε,   ||O − Vq|| ≤ η,

with a,b,ε,η nonnegative. For every finite chronological word w of length n,

    ||q T_w − U_w q|| ≤ ε H_n(a,b),
    ||O T_w − V U_w q|| ≤ η a^n + ||V|| ε H_n(a,b),

where

    H_0 = 0,    H_(n+1) = a H_n + b^n.

The finite convolution, unequal-rate and equal-rate formulas are all proved.
Noncommuting operations are allowed. No finite dimension, finite alphabet,
completeness, injectivity or surjectivity of q is required for these norm bounds.

When the true operations are nonexpansive and the reduced operations have a common
norm bound b<1, the output error is uniformly bounded by

    η + ||V|| ε/(1−b).

The theorem also controls arbitrary reduced initial states, successive approximate
models, and split coordinate changes. Exact scalar systems attain the bound and
prove that one-step smallness alone cannot imply uniform future error control.

## New modules

| Module | Theorems | Content |
|---|---:|---|
| ApproximateAlgebra | 12 | Exact telescoping, word concatenation, output split, multilevel defects. |
| ApproximateBounds | 18 | Continuous-map bridge, heterogeneous gains, whole-map error and initial-state bounds. |
| ScalarBudgets | 17 | Response convolution, equal/unequal rates, monotonicity and contraction. |
| StableApproximation | 12 | Uniform/nonexpansive/contractive certificates, approximate behavioral indistinguishability. |
| ApproximateComposition | 11 | Two-stage bounds, split re-encoding, explicit conditioning and output invariance. |
| ApproximateExamples | 12 | Exact scalar sharpness and arbitrary-positive-error growth counterexample. |

`BLOCK_04_THEOREMS.md` gives the detailed mathematical contract and declaration map.
`PROGRESS.md` separates completed layers from remaining obligations.
`CONTINUE_HERE.md` provides the continuation protocol.

## Runnable exact-rational bound evaluator

    python scripts/approximate_certificate.py --input examples/approximate_model_input.json --output bounds.json

The program uses exact rational matrices and the induced infinity norm. It reports
one-step norms, actual finite-word errors and certified envelope values. Input
must contain rational strings or integers, not floating-point approximations.
The provided example has two noncommuting fine-state operations and a one-dimensional
approximate reduced state.

The earlier exact observable-model constructor is preserved:

    python scripts/observable_model.py --input examples/observable_model_input.json --output model.json

Neither Python program is formally verified or extracted from Lean. Their bounded
exact tests supplement, but do not replace, the generic Lean theorems.

## Formal reproduction

Pinned Lean/Lake: `leanprover/lean4:v4.34.0-rc2`.
Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
Mathlib commit: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
All nine dependency revisions are checked against `lake-manifest.json`.

    python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
    python3 scripts/validate_manifest.py verification/local-replay/computation-manifest.json --root .

The portable Linux x86_64 runtime and its Mathlib cache are not duplicated in this
source/evidence archive. Reproduction is offline once the preserved runtime is
restored. Windows/WSL was not separately exercised in this release.

The verifier compiles serially with warnings as errors, audits every explicitly
named declaration, runs `leanchecker` on each production module, and checks that
its proof/test/configuration inputs did not change during the run. Negative proof
controls are isolated and are not imported by the production library.

Allowed axioms are `propext`, `Classical.choice` and `Quot.sound`. Production sources
contain no `sorry`, `admit`, custom axioms, `unsafe` or `native_decide`.
Kernel replay reuses the same Lean kernel and imported artifacts. It is not an
independent implementation of the proof kernel, comparator validation, or a fresh
reconstruction of all imported Mathlib proofs.

## Evidence

- `verification/release/`: new cumulative compilation, axiom audit, kernel replay and controls.
- `verification/roundtrip/`: second fresh verification after source-archive extraction.
- `verification/fresh_predecessor_v0.3.0/`: predecessor replay performed before extension.
- `verification/predecessor_v0.3.0_sources.json`: immutable hashes for all 16 old proof files.
- `verification/PRINCIPAL_SIGNATURES_v0.4.0.log`: principal elaborated theorem signatures.
- `verification/development_v0.4.0/`: unsuccessful drafts and corrected reruns.
- `history/`: preserved prior ZIPs and status documents, labeled historical.

The new exact Python controls passed 7,509 assertions across 30 systems and 370
words, with ten negative controls rejected. Earlier tests are retained separately.
The definitive verification outcomes and trust boundary are in VERIFICATION_SUMMARY.md.

## Boundaries

No model identification from samples, approximate minimum-dimension result,
continuous-time memory equation, automatically discovered stability norm,
positivity/normalization realization, nonlinear descent or arithmetic existence
is established by this release. Whole-map norm bounds are not interchangeable
with sampled residuals or per-operator spectral radii. No historical novelty or
priority certificate is claimed.
