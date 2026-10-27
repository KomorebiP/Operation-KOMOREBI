# Audit report — v0.4.0 Lean block 1

**Date:** 15 October 2026.

## Outcome

58 named theorem declarations compile across six production modules. Their aggregate library also compiles. Every theorem is queried by `#check` and `#print axioms`; its transitive axiom names must belong to `{propext, Classical.choice, Quot.sound}`. All 58 pass that policy, and 16 have no axiom dependencies. No production theorem uses `sorryAx` or a native compiler-reduction axiom.

These are Lean proofs, not Python enumeration counts. The count includes supporting lemmas. Successful repeat builds are not additional theorems.

The release gates are the strengthened clean build in `reports/clean_run_02` and the build from a separate extracted source archive in `reports/archive_replay`. Each process uses `-j1 -DwarningAsError=true`. The local project object directory is removed before compilation. The cached external Mathlib dependencies come from the pinned restored kit rather than a new source rebuild.

## Negative controls

| Fixture | Expected result | Final result |
|---|---|---|
| FalseArithmetic | Reject 0 = 1 | Compiler explicitly reports the proposition false |
| Placeholder | Reject a proof placeholder under warnings-as-errors | Compiler reports declaration uses `sorry` |
| MutatedHaarDecoder | Reject sign-reversed supplemental decoding | Compiler explicitly reports the proposition false |
| FalseSourceRecovery | Reject equality of the invisible source vector and zero | Compiler explicitly reports the proposition false |
| InjectedAxiom | Detect a new assumed axiom even when Lean accepts the file | Compiler accepts the explicit assumption; axiom allowlist rejects it |

The controls are intentionally invalid fixtures outside the production library. Their failed compilation is expected. The custom-axiom fixture illustrates why a zero compiler exit by itself is not enough. No runtime error or timeout is accepted as a successful rejection.

## Failures encountered and corrected

1. **Initial environment failure:** neither Lean nor Lake was installed on PATH. A direct GitHub curl attempt failed with `Could not resolve host: github.com`. The seven stored offline parts were recovered via Library metadata and materialization, assembled, hash-checked, and extracted. Search-by-name had returned no indexed matches; the metadata listing located the files. No download success is claimed for the failed route.
2. **Tool session failure:** an attempted streaming extraction call returned `StreamingExecNotEnabledContainerError` without starting the requested extraction. A synchronous extraction completed normally.
3. **Authoring-time Lean errors:** the initial API probe included names absent in the pinned Mathlib. Early proof drafts exposed a deprecated `dif_pos` name, new module-definition visibility requirements, missing imports, coercion/rewriting mismatches, a submodule/type-coercion ambiguity, and a no-progress tactic branch. These were corrected using the actual installed source and compiler diagnostics. No failing draft is classified as checked. The probe is retained as a text transcript in `reports/development`, not as an invalid build target.
4. **Finite-field instance and notation imports:** initial Haar/Dimension attempts used nonexistent import paths; the paths were corrected. Explicit prime facts and the ZMod field import were added for the concrete examples. The general inverse proofs retain the required `2 ≠ 0` assumption.
5. **Negative-control diagnostic weakness:** the first sign-mutated Haar test failed because `decide` could not reduce a field-inverse decision instance. The original verifier accepted too broad a category of `decide` failures. That is not a satisfactory falsity check. The final fixture uses the explicit inverse coefficient 3 in GF(5), and the verifier now requires the diagnostics `proved that the proposition` and `is false` for false finite examples. The strengthened run rejects the statement for its falsity, not stuck reduction. `clean_run_01` is preserved as development evidence and is not the release-gating negative-control run.

All corrected source was rebuilt from scratch in the strengthened final runs. Development logs are retained rather than relabeled as success.

## Scope of formal verification

The strongest checked general result is feasible optimal access-aware repair: a helper-visible linear map into the obstruction space exists, and every nonlinear code needs at least that space's cardinality. The proof supplies the existence result rather than assuming the requested optimal encoder. The dimension/rank-increment identity and q^d cardinality are proved separately and linked.

The predictive quotient is constructed in Lean with its well-defined observation/actions and universal factorization property. The Haar all-time theorem quantifies over every natural time and every source in every field with 2 nonzero.

The linear-map proofs do not yet verify the Python matrix parser or row-reduction algorithm. The optimal message is represented as the actual d-dimensional obstruction subspace, not an exported d-row coordinate matrix. The finite row-space closure algorithm, entropy/risk identities, native floating library, and physical-noise models are not yet ported. Consult the obligation ledger rather than extrapolating from the theorem count.

## Trust boundary

The restored archive SHA-256 matches the recorded offline kit. The compiler version/commit and Mathlib git revision were read from the running environment. Its original path-discovery compatibility wrapper was used as shipped. The Lean kernel and cached Mathlib imports were not independently rebuilt or externally rechecked in this block. No claim of compiler correctness or universal mathematical unification follows from this run.

The prior v0.3 ZIP is retained byte-for-byte, with its SHA-256 and ZIP CRC test recorded. Its Python counts are historical, not newly replayed counts. No native Windows verification occurred.
