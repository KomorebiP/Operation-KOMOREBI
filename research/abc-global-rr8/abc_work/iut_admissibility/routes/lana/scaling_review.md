# Independent local scaling and hull calculation

Verdict: **proved as written**, for the local claim with the explicit hypotheses below. Applying it to the IUT admissible-output family is conditional on identifying that family and its normalization. This note neither establishes nor refutes IUT compatibility.

Review provenance: independent derivation by `/root/iut_responses/lana_scaling_review`, 2026-10-25, from the claim supplied in delegation. Base checkpoint RR5 has archive SHA-256 `79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01`. No full IUT or LANA proof is audited here, and no computation or Lean check is used.

## Exact local claim

Let \(F\) be a nonarchimedean local field, \(\pi\) a uniformizer, and \(r\) the cardinality of its residue field. Write \(|\pi|_F=r^{-1}\). Let \(V\) be a finite-dimensional unital \(F\)-algebra of dimension \(d\geq1\), and let \(\mathcal O\subset V\) be a unital order containing the scalar ring \(\mathcal O_F\). Let \(\mu\) be an additive Haar measure on \(V\). Define the algebraic module hull

\[
H(U)=\mathcal O U
=\left\{\sum_{i=1}^m a_i u_i:
m\geq0,\ a_i\in\mathcal O,\ u_i\in U\right\}.
\]

Let \(L:V\to V\) be an invertible \(F\)-linear map, \(S\subset V\) measurable, and \(R=L(S)\). Assume \(R\) and \(H(R)\) are measurable with finite, strictly positive measure. Let \(t\in F^\times\) act by scalar multiplication. The source does not need to assert that \(tS\) is an admissible IUT region for this local statement.

Then

\[
H(tU)=tH(U),\qquad L(tS)=tR,
\]

and, setting \(h(U)=\log\mu(U)\),

\[
\begin{aligned}
h(L(tS))&=h(R)+\sigma(t),\\
h(H(L(tS)))&=h(H(R))+\sigma(t),\\
\sigma(t)&=d\log|t|_F.
\end{aligned}
\]

Consequently the hull overhead

\[
\delta(R)=h(H(R))-h(R)\geq0
\]

is invariant under scalar rescaling.

The assumptions about positive finite measures matter. For a singular \(L\), a null set, or an unbounded hull of infinite measure, these displayed logarithmic identities are not statements about finite real numbers.

## Proof

Centrality of \(t\) gives
\(\sum_i a_i(tu_i)=t\sum_i a_i u_i\), proving both inclusions in \(H(tU)=tH(U)\). Since \(L\) is \(F\)-linear, it commutes with scalar multiplication. Multiplication by \(t\) has additive Haar modulus \(|t|_F^d\). This modulus can be computed on an \(\mathcal O_F\)-lattice: multiplication by a unit preserves the lattice, and \([I:\pi I]=r^d\). It therefore scales Haar measure on measurable sets by the same factor. Apply this to \(R\) and \(H(R)\), and subtract the two log-volume formulas. Finally, \(R\subset H(R)\), so monotonicity gives \(\delta(R)\geq0\).

## What is required to match a prescribed pilot

Let \(h_0=h(R)\), and let \(h_*\) be a desired target log-volume. Matching by a scalar requires

\[
\sigma(t)=h_*-h_0.
\]

For \(t=\pi^k u\), with \(k\in\mathbb Z\) and \(u\in\mathcal O_F^\times\), this is equivalent to

\[
k=\frac{h_0-h_*}{d\log r}\in\mathbb Z.
\]

Thus a fixed local scalar action supplies a discrete set of degree shifts, rather than an arbitrary real shift. Restricting to powers of a fixed \(q\in F^\times\) supplies the subgroup \(d\log|q|_F\,\mathbb Z\), which may be smaller. Adjoining roots of scalars changes the field and lattice contract and is not covered by treating \(t\) as an allowed scalar in this fixed setup.

Units have \(\sigma(t)=0\), so they cannot alter the pilot's log-volume or its hull log-volume. They may alter the underlying set if it is not unit-stable.

Now impose a bound \(h(H(L(tS)))\leq b\). After matching the pilot exactly, this bound becomes

\[
\boxed{h_*+\delta(R)\leq b.}
\]

This is an invariant obstruction to obtaining the desired bound merely by tuning a scalar: the overhead cannot be removed by rescaling. The scalar equality by itself supplies no proof of the boxed inequality.

## The containing log-shell restricts expansion

Let \(I\subset V\) be a full \(\mathcal O_F\)-lattice, and suppose \(S\) is bounded and contains a nonzero point. Define

\[
m_I(S)=\max\{m\in\mathbb Z:S\subseteq\pi^m I\}.
\]

The maximum is finite and exists: boundedness makes the set of admissible integers nonempty, a fixed nonzero point bounds it above, and membership is downward closed. Then

\[
tS\subseteq I\quad\Longleftrightarrow\quad
v_F(t)+m_I(S)\geq0.
\]

Indeed, units preserve \(I\), so \(tS\subseteq I\) is equivalent to \(S\subseteq\pi^{-v_F(t)}I\). For a scalar that matches the pilot, both this inequality and the required discreteness condition must hold. Any additional global, compact-structure, reconstruction, or orbit constraints may further restrict the scalar.

A one-dimensional example shows that allowing arbitrary measurable subsets of a containing lattice would still not allow arbitrary pilot values. Take \(V=F\), \(I=\mathcal O_F\), \(L=\pi^e\), \(S=I\), \(e>1\), and \(\mu(I)=1\). Then \(h_0=-e\log r\). Reaching \(h_*=-\log r\) requires \(t=\pi^{1-e}u\), which expands \(I\) outside itself. More generally, every measurable \(S'\subseteq I\) satisfies \(\mu(L(S'))\leq r^{-e}<r^{-1}\). This example concerns this explicit local model, not the full IUT construction.

## Pointed real lines and normalization

For fixed real lines \(C,D\), a fixed nonzero pilot \(p\in C\), and linear maps \(f,g:C\to D\), one has \(f=g\) if and only if \(f(p)=g(p)\). Indeed, every element of \(C\) is a real multiple of \(p\). Therefore equality of pilot degrees suffices to identify the two linear maps **provided** the same underlying target line and degree normalization have already been constructed, and its degree coordinate is injective. A nonzero source pilot cannot map to zero under an isomorphism, and orientation imposes the corresponding sign condition.

**Conditional eta-map scaling corollary.** Fix a common underlying target line \(D\) with an \(\mathbb R\)-linear degree coordinate \(\deg:D\xrightarrow{\sim}\mathbb R\). Suppose the underlying linear maps \(\eta_S,\eta_{tS}:C\to D\) are legitimately constructed, and their values at the same fixed nonzero source pilot \(p\) satisfy

\[
\deg(\eta_S(p))=h_0=\log\mu(LS)\ne0,
\qquad
\deg(\eta_{tS}(p))=h_0+\sigma(t)\ne0.
\]

Then

\[
\boxed{\eta_{tS}
=\frac{h_0+\sigma(t)}{h_0}\,\eta_S.}
\]

Indeed, the right-hand side and \(\eta_{tS}\) have identical degree at \(p\), hence identical value there by injectivity of \(\deg\), so the preceding one-dimensional linearity argument applies. The two maps have the same orientation behavior precisely when the displayed ratio is positive. In particular, if \(\eta_S\) is orientation preserving, then \(\eta_{tS}\) is orientation preserving if and only if that ratio is positive. This is a statement about underlying linear maps after fixing a common coordinate; it neither asserts that \(tS\) is admissible nor constructs that coordinate from the source's abbreviated region quotient.

A quotient of all measurable sets by equal volume is not, from that description alone, a defined real vector space: zero and infinite volumes and vector operations need treatment. This note uses a finite log-volume coordinate only under the stated positivity and finiteness conditions. It does not supply the missing definitions for a source's shorthand \(\mathbb R^{\mathrm{ss}}\).

Multiplying a Haar measure by a normalization constant changes log-volumes by an additive constant; it does not change the scalar modulus \(|t|_F^d\). If a procession-normalized log-volume instead uses a positive weight \(w\) on a local log measure, replace \(\sigma(t)\) by \(wd\log|t|_F\). Weighted sums of blocks require the corresponding sum of moduli. These weights must be established from the actual construction rather than inferred from a change in the normalization constant.

## Global caveat and dependency check

With compatible adelic normalizations in a constant-rank situation, a single principal global scalar has total log modulus zero by the product formula. It then cannot tune a global pilot degree. Independently choosing local scalars can change volume, but their admissibility and the contributions at all other places must be checked. Varying ranks or procession weights require verification of the exact global formula; cancellation is not asserted automatically in that setting.

| Obligation | Status |
| --- | --- |
| Hull commutes with central scalar multiplication | Passed, algebraic proof above |
| Local log-volume and hull overhead formulas | Passed under the finite-measure hypotheses |
| Expansion and discrete-degree restrictions | Passed in the fixed local-field/lattice contract |
| Equality of pointed linear maps from pilot equality | Passed once a common linear target is supplied |
| These scalar operations belong to the actual IUT admissible family | Not addressed by this lemma |
| Exact procession normalization and global principal-scalar cancellation in IUT | Conditional on the actual weights and place data |

The smallest remaining source-dependent implication is that an allowed construction produces a region meeting the native pilot comparison **and** the quantitative hull cap, with a common justified target and normalization. The identities here show what a scalar modification would have to satisfy; they provide no permission to enlarge the admissible family.
