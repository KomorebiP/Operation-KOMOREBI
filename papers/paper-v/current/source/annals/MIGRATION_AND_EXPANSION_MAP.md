# Migration and Expansion Map

## Article identity

**Final title:** *Multiresolution Signal Calculus, Singular Packets, and Stable Reconstruction*

**Author:** Komorebi P.

The original Paper V was a 28 page signal realization of the broader seed and packet program. It contained 11 theorems, 1 proposition, 4 corollaries, 13 proof environments, 3 conjectures, 16 figures, and 3 tables. The revised article is a 43 page standalone journal manuscript with 83 numbered mathematical records and 63 complete proof environments.

The revision does not enlarge the article by adding unrelated signal processing topics. It develops the mathematical chain that was already implicit in the original paper:

\[
\text{lattice coordinates}
\longrightarrow
\text{transfer matrices}
\longrightarrow
\text{stable filter banks}
\longrightarrow
\text{packet trees}
\longrightarrow
\text{singular packets}
\longrightarrow
\text{recovery and approximation}.
\]

## Main migration decisions

| Original material | Revised location | Disposition |
|---|---|---|
| Impulse orbit and one dimensional residues | Sections 2 and 3 | Generalized to \(\ell^p(\mathbb Z^d)\), \(c_0\), finite periodic lattices, and arbitrary finite index sublattices |
| One dimensional polyphase identities | Section 3 | Recast as an isometric lattice decomposition with translation covariance and exact nested refinement |
| FIR transfer law | Section 4 | Generalized to bounded \(\ell^1\) convolution on \(\mathbb Z^d\), with norm control and composition |
| Perfect reconstruction banks | Section 5 | Expanded to rectangular banks, quantitative reconstruction defects, perturbation estimates, frame bounds, canonical synthesis, and frame stability |
| Haar and one lifting example | Section 5 | Retained, clarified, and placed inside the general bank theory |
| Finite Haar packet tree | Section 6 | Generalized to arbitrary finite pruned unitary trees and recursively bounded nonunitary trees |
| Provisional adaptive packet tree | Section 6 | Replaced by an exact dynamic recursion for every finite tree with additive node cost, plus cost and basis stability theorems |
| Exact known edge identity | Section 7 | Expanded to finite packets of truncated powers that encode jumps in the function and its derivatives |
| Mask perturbation estimate | Section 8 | Replaced by exact scalar region and overlap matrix formulas, higher order location bounds, and geometric tube estimates |
| Broad automatic edge recovery conjecture | Sections 9 and 10 | Proved for a declared one dimensional class of separated jumps under deterministic and sub Gaussian noise. Broad image recovery remains open |
| Haar localization examples | Section 10 | Strengthened by exact smooth and jump coefficient laws, a two shifted grid guarantee, and higher order annihilating differences |
| Gibbs discussion | Section 11 | Restated as a conditional approximation theorem. No unconditional elimination claim is made |
| Nonlinear cyclic product law | Section 12 | Retained and expanded to exact shifted monomial and polynomial shift formulas |
| Numerical experiments | Section 13 | Reduced to clearly labeled finite illustrations with negative scope statements |
| Smith chart realization | Section 14 | Retained as a secondary independent realization rather than part of the recovery theorem chain |
| General seed rank, obstruction, and holonomy theory | Not repeated | Left in the foundational papers rather than reproved in a signal article |

## New theorem groups

### Lattice and transfer theory

The revised paper adds exact finite index lattice packets in arbitrary dimension, internal translation formulas, transfer norm control, and composition of packet transfer matrices.

### Stable filter banks

The perfect reconstruction identity is supplemented by an operator norm reconstruction certificate. The article also derives perturbation bounds for both analysis and synthesis filters, pointwise frame criteria, canonical coefficient noise bounds, and stability of the frame bounds.

### Packet trees and best basis selection

The original complete Haar tree is replaced by a theorem for every admissible pruning of a finite unitary packet tree. The paper also treats nonunitary local splits. Additive best basis selection is solved exactly by bottom up dynamic programming, and the selected pruning is stable whenever the original cost gap dominates the cost perturbation.

### Higher order singular packets

A finite family of truncated powers

\[
\phi_{m,\tau}(t)=\frac{(t-\tau)_+^m}{m!}
\]

removes the trace jumps of a piecewise Sobolev function through any declared finite order. The remaining component is globally Sobolev. The packet coefficients are uniquely determined by the trace jumps.

### Exact estimated packet errors

The revised article separates amplitude mismatch, region overlap, location displacement, background approximation, and reconstruction operator stability. It includes exact formulas for scalar regions and full partitions, along with boundary tube estimates for geometric perturbations.

### Stable one dimensional recovery

The original broad recovery target has been replaced by a theorem that can be proved completely. For separated jumps sampled on a uniform grid, an explicit adjacent contrast gap yields exact jump cell recovery, midpoint location accuracy, amplitude control, jump count recovery, sign recovery, and finite \(L^p\) consistency. Independent sub Gaussian noise and repeated measurements are treated with finite probability certificates.

### Alignment and polynomial structure

Two half shifted Haar grids remove exact boundary alignment at a fixed scale. Higher differences annihilate polynomial interiors and localize their response to finite breakpoint bands.

## Material intentionally not claimed

The revised paper does not prove any of the following:

1. Universal recovery of arbitrary edges from general noisy data
2. Recovery of arbitrary two dimensional boundary topology
3. Minimax optimality of the adjacent contrast detector
4. Consistency under fixed single sample noise as the grid is refined
5. Universal removal of Gibbs oscillation without correct packet identification
6. Optimality of the finite Smith coordinate weighting
7. Superiority of one basis over every other basis or every signal class

These boundaries are stated in the article rather than left implicit.
