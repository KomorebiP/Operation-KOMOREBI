# Komorebi Unified Inference / Stochastic / Bayesian — v9

Active release: CHECKED_RELEASES/FD_Rounded_Posterior_Certificates_v0.1.0_Checked.
The v8 root controls are preserved under HISTORY/v8_root_control. All inherited
checked-release files are byte-for-byte unchanged. Read AUDIT.json and the active
PROOF_NOTE.md, README.md, FINAL_VERIFICATION_RECEIPT.json, AXIOM_AUDIT.json and
FAILURE_LOG.md before continuing.

## Newly closed

Outward-rounded finite-fractional-precision center-radius evaluation is now checked.
The input remains the exact rational Gram/floor model P=L L^T, R=N N^T+sigma I,
sigma>0, with exact complete self-adjoint rational packets. The represented gain B
is arbitrary. Rounding the evaluation is not perturbing the reference model.

For p fractional binary bits, center-down and radius-up operations preserve every
absolute enclosure. Matrix operations propagate these enclosures from input H,L,N,
sigma,m,y,B through P,R,S,F=P H^T-BS, v=y-Hm, and every packet Q_a F D_b.

Computed b_ab=sum_ij(|center_abij|+radius_abij)^2 and analogous V bound the EXACT
packet and innovation energies. With U=sum_ab b_ab,

    U*(sigma+V) <= eps^2*sigma^2, eps>=0

implies W2(actual posterior, Joseph approximation(B))<=eps. The executed rounded
checker checks exact setup geometry and its outward computed tolerance; it does
not recompute the full exact residual. Successful returns imply all old exact
checker obligations as a proved consequence.

The finite-list precision search is sound. The scalar [4,12] search return is
kernel-checked: p=4 has residual center zero but exact residual -1/1024 and radius
1/8, score 1/32, rejected at eps=1/500. At p=12 score 1/524288 passes. The rotated
singular two-state example rejects p=4 and passes p=12 with score
215859/4194304 at eps=1/4.

Main declarations:

    Komorebi.RoundedPosterior.roundedCandidate_valid
    Komorebi.RoundedPosterior.rounded_tolerance_bounds_posterior
    Komorebi.RoundedPosterior.rounded_return_bounds_posterior
    Komorebi.RoundedPosterior.precision_search_bounds_posterior

## Scope that must not be widened silently

This is a dyadic fixed-fractional-precision enclosure calculus with unbounded
integer parts and exact rational terminal scalar comparisons. It is NOT a proof
about arbitrary IEEE-754 operations, BLAS, overflow/underflow, NaNs, uncertain
measurements, parser/exporter fidelity, or all external numeric producers.
The exact rational model and floor witnesses remain authoritative.

The finite precision search may return None/NOT_CERTIFIED. No general monotonicity
of scores in p, eventual finite-precision success, or rounded Richardson iteration
termination is proved. The v8 termination theorem remains an ideal exact-arithmetic
theorem, not a theorem about rounded gain updates. Exact versus canonical posterior
quantifiers, singular-prior scope, and coupling versus optimality remain unchanged.

## Strongest next bounded target

Prove quantitative precision sufficiency when the exact candidate's score has
STRICT slack below eps^2. Propagate local rounding bounds through this finite
arithmetic graph; do not assume a non-strict boundary comparison eventually passes.
Then develop additive-roundoff residual forcing for rounded Richardson gain steps,
its error floor, and an adaptive-precision theorem that ensures positive-tolerance
success. Soundness of successful returns does not by itself prove these results.

A separate larger direction is finite-horizon filtering-kernel recursion. Do not
reopen the checked Gaussian, exact solver, packet-energy or rounded-soundness blocks.

## Verification

53 active modules passed. All 253 declared theorems/lemmas (68 new) were axiom
audited and use only propext, Classical.choice, Quot.sound. These are declaration
counts, not independent discoveries. All 42 active inherited modules were freshly
rebuilt unchanged; the rest of the historical program was retained, not rebuilt.
Use Lean 4.34.0-rc2 / mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Follow MODULE_ORDER.json in bounded sequential calls with one Lean thread and
warnings treated as errors. The source/compiled-output/dependency receipt audit
passed. Preserve failed and interrupted attempts as non-successful evidence.

The Python result is provisional until its exported Lean module compiles. The
producer's fixed input caps are not a proved hardware resource guarantee. No
literature novelty or numerical performance superiority is asserted.
