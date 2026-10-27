# Next Lean blocks after the regularization limits

This is a restart contract, not evidence that the remaining statements are formalized. Check the final release ledger and receipt before treating this continuation as accepted.

## First bounded target: WR15 coordinate-certificate invariance

Freeze the exact proposition in `records/targets/05k_stopping_rules.tex`. In finite-dimensional real Hilbert spaces, let the columns of B be an arbitrary basis of the entire protected correction space. Retain the ambient inner products and G = BᵀB. For the printed coordinate normal residual q, establish all of:

- The actual Hilbert normal residual is g = B G⁻¹ q.
- Its squared norm is qᵀ G⁻¹ q.
- For every invertible coordinate change C and B′ = B C, the same correction has c′ = C⁻¹c, G′ = Cᵀ G C and q′ = Cᵀq.
- The scalar certificate is invariant: (q′)ᵀ(G′)⁻¹q′ = qᵀG⁻¹q.

Include the zero-dimensional case. Do not silently require an orthonormal basis or prove only a scalar rescaling example. The basis must span the entire permitted kernel; a proper subspace solves a different problem.

First executable step: choose a finite basis/linear-equivalence interface and prove that the Gram operator is invertible and identifies the coordinate covector with the existing restricted Hilbert gradient. Reuse the accepted protected adjoint and normal-residual declarations. Keep matrix representation and abstract Hilbert identities visibly connected. Then prove basis-change identities and add a nonorthonormal scalar-line example and a rejection of the unweighted coordinate norm.

## Larger connected block: WR10–WR12

These remain written mathematical results whose full Lean statements must be frozen individually before implementation.

| Group | Required scope |
| --- | --- |
| WR10 | The infinite diagonal operator/model, Hilbert membership, optimizer identity, energy and residual bounds, and certified tail estimates. Finite truncations alone are insufficient. |
| WR11 | Both sum asymptotics and the exact infinite-problem budget limit. Close the passage from sampled optimal budgets to all large real budgets. |
| WR12 | The noisy attainable diagonal example, the rounded parameter choice, and the stated rate with constants. Its inexact-solver application also depends on the accepted WR16 transfer. |

The new WR08 limits and WR09/WR16 transfer theorems supply general convergence infrastructure but do not prove any of these explicit diagonal formulas or rates. Prioritize the exact infinite-dimensional membership/operator layer before numerical illustrations.

## Restart discipline

Use the accepted `formal/` source snapshot and exact receipt, not a development object directory. New proofs are additive; retain numbered attempts, diagnostics, owner scopes and base hashes. Every coverage promotion requires fresh strict compilation, full new exported types, all-declaration axiom checks, intended controls, and independent statement review. Endpoint hashes retain their documented limitations.

The v1.10.0 PDF remains historical. A future monograph edition should synchronize the three newly completed groups only after this continuation is accepted. The global independent monograph audit, executable-code refinement proof, application-specific model identification, and companion-guide updates remain separate tasks.
