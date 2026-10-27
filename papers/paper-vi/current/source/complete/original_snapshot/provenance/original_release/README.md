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

For a finite packet partition, conditioning commutes with coarsening for every prior exactly when the fine likelihood is constant on each coarse packet up to one global scale.  When this condition fails, the release computes the exact defect through the conditional effective-likelihood packet and supplies an explicit `L1` certificate.

## New bounded fractional-naturality theorem

For bounded nonnegative self-adjoint fine and coarse generators, the fractional intertwining defect is represented exactly by a resolvent integral.  The release proves a gap-free Holder estimate, a sharper common-gap linear estimate, and the corresponding fractional-semigroup Duhamel bound.  Exact generator intertwining therefore propagates to every fractional power `0 < alpha < 1` in this setting.  Unbounded-domain and nonnormal extensions remain separate analytic questions.
