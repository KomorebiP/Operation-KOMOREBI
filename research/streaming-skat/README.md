# Streaming Polyphase Factor Decomposition for SKAT-like Tests - v0.5

This release extends the illustrated v0.4 manuscript with a certified theory
for approximately sparse phase graphs.

## New in v0.5

- weighted phase-transfer matrix
  \(\mathcal B_{hg}=\|P_hHP_g\|_2\);
- phasewise propagation envelope
  \(\rho(H^kX)\le \mathcal B^k\rho(X)\);
- thresholded-operator certificate
  \(\rho((H^k-H_0^k)X)\le(\mathcal B^k-\mathcal B_0^k)\rho(X)\);
- certified approximate light cone for weak nonzero couplings;
- polynomial/Krylov certificate for \(p(H)-p(H_0)\);
- scalar depth-threshold law;
- deterministic numerical validation for depths 1-8, a phase-threshold sweep,
  and a signed degree-four polynomial;
- two new explanatory figures integrated into the manuscript.

## Evidence status

The transfer-matrix, thresholded-power, approximate-light-cone, scalar, and
polynomial results are proved analytically.  The finite computations validate
the implementation and illustrate conservatism; they are not the proof.

## Primary files

- `FINAL_MANUSCRIPT.tex`
- `FINAL_MANUSCRIPT.pdf`
- `APPROXIMATE_LIGHTCONE_THEOREM.tex`
- `approximate_lightcone.py`
- `test_approximate_lightcone.py`
- `benchmark_approximate_lightcone.py`
- `approximate_lightcone_depth.csv`
- `approximate_lightcone_threshold_sweep.csv`
- `approximate_lightcone_phase_profile.csv`
- `polynomial_krylov_certificate.csv`
- `APPROXIMATE_LIGHTCONE_MANIFEST.json`
- `PROOF_AUDIT_APPROXIMATE_LIGHTCONE.md`
- `VERIFICATION_V05.md`

The earlier exact streaming, tiling, partition-invariance, phase-local rank,
QR-core, range-core, and K-COS interface files remain included.


## v0.7 additions
- `spectral_tail_bridge.py`: phase-pruning -> operator -> spectrum -> K-COS tail certificate.
- `test_spectral_tail_bridge.py`: theorem-path regressions.
- `direct_spectral_tail_brackets.csv`: direct Weyl/K-COS brackets.
- `dual_budget_spectral_scheduler.csv`: simultaneous Krylov and operator budgets.
- `certify_after_prune_range_core.csv`: exact range-core stopping audit.
- `PROOF_AUDIT_SPECTRAL_TAIL_BRIDGE.md`: proof and limitation audit.

## v0.9 realistic SKAT validation
- `benchmark_realistic_skat.py`: corrected copy-LD and latent-Gaussian LD simulation battery.
- `test_realistic_skat.py`: reproducibility and streamed-kernel regression tests.
- `realistic_skat_scenarios.csv`: LD and spectral diagnostics.
- `realistic_streaming_invariance.csv`: raw-genotype block-size invariance.
- `realistic_deep_tail_accuracy.csv`: ordinary realistic-LD tail comparisons.
- `realistic_large_deeper_tail.csv`: corrected large copy-LD tails through about 10^-458.
- `PROOF_AND_SIMULATION_AUDIT_V09.md`: provenance, validation scope, and claim boundary.
