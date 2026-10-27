# Verification summary — Sufficient Resolution v0.16.0

**Passed · block/dependency-scoped verification · 14 September 2026**

## Actual completed validation

| Check | Result |
|---|---|
| Fresh predecessor v0.15 dependency run | PASS; block-15 dependency closure compiled/replayed before the extension. |
| Main block-16 compilation | PASS; all 31 required project modules plus `KomorebiBlock16` compiled serially with warnings as errors. |
| Main transitive axiom audit | PASS; all 52 new enumerated declarations. |
| Main same-kernel replay | PASS; all 31 required project modules. |
| Separate source-tree compilation | PASS; same 31-module closure plus block root rebuilt from a separate source tree. |
| Separate transitive axiom audit | PASS; all 52 new names again. |
| Separate same-kernel replay | PASS; all 31 required project modules again. |
| Executed inputs identical | PASS; all 69 recorded source/script/configuration inputs match byte-for-byte between the two final runs. |
| Predecessor proof preservation | PASS; all 87 v0.15 production proof files are byte-identical. |
| Forbidden production constructs | PASS; no `sorry`, `admit`, custom `axiom`, `unsafe`, or `native_decide` in production modules. |
| False proof and placeholder controls | Rejected. |
| Deliberate custom axiom | Compiles intentionally, then is detected by the axiom allowlist. |
| New exact-rational calibration controls | PASS; 289 assertions over 72 systems. |
| Approximate-frame finite cases | 36. |
| Redundant exact-frame finite cases | 24. |
| Invalid/nonspanning controls | 6 rejected. |
| Inherited operator-uncertainty, inexact-discrepancy, discrepancy and limit suites | PASS in both final runs. |
| Fresh full 93-module corpus replay | **NOT RUN.** |

## Source inventory

The cumulative source contains **998 theorem/lemma declarations in 93 production
modules and 1159 enumerated named declarations**. Block 16 adds 44 theorems/lemmas
and 52 enumerated names in six modules. Counts include helpers, definitions, examples,
and specializations; they are not counts of independent discoveries. Papers I–XII are
not updated by this package.

## Proof/runtime trust boundary

Lean/Lake: **4.34.0-rc2**, Lean commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`.
Mathlib revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
The imported dependency HEADs match the retained manifest.

The transitive axiom allowlist is exactly:

- `propext`
- `Classical.choice`
- `Quot.sound`

`leanchecker` uses the **same Lean kernel**, not an independently implemented proof
checker. Imported Lean/Mathlib compiled artifacts are reused from the pinned runtime,
not rebuilt from first principles. The portable runtime and `.lake` build cache are not
included in the release ZIP.

The final verification commands are recorded in:

- `verification/release_v0.16.0/report.json`
- `verification/roundtrip_v0.16.0/report.json`
- `verification/ROUNDTRIP_SOURCE_MATCH_v0.16.0.json`
- `verification/PREDECESSOR_PRESERVATION_v0.16.0.json`

Both final runs used serial Lean commands with one Lean thread and the recorded
per-command wall limit. The platform was Linux x86_64; native Windows execution is not
claimed.

## Finite computational evidence

`scripts/check_calibration.py` uses exact `fractions.Fraction` arithmetic with seed
20260914. Source dimensions are 1..3; calibration spaces range from source dimension to
source+2; data dimensions are 1..3. It checks 72 known finite systems, including
redundant exact split frames and approximate frames with reconstruction-defect bound
below one.

The finite checker uses the **entrywise l1 matrix norm** as a conservative exact-rational
bound. The generic Lean theorems are stated in the native operator norm. Therefore the
finite tests are structural implementation evidence, not a numerical proof of the Lean
operator-norm statements.

`scripts/calibration_certificate.py` receives the calibration synthesis/reconstruction
matrices, measured calibration response, model operator, and an externally supplied
calibration-truth allowance. It does **not** receive the unknown true operator. Python
matrix arithmetic and parsing are tested, not formally verified or extracted from Lean.

## Failures and repairs

The first direct compile of a new module failed because the v0.15 source-only checkpoint
intentionally contained no project `.olean` files. The v0.15 dependency closure was then
rebuilt serially in the pinned runtime and passed.

Draft Lean sources subsequently exposed ordinary development errors: unused section
variables under warning-as-error, an ambiguous `apply` instantiation, extensionality
patterns, one parser mistake in a composed-map expression, and a rewrite that expanded a
factorization recursively. These were corrected with explicit type-correct proofs; warning
checks were not disabled and no placeholder was introduced.

Both final production verification runs pass. No unresolved block-16 compilation,
axiom-audit, kernel-replay, rational-control, or parser failure remains.

## Mathematical boundaries

The exact positive theorem requires a calibration synthesis with a bounded right inverse.
The approximate theorem allows `||I-U R|| <= rho < 1` and pays the factor
`1/(1-rho)`. A formally checked proper-subspace example shows that perfect calibration
on a nonspanning subspace permits arbitrarily large unseen operator error.

The calibration-truth allowance `||Y-AU|| <= etaCal` remains an external premise. This
block does not derive it from individual noisy samples or a stochastic measurement model.
It also does not formally verify the Python checker, establish nonlinear/constrained or
arithmetic realization, or provide a Langlands correspondence.
