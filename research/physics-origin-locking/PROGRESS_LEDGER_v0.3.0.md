# Komorebi Physics: origin locking and expansion ledger

Version: **0.3.0**  
Date: **21 October 2026**  
Predecessor: Vacuum Matching and Dynamical Energy Transfer, ledger 0.2.0.  
Status: finite research block delivered with two explicit failed acceptance gates. Original cosmological recovery remains open.

## Critical correction

The original source model density-locks at **q=0**. The values **q=±4** are the empty-sector tree vacua. The preceding explanation conflated these distinct points. The old calculation of the energy cost at q=4 remains mathematically valid under origin matching, but it does **not** prohibit density locking at the origin. Source evidence and the precise interpretation are recorded in `notes/CORRECTION_LOCKING_TARGET.md`.

The exploratory depth-12 branch was begun before this source correction. It is preserved solely as an explicitly changed-model comparison, not as the necessary route to origin locking.

## Completed work

1. Re-read the original covariant bridge and cosmology, especially their classical FLRW exchange and origin stability conditions. Corrected the target-location interpretation.
2. Derived and proved the incoherent fixed-distribution identity Y=rho-3p, the local curvature Y-4D/S, monotonic dilution, and uniqueness of the conditional loss-of-curvature threshold. Separated these from capture, coherent dynamics, and attractor claims.
3. Derived a fixed-background bound for time-averaged coherence. It is not a Floquet stability result.
4. Proved uniqueness of the positive-radius empty-sector minimum of the origin-matched potential. Computed q_min≈3.70470009e-6 and fractional vacuum release≈1.14373356e-12 at depth 15 with high-precision arithmetic.
5. Audited exact inherited crossing states 1, 20, and 39. Computed hypothetical incoherent transport without rescaling occupations or deleting residual scalar kinetic energy. These are sensitivity diagnostics, not relic predictions.
6. Derived exact quartic-matching barrier/curvature identities and a conditional nonnegative double-well construction. Established that the original depth-15 content cannot simultaneously satisfy the tested central-maximum barrier window within the budget. This is a restriction of the stated model class, not a universal no-go.
7. Implemented a finite expanding Gaussian-mode action with coherent pressure, reaction force, variable kinetic coefficient, radiation, Raychaudhuri evolution, and an independently monitored Friedmann constraint.
8. Proved its finite pressure-work identity and mode invariant. Independently checked symbolic cancellations and an alternative complex-mode representation.
9. Ran 29 configurations: 25 with the stated correct finite equations and 4 intentionally incorrect controls. The altered-model long run was refined after its absolute invariant diagnostic failed, and the failure persisted.
10. Demonstrated fixed-cutoff quadrature convergence in an accelerated-expansion stress test, but failed its momentum-cutoff test. Derived the leading omitted H^2 and H*qdot structure as a diagnostic, not as an isolated subtraction.
11. Recovered the inherited flat-limit first crossing and compared actual microscopic Hubble scaling with the flat solution over tau≤12.
12. Audited saved mode states and replayed four named configurations. Wrote a 16-page supplement with five Python figures, code, evidence records, and licenses. No new Lean work was performed. Main monograph unchanged.

## Verification boundary

The final numerical audit reports **19 passing gates and 2 failed gates**. The strict acceptance command intentionally exits with code 3. Scope and individual numerical observations are in `VERIFICATION_REPORT.md` and `results/verification.json`.

The failures are not equivalent. The accelerated-expansion cutoff failure is a physical/renormalization acceptance failure in the primary finite origin branch. The absolute hyperboloid residual failure occurs in highly occupied secondary altered-model runs and limits that numerical representation. Excellent total-energy conservation does not override either failure.

No new Lean certification, independent external mathematical review, covariant fourth-order stress renormalization, physical incoming state, capture theorem, late out-state, target relic abundance, or intended vacuum-energy relaxation is asserted.

## Exact restart point

Continue from the **origin-matched depth-15 branch**, not the changed q=4 branch. Start with `code/expansion.py` and references `origin_stress128` / `origin_stress128_cut32` for the decisive failed cutoff gate, and `origin_static_refined` / `origin_physical_refined` for the short physical-scale comparison.

1. Derive a common curved-background subtraction or effective action for the force, rho, pressure, and metric terms. The two-derivative diagnostic contains qdot², H*qdot, and H² contributions. The old flat kinetic tail provides only the first. A fourth-order stress prescription is still required for a renormalized continuum claim.
2. Prepare a state with compatible expansion-dependent adiabatic regularity. The current flat rest-point state is a finite diagnostic input, not a cosmologically selected vacuum. Separate initial-state effects from bulk counterterm effects.
3. Hold physical matching data fixed and rerun the origin cutoff and quadrature tests. Do not cure a cutoff failure by fitting a different background potential at every cutoff.
4. Establish a valid late-time/incoherent state before applying the trace-locking transport criterion. Carry the residual scalar kinetic energy throughout and distinguish local curvature from actual capture or attraction.
5. Address the independent vacuum-fate issue: the origin-matched empty sector releases only ~1.14e-12 of D. Recovering a transient vacuum-energy scenario requires explicitly different physical matching/protection/completion, not just local release of the origin.
6. For the optional altered-model high-occupation runs, use structure-preserving or high-precision mode variables before accepting their absolute normalization. Do not silently loosen the existing absolute gate.

## Preservation and provenance

The original frozen benchmark SHA-256 is unchanged:
`7a08c0964796a8cd607b2a59ed8b2bfb6cfb8e4df31b7b03627c8201bc2c796e`.

Earlier monographs and archived source releases are not overwritten. All explicit changes, rejected models, execution issues, and the correction are retained. The manifest certifies byte identity only.
