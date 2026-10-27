# Paper XII — Checked Fitting block, v0.16.0

Recorded September 11, 2026, America/Chicago (verification timestamps use UTC).

**Completed:** original Claims 6.3, 6.4, 6.5 and 7.1.
**Revised ledger:** 47/49 complete, no partials, two unchecked (3.1 and 3.3).
**Original-wording ledger:** 39 complete, 7 partial, 3 unchecked.
**No new statement amendments.** All eight inherited amendments remain separate.

The block adds 56 named theorem declarations in 10 modules, plus one private helper.
The fresh low-memory replay compiles those ten modules and three unchanged predecessor
support modules. All 89 audited named declarations have only allowed foundational axioms.
All three invalid controls are rejected for the expected reason.

The actual intrinsic construction and independence theorem are in IntrinsicFitting.lean
and PresentationIndependence.lean. Arbitrary base change is FittingBaseChange.lean;
full support/Fitting transport is FittingTransport.lean; support and higher strata are
FittingStrata.lean. The support and strata proofs cover finitely presented modules over
any commutative ring, with separate wrappers deriving finite presentation from the
manuscript's Noetherian/finite assumptions.

The 71 original production sources are preserved byte-for-byte under upstream/v0.15.0/lean.
They were not all rebuilt in this release. See verification.json and UPSTREAM_PRESERVATION.json.

Remaining work: actual completed tensor-product quotient (3.1), then completed global
base change imposing the local conditions (3.3). Ordinary tensor right exactness alone
must not be counted as either completed theorem. No universal arithmetic existence or
automorphy input is proved by this block.
