# Block 10 development failures and repairs

16 development compilations were recorded; 11 failed. No failed compilation was counted as a checked theorem.

Failures concerned infinity notation scope, the actual adjoint-characterization API, complex inner-product order, finite-sum/function coercions, explicit limit constants, deprecated names under warnings-as-errors, a reserved Greek-token spelling, field normalization and scalar coercions. Some early type errors caused cascading metavariable/admission diagnostics in dependent declarations. These were failed elaborations, not accepted proof terms. Final sources contain no such holes.

The first cumulative production attempt compiled all 52 mathematical modules and passed the complete axiom inventory, but the complete release audit FAILED: eight new negative controls had unclosed noncomputable sections. Their intended false goals were rejected, yet the extra namespace-end syntax diagnostics lay outside the mapped control bodies. The verifier correctly refused a pass. The failed report, generated batch, logs and original control snapshots are retained under verification/block10_failed_control_scope_audit and verification/development/block10/control_scope_originals. Adding the missing end command in each new control repaired the test-source structure. No mathematical source, false assertion, old control or diagnostic guard was changed. A complete cumulative rerun, not merely a local control test, was required.

The portable runtime was restored from all seven existing mounted parts with per-part and combined SHA-256 verification. The baseline completed. Production/fresh-extraction status is read from their completed reports, not inferred from these development runs.

| Module | Exit | Seconds | Recorded snapshot and diagnostic |
|---|---:|---:|---|
| KomorebiPhysics.BoundedSpectral | 1 | 5.58 | `verification/development/block10/20260913T234538826815Z` |
| KomorebiPhysics.BoundedSpectral | 1 | 3.09 | `verification/development/block10/20260913T234600031881Z` |
| KomorebiPhysics.BoundedSpectral | 1 | 4.61 | `verification/development/block10/20260913T234613469717Z` |
| KomorebiPhysics.BoundedSpectral | 1 | 4.62 | `verification/development/block10/20260913T234639399653Z` |
| KomorebiPhysics.BoundedSpectral | 1 | 4.82 | `verification/development/block10/20260913T234657915547Z` |
| KomorebiPhysics.SpectralTruncation | 1 | 7.37 | `verification/development/block10/20260913T234854775556Z` |
| KomorebiPhysics.SpectralTruncation | 1 | 5.36 | `verification/development/block10/20260913T234932703616Z` |
| KomorebiPhysics.HarmonicSurrogates | 1 | 4.74 | `verification/development/block10/20260913T235148072666Z` |
| KomorebiPhysics.AnchoredSurrogates | 1 | 4.49 | `verification/development/block10/20260913T235327252598Z` |
| KomorebiPhysics.AnchoredSurrogates | 1 | 4.88 | `verification/development/block10/20260913T235349977229Z` |
| KomorebiPhysics.SpectralErrorBounds | 1 | 4.90 | `verification/development/block10/20260913T235524639451Z` |
