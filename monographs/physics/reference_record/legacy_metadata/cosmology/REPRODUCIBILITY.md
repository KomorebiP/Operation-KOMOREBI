# Reproducibility Guide

## Build the book

Run `Build_Volume_II.ps1` on Windows or `Build_Volume_II.sh` on Linux or WSL. Both invoke `latexmk` with halt-on-error behavior.

## Frozen inputs

The source archive includes the figures and numerical tables used by the monograph. The `data/` directory contains CSV and JSON records from the background, perturbation, dark-sector, Boltzmann, CMB, lensing, nonlinear-structure, baryonic-response, and subhalo analyses. The `verification/` and `code/` directories retain the corresponding computational programs where available.

## What the build proves

A successful LaTeX build proves only that the archived source compiles. Numerical records retain the domains, tolerances, and approximation classes stated in their originating chapters. Formula presence, a zero numerical residual, or a deterministic script does not by itself establish historical novelty or a general theorem beyond the declared hypotheses.

## Independent reproduction

An independent reproduction should record:

1. the exact release tag or asset hashes
2. operating system, Python and compiler versions, and numerical libraries
3. whether the implementation was rewritten or imported
4. all changed parameters and tolerances
5. raw residual and convergence records
6. any failed or sign-changing result

## PDF quality checks

The release process renders every page, checks for blank pages and extreme-border contact, performs PDF preflight, rebuilds from a clean source tree, and compares rendered output.
