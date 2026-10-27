# Projector-Seed Calculus for Integer Sequences

## Spectral, Local, Adelic, and Polyphase Transfer Extension

**Author:** Komorebi P.

This package contains the complete 127-page monograph, modular and flattened LaTeX sources, twenty-four generated figures, exact verification code, machine-readable result files, and reproducible build scripts.

## Main results

The paper develops a restricted finite grammar for structured integer sequences and proves exact realization and packet compilation for legal, well-founded specifications. It unifies finite recurrences, holonomic and hypergeometric systems, automatic digit systems, Riordan and Sheffer transforms, Bell composition, algebraic tree equations, filtered products, multiplicative arithmetic functions, generalized Euler families, and local arithmetic coordinates.

The **spectral torsion--Fourier transfer theorem** determines, for every persistent C-finite sequence, the exact minimal recurrence, reduced rational denominator, Hankel rank, and linear-state dimension of every arithmetic subsequence. It gives a complete root-of-unity rank-drop criterion, exact double periodicity, a finite torsion packet signature, quasipolynomial rank counts, Fourier reconstruction, and a packet uncertainty inequality.

The **local and adelic extension** adds:

- one source-kernel formulation for odd-prime and dyadic Euler reconstruction;
- a finite-field Fourier proof of the exact standard-window period;
- the exact dyadic kernel valuation `v_2(kappa_{2,m}) = 4m - 1`;
- the optimal dyadic truncation modulus `2^(4M+3)`;
- scalar, polynomial-exponential, matrix, and finite-adelic Carmichael--Mahler transfer;
- odd-prime depleted Euler interpolation and direct dyadic Euler interpolation;
- explicit valuation ledgers separating transfer depth, kernel arithmetic, source valuation, and base-prime carries.

The **polyphase extension** adds:

- exact discrete polyphase analysis, synthesis, and nested mixed-radix factorization;
- the carry algebra for Cauchy products and the polyphase shift matrix;
- an explicit affine Mahler kernel `Theta_(M,s)`;
- exact mixed-radix kernel composition;
- preservation of monotone p-adic valuation ladders;
- Frobenius sparsification at prime-power radix;
- scalar and matrix precision amplification under repeated p-power refinement;
- the character--polyphase coordinate lattice for separating torsion phase, local digit address, and Mahler depth.

## Reproduction

From the project root:

```text
python code/verify_sequences.py
python code/generate_figures.py
python code/flatten_latex.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The reference suite performs **87,915 exact checks** with **0 failures**. It uses arbitrary-precision integers, exact rational arithmetic, exact polynomial identities, modular arithmetic, matrix arithmetic, and exact Hankel ranks. Floating-point conversion is used only by the plotting layer.

## Layout

- `paper.pdf` — compiled 127-page monograph
- `main.tex` — modular master source
- `Projector_Seed_Calculus_for_Integer_Sequences_Local_Polyphase_Extension.tex` — flattened single-file source
- `sections/` — theorem and appendix modules
- `code/verify_sequences.py` — exact verification suite
- `code/generate_figures.py` — generation of twenty-four figures
- `code/flatten_latex.py` — single-file source generator
- `results/verification_summary.json` — machine-readable verification summary
- `results/verification_run.txt` — human-readable verification output
- `tables/verification_ledger.csv` — check-family ledger
- `Build.ps1` and `build.sh` — reproducible build scripts

## Claim boundary

Finite computations certify the declared ranges; they do not replace general proofs. The paper does not claim that finite terms determine an intended continuation, that every sequence has a short legal grammar, that every family or terminology is historically new, or that polyphase decomposition automatically simplifies every branch. The new polyphase layer is exact and theorem-backed; exact higher valuations of the affine kernel, optimal mixed-radix trees, nonlinear polyphase transfer, and a combined spectral-local minimality signature remain open.
