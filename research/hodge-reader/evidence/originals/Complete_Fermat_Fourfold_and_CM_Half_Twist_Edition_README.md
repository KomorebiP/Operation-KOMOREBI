# Complete Fermat Fourfold and CM Half-Twist Edition

This package rebuilds the focused constructive monograph:

**Complete Fermat Fourfold and CM Half-Twist Edition**  
*Projector-Resolved Character Packet Calculus*

Author: Komorebi P.

## Purpose

The edition is organized around the explicit structure of Fermat fourfold character packets. Its goal is not to argue for or against a broad conjecture. It develops a constructive calculus for:

- balanced six-packets and rational Galois packets
- exact conductor descent and Mobius packet projectors
- complementary-pair, saturated-join, curve, and Delsarte channels
- the exceptional degree-33 Klein-Delsarte transfer
- infinite packet towers and prime-power classifications
- weighted dyadic refinement
- CRT-Kummer phase decomposition
- K4 and K23 packet factorizations
- imaginary CM selectors and explicit Fermat-curve half-twist carriers

The final constructive target is an explicit rank-one Chow correspondence from the selected lower Fermat-curve CM packet to the K23 weight-one packet.

## Build

From this directory, run:

```bash
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Fermat_Fourfold_CM_Half_Twist_Complete.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Fermat_Fourfold_CM_Half_Twist_Complete.tex
```

A current TeX Live installation with `tcolorbox`, `cleveref`, `microtype`, and the standard AMS packages is required.

## Status convention

The manuscript distinguishes:

- symbolic theorems proved in the text
- exact finite certificates reproduced by the included scripts
- correspondence constructions complete at manuscript level
- uniform statements still requiring a proof
- the final explicit Chow map still to be constructed

Finite packet checks are supporting certificates, not substitutes for correspondence-level proofs.

## Package layout

- `figures/`: vector figures used by the focused edition
- `tables/`: generated LaTeX tables
- `data/`: machine-readable verification ledgers
- `scripts/`: selected exact verification programs
- `CLAIM_BOUNDARY.md`: concise proof and construction status
