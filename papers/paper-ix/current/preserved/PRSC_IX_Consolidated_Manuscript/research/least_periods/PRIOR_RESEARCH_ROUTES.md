# Routes for the remaining Paper IX questions

Komorebi P. | Research checkpoint | 8 September 2026

This checkpoint contains new mathematical derivations and bounded exact computations. No new Lean theorem was compiled for these proposed extensions. The certified starting point remains PRSC_IX_Sharp_Dyadic_Continuation.zip, SHA256 c2be1ae2fbaa974e177a008c6a4919d4ab307d2df88ad36acd04608834970ef6. No novelty claim is made.

## 1. A concrete route to all four least dyadic periods

Put f_j(n)=C_(4,j)(n) and a_(j,k)=Delta_1^k f_j(0). The checked all-row theorem gives v2(a_(j,k))>=k. Exact recurrence calculations give:

| j | v2(a_(j,1)) | Required additional prefix valuations |
|---|---:|---|
|0|1|k=2: 3|
|1|1|k=2: 3|
|2|4|k=2,...,6: 6,9,13,16,22|
|3|2|k=2,...,4: 8,8,15|

Here is the proposed generic lemma, with a complete mathematical proof route. For a rational-valued sequence f let a_k=Delta_1^k f(0). Suppose v2(a_1)=c and v2(a_k)>=c+1+floor(log2(k)) for all k>=2. Then

    v2(f(n+T)-f(n)) = c+v2(T)    (n>=0, T>0).

Finite Newton expansion and Vandermonde give

    binom(n+T,k)-binom(n,k)
      = sum_(ell=1)^k binom(T,ell) binom(n,k-ell).

For a nonzero summand, ell*binom(T,ell)=T*binom(T-1,ell-1) gives valuation at least v2(T)-v2(ell), hence at least v2(T)-floor(log2(k)). Every Newton term of order k>=2 therefore has valuation at least c+v2(T)+1. The order-one term is a_1*T and has valuation exactly c+v2(T). Strict leading-term dominance proves the displayed equality. All sums are finite; terms outside support vanish.

The known bound v2(a_(j,k))>=k handles every k beyond the finite prefixes in the table: k-floor(log2(k))>=2 for k>=3, >=5 for k>=7, and >=3 for k>=5. This yields c=(1,1,4,2). For original coefficients U_j=j!*f_j, put d=(1,1,5,3). The next proposed Lean theorem is

    v2(U_j(n+T)-U_j(n)) = v2(T)+d_j,

and the least positive packet period modulo2^r is then

    P_j(r)=2^max(0,r-d_j).

This would in particular prove U_2 is constant modulo32 and U_3 modulo8. Periods here are packet shifts, not literal degree shifts. The latter multiply packet shifts by4.

There is a further mathematical consequence: (f_j-f_j(0))/2^c_j extends to an isometric bijection of Z2. Density gives the isometric extension; each finite reduction is injective and hence bijective; compatible preimages give surjectivity. This consequence is also not newly formalized.

The periods/ folder supplies the standalone recurrence computation, exact prefix fractions, full results for j0..3,n0..16,T1..16 (1088 cases), and hashes. The finite experiment is a check on the derivation, not the uniform proof. Confidence in this route is high; the remaining step is formalizing the generic dominance lemma and exact prefix values.

Exact valuations of every higher-order difference are a further question. First-difference isometry alone does not settle them; higher differences can cancel.

## 2. Affine kernel: exact families and residue-aware composition

Define Theta_(M,s)(r,k)=[z^r](1+z)^s((1+z)^M-1)^k.

New elementary coefficient-extraction formulas:

    (k+1) Theta_(2,1)(k+j,k)
      = 2^(k-j)(k+j+1) binom(k+1,j),    0<=j<=k,

    Theta_(M,s)(k+1,k)=M^k (k(M-1)+2s)/2,    M>=2,

    Theta_(M,s)(Mk+s-1,k)=Mk+s,    M>=2, Mk+s>=1.

These give credible short Lean targets, including the missing binary digit s=1. The full universal digit/carry valuation formula remains much harder.

A valuation-only composition ledger cannot be exact universally. For a>=2 let N=2^(a-1). The two nonzero paths for Theta_(2^a,1)(3,2) give

    8*N^2 + 8*N^2*(N-1) = 8*N^3 = 2^(3*a).

Both path contributions have valuation2a+1, while the sum has valuation3a. The discrepancy a-1 is unbounded.

A sound replacement tracks normalized unit residues. For m=min_i vp(t_i), the sum has valuation exactly m iff sum_i p^(-m)*t_i is nonzero modulo p. Unique minimal valuation suffices. Ties require further digits and higher-valuation paths as they enter. Fixed precision and bounded degree give a realistic certified computation target; a uniformly fixed finite-state machine is not justified by this argument.

## 3. Native13.2: polynomial obstruction and intrinsic presentation

Next formalize the polynomial Taylor congruence

    F(x+p^L*t) = F(x)+p^L*J_F(x)*t mod p^(L+1),   L>=1.

This yields the finite cokernel obstruction for any fixed finite polynomial presentation, extending the checked affine result. The existing prose proof establishes this precisely. For presentation independence one must incorporate relations between equations; the raw Jacobian cokernel changes under addition of a redundant zero equation. The intrinsic finitely presented algebra obstruction is a verified classical result (Stacks tag08S5 and the cotangent-complex presentation comparison in the prior notes).

A full general seed-system result still requires a declared category and a faithful encoding preserving the intended lifts. There is no convincing unrestricted route without specifying these hypotheses.

One-step success does not ensure indefinite lifting. A useful next theorem is: a fixed root has a compatible p-adic lift iff it has descendants at every finite precision, because the finite solution sets form a nonempty inverse system. A surjective Jacobian is a sufficient condition ensuring every correction exists. Singular systems require tracking the whole obstruction tree.

## 4. Native13.3: a precise common-correction spine

For finite F_p-spaces and J:U->V, K:U->W, set

    A=imJ, B=imK, C=U/(kerJ+kerK).

The labels f(Ju)=[u], g(Ku)=[u] are well-defined, and

    im(J,K) is isomorphic to A x_C B.

For the converse, if Ju=a and Kv=b and [u]=[v], write u-v=j+k with j in kerJ and k in kerK. Then w=u-j=v+k is a common solution. This is an exact, nontrivial finite shared-correction theorem and a high-confidence next Lean target.

For two polynomial equation blocks F,G, fixing a root modulo p fixes both Jacobians at every higher level. The space C is therefore persistent along the lifting tower, while the residual labels vary. This connects finite obstruction and finite gluing within one precisely defined family.

Finite level identities can then pass to compatible profinite systems. This does not recover arbitrary global integers from unrelated local branches. The existing dense-diagonal/Hausdorff counterexample blocks that interpretation. Independent prime factors also do not automatically provide a nontrivial spine: their finite residues already glue by CRT. A nontrivial spine must encode actual shared constraints.

## Priority

First formalize the Mahler dominance lemma and the four exact least-period formulas. Next formalize the shared-correction quotient and polynomial obstruction. In parallel, add exact affine-kernel edge families and residue-sensitive composition. A compact universal formula for all kernel valuations and unrestricted global arithmetic reconstruction currently have no convincing complete route.

## Primary references checked for this brainstorm

- Stacks Project, Lemma91.2.1, tag08S5: https://stacks.math.columbia.edu/tag/08S5 . Canonical obstruction to lifting ring maps under square-zero extensions; applications here retain the declared finite-presentation hypotheses.
- Stacks Project, Lemma4.21.7, tag086J: https://stacks.math.columbia.edu/tag/086J . Inverse limits of finite nonempty sets are nonempty. This supplies the compactness step, not existence at every finite level.

Sources and hypotheses were checked on8September2026. These references support standard machinery, not novelty of the proposed specializations.
