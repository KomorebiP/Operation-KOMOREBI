# Finite-dimensional multiscale posterior semantic bridge

Author: Komorebi P.  
Checkpoint: v0.1.0, 2026-09-11 (America/Chicago)

## Completed result

For two finite-dimensional linear-Gaussian models with positive semidefinite prior
covariances and positive definite observation-noise covariances, the existing
operator perturbation and projector refinement theory now applies to the actual
centered covariance operators and expectations of their Bayesian posterior laws.
The observation matrices may be rectangular. Both priors may be singular.

The main assembled declaration is:

```lean
Komorebi.FiniteDimensionalGaussianKalman.GaussianModel.multiscale_posterior_certificate
```

`GaussianModel` contains the mean, prior covariance, observation matrix, noise
covariance, and their stated positivity proofs. It does not contain an assumed
posterior-law equality, a desired error bound, or an innovation inverse hypothesis.
Those conclusions are derived.

## Important definition

`centeredCovOp` is defined from Mathlib's centered `covarianceBilin`, independently
of a supplied covariance matrix. In this pinned Mathlib, the separately named
`covarianceOperator` is uncentered. It must not be substituted for `centeredCovOp`.
The module `FDCenteredCovariance` proves the centered-integral interpretation and
the Gaussian matrix identification.

## Verification scope

The active build has 38 Lean modules, including two audit modules. It contains
138 theorem/lemma declarations: 51 inherited Gaussian declarations, 39 unchanged
perturbation/refinement declarations extracted into small dependency modules,
and 48 new declarations including support lemmas and six regression theorems.
These counts are not counts of independent mathematical discoveries.

Every active module has a successful final-source compile receipt with warnings
as errors. All 138 theorem/lemma declarations have an explicit axiom audit.
Only `propext`, `Classical.choice`, and `Quot.sound` appear. The source scan excludes
placeholders, new axiom declarations, unsafe code, and native-decide shortcuts.
The older entire research program has not been recompiled in this release.

## Reproduction in bounded blocks

Restore the supplied portable Lean 4.34.0-rc2 runtime with mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06` first. The runtime is not included here.
Then run from this release:

```bash
python3 verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --clean --modules
python3 verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --modules FDKalmanDefs
```

Continue with one named module per invocation, in `MODULE_ORDER.json` order.
The default per-process cap is 25 seconds; a slower local host can increase it
with `--timeout`. Every process is independently logged. No network fetch occurs.
Do not import the original monolithic perturbation source alongside its split
modules: the same declarations would be imported twice.

`split_dependencies.py` reconstructs the needed dependency slices byte-for-byte
from the preserved predecessor source. `DEPENDENCY_SPLIT.json` records original
line ranges and hashes. The continuous-time parts of that predecessor are retained,
not promoted to newly verified results by this one-step bridge.

Run `checks/exact_regression.py` for one independent exact rational two-state
convention check. It is not the proof of the universal result. In that deliberately
singular-prior example, the off-diagonal posterior discrepancy is 1/3, so the
example does not impose exact packet closure on the true posterior.

## Remaining boundaries

No Wasserstein, Hellinger, total-variation, or KL estimate is asserted. No
Pythagorean/Frobenius identity is substituted for an operator-norm estimate.
Canonical posterior versions retain their own evidence-almost-everywhere
qualifications. Primitive model errors are not identifiable from posterior
agreement. Singular innovation, nonlinear/non-Gaussian filtering, full Itô
semantics, and optimal adaptive refinement are not established here.

See `PROOF_NOTE.md`, `CONTINUE_HERE.md`, `FAILURE_LOG.md`, and
`FINAL_VERIFICATION_RECEIPT.json` for precise details. No literature priority is claimed.
