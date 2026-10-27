# Projector-Resolved Seed Calculus VI

This release accompanies **Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations** by **Komorebi P.**

The Python package implements the finite and spectral models used in the paper:

- packet block decompositions of matrix semigroups;
- exact Markov lumping and refinement defects;
- Bayesian updates, packet evidences, exact coarsening criteria, information-loss packets, conjugacy, and nonlinear Bayesian flows;
- finite conditional-expectation projectors and martingale increments;
- spectral fractional powers and square-root subordination;
- finite-difference Green kernels and low-mode convergence;
- finite-state Feynman-Kac transfer;
- exact Schur-Feshbach latent-state elimination and memory kernels;
- survival and hazard functions from transient semigroups.

The code supports the finite proofs and numerical certificates in the paper. It does not assert universal continuum convergence or solve arbitrary stochastic, Bayesian, fractional, or PDE models.

## Current checked edition — v0.5.0

The reviewed manuscript is 34 pages. Paper VI has **33 complete scoped manuscript results, zero partial and zero pending**, with **341 checked supporting Lean theorem declarations in 47 modules** and 782 namespace declarations audited. The full pinned build, axiom audit, 54 companion tests and six verifier controls pass.

This block closes the final two results: general nonnormal memory/Laplace self-energy (13.2) and canonical holomorphic naturality (15.1). Both manuscript proofs are expanded. See `../THEOREM_LEDGER.md` and `../REVIEW.md`. The three separately stated conjectures remain open and are excluded from the ledger count.

## PowerShell

After extracting the folder into Downloads:

```powershell
$Work = "$env:USERPROFILE\Downloads\Projector_Seed_Calculus_VI_Release"
Set-Location $Work
Set-ExecutionPolicy -Scope Process Bypass -Force
& .\Run_All.ps1
```

`Run_All.ps1` checks imports and installs only missing Python packages. To request dependency updates explicitly:

```powershell
& .\Run_All.ps1 -Update
```

To run the Python study and tests without rebuilding the PDF:

```powershell
& .\Run_All.ps1 -SkipPdf
```

## Direct Python commands

```powershell
python .\run_all.py
python -m pytest -q
```

## New finite Bayesian refinement theorem

For strictly positive likelihoods and a finite partition with at least two coarse packets, conditioning commutes with coarsening for every prior exactly when the fine likelihood is constant on each coarse packet up to one global scale. A one-packet coarsening is automatically closed. The canonical equality-of-profiles partition is the coarsest likelihood-resolving partition; see the corrected main statement.  When this condition fails, the release computes the exact defect through the conditional effective-likelihood packet and supplies an explicit `L1` certificate.

## New bounded fractional-naturality theorem

For bounded nonnegative self-adjoint fine and coarse generators, the fractional intertwining defect is represented exactly by a resolvent integral.  The manuscript gives a gap-free Holder estimate, a sharper common-gap linear estimate, and the corresponding fractional-semigroup Duhamel bound.  Exact generator intertwining therefore propagates to every fractional power `0 < alpha < 1` in this setting.  Unbounded-domain and nonnormal extensions remain separate analytic questions.

## Verification and numerical provenance

The canonical reviewed PDF and TeX are in `../manuscript`. The 54 companion tests include the original 37 and 17 review boundary/validation cases; all pass again. Full Lean status and exact scoped coverage are recorded in `../verification/verification_status.json` and `../THEOREM_LEDGER.md`. Prose-to-Lean correspondence and ordinary specializations are manually reviewed.

The numerical implementation and all 19 figure pairs are unchanged. The retained 79-field numerical comparison was performed for the first checked block; this block reruns the 54 tests and the full Lean build and axiom audit.
