# Deliberately invalid controls

All **43** Lean files here must be rejected and remain outside the proof import graph. All 34 predecessor control files are unchanged.

Nine new controls reject finite-test acceptance treated as invariance, unsupported adjacent-level stabilization, strict mass or pointedness without observability, unique positive lifts with redundant synthesis, independently mixed branches treated as normalized, one feasible family treated as whole-set validity, loss of the factor two in the correction bound, and a sufficient certificate cone equated with the canonical domain.

Each is paired with a positive exact counterexample theorem in `Block6Examples.lean`. The inherited placeholder control tests warnings-as-errors. A missing import, unknown identifier, invalid field, unavailable runtime or timeout is not an acceptable rejection. Compiler diagnostics are retained in the complete verification report. Expected rejections are not counted as positive theorem declarations.

## Lean 0.8.0 controls

- `LocalResidualIsGlobalBound.lean`: deliberately false assumption-dropping claim.
- `GainOneUniformError.lean`: deliberately false assumption-dropping claim.
- `NilpotentSwitchingContractive.lean`: deliberately false assumption-dropping claim.
- `FixedHorizonEqualsUniform.lean`: deliberately false assumption-dropping claim.
- `DroppedMemoryPrehistory.lean`: deliberately false assumption-dropping claim.
- `NonlinearDiagonalExact.lean`: deliberately false assumption-dropping claim.
- `UnweightedReconciliation.lean`: deliberately false assumption-dropping claim.
- `ConsensusImpliesTruth.lean`: deliberately false assumption-dropping claim.
- `AmbientAtlasIsometry.lean`: deliberately false assumption-dropping claim.
- `DropPolynomialDomain.lean`: deliberately false assumption-dropping claim.
