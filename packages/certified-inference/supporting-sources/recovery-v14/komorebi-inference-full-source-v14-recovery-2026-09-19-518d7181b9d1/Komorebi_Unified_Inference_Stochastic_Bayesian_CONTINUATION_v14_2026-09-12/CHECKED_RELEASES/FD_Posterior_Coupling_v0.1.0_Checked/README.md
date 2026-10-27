# Finite-dimensional posterior coupling — v0.1.0

This release proves distribution-level error certificates for actual finite-dimensional
Gaussian Bayesian posterior versions. It closes the shared-noise coupling block left
open in the v4 continuation and adds a residual-only stopping certificate for inexact gains.

## Main results

For P positive semidefinite, R positive definite, arbitrary rectangular real H,
S = H P Hᵀ + R, K = P Hᵀ S⁻¹, v = y-Hm, and any proposed gain B, set

    F = P Hᵀ - B S
    J(B) = (I-BH) P (I-BH)ᵀ + B R Bᵀ.

The exact posterior version is η_y. The valid approximation is

    ηhat_y = N(m+Bv, J(B)).

The proved shared-noise coupling has exact squared cost

    ||F S⁻¹ v||² + tr(F S⁻¹ Fᵀ),

and therefore bounds the standard all-coupling squared Wasserstein-2 infimum.
No inverse of P or of the posterior covariance is required.

If a certified noise floor R >= σ I is supplied, σ > 0, the checked bound is

    W2²(η_y, ηhat_y) <= ||F||_F² (1/σ + ||v||²/σ²).

The squared stopping condition

    ||F||_F² (σ+||v||²) <= ε² σ²,  ε >= 0

implies W2(η_y, ηhat_y) <= ε. Its reported right-hand side contains no exact gain,
posterior covariance, or innovation inverse. Numerical evaluation and rounding
certification of its inputs remain separate tasks.

For two valid factored models with compatible latent dimensions, P=L Lᵀ and
R=N Nᵀ, the release also proves

    W2²(η_y, η0_y0) <= ||a(y)-a0(y0)||²
      + ||(I-KH)L-(I-K0 H0)L0||_F² + ||K N-K0 N0||_F².

The actual posterior sampler laws and both marginal equations are proved, not
assumed as a coupling interface.

## Verification scope

31 active Lean modules, comprising 16 retained dependency modules and 15 new modules
(including the comprehensive audit module). The active theorem inventory contains
119 theorem/lemma declarations: 53 retained and 66 new. These are not counts of
independent discoveries. The checks include six symbolic regression theorems and
one nonnegativity support lemma.

All 31 modules were compiled in separate pinned Lean processes with warnings treated
as errors. All 119 theorem/lemma declarations passed #print axioms checks. Only
propext, Classical.choice, and Quot.sound occur. The historical v4 chain is preserved
but its full 38-module moment-bridge build was not repeated; this release freshly
builds the 16-module dependency slice it actually uses.

Read FINAL_VERIFICATION_RECEIPT.json for the actual process receipts, hashes and
scope, AXIOM_AUDIT.json for all audited declarations, and FAILURE_LOG.md for failed
attempts. No failed draft is counted as checked.

## Transport definition and limits

QuadraticTransport.lean defines the standard extended nonnegative all-plan infimum,
not an infimum over a selected finite family, not a Gaussian-only restriction, and
not the displayed coupling cost itself. Quadratic costs use nonnegative extended
Lebesgue integrals. The square-root relation, probability-plan normalization and
self-zero identities are proved. General metric axioms, optimality/existence of
optimal plans, and comparison to any independently defined transport API are not
formalized in this release. The bound nevertheless directly concerns the usual
all-coupling definition.

The approximation using B is not claimed to be the original model's exact conditional
law unless its gain-equation residual is zero. Explicit posterior versions are used
pointwise; canonical-kernel equalities retain the inherited evidence-almost-everywhere
scope. Factor alignment is declared input data and the factor coupling need not be
optimal. No factor-error conversion from covariance-only bounds, packet-energy
refinement theorem, adaptive termination, sequential filtering, singular innovation,
full Itô derivation or literature-priority claim is included.

## Reproduction

The preserved portable runtime is external to this source release:
Lean 4.34.0-rc2 (6a10ac8c22beadecabdbb0919c2b50214762f91d), mathlib
 aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Use MODULE_ORDER.json. Each invocation below checks one module:

    python verify_blocks.py --runtime /path/to/runtime --modules MODULE --timeout 40

Use --clean with the first module for a new project-cache build. Continue in module
order. Do not use --clean for every module. On a normal terminal the verifier can
also run the full listed order, one separate Lean process per module, by omitting
--modules. Tool sessions with a short outer time cap should invoke one module each.

Then run:

    python checks/exact_checks.py
    python checks/negative_controls.py --runtime /path/to/runtime
    python checks/verify_release.py --runtime /path/to/runtime

The last command verifies this sealed release's recorded hashes against the present
runtime outputs; a newly rebuilt binary need not have the same hash across a modified
toolchain. Rebuilding is the proof check. Hash validation authenticates the archived
evidence and detects accidental stale/mismatched outputs; it does not replace Lean.
