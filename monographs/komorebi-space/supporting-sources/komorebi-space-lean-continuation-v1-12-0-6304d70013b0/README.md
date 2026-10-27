# Komorebi Space — Lean continuation v1.12.0

This continuation formalizes WR15, the invariant norm of a coordinate certificate. The exact acceptance state and evidence are in `PROGRESS_LEDGER.json` and `VERIFICATION_SUMMARY.json`. The accepted predecessor is the v1.11.0 regularization-limit checkpoint.

## Result

For an arbitrary full basis B of the actual protected kernel, the Lean statements derive the Gram matrix G = BᵀB and its invertibility. They compute q from the coordinate normal equation and identify the existing restricted Hilbert normal residual with B G⁻¹q. Its actual squared norm is qᵀG⁻¹q. Every invertible basis change has inverse coordinate transport, transpose covector transport, and the same scalar certificate.

The construction includes the empty basis. It does not assume orthonormality of B or replace the Hilbert norm with the maximum norm on coordinate functions. Ambient and residual matrices use orthonormal coordinates, with explicit bridges to the declared Hilbert spaces. The algebraic identities hold for every real regularization parameter. This does not extend positive-parameter optimizer bounds to negative parameters.

`CoordinateBasisChange.lean` supplies arbitrary finite matrix transformations and an actual changed full basis. `CoordinateCovector.lean` connects those matrices to the accepted gradient, proves the Gram norm identity, and specializes the result to the entire kernel. Together they add 43 explicit theorems and eight definitions.

## Package layout

- `formal/`: complete current source snapshot from the accepted cumulative run, including controls and pinned dependency descriptions.
- `wr15_v1.12.0/`: new source overlay, frozen targets, development attempts, compiler logs, full declaration exports, independent reviews and verification records.
- `inherited_v1.11.0/`: every predecessor file preserved unchanged, including its earlier release history and historical monograph PDF.
- The six release documents at the root match their copies under `wr15_v1.12.0/`.
- `SHA256SUMS.txt` covers every payload. External delivery and independent archive reports bind the complete ZIP digest.

## Verification and reproduction

The verification policy is Lean 4.34.0-rc2 with one compiler thread, warnings as errors and `autoImplicit=false`. Cumulative project objects are rebuilt in an empty directory. Every imported project declaration receives an axiom/safety audit, and every new declaration receives a full explicit type export. The only permitted axioms are `propext`, `Classical.choice`, and `Quot.sound`.

Use the separately saved portable runtime. Its recovery and pinned dependency checks are recorded under `wr15_v1.12.0/recovery/`. To repeat after extraction, pass the actual recovered parent run under `inherited_v1.11.0/limits_v1.11.0/integration/runs/clean_limits_01` to the new assembler, with the new overlay and fresh attempt labels. Use the actual runtime and compatibility-adapter paths with the verifier. Original absolute command paths are retained as historical provenance. Do not edit old receipts to make those paths current.

The compiler/kernel and external compiled dependencies remain trusted; dependencies are not rebuilt from source. Endpoint checks cannot detect a temporary change restored between observations. Independent mathematical and terminal reviews have separate scopes. The archive reviewer checks identity and packaging, not a second proof of the theorem.

## Remaining work

WR10–WR12 are the remaining principal formalization groups after WR15 is accepted. `NEXT_RESEARCH_BLOCK.md` records the exact infinite-diagonal-model obligations. The global monograph audit, executable-code refinement, application-specific model identification and synchronized publication editions remain separate. This continuation produces no revised monograph PDF.
