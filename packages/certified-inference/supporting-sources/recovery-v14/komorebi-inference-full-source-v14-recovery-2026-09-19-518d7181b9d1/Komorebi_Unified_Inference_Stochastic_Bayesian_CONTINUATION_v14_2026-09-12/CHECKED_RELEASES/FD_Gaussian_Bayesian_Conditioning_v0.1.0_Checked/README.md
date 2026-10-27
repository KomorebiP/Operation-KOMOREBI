# Finite-dimensional Gaussian Bayesian conditioning — checked release

## Central result

Let the state and observation index types be arbitrary finite types. Let

- `m : EuclideanSpace ℝ ι`,
- `H : Matrix κ ι ℝ`,
- `P : Matrix ι ι ℝ`, with `P.PosSemidef`,
- `R : Matrix κ κ ℝ`, with `R.PosDef`.

The prior is Mathlib's `multivariateGaussian m P`. The likelihood is the actual
Markov kernel `gaussianAffineKernel H 0 R`, whose value at `x` is
`multivariateGaussian (H x) R`.

With `S = H P Hᵀ + R`, `K = P Hᵀ S⁻¹`, and `C = P - K H P`, the checked theorem
`canonicalPosterior_eq_multivariateGaussian` proves

```
∀ᵐ y ∂N(Hm,S),
  posterior (gaussianAffineKernel H 0 R) (N(m,P)) y
    = N(m + K(y-Hm), C).
```

Here matrix action is implemented by `matrixCLM`. The covariance is also proved
equal to the Joseph expression `(I-KH) P (I-KH)ᵀ + K R Kᵀ`.

The prior covariance may be singular. Observation noise is still required to be
positive definite. No inverse of `P` is used.

## What changed

The prior covariance checkpoint established matrix identities. This release
constructs the actual forward and reverse joint measures and proves their equality:

```
N(Hm,S) ⊗ₘ fdPosteriorKernel H m P R
  = (N(m,P) ⊗ₘ gaussianAffineKernel H 0 R).map Prod.swap.
```

It then derives the evidence marginal and invokes Mathlib's posterior uniqueness
theorem. The main conclusion is not assumed as a hypothesis.

The combined finite-dimensional source has 51 theorem/lemma declarations: 17
retained from the covariance checkpoint and 34 newly checked here. These counts
include elementary support identities, one formerly unverified wrapper, and two
symbolic regression theorems. They are not counts of distinct mathematical discoveries.
There are 18 source modules including the all-theorem axiom-audit module.

## Verification

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- Every module is checked with `-DwarningAsError=true`.
- The final build removes all project `.olean` outputs before rebuilding in order.
- Existing pinned mathlib dependency caches are reused, not rebuilt.
- No `sorry`, `admit`, custom `axiom`, or `unsafe` declarations occur in the sources.
- All 51 theorem/lemma declarations are covered by `#print axioms`.
- Only `propext`, `Classical.choice`, and `Quot.sound` occur in those audits.
- Source, logs, receipts, and retained baseline files are hashed.

See `FINAL_VERIFICATION_RECEIPT.json`, `audit/`, and `SHA256SUMS` for the execution
record. Development failures are preserved rather than counted as evidence.

## Reproduce in small blocks

The large Linux/WSL portable runtime is not included. Use the same restored
`Komorebi_Portable_Lean_4.34.0-rc2` bundle. From this release directory:

```bash
python3 verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The script makes one separate Lean invocation per module, with a 75-second cap
per invocation. It performs no network access and rejects a different Lean/mathlib
revision. It refuses to overwrite an existing staged source with different bytes.

For a single module after its dependencies have been checked:

```bash
python3 verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --only FDGaussianConditioning
```

Fresh recheck logs are written below `audit/rechecks/` rather than overwriting the
sealed verification evidence.

## Explicit boundaries

This release does not establish a finite-dimensional multiscale posterior-error
budget by itself. The matrix-to-continuous-linear-map interface to the earlier
operator-norm perturbation results still needs to be formalized.

It does not prove a Wasserstein, Hellinger, or KL bound. It does not cover singular
innovation matrices, pseudoinverse conditioning, nonlinear or non-Gaussian models,
or derive linear SDE moment equations from Itô integration.

The canonical posterior equality is evidence-almost everywhere. The explicit
Gaussian kernel is defined at every observation and is a valid posterior version,
but pointwise equality to Mathlib's selected canonical version is not claimed.
No multivariate density-normalization formula or every-observation normalized
Bayes-density identity was needed or checked in this proof.

Literature priority and novelty have not been established.

## Archive integrity

Run `python3 verify_artifacts.py` to check packaged hashes and recorded proof
evidence without compiling Lean. This is distinct from rerunning
`verify_blocks.py`. The evidence manifest uses the version-1 computation-audit
record shape; detailed before/after source hashes and execution commands are in
the per-module receipts. Its structural/hash check is package-local, not a claim
that the separately distributed Mathbox validator was executed.
