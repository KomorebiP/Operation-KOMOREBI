# Strengthening directions

Komorebi P. | Brainstorming checkpoint, 8 September 2026

No new Lean proof was run for these proposed upgrades. Their statuses are distinguished below.

## 1. Recover precision already supported by the proof

On the divisor branch m | p-1, the checked `divisor_period` theorem assumes r <= m*n. Thus n >= ceil(r/m) is already a proved sufficient threshold. Presenting only n >= r hides this improvement.

For the exceptional N=4 branch put E_j(n)=j! C_(4,j)(n). The checked normalized difference bound is min(k,n). Multiplying by j! gives

    v_2(Delta_u^k E_j(n)) >= v_2(j!) + min(k,n).

For j=2,3 the factorial contributes one full extra power of two, which the current unnormalized theorem discards. For r>=2, the packet shift 2^(r-2) therefore works modulo 2^r whenever n>=r-1. This halves the established sufficient period. At r=1 these two sequences are zero modulo two at every row. These are derived corollaries requiring new Lean declarations, not yet new checked theorems. They do not assert least periods. The same gain cannot simply be applied to odd singular addresses because their normalized bound has a factorial loss.

## 2. Track divisibility of the difference step

Suppose at a fixed row the established bound is

    v_p(Delta_h^ell f(n)) >= min(ell,M)  for every ell.

Then elementary finite difference algebra gives

    v_p(Delta_(p^s h)^k f(n)) >= min((s+1)k,M).

Here M=m*n on the divisor branch and M=n for the dyadic normalized branch. Interpret zero differences as satisfying every precision.

Proof sketch: set x=Delta_h and H=p^s. Expand ((1+x)^H-1)^k. For 1<=j<=H, the coefficient binomial(H,j) has valuation s-v_p(j), at least max(0,s+1-j). Consequently the coefficient of x^ell in the k-th power is divisible by p^max(0,(s+1)k-ell). Combining this with p^min(ell,M) divisibility of Delta_h^ell f(n) gives p^min((s+1)k,M) term by term. This is a derived mathematical corollary; the finite operator expansion still needs to be implemented in Lean.

This improves the higher-difference theorem rather than asserting a sharper earliest starting row.

## 3. Try to remove the dyadic starting threshold

Candidate target for j=0,1,2,3:

    E_j(n+2^(r-1)) = E_j(n) mod 2^r  for every n>=0 and r>=1.

The j=0 case already occurs in Nishibuchi's Proposition 3.10. The nonzero addresses are the research targets here. The exploratory exact check found no failures for all four addresses, r=1,...,6 and n=0,...,12 (312 cases). That is finite evidence, not a proof. `early_row_check.json`, the reproducible script and computation manifest retain the range.

The existing extraction argument only accesses nonnegative degrees when k<=n. A new argument must control the boundary rows directly, rather than deleting the n>=r hypothesis. A recurrence or special kernel identity that propagates the relevant divisibility through those rows is a plausible route.

Removing the threshold uniformly across all allowed primes is false: p=3,m=2,j=0,r=1,n=0 gives E_6^(6,0)-E_0^(6,0)=-2, not divisible by three.

Reference for the existing j=0 result: Yuta Nishibuchi, arXiv:2605.10677v2, Proposition 3.10, https://arxiv.org/pdf/2605.10677 .

## 4. Turn the dyadic proof into a family theorem

Consider rational kernels

    g(n)=product_i (b_i/(b_i+2*a_i*n))^e_i,

with integer a_i,b_i, odd b_i and nonnegative integer e_i. Then g(0)=1 and every denominator is a 2-adic unit. Form

    G(t)=sum_(n>=0) g(n)*t^(4n)/(4n)!,
    e(n)=(4n)!*[t^(4n)] G(t)^(-1).

The existing affine Kummer-sequence estimates and product/inverse closure suggest extracting one general theorem giving integrality and v_2(Delta_u^k e(n))>=min(k,n). This would include an explicit parameterized collection of kernels, beyond four addressed examples. The route reuses existing proofs, but the general theorem and instances have not been compiled in Lean. No novelty search has been performed.

## 5. Join the two native partial results through shared corrections

Let U,V,W be finite modules and J:U->V, K:U->W be linear maps. Put A=im J, B=im K and

    C=U/(ker J+ker K).

Define labels f(Ju)=[u] and g(Ku)=[u]. These are well-defined. For a in A, b in B,

    there exists u with Ju=a and Ku=b  iff  f(a)=g(b).

To prove the backward direction, choose representatives u,v. Label equality says u-v=j+k with j in ker J and k in ker K. The common correction w=u-j=v+k then satisfies Jw=Ju and Kw=Kv. The forward direction is immediate. Thus A x_C B is isomorphic to im(J,K). This is also the vanishing condition for [(a,b)] in (V direct_sum W)/im(J,K).

Over F_p, the spine has p^(rank J+rank K-rank(J,K)) elements, and a compatible pair has p^(dim U-rank(J,K)) simultaneous corrections. These are elementary algebraic deductions, not yet Lean-checked additions.

This provides an explicit connection between the finite lifting obstruction and the finite gluing criterion. Apply it to two blocks of equations sharing a correction vector. The original unrestricted native conjectures remain unresolved. Independent prime factors glue freely by CRT, so a nontrivial shared spine requires shared constraints; it is not supplied merely by having different primes.

## Recommended order

First formalize the factorial gain and dependence on step divisibility. Then investigate the early-row dyadic target. In parallel, the shared-correction quotient is the cleanest next precise theorem for the native conjectures. General kernel transfer is the broader family-level extension.
