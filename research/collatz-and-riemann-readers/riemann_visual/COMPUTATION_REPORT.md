# Riemann visual guide computation audit

Date: 2026-10-08. Guide release: v1.1. Author label: Komorebi P.

The mathematical role of this computation is to generate twenty four explanatory figures and check their finite arithmetic and normalization examples. Its contract does not include testing RH, locating off line zeros, or estimating asymptotic signed Möbius cancellation. The universal implications and the absolute cube barrier are manuscript proofs in the companion monograph. Source dependent facts use its verified source register and `shared/LITERATURE_CHECK.md`.

## Reproduction

From the parent of `conjecture_set`, run:

```sh
python conjecture_set/riemann_visual/figures.py
python conjecture_set/build.py --only riemann_visual
```

`requirements.txt` records the numpy and matplotlib versions actually used. The script needs ordinary Python standard library modules plus those two packages. It does not need mpmath, sympy, a network connection, or a zeta oracle. It reads `shared/figures/data.json` for the previously audited xi samples. Its input hash and code hash are recorded in `COMPUTATION_REPORT.json`. The script writes `data.json`, twenty four vector PDFs, twenty four PNG previews, and the JSON report. No randomness is used.

The run is bounded by the declared grids and finite loops. No machine enforced memory or CPU cap was applied. The schema version 1 manifest passed the computation audit validator with output hashes checked from the `conjecture_set` root. The validator reports the schema's legacy provenance limits. Recording input hashes does not convert it to a version 2 runner record.

## Exact finite arithmetic

Python integers and `fractions.Fraction` are used for these checks:

| Check | Range | Result |
|---|---|---|
| Closed K = 1 cube formulas | Q = 6 and 30, 1 ≤ m ≤ 100 | 200 equalities passed |
| Squarefree support identity | 1 ≤ n ≤ 200 | 200 equalities passed |
| Direct sum versus rough base grouping | Q = 6 and 30, K = 1, 2, 3, n ≤ 200 | Six equalities passed |
| Partial triangle inequality | Q = 6, K = 1, coprime bases m ≤ 100 | 33 prefix inequalities passed |
| Positive cube tail benchmarks | Q = 6 and 30, K = 900, m = 90, 120, 180, 360 | Eight rational controls passed |

The grouped finite n sum truncates each divisor corner by `b*m <= 200`. This is essential. A common base cutoff without the corner cutoff would represent a different finite object. Spread 18 instead deliberately shows two finite sums with the same base cutoff 100. It states that neither is the full infinite sum. Exact rational values and summands are stored in `data.json`.

The Möbius implementation removes each prime factor once and returns zero immediately on a repeated prime. The support check uses the separate divisor square identity μ(n)² = sum over l² dividing n of μ(l). The nonsquarefree rows 25 and 49 have zero Möbius coefficients in the coprime sector for Q = 6. That support survives the majorant.

## Numerical controls

| Check | Input and convention | Error or output |
|---|---|---|
| Gaussian physical norm | t = 1/4, 1/2, 1, 16001 points on [−12,12] | Maximum error 2.22 × 10⁻¹⁶ |
| Gaussian overlap | t = 1/2, center separation 1.25 | Formula and quadrature agree to reported binary64 precision |
| Hermite Gram matrix | Modes 0 through 4, same 16001 point grid | Maximum matrix error 4.44 × 10⁻¹⁶ |
| Coherent Poisson coefficients | λ = 6, indices 0 through 24 | Independent recurrence discrepancy 2.78 × 10⁻¹⁷ |
| Finite Báez Duarte coefficients | K = 0 through 12, Decimal precisions 60 and 80 | Maximum discrepancy below 5.4 × 10⁻⁵⁷ |
| Positive tail curves | M = 30, Q = 6 and 30, 90 ≤ m ≤ 360 | Both remain above κ₃ ≈ 0.487669 |

These quadratures and tolerances are implementation controls, not interval certified integration. The exact norm, overlap, coherent, and Poisson identities come from their analytic formulas. Hermite functions use the normalized three term recurrence. This avoids computing large raw Hermite polynomials for the plot.

For finite c_K values, the script constructs even Bernoulli numbers with an exact rational triangular recurrence, then evaluates the classical even zeta formula with a recorded 100 digit π literal. Decimal arithmetic is checked at 60 and 80 digit settings. Controls include B₂ = 1/6, B₄ = −1/30, B₆ = 1/42, and c₀ = 6/π². The internal precision comparison does not validate the decimal π literal independently. The reviewer separately recomputed π with Machin arctangent series and the Bernoulli numbers with their defining triangular sum, using Decimal settings 70 and 90. All thirteen values passed, with maximum difference 4.66 × 10⁻⁷⁷ from the recorded 80 digit results. That independent check is preserved in the shared review record.

Spread 02 reuses 701 xi samples on critical line height 0 through 35 from the first release. The prior report documents 50 digit evaluation, nine 75 digit controls, Hardy Z comparisons, and functional equation controls. This run plots those recorded values. It does not claim a new zeta evaluation.

## Diagram and model boundary

Spreads 01, 03, and 06 use selected point coordinates to show centered strip geometry, reflection, and Laplace domains. They contain no sampled off line zeros. Spread 05 plots hypothetical single mode amplitude envelopes with the fixed nonzero heat coefficient omitted. It uses exponent δ, while spread 07 uses squared energy models with exponent 2δ.

Spread 21 is a declared scale model with d = floor(sqrt(log M)), constants omitted. It is not an actual count of supported bases. Spread 22 is a schematic power comparison, constants suppressed. It is not a measured full majorant or a lower bound on signed c. The other formula diagrams encode exact identities without assigning artificial numerical channel sizes. The dependency map has no new direct transfer arrow between the Möbius packet and the prime heat packet.

## Failures and corrections

The first figure run stopped at spread 03 because matplotlib's math parser requires braces around the argument to `overline`. The unbraced label was corrected. The same review added braces to wide tilde and square root labels before the full rerun. The successful run produced every figure and all finite checks. No failed run output is treated as complete evidence.

The default environment has no mpmath import. This was detected before numerical design. The guide therefore reuses the audited xi input and uses exact rational plus Decimal evaluation for its finite coefficient example. There was no failed or silently truncated zeta computation.

The first truncation chart included q = α as an endpoint while its title stated q > α. The plotted interval now begins at q = 1.001 with α = 1. The rate formula itself remains unchanged.

The first guide build also encountered a missing `ShortTitle` header definition in `main.tex`. The root build workflow added the required definition and PDF title metadata. The corrected guide compiled successfully. This was a document integration failure, not a mathematical failure.

All twenty four figure previews were visually inspected in four contact sheets. Labels, arrow endpoints, signs, support rows, formula constants, and plot bounds were checked. Final PDF spread inspection is recorded in the root layout report. RH remains unproved in this work.
