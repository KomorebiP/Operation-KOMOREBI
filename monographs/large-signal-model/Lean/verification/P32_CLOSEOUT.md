# P32 phase closeout — block14

Checkpoint and contemporaneous assessment: `P32-block14-complete`, 2026-10-15. Base: exact delivered Lean 0.13.0 archive SHA256 `7a8f9e5e94c88afb5ada3f73496b09c00e3479d9b165906a7cfe7a3bf914f8c5`. Current proof-file hashes are in BLOCK14_CLAIM_CARD.json; accepted source inventory is in block14_release_run/report.json. This project is an archive-based handoff, not a Git checkout.

The target was P32 as printed in frozen Foundations 1.0.0 §33. It is reached in its finite-table scope. The inverse-norm, leading-subspace, perturbation, coordinate-conditioning and explicit decoder dependencies are all proved. Earlier releases' partial status remains correct for their historical cutoffs.

Decisive records: block11 constructed coordinates under a supplied gap; block12 supplied the one-sided-to-full projection argument; block13 derived and sharpened the actual spectral pseudoinverse norm; block14 constructed the leading-left subspace, proved exact tail and perturbation bounds, and closed the basis matrix decoder. The preserved predecessor summaries and all source files retain that history.

Current formal endpoints:

- `Spectral.finite_table_stability` in NoisySpectralSubspace.lean: actual noisy spectrum and projection gap.
- `FiniteTableP32.coordinates_and_decoder` in FiniteTableP32.lean: actual cross-matrix minimum singular value, injection, both inverse laws and norm.
- `BasisCoordinates.decoder_matrix_formula` in DecoderMatrixFormula.lean: literal U(UhatᵀU)⁻¹ formula in ambient orthonormal coordinates.
- `Spectral.leadingLeft_eq_span_leftModes` and `leftModes_orthonormal`: proof that the constructed space is the claimed leading-left singular subspace.

The structural spectral route succeeded. Implementation failures and two output-write failures were repaired and retained in development_block14; no contrary mathematical result remains unresolved. The attempted trace diagnostic was blocked and abandoned. No fresh-agent independence is claimed.

P32 has no remaining named implication. Further unformalized work is outside this phase. The live continuation is CONTINUE_HERE.md; its next target is P31's exact one-state controlled stochastic counterexample. The broader 48-item list remains in ROADMAP_1.0.json.

PASS: 282 cumulative stages; 84 metadata/tooling checks. Exact delivered-ZIP replay is recorded separately in the external verification JSON.

See AUDIT.md, BLOCK14_DEVELOPMENT_SUMMARY.json, BLOCK14_PROOFREAD.json and the external exact-archive verification JSON for review and execution limits.
