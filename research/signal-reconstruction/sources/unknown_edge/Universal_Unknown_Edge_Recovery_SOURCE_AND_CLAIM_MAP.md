# Source and claim map

## Exact theorems proved in the manuscript

1. Noninjective measurements forbid universal recovery.
2. Overlapping background and edge classes forbid unique decomposition.
3. No finite Fourier measurement set admits a separation-free Lipschitz inverse over colliding opposite jumps.
4. Finite dictionary recovery is universal over all `s`-sparse packets exactly when the residualized dictionary has no nonzero `2s`-sparse null vector.
5. The restricted separation constant gives a deterministic coefficient-error bound.
6. A periodic piecewise-constant edge becomes a finite atomic measure after distributional differentiation.
7. Fourier modes above the declared background band contain edge moments only.
8. The Hankel rank equals the active number of distinct nonzero jumps.
9. The annihilating polynomial recovers every off-grid jump location.
10. A Vandermonde system recovers every jump amplitude.
11. Zero-mean periodic integration reconstructs the edge packet.
12. Low-mode subtraction reconstructs the bandlimited background.
13. The complete signal is exactly recovered from finitely many Fourier coefficients.
14. Separate edge and smooth synthesis gives an exact Gibbs-free final reconstruction.
15. A Rouché disk condition gives a deterministic local root certificate.
16. Shared-edge multichannel recovery is exact when the stacked recurrence system has full column rank.
17. Piecewise-polynomial derivative moments satisfy a confluent annihilating recurrence.
18. The finite residualized-dictionary theorem applies without change to the supplied two-dimensional rectangle library.

## Computational certificates

The single Python file performs 19 named checks and generates all numerical records. Representative errors are:

- location error: `4.6629367034256575e-14`
- jump error: `2.9309921493206785e-13`
- full reconstruction error: `3.8191672047105385e-14`
- maximum reconstruction error across four exact random cases: `3.9601655288379334e-13`
- finite dictionary separation constant: `0.5116895108313039`
- symbolic annihilator: `z**4 - 1`
- symbolic Hankel determinant: `6144`

## Established ingredients used

Prony-type annihilation and finite-rate-of-innovation sampling are established signal-processing ideas. The bibliography names the primary sources used for historical context. This release does not claim invention of annihilating filters, Prony recovery, or finite-rate-of-innovation sampling.

## What remains outside the proof

- model-free recovery of arbitrary edges
- one stability constant valid as edges collide
- a complete noisy minimax theorem for the full piecewise-smooth class
- arbitrary continuous two-dimensional edge curves
- unbounded edge counts without a finite-rate hypothesis
- unknown background spectra without a valid separation mechanism
- historical novelty of the classical recovery ingredients

## Role of the projector-resolved calculus

The calculus organizes the proof as a sequence of exact objects:

\[
\text{background projector}
\to
\text{derivative packet}
\to
\text{Hankel packet}
\to
\text{annihilator}
\to
\text{edge synthesis}
\to
\text{background synthesis}
\to
\text{complete reconstruction}.
\]

The Gibbs result follows because the recovered singular packet is never sent through the truncated global Fourier synthesis used for the smooth packet.
