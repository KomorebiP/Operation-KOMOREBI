# Block 09 failures and repairs

28 snapshotted development compilations: 10 passed and 18 failed. These are development invocations, not theorem counts. Each receipt preserves actual command, source SHA-256, duration, return code and compiler log. A pass is not a cumulative audit.

The failures included reserved-identifier parsing (`partial` and `λ`), dependent-domain/`lp` coercions, finite-sum and derivative API normalization, deprecated API and warnings-as-errors failures, and one import attempted before its dependency compiled. Four diagonal-domain attempts contained Lean’s deterministic 200000-heartbeat-limit diagnostics. Explicitly fixing the `ℓ²(I, ℂ)` type of the singleton avoided that elaboration bottleneck; no heartbeat or kernel-check bypass was added. Cascading errors from failed declarations are retained as failures, not mathematical counterexamples.

The final API probe under `verification/development/block09/api_probe_final.lean` is discovery scratch with unknown-name probes, not active mathematics and not a passed module. Additional ad hoc #check probes were not counted as mathematical development snapshots.

A supplementary 15-signature #check inspection exceeded its 30-second limit; its input and a TIMEOUT receipt are preserved under development/block09/supplementary_signature_timeout. Its stdout was not written before the subprocess exception, and no completed signature-inspection result is claimed. This was not an active mathematical-module compilation. A status-poll tool call also timed out while the separately launched cumulative verifier continued; the completed report was later read directly.

Files could not provide source page images 30, 31 and 33. The included original PDF was rendered and inspected locally. Its bytes were not changed. The portable runtime restoration succeeded with the exact seven-part checksums; the restoration log is retained.

The first cumulative mathematical audit passed, but a subsequent packaging review found that lakefile.toml still advertised version 0.8.0. It was corrected to 0.9.0. Because that file is a hashed proof input, the prior audit was retained as superseded and the in-progress first extraction recheck was deliberately stopped, not counted as PASS. The corrected cumulative audit and a new fresh-extraction audit are the production pair. See verification/block09_metadata_correction.json. No mathematical source changed for this repair.

| Attempt | Module | First compiler diagnostic |
|---|---|---|
| `20260913T223931702912Z` | GraphDomain | KomorebiPhysics/GraphDomain.lean:65:21: error: Application type mismatch: The argument |
| `20260913T223950282884Z` | GraphDomain | KomorebiPhysics/GraphDomain.lean:65:23: error: Application type mismatch: The last |
| `20260913T223957875616Z` | CountableAtlas | KomorebiPhysics/CountableAtlas.lean:1:0: error: object file '/mnt/data/Komorebi_Physics_Lean_v0.9.0/.lake/build/lib/lean/KomorebiPhysics/GraphDomain.olean' of module KomorebiPhysics.GraphDomain does not exist |
| `20260913T224028952230Z` | CountableAtlas | KomorebiPhysics/CountableAtlas.lean:31:3: error: unexpected token 'partial'; expected identifier |
| `20260913T224102353569Z` | CountableAtlas | KomorebiPhysics/CountableAtlas.lean:54:20: error: Type mismatch |
| `20260913T224408841356Z` | CountableContinuity | KomorebiPhysics/CountableContinuity.lean:99:17: error(lean.unknownIdentifier): Unknown identifier `abs_ofNat` |
| `20260913T224624022843Z` | DiagonalDomain | KomorebiPhysics/DiagonalDomain.lean:20:10: error: unexpected token 'λ'; expected '_' or identifier |
| `20260913T224641244924Z` | DiagonalDomain | KomorebiPhysics/DiagonalDomain.lean:27:4: error: Type mismatch: After simplification, term |
| `20260913T224724332486Z` | DiagonalDomain | KomorebiPhysics/DiagonalDomain.lean:42:20: error: Variable name `x` is not explicitly referenced. |
| `20260913T224802322961Z` | DiagonalDomain | KomorebiPhysics/DiagonalDomain.lean:61:8: error: (deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached |
| `20260913T225055634209Z` | DiagonalDomain | KomorebiPhysics/DiagonalDomain.lean:60:41: error: (deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached |
| `20260913T225248887277Z` | SpectralGraph | KomorebiPhysics/SpectralGraph.lean:29:79: error: unexpected token 'omit'; expected 'lemma' |
| `20260913T225309944489Z` | SpectralGraph | KomorebiPhysics/SpectralGraph.lean:60:2: error: Type mismatch: After simplification, term |
| `20260913T225339621809Z` | SpectralGraph | KomorebiPhysics/SpectralGraph.lean:108:4: error: try 'simp' instead of 'simpa' |
| `20260913T225502648625Z` | UnboundedExamples | KomorebiPhysics/UnboundedExamples.lean:35:50: error: Application type mismatch: The argument |
| `20260913T225525319312Z` | UnboundedExamples | KomorebiPhysics/UnboundedExamples.lean:98:2: error: Type mismatch: After simplification, term |
| `20260913T225638359154Z` | DomainExamples | KomorebiPhysics/DomainExamples.lean:28:26: error: `ContinuousLinearMap.smul_apply` has been deprecated: Use `smul_apply` instead |
| `20260913T225701256235Z` | DomainExamples | KomorebiPhysics/DomainExamples.lean:76:2: error: Type mismatch: After simplification, term |

Current cumulative report status when this file was generated: **PASS**. Its completed `verification/final/report.json` is authoritative. Intentionally invalid controls are a separate expected-failure contract and are not included in the 18 development failures.
