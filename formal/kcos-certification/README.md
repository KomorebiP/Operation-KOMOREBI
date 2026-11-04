# K-COS logarithmic certification companion

Author: Komorebi P.

This companion adds **15 universal theorems and 3 definitions** for exact real logarithmic enclosures and the final logarithmic acceptance contract. It closes the positive-domain logarithm gap explicitly recorded in the original [claim concordance](../../monographs/cos-method/lean/Claim_Lean_Concordance.json). The preserved monograph, engine, original formal sources, and historical verification receipts remain unchanged.

The existing [formal continuation](../../monographs/cos-method/formal-continuation/README.md) already proves the real relative-error bound and rational acceptance rules. This project imports those proofs through two byte-identical prerequisite copies; their declarations are **not** counted as new results. Their original paths and SHA-256 digests are recorded in [CLAIM_MAP.json](CLAIM_MAP.json).

## The mathematical contract

For real logarithmic endpoints \(L,U\), define

\[
\operatorname{decimalLog}(p)=\frac{\log p}{\log 10},\qquad
\operatorname{decimalExp}(x)=\exp((\log 10)x),\qquad
R(L,U)=\exp((\log 10)(U-L))-1.
\]

Assume a true positive value \(p>0\), a valid log enclosure \(L\le\operatorname{decimalLog}(p)\le U\), an estimate \(\widehat p\) between \(\operatorname{decimalExp}(L)\) and \(\operatorname{decimalExp}(U)\), and \(R(L,U)\le\varepsilon\). The new bridge theorem proves

\[
\frac{|\widehat p-p|}{p}\le\varepsilon.
\]

This proof reduces the logarithmic representation to the retained real multiplicative-budget theorem. It does not re-prove or recount that earlier theorem as new coverage.

The directed acceptance theorem also allows separate real bounds \(r^+\) and \(\varepsilon^-\). Its premises are

\[
R(L,U)\le r^+,\qquad r^+\le\varepsilon^-,\qquad
\varepsilon^-\le\varepsilon.
\]

These are the mathematical roles of `ratio.b` and `eps.a` in [`directed_relative_accuracy`](../../monographs/cos-method/engine/directed_accuracy.py). The theorem verifies their logical consequence. Construction of those directed numerical bounds remains an explicit input obligation.

For the tilted-sum transformation used by [`interval_positive_logsf`](../../monographs/cos-method/engine/interval_kcos.py), the companion proves that

\[
0<s_-\le s\le s_+,\qquad c_-\le c\le c_+
\]

implies

\[
\frac{c_-+\log s_-}{\log 10}
\le\operatorname{decimalLog}(e^c s)
\le\frac{c_++\log s_+}{\log 10}.
\]

The log-prefactor may have its own enclosure. A separate exact identity proves that a common exact exponential prefactor cancels from the multiplicative width. Widening caused by an interval-valued prefactor does not disappear under that identity.

## Exact claim inventory

All new declarations are in [KCosCertification/Logarithmic.lean](KCosCertification/Logarithmic.lean), under namespace `KCosCertification`. The machine-readable claim map includes every exact declaration signature, hypotheses, source correspondence, and boundary.

| Theorem | Scoped consequence |
|---|---|
| `enclosed_log` | A supplied positive-lower-endpoint enclosure is preserved by natural logarithm. |
| `enclosed_decimalLog` | The same enclosure is preserved in base-ten log coordinates. |
| `decimalExp_pos` | An exact finite real log endpoint represents a positive value. |
| `decimalExp_decimalLog` | A positive value survives the exact coordinate round trip. |
| `decimalLog_enclosure_iff` | A positive value's log enclosure is equivalent to its enclosure between exponentiated endpoints. |
| `decimalExp_ratio` | The endpoint ratio excess equals the exponential log-width formula. |
| `logWidthRatio_budget_iff` | The log-width test is equivalent to the existing real multiplicative budget. |
| `log_enclosure_relative_error` | A value and an estimate inside an accepted enclosure satisfy the relative-error contract. |
| `directed_log_acceptance` | Valid directed upper-error and lower-tolerance bounds suffice for acceptance. |
| `logWidthRatio_nonneg` | Ordered log endpoints have a nonnegative ratio excess. |
| `logWidthRatio_narrow` | Increasing the lower and decreasing the upper endpoint decreases the exact ratio excess. |
| `logWidthRatio_narrow_accepts` | Such endpoint narrowing preserves a previously accepted width tolerance. |
| `prefactor_log_enclosure` | An exact exponential prefactor transports a positive sum enclosure into log-probability coordinates. |
| `prefactor_interval_log_enclosure` | A separately enclosed log-prefactor contributes its own lower and upper endpoint errors. |
| `prefactor_log_width` | A common exact exponential prefactor cancels from the ratio excess. |

The three definitions are `decimalLog`, `decimalExp`, and `logWidthRatio`. The declaration inventory in [verification.json](verification.json) contains these 18 new names only. The retained prerequisites supply `Enclosed`, `MultiplicativeBudget`, and the earlier acceptance proofs.

The narrowing theorems compare exact endpoint widths. They do not prove that a numerical controller actually constructs nested enclosures. To apply the relative-error conclusion after refinement, the refined interval must still contain the true value and the estimate.

The [recorded replay](verification/2026-11-04/run.json) binds the exact checked sources, verification program, and compiler diagnostics.

## Verification and controls

The package pins Lean `4.34.0-rc2`, compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, matching the retained continuation. The dependency manifest pins the other eight packages as well.

The shared repository verifier creates a fresh temporary build, checks the pinned dependency revisions and tracked cleanliness, compiles with warnings as errors, audits the exact new declaration inventory for axiom dependencies, replays project modules in the Lean kernel, and checks positive and negative controls. Each run writes a fresh evidence directory and refuses to overwrite earlier evidence. Kernel replay uses the same Lean kernel against the pinned imported environments; it does not independently rebuild or verify the whole Mathlib dependency closure.

From the repository root, with the portable runtime already restored:

```bash
python3 tools/verify_lean_companion.py \
  --project formal/kcos-certification \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --output verification/current/kcos-logarithmic-replay
```

Choose a new output directory for each additional replay. Ordinary development compilation is `lake build` inside this directory after the exact dependencies are available.

[Controls/Positive.lean](Controls/Positive.lean) contains eight checks: a one-decade ratio, zero-width endpoints, a positive log enclosure, a counterexample to unrestricted log monotonicity, concrete endpoint acceptance, directed tolerance comparison, accepted narrowing, and a separately enclosed log-prefactor.

The following files deliberately fail and are never imported by the production root:

| Control | Required rejection |
|---|---|
| `RejectMissingPositivity.lean` | The log-enclosure theorem cannot be used without its positive-lower-endpoint premise. |
| `RejectReversedDirectedBound.lean` | A lower error bound cannot be supplied where an upper error bound is required. |
| `RejectFalseDecimalWidth.lean` | A one-decade interval has ratio excess 9; the deliberately asserted value 1 is rejected. |
| `RejectPlaceholder.lean` | A proof placeholder is rejected by warnings-as-errors. |

The production source has no proof admissions, custom axioms, or native-decision calls. Successful evidence must additionally show that all 18 audited declarations use only the verifier's allowed standard axiom set.

## Remaining boundaries

This companion does not prove COS inversion, exponential tilting validity, support or alias estimates, omitted-mode bounds, numerical spectral inclusion, or validity of the supplied error ledger. It does not model `mpmath.iv`, `Decimal`, finite-precision logarithm or exponential evaluation, decimal parsing, serialization, floating-point endpoint conversion, infinities, or underflow. Exact positivity is a hypothesis; the numerical positivity guard is not formally verified here.

It also does not show that the controller converges, terminates, honors resource caps, or creates valid narrower intervals. Displaying or rounding an estimate may move it outside the exact endpoint interval; that step is outside the estimate-enclosure premise. The separate [numerical certification audit](../../docs/KCOS_NUMERICAL_CERTIFICATION_AUDIT.md) provides computational evidence with its own stated scope. These formal additions do not upgrade that numerical evidence into an end-to-end implementation proof.
