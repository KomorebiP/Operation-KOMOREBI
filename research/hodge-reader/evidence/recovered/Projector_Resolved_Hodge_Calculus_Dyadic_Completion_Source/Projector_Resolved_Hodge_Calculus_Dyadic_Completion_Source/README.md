# Projector-Resolved Hodge Calculus - Complete Edition

This source package rebuilds the complete PDF:

**Projector-Resolved Hodge Calculus: Complete Fermat Fourfold and CM Half-Twist Edition**

Author: Komorebi P.

## Build

From this directory, run:

```bash
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Hodge_Calculus_Complete.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Hodge_Calculus_Complete.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Hodge_Calculus_Complete.tex
```

A modern TeX Live installation with `tcolorbox`, `cleveref`, `microtype`, and the standard AMS packages is required.

## Claim boundary

- The general rational Hodge conjecture is **not** claimed as proved.
- The manuscript records a prior published all-degree Fermat-fourfold generalized-Hodge claim, but treats the literature relationship as requiring independent audit.
- The constructive contribution is the packet-resolved program: exact conductor projectors, degree-33 Klein-Delsarte closure, infinite packet towers, odd prime-power classification, the all-degree dyadic uniqueness theorem, Kummer phase grammar, K23 pair-triple factorization, and an explicit CM carrier.
- The final constructive gap is an explicit Chow-level CM packet correspondence. Finite checks and Hodge-level identifications do not replace that correspondence.

## Layout

- `figures/`: 41 vector-PDF figures used by the manuscript
- `tables/`: generated LaTeX tables
- `data/`: machine-readable verification ledgers, including the all-degree dyadic audit
- `scripts/`: selected exact verification programs; `fermat_hodge_dyadic_uniqueness.py` is the dyadic theorem verifier


## Dyadic verification

Run the independent exact audit with:

```bash
python scripts/fermat_hodge_dyadic_uniqueness.py --max-symbolic-s 14 --max-exhaustive-m 128 --out data/Fermat_Hodge_Dyadic_Uniqueness_VERIFICATION.json
```

The exhaustive phase reproduces the full-conductor orbit classification through modulus 128. The structural phase checks the triangle, star-conductor, orbit, and SAT(3) identities through modulus $2^{14}$. The universal theorem is proved in the manuscript and does not depend on stopping at those bounds.
