# K-COS end-to-end verification — checkpoint 0.1.0

## Result

**PASS for the stated checkpoint. The full numerical engine is not yet verified end to end.**

A clean, isolated offline replay completed on 23 October 2026. All **32 verification gates** passed. The exact receipt is `verification/accepted/run.json`. The frozen official monograph and publication ZIP are unchanged.

| Formal inventory | Original publication companion | This checkpoint |
|---|---:|---:|
| Production theorem declarations | 26 | **85** |
| Production definitions | 8 | **19** |
| Named probability-measure instance | 0 | **1** |
| Explicitly axiom-audited declarations | 34 | **105** |
| Mathematical modules | 2 | **8** |

This is **59 additional theorems**, eleven additional definitions, and one named instance. Counts refer to explicit production declarations, not all generated helper declarations, imported Mathlib theorems, or build jobs. The declaration audit follows the dependencies of each audited declaration. The 19 control theorems are counted separately.

## What is now proved

**Actual probability semantics.** Closed upper-tail events are defined using a genuine measure. Measurability is established for the statistics used as distributions. Coefficient order is lifted from the original pointwise weighted-square inequality to an actual stochastic tail enclosure. Finite-measure assumptions are explicit where real-valued measure comparisons need them.

**Concrete Gaussian coordinates.** The spectral law is the pushforward of an actual product of standard Gaussian measures. Individual coordinate laws and independence are derived, not postulated. Signed and zero coefficients are admitted by the exact reduction; the closed-tail convention includes atoms at the query threshold.

**Exact spectral reduction.** A real symmetric operator's quadratic form under the actual standard Gaussian law has the same distribution as the independent weighted-square form built from its mathematical eigenvalues. The eigenbasis is obtained from the proved spectral theorem. Gaussian basis invariance is used explicitly. All eigenvalues, including zeros, are retained.

**Singular central linear images.** For the explicitly defined law X = BZ, the quadratic form is reduced to the spectral law of B* M B. B is not required to be injective or surjective. This does not yet interpret an arbitrary covariance-file encoding or prove the noncentral shift.

**Connection to the original Gram input.** The finite `gramEntry`, `quadraticForm`, and streamed-factor definitions are connected to the Euclidean operator realization. Symmetry is proved from the Gram entries. The resulting law and tail equalities therefore begin at the original mathematical factor representation, not an unrelated spectral interface.

**Exact acceptance.** A computable Lean Boolean checks rational positivity, endpoint order, tolerance nonnegativity, and `U ≤ (1+ε)L`. Its real-valued soundness and equivalence to `U/L - 1 ≤ ε` are proved. For any true probability and estimate both in the accepted interval, the requested relative-error inequality follows. Midpoint-error and full-interval-width budgets are formalized separately.

## The remaining premises are explicit

The final conditional theorem is `gram_quadratic_rational_acceptance`. It still requires:

- Valid lower and upper bounds on the actual mathematical eigenvalues.
- Valid lower and upper probability bounds for the endpoint spectra.
- An estimate lying within the reported interval.

The theorem proves the stochastic connection and acceptance consequences. It does **not** prove the numerical procedures that supplied those spectral or probability bounds. Numerical spectral inclusion, exponential tilting, COS inversion and remainders, interval/transcendental implementation, decoding, and serialization remain open formalization blocks.

The new Boolean checker is verified source in this branch. It is not a proof that the released Python engine executes it, or that Python parsing and control flow implement its exact rational inputs.

## Verification performed

| Check | Result |
|---|---|
| Stored compact runtime reconstruction | Hash and part checks passed |
| Lean compiler | 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` |
| Mathlib | `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` |
| Locked dependencies | All nine revisions match; tracked sources clean |
| Fresh isolated project build | Passed with warnings treated as errors |
| Production axiom audit | All 105 explicitly inventoried declarations matched and passed |
| Project-only kernel replay | All eight mathematical modules and the root import passed |
| Positive and counterexample controls | All 19 control theorems accepted and axiom-audited |
| Intended rejection controls | All five rejected with their expected diagnostic category |
| Checked-source correspondence | Every replayed production source matches the delivered source |
| Predecessor formal inputs | Both original mathematical modules and the toolchain/lock file unchanged |
| Official publication identity | PDF and ZIP hashes unchanged |

The audited axiom union is exactly `Classical.choice`, `Quot.sound`, and `propext`. No `sorryAx`, custom axiom, or native-decision axiom occurs in the audited production declarations. The deliberately invalid placeholder is confined to its rejection control.

Kernel replay uses the same Lean kernel and the pinned imported environments. It is not external independent verification, a fresh rebuild of every Mathlib dependency, or a formal proof of the compiler implementation.

## Controls and retained numerical records

Fifteen controls cover the acceptance equality boundary, wide intervals, nonpositive lower endpoints, reversed endpoints, negative tolerance, exact intervals, interval narrowing, relative-error soundness, zero-spectrum atoms, thresholds above a zero spectrum, signed coefficients, and explicit counterexamples to missing-budget and reversed-probability claims.

Four additional Lean theorems check exact rational inequalities from the retained worked example's **tilted-functional intervals**. The 8,192-mode interval rejects 2%, the 16,384-mode interval accepts 2%, and both reject 0.1%. The original JSON, source hash, exact rational translations, and a reproduction script are included. These checks do not validate the analytic error bound, the prefactor, the logarithmic probability interval, or the JSON parser.

The five intended rejections test false arithmetic, an omitted accuracy-budget premise, reversed probability order, substitution of a midpoint budget for an interval-width budget, and a proof placeholder. The runner checks both the exit code and the diagnostic, and excludes missing-import or syntax errors from being counted as a successful negative control.

No Python solver regression suite or new numerical benchmark was run in this branch. No numerical engine source was changed. The official release's prior numerical evidence remains distinct from these new formal checks.

## Recovered development failures

The development logs are retained under `verification/development/`.

1. An interactive streaming execution call was unavailable. Runtime restoration used ordinary process execution instead. The five-part reconstructed archive matched the expected hash before extraction.
2. Initial source checks exposed a deprecated set-membership lemma, explicit finite-measure side conditions, order-lemma orientation, and unused hypotheses or section instances. These were corrected without disabling the strict linter.
3. The first spectral and matrix-interface drafts needed corrected inner-product notation, documentation placement around `omit`, and an explicitly typed `gramMatrix` wrapper. The tail-law proof now composes explicit equalities rather than relying on fragile rewrite inference.
4. A direct `decide` attempt did not reduce the large rational-division expressions in the recorded controls. Proof-producing `norm_num` was used instead. No `native_decide` shortcut or added axiom was introduced.
5. The zero-spectrum, above-support control required explicit numeric normalization rather than plain simplification.

All of these issues were resolved before the accepted isolated replay. Failed attempts are not counted as checked results. The two inherited mathematical modules were not edited to accommodate the new development.

## Next block

The precise next target is `TiltedMeasure.lean`: construct the actual tilted measure, prove normalization, and derive the exponential change-of-measure identity. Then specialize its moment formula to the positive weighted-square Gaussian law and derive support bounds. `docs/PROGRESS_LEDGER.md` and `docs/COVERAGE.json` preserve the restart point and remaining obligations.
