# Komorebi Unified Inference / Stochastic / Bayesian — v8

Active release: `CHECKED_RELEASES/FD_Richardson_Posterior_Solver_v0.1.0_Checked`.
Checkpoint sealed September 12, 2026. All root v7 controls are immutable historical
snapshots under `HISTORY/v7_root_control`; this file supersedes their next-task
instructions. All 1114 inherited checked-release files are preserved byte for byte.

## Read first

1. Active `PROOF_NOTE.md` and `README.md`.
2. Active `FINAL_VERIFICATION_RECEIPT.json`, `AXIOM_AUDIT.json`, `FAILURE_LOG.md`.
3. `Komorebi/RationalSolverPosterior.lean`, `RationalSolverSearch.lean`,
   `RationalRichardsonConvergence.lean`, `RichardsonSpectrum.lean`, `GeometricFuel.lean`.
4. `results/FORMAL_INSTANCES.json` and `checks/solve_richardson.py`.

## Newly closed in v8

The exact-rational solver-specific convergence and successful termination gap is
CLOSED_CHECKED. For the existing valid rational model

    P=L L^T, R=N N^T+sigma I, sigma>0,
    S=H P H^T+R, F(B)=P H^T-B S,

choose automatically

    Lambda=sigma+trace(S), tau=1/Lambda,
    rho=1-sigma/Lambda, q=rho^2 in [0,1).

The executable recurrence B_next=B+tau F(B) satisfies

    F_next=F*(I-tau S),
    ||F_n||_F^2 <= q^n ||F_0||_F^2.

The exact packet candidate score a_n obeys a_n<=q^n a_0. For every positive
rational eps, N=ceil_N(a_0/(eps^2*(1-q))) guarantees a passing last iterate.
The early-stop executable solveGain therefore returns Some valid certificate
within N updates, and its actual posterior approximation obeys W2<=eps.
Every Some return is sound even without assuming the inputs valid beforehand.
The existing acceptance policy accepts every exact Richardson next proposal.

Main theorem:

    Komorebi.ExactPosterior.solver_reaches_posterior_tolerance

The scalar instance returns after 4 updates (gain 40/81, W2<=1/20); the singular
two-state rotated-packet instance returns after 3 (gain=(39/125)ones(2), W2<=1/4).
Actual solver returns and iterate counts are kernel-reduced, not inferred from
Python output. These cases do not establish general performance superiority.

## Strongest next bounded target

Develop certified finite-precision residual/energy/floor enclosures. Start with
an exact rational center and explicit rational entrywise error radii, prove
entrywise or packet Frobenius upper bounds for residual formation and innovation
energy, and feed those bounds into the existing checker/actual posterior theorem.
Distinguish fixed exact model data with rounded arithmetic from uncertain physical
model input: the latter needs a model-perturbation bridge as well. A small rounded
residual is not automatically a small exact residual. Do not call interval output
certified until its enclosure proof and real semantics are present.

A separate larger direction is finite-horizon Gaussian filtering-kernel recursion
with propagated certificates. Do not reopen the completed conditioning, packet
energy, rational checker, or exact Richardson termination blocks.

## Other open boundaries

Automatic covariance-factor/floor discovery, parser/exporter proof, bit-complexity
or efficient adaptive algorithms, packet/model-changing policies, factor-alignment
sharpness, the sharper four-term covariance identity, transport metric axioms and
optimality, singular innovation/pseudoinverse conditioning, general matrix-drift
Ito foundations, nonlinear/non-Gaussian systems, and literature-priority comparison.

## Verification and integrity

64 active modules passed with matching final-source/direct-dependency hashes:
50 unchanged inherited active sources, 13 new sources, one complete axiom audit.
All 294 active theorem/lemma declarations, including 62 new declarations, have
axiom audits contained in propext, Classical.choice and Quot.sound. These are
source declaration counts, not counts of independent discoveries.

Use Lean 4.34.0-rc2 / mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Follow
MODULE_ORDER.json in bounded sequential calls, one Lean thread and warnings as
errors. Do not run competing rebuilds in parallel or count timed-out/interrupted
checks. The pinned Mathlib cache is reused. Unrelated historical chains were not
all rebuilt. Preserve exact-vs-canonical posterior quantifiers and all existing
proof boundaries. Positive eps is necessary for the claimed uniform success.

A Python PASS is provisional until the generated Lean proof instance compiles.
Resource-capped Python runs report RESOURCE_LIMIT and export no success theorem.
No floating-point/uncertain-input, practical resource sufficiency, true-error
monotonicity or numerical speedup guarantee is established by exact termination.
