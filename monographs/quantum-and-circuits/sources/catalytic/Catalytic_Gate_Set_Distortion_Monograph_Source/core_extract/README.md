# Catalytic Escape from Unitriangularity

**Title:** *Catalytic Escape from Unitriangularity: Thresholds, Algebraic Rarity, and Asymptotic Distortion*  
**Author:** Komorebi P.  
**Date:** August 2026

This release contains the publication-ready paper, its standalone LaTeX source, sixteen vector figures, the figure-generation script, and a frozen computational supplement.

## Main results

The paper proves analytically that the canonical six-row lower-unitriangular target has intrinsic and ambient transvection lengths

```text
lower-directed length = 7
ambient length        = 6
```

over every nonzero commutative ring with identity, when each nonzero scaled row transvection has unit cost. Over a field, the ambient group is the elementary group `E_n(F)=SL_n(F)`; over `F_2` this equals `GL_n(F_2)` and the generators are CNOT gates.

The computer-assisted portion gives complete exact censuses over `F_2` through dimension six and over `F_3` through dimension five. Over `F_2`, dimension six contains exactly twenty defective targets, all with distance pair `(7,6)`. These targets are exactly the three-cross, one-phase catalytic motifs.

The paper also proves:

- a Schreier-holonomy interpretation of catalytic escape;
- the regular-matroid identification of the six carrier states with `M(K_4)`;
- interval-tree rank certificates and connected snapshot targets in every dimension `n >= 7`;
- a rank-one, bandwidth-one excursion theorem: one adjacent upper flag layer can support a linear saving;
- an exact theorem that two upper-directed gates can save at least `floor((n-5)/2)` gates;
- a weighted theorem showing that every fixed finite upper-gate penalty is eventually amortized;
- a general dimension-per-gate principle for algebraic gate families;
- generic rigidity over infinite fields: a Zariski-generic target has both lengths `binom(n,2)`;
- a defect-codimension theorem: defect at least `d` lies in codimension at least `d`;
- finite-field sparsity bounds and an `O_n(q^-1)` average defect at fixed dimension;
- exact ambient distances for selected binary targets in dimensions 7, 8, and 9;
- recursive, direct-sum, and tensor amplification;
- stable tensor length and the possibility of tensor activation;
- an explicit `Omega(n log n)` worst-case additive separation, with coefficient `8/(21 log2(21))` up to a linear term.

## Build the paper

A current TeX Live distribution with `latexmk` is sufficient:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error Catalytic_Escape_Unitriangularity_Thresholds_Algebraic_Rarity_and_Asymptotic_Distortion.tex
```

The pre-generated vector figures are in `figures/`. To regenerate them:

```bash
python3 -m pip install numpy matplotlib
python3 make_figures.py
```

## Reproduce the exact computations

```bash
cd supplement
./run_all.sh
```

The script compiles the C++ programs in a temporary `_build/` directory, reruns every circuit-specific computation, executes the symbolic matroid, resource, algebraic-rarity, and tensor-regularization checks, and compares all results byte for byte with `expected/`.

The complete driver can take several minutes because it includes exhaustive finite-state searches. Each program may also be run separately as described in `supplement/README.md`.

## Proof status

The ring-valued atom, Schreier-holonomy proposition, regular-matroid identification, interval-tree family, bounded, weighted, and microscopic resource theorems, algebraic-rarity theorems, block additivity, recursive lift, tensor rule, stable tensor limit, and asymptotic amplification are symbolic. The finite first-threshold statements, the complete twenty-target classification, and the exact ambient values in dimensions 7 through 9 are computer assisted. The paper separates these proof types and provides search-completeness arguments.

## Publication source

The publication source is:

`Catalytic_Escape_Unitriangularity_Thresholds_Algebraic_Rarity_and_Asymptotic_Distortion.tex`
