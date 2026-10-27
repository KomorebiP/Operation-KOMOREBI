# Full-edition formalization roadmap

## Current boundary

Chapter 2 is checked in the declared finite-atlas/bounded setting. Chapter 4.1–4.8 are checked in the precise scopes of Blocks 03–05. Chapter 4.9 is now checked under explicit finite-expansion, fixed-depth and fixed-ratio assumptions. Mixed-state, tensor, partial-trace and Lindblad results use finite complex matrices. Entropy derivatives retain strict-positive hypotheses. Chapter 5.1–5.3 are checked for finite bounded positive resolutions, including actual moving derivatives and exact coarsening. This is not an exhaustive inventory or a completion percentage.

| Stage | Source area | Current status | Next obligation |
|---|---|---|---|
| 1 | Atlas, energy transfer, coarsening | Block 01 checked | Preserve finite/bounded scopes. |
| 2 | Moving frames and whole-object deformation | Block 02 checked | Preserve invertibility, completeness, unitarity and actual derivatives. |
| 3 | Chapter 4.1–4.8 transfer extensions | Blocks 03–05 checked | Retain positivity, logarithm, graph and dynamical-existence boundaries. |
| 4 | Chapter 4.9 refinement cancellation | Block 06: exact tower plus actual remainder, sharpness and noise bounds | Establish expansion hypotheses separately for any later physical discretization. No formal infinite-series convergence is claimed. |
| 5 | Chapter 5 positive/overlapping atlases | Block 07: (5.1)–(5.21) and sharp specialization (5.32) checked | Next: actual Parseval-channel analysis/synthesis and dilation (5.22)–(5.31). |
| 6 | Countable/unbounded extensions and later finite differential obstruction | Not completed | Inventory source and prove domain, convergence and noncommutative identities separately. |
| 7 | Discrete relativity and gauge fields | Not started in this release | Clifford algebra, walk unitarity, dispersion branches, holonomy and locality. |
| 8 | Gravitation, constraints and strong fields | Not started in this release | Actual brackets, propagation, regularity and continuum boundaries. |
| 9 | Cosmology, dark sectors and observation | Not started in this release | Model equations, approximation assumptions and corrected-branch bookkeeping. |

## Immediate next block

Physical PDF page 28 (printed 15), Chapter 5.4, equations (5.22)–(5.31). Construct effects from an actual bounded Parseval-channel family, prove probabilities as channel norms, prove state and operator reconstruction, then build the direct-sum isometry and coordinate-projector compression. Do not conflate a given Parseval family with an unproved universal factorization of all positive atlases. The sharp-current identity (5.32) is already checked in Block 07.

## Limits not closed by Block 07

Positive effects need not be projectors. No universal effect factorization/dilation, countable positive-operator measure, or unbounded-generator theorem is claimed here. The effect/state derivatives are actual inputs. Weighted postprocessing is nonnegative and column-normalized with weights fixed in time; arbitrary signed or time-dependent weights are not covered. The exact two-dimensional example uses commuting overlapping effects, although the general theorem does not impose commutation.

## Earlier limits still active

The source's formal series is not an automatic analytic expansion. The new theorem assumes a finite-order remainder for the actual original approximation, with fixed finite depth and fixed b>1. It does not cover variable-depth limits, certified floating-point arithmetic, or unconditional noise contraction. It is not a proof that a lattice or gravitational model converges to its intended continuum theory.

Earlier actual trajectories remain inputs. Generator Hermiticity and trace conservation do not establish positivity preservation or existence. Strict-positive entropy derivatives do not cover zero populations, and detailed balance is not arbitrary-reference or quantum-relative-entropy dissipation. General graph connectivity/convergence rates and coarse Markov closure remain separate.

## Source reconciliation

Chapter 3's unit, variational and asymptotic claims remain separately uninventoried. Compare the master with the two-volume research edition and supplements before claiming exhaustive full-edition coverage. Keep the source's own P/N/C/Q/O labels separate from Lean status. Preserve the corrected scale-covariant dark-sector candidate and the rejection of earlier additive branches. Formal validity of a model does not establish its empirical adequacy.
