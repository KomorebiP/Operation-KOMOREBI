# Komorebi Unified Inference / Stochastic / Bayesian — v12

Active release: CHECKED_RELEASES/FD_Posterior_Output_Enclosures_v0.1.0_Checked.
Parent: v11 SHA256 588640ecfc3faba00ff98bea0e82b1c6586cead970f2ecc4a6ad1a5c745761be.

## Newly completed and Lean checked

The canonical program Komorebi.PosteriorOutput.run extends the retained rounded
gain solver with actual dyadic mean/covariance interval arrays. For valid exact
factor-coded data, fixed complete self-adjoint packets, and any positive rational
epsilon and delta, it returns a passing candidate with

    W2(actualPosterior, JosephGaussian(returnedGain)) <= epsilon,

and parameter enclosures of that SAME Gaussian, every radius <= delta.

The exact specification is mu_B=m+B(y-Hm), A_B=I-BH,
C_B=A_B P A_B^T+B R B^T. The actual output graph rounds its model-factor products,
mean and Joseph covariance operations through the inherited dyadic ball nodes.
All terminal radius coefficients are bounded by their finite sum K(B), and
p_out=1+floor_log_2(ceil_nat(K(B)/delta)) suffices at EVERY p>=p_out.
No precision monotonicity, inverse, eigenvalue or square-root calculation is used.

Key declarations in namespace Komorebi.PosteriorOutput:
  evaluate_encloses, evaluate_grid, evaluate_radii_le, represent_spec,
  outputCovariance_posSemidef, approximation_eq_output_gaussian,
  represented_real_errors, run_terminates, run_sound.

The probability identity is checked against the retained RationalModel.approximation
and gainJoseph/gainMean definitions. The return theorem connects the arrays to the
actual evaluator and the same returned gain, not unrelated existential witnesses.

## Concrete instances

Scalar: same v11 rounded gain, epsilon=1/20, output delta=1/1000, p_out=27.
Mean center 66280359/134217728, radius 1/134217728.
Covariance center 16779773/33554432, radius 1/33554432.

Singular two-state rotated-packet model: same v11 rounded gain, epsilon=1/4,
delta=1/1000, p_out=32. Mean centers zero, radii 1/2147483648.
All covariance centers 90211493/268435456, radii 7/4294967296.
All these values, actual combined returns and ResultValid statements compile.

## Boundary that must not be erased

The intervals enclose the parameters of the certified APPROXIMATION, not exact
posterior parameters with only delta error. Epsilon controls error to the actual
posterior. The centers alone do not define a separately certified Gaussian.

A checked counterexample: C=[[1/4,3/4],[3/4,9/4]] is a singular Gram covariance;
one-bit downward entry rounding gives D=[[0,1/2],[1/2,2]]. For z=(-3,1),
z^T D z=-1. Entry enclosures survive but the center matrix is not PSD.
Do not claim a sampler or a center-defined Gaussian without a separate proof.

## Verification and reproduction

82 active modules freshly compiled, including 74 unchanged inherited modules;
416 theorem/lemma declarations audited, including 47 new support/example
statements. Allowed axioms only: propext, Classical.choice, Quot.sound.
Pinned Lean 4.34.0-rc2, mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
One thread, warnings as errors. Six corrected draft compiler failures, no
incomplete receipts. Three invalid controls rejected. Exact diagnostics: six
matrix cases, five fixed precisions, three output tolerances, 398 assertions and
three expected producer rejections. The final v2 experiment manifest validates.
The seal checks final source/log/compiled-output/direct-dependency hashes.

Read the focused README for a runnable producer and rebuild commands. Python
PASS_OUTPUT_PROVISIONAL is not a formal certificate until its exported instance
compiles. Resource caps can stop the executable and prohibit success-proof export.
The large portable runtime remains separate; its restoration metadata is retained.

## End goal and strongest next routes

This closes interval parameter output and quantitative output precision in the
finite-dimensional one-update release contract. A separately certified point
factor output/sampler is still open. The wider goal remains certified genuinely
resolution-adaptive inference: specify one packet-selective update policy, account
for cross-packet effects, prove progress/termination, and measure full computation
plus certification cost. Sequential filtering, uncertain-input and parser semantics,
hardware arithmetic, performance advantage and literature novelty remain open.
Do not reopen the completed conditioning, exact/rounded solver or precision layers
without identifying an actual error. Preserve all v11 proof boundaries and history.
