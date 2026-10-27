# Paper IX: final all-residue amendments

**Komorebi P. — v0.10.0**

## 1. Theorem 7.5 is now covered for every allowed residue

For prime `p`, positive `m | p-1`, `N=m*p`, `h=(p-1)/m`, every `j<N`, and all natural `n,k,u`, the actual rational family `E(n)=j! C_(N,j)(n)` is p-integral and has precision at least `min(k,m*n)` after k differences of step `u*h`. The normalized family has precision at least `min(k,m*n)-v_p(j!)`. Precision means zero OR the corresponding rational valuation inequality. In particular, zero is not assigned a finite valuation as the interpretation of unlimited precision.

A separately constructed Z_p lift equals the original rational coefficient after embedding in Q_p and has genuine ideal divisibility by `p^min(k,m*n)`. Both rational and integral statements are proved, not just a congruence in a field.

The final declaration is `KomorebiPaperIX.Theorem75.global_finite_difference`; it requires no flatness, weighted-series or convergence hypothesis. The manuscript's primality requirement is explicit in the Lean type, even where its prose says only that p is odd. Zero order, zero row, zero step and the `p=2,m=1` specialization are included. No additional external dyadic conjecture is asserted.

## 2. New proof route after the singular Amice estimate

The saved v0.9.0 proof that the actual singular ratios have weighted logarithmic coefficients is used unchanged. The normalized operator `(Theta^(p^2)-Theta^p)/p`, with `Theta=(1+T)d/dT`, is proved to preserve the entire weighted ring. Its finite coefficient dependence permits exact truncation arguments, rather than an unproved analytic limit. The actual substitution `T=exp(t)-1` intertwines this operator with the Hurwitz differential defect and transfers the estimate to all higher differences. This is an alternative to separately formalizing the supporting manuscript's dual Mahler polynomial argument. That prose argument is not imported as an axiom.

For nonsingular c, the equation `(tD+c)y=cq+yq-y^2` is derived from the original sections and ratios. The scalar pivots are proved to be p-adic units only when p does not divide c on the p-supported degrees. Constructed Picard iterates agree with the actual solution on successively longer finite coefficient prefixes. Every iterate is flat; finite differential dependence then proves flatness of the actual ratio. The singular pivots are never declared units.

Finally, the actual source/reciprocal identities prove `F_(N,j+1)=F_(N,j) R_(j+1)` and identify `(Nn)! [t^(Nn)] F_(N,j)` with the original `j! C_(N,j)(n)`. The previously checked saturation and step-multiple lemmas now have their actual-family premises discharged.

## 3. Normalization remains sharp

The existing no-loss counterexample is unchanged: `v_3(C_(6,3)(2)-C_(6,3)(1))=0`. Completion of the corrected theorem does not make the discarded unrestricted normalized bound true.

A new exact singular example is

```
Delta_1^2 (3! C_(6,3))(1) = -1464768/8645,
v_3(-1464768/8645) = 2 = min(2,2*1).
```

The third coefficient `C_(6,3)(3)=-223199/7980` and this difference are derived from the general triangular recurrence. A regular address after the singular boundary, j=4, is also checked from the actual recurrence. Negative controls demand false extra precision, discard normalization, use a composite Frobenius base, and center a ratio at the wrong constant.

## 4. Scope and preservation

The named manuscript-proved register is 24/24. It excludes the three classical input environments, two unproved conjectures, unnumbered calculations and historical numerical certificates. No independent novelty or priority claim is made. All 57 v0.9.0 proof modules and the original manuscript are byte-identical. Earlier supplements and amendments remain valid within their historical scopes; their old counts are not current counts.

The pinned Mathlib compiled cache is reused, not rebuilt. No earlier paper or historical experiment suite is rerun. A successful formal proof establishes the precise Lean proposition under its recorded definitions and hypotheses. Review of the mathematical correspondence to prose remains a separate obligation.
