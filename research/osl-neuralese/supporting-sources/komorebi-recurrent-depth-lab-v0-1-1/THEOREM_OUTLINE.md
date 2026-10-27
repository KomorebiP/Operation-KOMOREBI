# Komorebi Recurrent-Depth Theorem Outline

Version 0.1.1

## Purpose

This document states the mathematical bridge between recurrent-depth latent computation and Komorebi packet transport. It separates three levels of statement:

1. exact finite-dimensional algebraic identities
2. conditional theorems whose hypotheses must be verified
3. empirical hypotheses to be tested on recurrent-model trajectories

The motivating model is the prelude, recurrent core, and coda architecture in Geiping et al., [*Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach*](https://arxiv.org/html/2502.05171v2). Its architecture is defined in [Section 3](https://arxiv.org/html/2502.05171v2#S3), its adaptive-compute and cache mechanisms appear in [Section 6](https://arxiv.org/html/2502.05171v2#S6), and its qualitative latent-trajectory observations appear in [Section 7](https://arxiv.org/html/2502.05171v2#S7).

## 1. Recurrent dynamical system

For a fixed token sequence \(x\), define

\[
e=P(x), \qquad T_e(s)=R(e,s), \qquad s_{i+1}=T_e(s_i),
\]

where \(P\) is the prelude and \(R\) is the shared recurrent block. Let

\[
z_i=g(s_i), \qquad p_i=\operatorname{softmax}(z_i)
\]

denote coda logits and probabilities.

For a prompt-independent system, retain the embedded prompt as a frozen state coordinate:

\[
\widehat T(e,s)=(e,T_e(s)).
\]

### Augmented-state requirement for generation and cyclic caches

The autonomous map \(T_e\) is valid only when everything used by the next recurrent step is fixed or included in the state. With warm starts, mutable KV caches, or the paper's cyclic read/write rule \(i\bmod k\), define an augmented state such as

\[
X_i=(e,s_i,M_i,\rho_i), \qquad \rho_i=i\bmod k,
\]

and an autonomous update

\[
X_{i+1}=\mathcal T(X_i).
\]

Here \(M_i\) contains every cache value that can affect later computation. Omitting \(M_i\) or \(\rho_i\) makes the observed \(s_i\) process nonautonomous. A Koopman or tangent analysis that ignores these variables is then a reduced model with memory, not an exact analysis of the implemented recurrence.

The phase indicators \(1_{\{\rho=a\}}\), \(a\in\mathbb Z/k\mathbb Z\), define exact residue packets on the augmented system. Their nonzero transfer pattern is cyclic, with orientation determined by whether state transport or the pullback Koopman convention is used.

## 2. Exact packet path identity

Let \(\mathcal H\) be a Banach or Hilbert space of observables on which the Koopman operator

\[
U_e f=f\circ T_e
\]

is bounded. Let \(\{\pi_a\}_{a\in\mathcal A}\) be idempotents satisfying

\[
\pi_a\pi_b=\delta_{ab}\pi_a,
\qquad
\sum_{a\in\mathcal A}\pi_a=I.
\]

Define the one-step transfer block

\[
U_{ba}=\pi_bU_e\pi_a.
\]

### Theorem 2.1: exact recurrent packet expansion

For every integer \(r\ge 1\),

\[
\pi_bU_e^r\pi_a
=
\sum_{a_1,\ldots,a_{r-1}}
U_{b a_{r-1}}\cdots U_{a_2a_1}U_{a_1a}.
\]

The proof is the repeated insertion of \(I=\sum_a\pi_a\) between consecutive Koopman factors. Orthogonality is not required for the identity. It is required for Pythagorean energy interpretations.

An edge \(a\to b\) is exact only when \(U_{ba}\ne0\), or when a proposed grammar is proved to contain every nonzero block. If small blocks are thresholded, the omitted block operator must be reported as a separate grammar residual.

For any coda coordinate \(g_j\in\mathcal H\),

\[
g_j(T_e^r(s_0))=(U_e^rg_j)(s_0).
\]

Thus Theorem 2.1 gives an exact observable-path expansion whenever the packet system resolves the full observable space under study.

## 3. Finite Koopman lift and leakage

Let \(Q\) be an orthogonal projection onto a finite observable space \(V\). Define

\[
A=QU_eQ, \qquad
L=(I-Q)U_eQ, \qquad
B=QU_e(I-Q), \qquad
D=(I-Q)U_e(I-Q).
\]

The operator \(A\) is a finite compression. It is generally not itself a Koopman operator: it need not preserve products, constants, or positivity. Its packet expansion is exact for \(A^r\), but it equals the true projected evolution only under an invariance condition.

### Theorem 3.1: exact leakage identity

For \(f\in V\) and \(r\ge1\),

\[
U_e^rf-A^rf
=
\sum_{j=0}^{r-1}U_e^{r-1-j}LA^jf.
\]

Projecting the result back into \(V\) gives

\[
QU_e^rQ-A^r
=
\sum_{j=0}^{r-2}QU_e^{r-1-j}LA^j,
\]

where the sum is empty for \(r=1\). Exact equality \(QU_e^rQ=A^r\) for all \(r\) follows if \(U_e(V)\subseteq V\), equivalently \(L=0\).

Leakage may later return through \(B\). If

\[
K_n=QU_e^nQ\vert_V,
\]

then the exact memory recurrence is

\[
K_{n+1}
=
AK_n+
\sum_{j=0}^{n-1}BD^{n-1-j}LK_j.
\]

For example,

\[
K_2=A^2+BL,
\]

\[
K_3=A^3+ABL+BLA+BDL.
\]

This formula identifies exterior excursions and their returns rather than treating all discarded behavior as unstructured error.

### Corollary 3.2: norm bound

If \(\|U_e\|\le M\), \(\|A\|\le a\), and \(\|L\|\le\varepsilon\), then

\[
\|U_e^rf-A^rf\|
\le
\varepsilon\|f\|
\sum_{j=0}^{r-1}M^{r-1-j}a^j.
\]

If \(M,a\le1\), this reduces to \(r\varepsilon\|f\|\).

A fitted EDMD or DMD residual is a sampled trajectory residual. It is not automatically a bound on \(\|L\|\). Closure leakage, block-thresholding error, and finite-sample estimation error must be reported separately.

## 4. Exact tangent-cocycle expansion

Assume \(T_e\) is differentiable along the trajectory and set

\[
J_i=DT_e(s_i).
\]

The chain rule gives

\[
D(T_e^r)(s_0)=J_{r-1}\cdots J_0.
\]

Let \(\{\rho_a^{(i)}\}\) resolve the identity on the tangent space at \(s_i\). Then

\[
\rho_b^{(r)}D(T_e^r)(s_0)\rho_a^{(0)}
=
\sum_{a_1,\ldots,a_{r-1}}
\rho_b^{(r)}J_{r-1}\rho_{a_{r-1}}^{(r-1)}
\cdots
\rho_{a_1}^{(1)}J_0\rho_a^{(0)}.
\]

This is an exact first-order sensitivity decomposition. For a small intervention \(\delta s_0\),

\[
g(T_e^r(s_0+\delta s_0))-g(T_e^r(s_0))
=
Dg(s_r)D(T_e^r)(s_0)\delta s_0
+O(\|\delta s_0\|^2).
\]

The tangent path prediction is causally testable by shrinking intervention magnitude and checking convergence to the predicted derivative.

### Dynamical classifications

- A fixed point requires \(T_e(s^*)=s^*\). Local attraction requires a contraction argument or suitable local stability hypotheses.
- A period-\(q\) orbit requires \(T_e^q(s^*)=s^*\) in the original latent space and failure of this identity for every smaller candidate period. Stability is governed by the Floquet multipliers of \(J_{q-1}\cdots J_0\).
- Complex eigenvalues of an individual \(J_i\), or loops in a PCA chart, do not prove a periodic orbit.
- A slider may arise from affine translation. In homogeneous coordinates, \(u_{i+1}=u_i+c\) produces unit-eigenvalue Jordan behavior. A Jordan chain is sufficient for polynomial drift in a constant linear system, but affine forcing can create drift without a nontrivial Jordan block in the unaugmented linear part.
- For nonnormal and time-varying dynamics, singular values, cocycle products, and finite-time Lyapunov exponents are more reliable than isolated Jacobian eigenvalues.

## 5. Conditional adaptive-stopping certificate

Assume \(T_e\) maps a complete invariant region \(\Omega\) into itself and is a \(\kappa\)-contraction there:

\[
\|T_e(s)-T_e(t)\|\le\kappa\|s-t\|,
\qquad 0\le\kappa<1.
\]

Let \(s^*\) be its fixed point and let \(d_r=\|s_r-s_{r-1}\|\).

### Theorem 5.1: state and output tail bounds

\[
\|s_r-s^*\|
\le
\frac{\kappa}{1-\kappa}d_r
=
\frac{1}{1-\kappa}\|s_{r+1}-s_r\|.
\]

If the logit coda \(g\) is \(L_g\)-Lipschitz into \(\ell_\infty\), then

\[
\|z_r-z^*\|_\infty
\le
\varepsilon_r
:=
L_g\frac{\kappa}{1-\kappa}d_r.
\]

For \(p_r=\operatorname{softmax}(z_r)\) and \(p^*=\operatorname{softmax}(z^*)\), Hoeffding's lemma gives

\[
\operatorname{KL}(p_r\|p^*),
\operatorname{KL}(p^*\|p_r)
\le
\frac{\varepsilon_r^2}{2}.
\]

If the current top-logit margin exceeds \(2\varepsilon_r\), the limiting argmax is certified to be the same token.

A rigorous use of this theorem requires a proved bound

\[
\sup_{s\in\Omega}\|DT_e(s)\|\le\kappa<1
\]

on a trapping region. Sampled Jacobian norms and visual convergence are empirical evidence, not a certificate. For a period-\(q\) attractor, the theorem may be applied to \(T_e^q\) and the residual \(\|s_r-s_{r-q}\|\). It does not apply directly to slider or drift regimes.

The paper's successive-output KL threshold is therefore a heuristic. Small successive KL does not bound hidden-state motion because the coda is noninjective, softmax ignores common logit shifts, and KL has no triangle inequality.

## 6. Refinement criterion

Recurrence index is path length. It becomes a Komorebi multiscale or refinement coordinate only if nested packet systems are supplied and verified. A sufficient algebraic condition is

\[
\pi_a^{(\ell)}
=
\sum_{b\in\operatorname{child}(a)}\pi_b^{(\ell+1)}.
\]

Then a coarse transfer block must equal the sum of its fine blocks:

\[
\pi_c^{(\ell)}U_e\pi_a^{(\ell)}
=
\sum_{d\in\operatorname{child}(c)}
\sum_{b\in\operatorname{child}(a)}
\pi_d^{(\ell+1)}U_e\pi_b^{(\ell+1)}.
\]

If different feature spaces are learned at different levels, explicit coarsening maps and an intertwining relation must replace this common-space identity.

## 7. Experimental gates

The bridge is empirically supported only if it passes all applicable gates on held-out prompts and initializations.

1. **Full-space dynamics:** Verify fixed-point residuals, original-space period returns, drift linearity, and attraction across seeds. PCA is used only as a chart.
2. **Finite closure:** Fit a feature map \(\psi\) and operator \(A\) on discovery data. Report held-out one-step and multistep normalized errors and compare them with time-shuffled, random-feature, and rank-matched baselines.
3. **Packet algebra:** Report idempotence, annihilation, completeness, conditioning, block sparsity, and stability across prompts, seeds, checkpoints, and feature ranks.
4. **Path reconstruction:** Verify that the complete block sum reconstructs \(A^r\). Keep closure leakage, grammar-thresholding error, and estimation error separate.
5. **Causal transport:** Inject small tangent-packet perturbations at selected depths. Compare observed logit changes with cocycle path predictions over a sequence of shrinking perturbation sizes.
6. **Refinement:** Verify child-sum projector identities and aggregated block identities before using multiscale terminology.
7. **Stopping:** Apply certified stopping only where a trapping region and contraction bound have been established. Report fixed-point, periodic, and drift cases separately.

## 8. What would constitute a substantive Komorebi result

The identities above organize recurrent computation, but they do not by themselves establish a new model mechanism. A substantive result would be a compact packet system that is simultaneously:

- low leakage on held-out trajectories
- stable across prompts and random initializations
- causally predictive under intervention
- compatible across verified refinement levels
- useful for certified stopping, compression, interpretability, or performance

Anything weaker should be reported as a structural analogy or exploratory diagnostic.
