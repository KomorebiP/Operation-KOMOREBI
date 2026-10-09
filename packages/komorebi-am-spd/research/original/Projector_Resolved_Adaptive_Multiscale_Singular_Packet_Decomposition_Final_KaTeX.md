# Adaptive Multiscale Singular Packet Decomposition

## Final theory and verification edition

**Author:** Komorebi P.

AM-SPD represents an image with three deliberately separate objects:

1. a geometry-aware packet core
2. a finite family of localized singular subspaces
3. an exact residual archive

The reconstruction is

$$
F
=
P_KA_K
+
\sum_{\nu\in\mathcal T}
M_{\Omega_\nu}
\left(
U_\nu\Sigma_\nu V_\nu^{\mathsf T}
\right)
+
R_{\mathrm{archive}}.
$$

The first two terms form the finite compressed model. The last term keeps every value not explained by that model. Therefore

$$
\boxed{F=\widehat F+R_{\mathrm{archive}}.}
$$

## 1. Singular packets

A final singular packet is the tuple

$$
\mathcal P_\nu
=
(\Omega_\nu,o_\nu,r_\nu,Q_\nu,\sigma_\nu,C_\nu,\pi_\nu).
$$

Here:

- $\Omega_\nu$ is its spatial support
- $o_\nu$ is the row, column, or channel unfolding
- $r_\nu$ is its selected local rank
- $Q_\nu$ is the embedded orthonormal packet basis
- $\sigma_\nu$ stores the retained singular values
- $C_\nu$ is the declared parameter cost
- $\pi_\nu$ records its parent or residual source

A packet is therefore a localized subspace, not merely one singular vector.

## 2. Best local rank theorem

Let

$$
A=U\Sigma V^{\mathsf T}
$$

be one unfolded local residual patch, with singular values

$$
\sigma_1\ge\sigma_2\ge\cdots\ge0.
$$

Define

$$
A_r=U_r\Sigma_rV_r^{\mathsf T}.
$$

For every matrix $B$ with $\operatorname{rank}(B)\le r$,

$$
\boxed{
\|A-A_r\|_F^2
=
\sum_{j>r}\sigma_j^2
\le
\|A-B\|_F^2.
}
$$

### Proof

Let $P$ be the orthogonal projector onto the column space of $B$. Since $PB=B$,

$$
A-B=(I-P)A+(PA-B).
$$

The two terms are orthogonal, so

$$
\|A-B\|_F^2
\ge
\|(I-P)A\|_F^2.
$$

Writing

$$
AA^{\mathsf T}
=
\sum_j\sigma_j^2u_ju_j^{\mathsf T},
$$

we obtain

$$
\|PA\|_F^2
=
\sum_j\sigma_j^2\|Pu_j\|_2^2.
$$

The weights lie in $[0,1]$ and sum to at most $r$. Their weighted sum is largest when the first $r$ weights are one and all others are zero. Hence

$$
\|PA\|_F^2
\le
\sum_{j=1}^r\sigma_j^2.
$$

Therefore

$$
\|(I-P)A\|_F^2
\ge
\sum_{j>r}\sigma_j^2.
$$

Equality is attained by $B=A_r$.

The theorem is applied separately to row, column, and channel unfoldings. AM-SPD compares these local model classes rather than declaring one unfolding universally best.

## 3. Exact post-projection block gain

Let $V$ be the active reconstruction space and $P_V$ its projector. The current residual is

$$
r=(I-P_V)F.
$$

A proposed packet block has raw directions $D$. Remove all directions already represented:

$$
D_\perp=(I-P_V)D.
$$

Let $Q$ be an orthonormal basis for $\operatorname{range}(D_\perp)$. After adding this block and refitting globally,

$$
\boxed{
\|r_{\mathrm{new}}\|_2^2
=
\|r\|_2^2-
\|Q^{\mathsf T}r\|_2^2.
}
$$

### Proof

The new residual is

$$
r_{\mathrm{new}}
=
(I-QQ^{\mathsf T})r.
$$

Since $QQ^{\mathsf T}r$ and $r_{\mathrm{new}}$ are orthogonal, Pythagoras gives the identity.

This gain is exact. A complexity penalty may change which block is tried first, but it does not change the measured gain.

## 4. Exact integer-budget tree theorem

At a node $\nu$, every local stop model $m$ has integer cost $C_m$ and local squared error $E_m$. Let $E_\nu(B)$ denote the smallest local error achievable inside the subtree rooted at $\nu$ under budget $B$.

For children $\mu_1,\ldots,\mu_s$,

$$
\boxed{
E_\nu(B)
=
\min\left\{
\min_{\substack{m\in\mathcal M_\nu\\C_m\le B}}E_m,
\quad
\min_{B_1+\cdots+B_s\le B}
\sum_{j=1}^sE_{\mu_j}(B_j)
\right\}.
}
$$

### Proof

A complete pruning has exactly two forms. It stops at $\nu$, or it enters every child. In the split case, costs and local squared errors add because the terminal regions are disjoint. Induction from the leaves therefore enumerates every admissible pruning. Removing a dominated state is safe because adding the same sibling state preserves domination.

Thus the recursion returns the exact optimum for every integer budget in the declared finite tree, unfolding family, rank range, local error model, and scalar cost model.

A direct corollary is budget monotonicity:

$$
B_1\le B_2
\quad\Longrightarrow\quad
E^*(B_2)\le E^*(B_1).
$$

## 5. Global refit dominance

Let $W$ be the span of the inherited geometry core and all directions selected by the tree. Let $\widetilde F\in W$ be the additive tree reconstruction. Orthogonal projection gives

$$
\widehat F=P_WF.
$$

Then

$$
\boxed{
\|F-\widehat F\|_F
\le
\|F-\widetilde F\|_F.
}
$$

This follows immediately because $P_WF$ is the least-squares minimizer over $W$.

## 6. Three-seed nonregression

The final finite portfolio contains:

1. the unchanged greedy singular-packet seed
2. the unchanged Lagrange-tree seed
3. the unchanged exact-budget tree seed
4. every completed backward-replacement candidate generated from those seeds

Let the portfolio be $\mathfrak P$, and choose

$$
\widehat F_*
=
\arg\min_{G\in\mathfrak P}\|F-G\|_F.
$$

Since every unchanged seed is still in $\mathfrak P$,

$$
\boxed{
\|F-\widehat F_*\|_F
\le
\min_{G\in\mathfrak S}\|F-G\|_F,
}
$$

where $\mathfrak S$ is the set of the three seeds. This is an exact nonregression result over the finite portfolio that was actually completed.

The moving support proposals inside each replacement run remain heuristic.

## 7. Singular-gap stability

Let $M$ be one local unfolding and let $\widetilde M=M+E$. If

$$
g=\sigma_r(M)-\sigma_{r+1}(M)
$$

and

$$
2\|E\|_2<g,
$$

then the selected rank is stable under the midpoint threshold. A conservative projector bound is

$$
\boxed{
\|P_r-\widetilde P_r\|_2
\le
\frac{4\|E\|_2}{g-2\|E\|_2}.
}
$$

The proof uses the symmetric dilation

$$
\mathcal H(M)
=
\begin{pmatrix}
0&M\\
M^{\mathsf T}&0
\end{pmatrix}
$$

and a resolvent contour that separates the retained singular values from the rest.

This theorem concerns one fixed support and rank. It does not claim that the support selected from noisy data is unchanged.

## 8. Exact archive and finite raster closure

For every finite stage,

$$
R_{\mathrm{archive}}=F-\widehat F,
$$

so

$$
\boxed{F=\widehat F+R_{\mathrm{archive}}.}
$$

When $\widehat F$ is an orthogonal projection,

$$
\|F\|_F^2
=
\|\widehat F\|_F^2+
\|R_{\mathrm{archive}}\|_F^2.
$$

For a finite $H\times W\times C$ image, refining the spatial tree to singleton pixels and retaining the $C$ coordinate directions at each pixel gives the standard basis of $\mathbb R^{HWC}$. Exact finite closure is therefore always available.

Exact closure does not imply that every image has a short semantic representation.

## 9. Final four-image benchmark

Under the inherited parameter budgets, the final bounded RMSE values are

| Image | Original SPD | Exact tree | Final AM-SPD | Reduction | Selected seed |
|---|---:|---:|---:|---:|---|
| Synthetic geometry | 0.003726 | 0.004365 | **0.003155** | 15.3% | exact-budget tree |
| Synthetic text and curves | 0.003394 | 0.003958 | **0.003141** | 7.5% | exact-budget tree |
| Camera | 0.014943 | 0.006578 | **0.005064** | 66.1% | Lagrange tree |
| Astronaut | 0.033553 | 0.013374 | **0.010742** exact, **0.010691** bounded | 67.6% bounded | Lagrange tree |

The mean exact-error reduction is approximately $39.2\%$. Every final case remains within its inherited budget and improves on the approximately parameter-matched residual SVD used in the same comparison.

## 10. Ten-case structural stress suite

A second suite uses ten $32\times32$ images under one common parameter budget. It compares global SVD, a row-only rank-one tree, a row-and-column rank-one tree, and the full row/column/channel variable-rank model.

The full model matches or improves on both packet ablations in all ten cases. It beats the parameter-matched global SVD in seven. The median ratios are

$$
\operatorname{median}
\frac{\mathrm{RMSE}_{\mathrm{AM\text{-}SPD}}}
{\mathrm{RMSE}_{\mathrm{global\ SVD}}}
=0.947
$$

and

$$
\operatorname{median}
\frac{\mathrm{RMSE}_{\mathrm{AM\text{-}SPD}}}
{\mathrm{RMSE}_{\mathrm{row\ rank\ 1}}}
=0.624.
$$

Global SVD remains stronger on some globally low-rank or poorly matched geometries. That is a real model boundary, not an error in the theorem.

## 11. Noise boundary

The noise test contains four images, three noise levels, and three seeds, for thirty-six noisy scenarios. Only nine scenarios reduce RMSE relative to the noisy input. Mean denoising gain is negative.

AM-SPD is a representation method. It becomes a denoiser only when a noise model, risk criterion, or noise-calibrated penalty is added.

## 12. Comprehensive verification

The final proof-oriented suite passed

$$
\boxed{12{,}154/12{,}154}
$$

scenarios in eleven groups:

- 90 patch round trips
- 791 local SVD optimality checks
- 60 orthogonal-complement checks
- 80 exact block-gain checks
- 320 monotone global-refit checks
- 9,960 exact budget dynamic-programming comparisons
- 394 spatial partition checks
- 70 singular-gap stability checks
- 60 exact archive identities
- 300 portfolio nonregression checks
- 29 reported-result consistency checks

The largest recorded residual was below $10^{-13}$.

## 13. Final boundary

Exact within the declared finite model:

- best local rank for a fixed support and unfolding
- every integer-budget tree frontier
- global least-squares refitting on a completed span
- post-projection gain of an accepted block
- the minimum over the completed three-seed portfolio
- exact residual accounting and finite raster closure

Still heuristic or model dependent:

- which moving residual regions are proposed
- the order used to reopen weak directions
- the scalar parameter proxy
- the geometry grammar available to the search
- behavior under noise without a statistical model

AM-SPD now has a complete finite mathematical core. Its open-ended geometry search remains the part designed to evolve.
