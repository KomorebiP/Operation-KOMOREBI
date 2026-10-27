# Block 29 failure ledger

- **Original curvature-only target:** the proposed implication from small or
  zero face plaquettes to arbitrary fixed-order Clifford refinement is false
  without straight-edge reconstruction assumptions.  The target was corrected
  rather than forced.
- **Hilbert expansion:** an initial `simp` proof expanded the spinor inner
  product into coordinate norm squares before using projector orthogonality.
  The repaired proof expands sesquilinearly first, eliminates cross terms with
  `ip_plus_minus` and `ip_minus_plus`, and only then normalizes coefficients.
- **Interpolation subtraction:** the midpoint branch required the explicit
  `smul_sub` identity.
- **Global energy sum:** pointwise mismatch energy did not rewrite under a
  broad simplifier.  The proof now uses `Finset.sum_congr` and the exact
  pointwise theorem.
- **Runtime extraction:** the first portable-runtime extraction was interrupted
  before completion.  The assembled archive hash was verified and extraction
  was restarted from the verified archive.
- **Monolithic cumulative rebuilds:** several attempts to rebuild every
  unrelated parent module exceeded the outer execution window while filling an
  empty project cache.  They are recorded as inconclusive and excluded.  The
  release instead uses byte-identical inheritance of the checked v0.28 parent
  plus a complete Block 29 import-closure rebuild.
- **First production-wrapper run:** one wrapper invocation exceeded its outer
  window after the new module, API, audit, and two controls had passed.  It was
  discarded.  A clean rerun completed all gates and produced the authoritative
  PASS report.
