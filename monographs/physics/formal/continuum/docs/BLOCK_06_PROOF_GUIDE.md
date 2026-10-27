# Block 06 — Exact refinement cancellation and analytic error control

Komorebi Physics Lean v0.6.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, 550 pages, physical PDF page 26, printed page 13. The literal target is Chapter 4.9, equations (4.59)–(4.67). The page image was inspected. The authoritative cumulative machine result is `verification/final/report.json`.

## 1. Scope and declaration counts

| Module | New theorems | New definitions | Content |
|---|---:|---:|---|
| `RefinementCancellation` | 25 | 4 | Actual tower, exact response multipliers, polynomial cancellation and surviving terms |
| `RefinementAsymptotics` | 17 | 0 | Genuine Big-O/little-o, one-sided estimates, convergence and failure of an extra order |
| `RefinementBounds` | 10 | 1 | Finite-radius remainder and sample-perturbation bounds |
| `RefinementExamples` | 29 | 3 | Source formulas, exact nonzero witnesses and invalid-alternative tests |
| **Block 06** | **81** | **8** | **89 new named declarations** |

The cumulative inventory is **483 theorem declarations, 579 named declarations, and 29 mathematical modules**. The previous 25 mathematical source files are byte-identical. Of the 483 theorems, 39 are recovered Paper VII declarations and 444 were authored across the six full-edition blocks. The new count comprises 52 general/support theorems and 29 example/formula/support theorems. It is not a count of independently discovered physical laws or a percentage of the full edition.

The algebraic layer allows any real vector space. The analytic layer allows any real normed space. No finite-dimensionality or completeness assumption is needed for the new statements. Complex vectors and suitable operator spaces can be used through their real normed-space structures, but no later physical discretization is automatically proved to satisfy the input expansion.

## 2. Actual recursion and literal source indexing

Write `T_m f(h)` for `RefinementCancellation.tower b f m h`, with a fixed real ratio b>1:

\[
T_0 f(h)=f(h),\qquad
T_{m+1}f(h)=\frac{b^{m+1}T_m f(h/b)-T_m f(h)}{b^{m+1}-1}.
\]

Division of vectors denotes multiplication by the reciprocal real scalar. `denominator_pos` and `denominator_ne_zero` prove that every displayed denominator is valid when b>1. This is not a convention that treats division by zero as an acceptable extrapolation.

The source's two-index array is constructed as

\[
R_j^{(m)}(h)=T_mf(h/b^j).
\]

`table_zero`, `table_base_column`, and `table_succ` prove its starting row and literal recursive rule. Taking b=2 gives equations (4.60) and (4.61). All depths and column numbers in these statements are arbitrary natural numbers, not a fixed finite collection of tested levels.

`tower_congr_nonzero` additionally proves that functions agreeing away from zero have the same tower at every nonzero sample point when b is nonzero. The value assigned to f(0) is therefore irrelevant to the punctured-domain result; it is not tacitly equated with the limiting value F.

## 3. Exact cancellation before any asymptotic argument

The coefficient is an actual recursively defined real number, not an assumed cancellation certificate. Its product formula is

\[
a_{m,r}(b)=\prod_{k=1}^{m}\frac{b^k/b^r-1}{b^k-1}.
\]

`tower_monomial` proves the exact response

\[
T_m(h\mapsto h^r v)(h)=a_{m,r}(b)h^r v.
\]

The following statements are proved separately:

\[
a_{m,0}=1,\qquad a_{m,r}=0\quad(1\le r\le m),
\qquad a_{m,r}\ne0\quad(r>m).
\]

The finite expansion in Lean is

```lean
expansion F c n h = F + ∑ k ∈ Finset.range n, h^(k+1) • c k
```

**Indexing:** `c k` multiplies degree k+1. It is c_1 at k=0 in conventional mathematical indexing. `tower_expansion` gives every transformed coefficient; `tower_expansion_exact` proves exact recovery of F for every polynomial represented this way with degree at most m.

The central bridge is the exact identity

\[
\boxed{T_m f(h)-F=T_m(f-P_m)(h),\qquad
P_m(h)=F+\sum_{r=1}^{m}c_rh^r.}
\]

This is `tower_error_identity`. The right-hand side is the actual recursively sampled remainder. No remainder estimate or asserted convergence is used to prove the identity.

`transformed_error_identity` also handles longer finite expansions: all surviving coefficients are retained rather than discarded. `tower_expansion_next` isolates the first surviving degree m+1 exactly.

## 4. What the analytic theorem assumes and proves

The manuscript's display (4.59) is written as an infinite expansion. This release does **not** infer analytic convergence from that notation. The precise input is a finite expansion of the **original approximation function**:

\[
f(h)-P_m(h)=O(h^{m+1})\quad\text{as }h\to0,\ h\ne0.
\]

From this input and b>1, `cancellation_isBigO` and `dyadic_order_improvement` prove

\[
\boxed{R_0^{(m)}(h)-F=O(h^{m+1}).}
\]

The input does not contain the extrapolated expression or its desired cancellation. Exact polynomial cancellation is supplied by the preceding independent algebraic theorem; scaling and finite linear combinations propagate the actual remainder bound.

This uses Mathlib's actual `Asymptotics.IsBigO` on the nontrivial punctured neighborhood filter `𝓝[≠] 0`. The proof establishes that h↦h/b maps that limiting domain to itself and derives the scaled power estimate. The recursive tower is a function, not a formal power series.

Further checked versions include:

- A general remainder order p in place of m+1, with Big-O or little-o hypotheses.
- Every fixed column j, not only j=0.
- The full transformed finite expansion with its surviving terms.
- Actual topological convergence `Tendsto (tower b f m) (𝓝[≠] 0) (𝓝 F)` when the proved error order p is positive.
- **Positive step sizes only:** `positive_step_order_improvement` takes a finite expansion on `𝓝[>] 0` and proves the result on the same one-sided filter. No expansion at negative h is assumed there.
- Big-O preservation on any filter invariant under sampling h↦h/b.

All tower depths and refinement ratios are **fixed** during the limit. No theorem here justifies m=m(h)→∞, a variable ratio, an infinite tower, convergence of the source's formal series, or a Taylor expansion from differentiability assumptions. Such hypotheses must be established separately for each later physical or numerical approximation.

## 5. Sharpness is an asymptotic proof, not a sampled mismatch

For every m and every b>1, `coefficient_ne_zero_above` proves that the degree m+1 monomial survives. `power_not_isBigO_higher` proves that a nonzero lower monomial cannot obey a higher-order bound near zero.

Combining them gives `tower_not_extra_order`:

\[
\boxed{T_m(h\mapsto h^{m+1})\notin O(h^{m+2})\quad(h\to0,\ h\ne0).}
\]

Thus the order m+1 is sharp for the stated class of original expansions. Extra regularity alone is not enough to erase a nonzero next coefficient; additional cancellation or a vanishing coefficient is needed. Special functions may have better order, but there is no unconditional extra-order theorem.

## 6. Quantified remainder and sample-error estimates

Big-O existence is supplemented by explicit norm bounds. Define

\[
B_{m,p}(b)=\prod_{k=1}^{m}\frac{b^{k-p}+1}{b^k-1},\qquad B_{0,p}=1.
\]

The Lean expression uses b^k/b^p instead of a possibly negative integer exponent. `amplification_product` proves the product formula, and `amplification_pos` proves positivity for b>1.

Suppose, for all 0<|h|<δ,

\[
\|f(h)-P_m(h)\|\le C|h|^p.
\]

Then `cancellation_bound` proves on that same punctured radius

\[
\boxed{\|T_mf(h)-F\|\le B_{m,p}(b)C|h|^p.}
\]

Sampling stays within the radius because b>1. `tower_bound_on` works more generally on any set closed under h↦h/b. The norm bound retains both terms at every recursive stage; it is not derived by pretending that their norms cancel.

For perturbed samples g with \(\|g(h)-f(h)\|\le\varepsilon\), `perturbation_bound` proves

\[
\|T_mg(h)-T_mf(h)\|\le B_{m,0}(b)\varepsilon.
\]

The combined result `noisy_cancellation_bound` is

\[
\boxed{\|T_mg(h)-F\|\le B_{m,p}(b)C|h|^p+B_{m,0}(b)\varepsilon.}
\]

For b=2, the noise factors at depths 1, 2 and 3 are proved to be 3, 5 and 45/7. An exact bounded noise function with norm identically 1 has first-level output 3 at h=1. Cancellation is therefore **not automatically a contraction of arbitrary sample errors**. The first-level example attains its noise bound; no all-depth optimality claim is made for the displayed general bound.

These are exact real/normed-space theorems. They do not certify a floating-point implementation, infer statistical independence of errors, or prove empirical convergence of a physical model. A nonzero sample-error floor must not be discarded from an asymptotic accuracy claim.

## 7. Literal formulas and nonzero witnesses

The following identities hold for arbitrary real-vector-space-valued f and all h. The first three are (4.65)–(4.67):

\[
T_1f(h)=2f(h/2)-f(h),
\]
\[
T_2f(h)=\frac{8f(h/4)-6f(h/2)+f(h)}3,
\]
\[
T_3f(h)=\frac{64f(h/8)-56f(h/4)+14f(h/2)-f(h)}{21}.
\]

An additional checked fourth level is

\[
T_4f(h)=\frac{1024f(h/16)-960f(h/8)+280f(h/4)-30f(h/2)+f(h)}{315}.
\]

The actual quadratic, cubic and quartic responses preserve the first surviving terms:

\[
T_1(F+ah+ch^2)=F-\tfrac12ch^2,
\quad T_2(F+ah+bh^2+ch^3)=F+\tfrac18ch^3,
\]
\[
T_3(F+ah+bh^2+ch^3+dh^4)=F-\tfrac1{64}dh^4.
\]

`first_level_second_order` also proves the genuine (4.64) asymptotic version with an original remainder O(h^3), rather than just the quadratic polynomial case. Additional exact tests include a ternary refinement ratio and a pair-valued observable.

For the concrete original approximation

\[
f(h)=7+2h+3h^2+h^3,
\]

Lean proves its original residual is exactly h^3, proves its input Big-O hypothesis, applies the general dyadic order theorem, and separately proves the exact output

\[
\boxed{T_2f(h)-7=h^3/8.}
\]

This demonstrates a nonzero instantiation of both the input and the output of the general analytic theorem. It is not merely a construction whose error vanishes identically.

## 8. Rejection tests and verification boundary

Seven new deliberately false controls reject a wrong first weight, the wrong quadratic sign, automatic extra coefficient cancellation, automatic extra asymptotic order, preservation at the singular ratio b=1, universal noise contraction, and a wrong third-level denominator. Their intended proof diagnostic is `unsolved goals`; import failures or timeouts do not count as successful rejections. The active exact theorems supply the genuine opposite facts or witnesses.

The final cumulative audit deletes local compiled outputs, recompiles 29 mathematical modules and the aggregate with one worker and warnings as errors, audits all 579 named declarations in one bounded invocation, tests all 41 negative controls, and checks the 25 previous mathematical files against `reference/block05_preservation.json`. Older preservation checks remain active. The 402-theorem Block 05 baseline was freshly reverified before extension. The unchanged negative-control bodies are run in separate namespaces in one batch, with imports hoisted and an exact source line-range map. Every control must have its own intended diagnostic; a nonzero batch exit alone is insufficient. Header/import diagnostics and timeouts fail the audit.

Lean is 4.34.0-rc2; Mathlib is pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine dependency repository revisions and clean tracked trees are checked. The existing imported dependency cache is used, not independently rebuilt wholesale. Only propext, Classical.choice and Quot.sound are permitted axiom dependencies. There are no admitted active proofs or custom axioms. The runtime and its seven parts are not bundled; checksum-verified restoration support is included.

`BLOCK_06_FAILURES.md` identifies the six failed development compilations and their repairs, plus an interrupted preliminary control batch and two intentionally superseded audit runs. Successful and failed snapshots remain separate. The completed final report, not this narrative alone, determines the cumulative pass status. A fresh-extraction check is delivered separately so its archive checksum can refer to the unchanged final ZIP.

## 9. Remaining boundary and next literal source

Chapter 4.9 is covered under the stated finite-expansion and fixed-depth assumptions. This does not prove a later field discretization has that expansion, that refinement produces the intended continuum theory, or that the model matches observations.

Earlier boundaries remain: no constructed ODE solution or initial-state positivity-preserving semigroup, zero-population/q=1 entropy extension, general-graph convergence rate, automatic closed coarse Markov model, quantum relative-entropy theorem, countable/unbounded or trace-class extension, gravitational/cosmological completion, or empirical validation. Chapter 3 still needs a separate complete inventory.

**Next: Chapter 5.1–5.3, positive-operator and overlapping atlases**, physical PDF pages 27–28. Construct positive effects summing to identity, not necessarily idempotents; derive actual probabilities and continuity, including the moving-effect source and exact coarse aggregation. Chapter 5.4 then supplies the Parseval-channel realization/dilation target. Do not import orthogonal-projector assumptions into overlapping effects.
