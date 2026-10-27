# Block 14 — Domain-correct resolvent commutators and nonreducing packets

Komorebi Physics Lean v0.14.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF page 34 of 550, printed page 21, Section 6.7, equations (6.53)–(6.56). The source page image was inspected. The original source PDF is unchanged. A completed `verification/final/report.json`, not this guide or an inventory alone, determines cumulative verification status.

## 1. Inventory and scope

| New module | Theorems | Other inventoried declarations | Role |
|---|---:|---:|---|
| ResolventDomain | 13 | 5 | Actual shifted partial map, true inverse certificate, domain lifts and bounded commutator extension |
| ResolventCommutator | 14 | 1 | Exact negative-sign identity, operator/state bounds and reduction equivalence |
| ResolventBounds | 6 | 0 | Derived imaginary-part coercivity and nonreal/imaginary-axis estimates |
| ResolventParameters | 6 | 0 | Two-parameter identity, commuting resolvents and quantitative comparison |
| DiagonalResolvents | 13 | 5 | Constructed nonreal resolvent for every real diagonal sequence on its maximal domain |
| NonreducingPacket | 14 | 4 | Actual orthogonal packet, explicit finite-rank extension and exact norm |
| ResolventExamples | 21 | 3 | Harmonic realization, nonzero exact norms and hypothesis-sensitive tests |
| **Block 14** | **87** | **18** | **105 new inventoried declarations** |

The cumulative inventory has **1,260 theorem declarations, 1,502 inventoried names, 78 mathematical modules and 101 negative controls**. The 71 mathematical files from Block 13 are byte-identical. There are 39 recovered Paper VII theorem declarations and 1,221 full-edition declarations. Counts include support lemmas, constructors and exact examples, not independent physical discoveries or a completion percentage for the full edition.

The general identities use an arbitrary complex inner-product space and an actually partially defined linear operator. Completeness, finite-dimensionality, self-adjointness, orthogonality and idempotence of the packet are not imposed when they are unnecessary. The constructive spectral realization uses the complete, infinite-dimensional space l2(N,C). No differential-oscillator identification is asserted.

## 2. An inverse symbol is not an inverse proof

For a partially defined linear map T with domain D(T), define the actual shifted linear map

    shifted T z : D(T) -> H
    shifted T z x = T x - z x.

The structure `ResolventDomain.Certificate T z` contains a bounded operator R, proof that R maps H into D(T), and both genuine inverse identities:

    (T-z) R x = x                 for every x in H,
    R (T-z) y = y                 for every y in D(T).

It does not contain a commutator or norm conclusion. The proof-bearing `Certificate.lift` constructs a domain-valued linear map from the range proof. Every later application of T uses a domain member, not an ambient vector with an omitted domain obligation.

The new proofs show that the range of R equals D(T), that the shifted map is bijective, that R is injective, and that any second such bounded inverse agrees with R. These are consequences of the two identities, not an existence theorem for arbitrary T or z.

For a bounded packet P, `BoundedCommutator T P` separately records domain preservation, a bounded operator B, and the exact agreement

    T(P y) - P(T y) = B y          for every y in D(T).

The restricted P is constructed on D(T). This interface does not pretend that T is bounded or that the expression TP is defined on all of H. The finite-rank example below constructs and verifies B rather than supplying it as an unexplained assumption.

## 3. The actual domain argument gives (6.53)–(6.54)

The scalar shift cancels in the commutator on the domain:

    (T-z)P y - P(T-z)y = B y.

For y=R x, both y and P y are in D(T). Applying R to the identity and using the two inverse laws gives

    P R x = R P x + R B R x.

Subtracting proves the actual bounded-operator identity

\[
\boxed{[R_z,P]=-R_z B R_z.}
\]

Here [R,P]=RP-PR and B agrees with [T,P] on D(T). The negative sign is not a convention added after the proof. `shifted_commutator` supplies the literal shift-cancellation step in (6.53); `Certificate.commutator_identity` supplies (6.54).

P need not be an orthogonal projector for this theorem. In particular, P is not assumed to reduce T. The theorem can measure nonzero failure of reduction.

## 4. The norm bounds are derived, not input fields

Submultiplicativity of the actual bounded-operator norm gives

\[
\boxed{\|[R_z,P]\|\le\|R_z\|^2\|B\|.}
\]

The corresponding statewise estimate is also checked:

    ||[R_z,P]x|| <= ||R_z||^2 ||B|| ||x||.

These are (6.55) and an added consequence. A version accepting any proved upper bound r on ||R_z|| is included.

For a symmetric partial operator, the imaginary quadratic pairing satisfies

    Im <x,(T-z)x> = -Im(z) ||x||^2.

The imaginary-part estimate and Cauchy–Schwarz imply the coercive bound

\[
|\operatorname{Im}z|\,\|x\|\le\|(T-z)x\| \qquad(x\in D(T)).
\]

Applying this to the actual domain-valued R_z x and its right-inverse identity proves

\[
\boxed{\|R_z\|\le |\operatorname{Im}z|^{-1}}
\]

when Im(z) is nonzero. Combining this independently derived bound with (6.55) gives

\[
\boxed{\|[R_z,P]\|\le\frac{\|B\|}{(\operatorname{Im}z)^2}.}
\]

Setting z=i eta yields the literal (6.56), with **eta != 0** explicit.

Symmetry plus an already existing bounded inverse is sufficient for this estimate. Self-adjointness is stronger and includes this case, but this theorem does not construct nonreal inverses for every abstract self-adjoint operator. The next section does construct them for arbitrary real diagonal operators.

## 5. Actual nonreal inverses for every real diagonal sequence

Take an arbitrary real sequence lambda_n, not necessarily bounded, positive, increasing or distinct. The operator is the previously constructed self-adjoint maximal multiplier

    D(H) = {x in l2 : (lambda_n x_n) is in l2},
    (Hx)_n = lambda_n x_n.

For every complex z with Im(z) != 0, construct the bounded symbol

    r_z(n) = 1/(lambda_n-z)

and its actual bounded multiplication operator R_z. The proof of boundedness is

    |lambda_n-z| >= |Im(z)|,
    |r_z(n)| <= 1/|Im(z)|.

To prove domain range, the formalization establishes the coordinate identity

    lambda_n (R_z x)_n = x_n + z (R_z x)_n.

The right side is a genuine l2 vector. This proves weighted square summability of R_z x, hence membership in the maximal domain. Only then are the two inverse identities proved coordinatewise and assembled into `DiagonalResolvents.certificate`.

Thus the general commutator theorems now have a constructed realization for **all real diagonal sequences and all nonreal complex parameters**, rather than an inverse supplied only by notation.

The earlier positive-gap harmonic construction is also packaged as a genuine certificate. It permits eta=0 because the spectrum starts at 1/2. Uniqueness proves agreement between the old and new constructions where both apply. This does not authorize substituting eta=0 into the nonreal inverse-square estimate.

## 6. Zero leakage characterizes actual domain reduction

A separate converse proves

\[
[R_z,P]=0
\quad\Longleftrightarrow\quad
P D(T)\subseteq D(T)\ \text{and}\ TPx=PTx\ \text{for all }x\in D(T).
\]

The forward implication does not assume domain preservation. Since every y in D(T) equals R_z(T-z)y, commutation with R_z places P y in its range, which has already been proved equal to D(T). The shifted inverse then gives the actual generator commutation law.

The backward implication constructs a zero bounded commutator certificate and applies the proved identity. No density assumption is needed for this domain-level equivalence. The release does not assert uniqueness of every bounded extension B from a possibly nondense domain, nor infer a generic operator-norm reverse estimate for the unbounded generator from small resolvent leakage.

## 7. Additional two-parameter control

For genuine certificates R_z and R_w of the same partial operator, the new domain calculation proves

\[
R_z-R_w=(z-w)R_zR_w,\qquad R_zR_w=R_wR_z.
\]

It also gives

    ||R_z-R_w|| <= |z-w| ||R_z|| ||R_w||,

and, under symmetry with both imaginary parts nonzero,

\[
\|R_z-R_w\|\le
\frac{|z-w|}{|\operatorname{Im}z|\,|\operatorname{Im}w|}.
\]

These are added support results, not additional literal equations attributed to the manuscript. They compare actual inverse certificates; no analyticity theorem or arbitrary-parameter inverse existence is assumed.

## 8. Nonzero infinite-dimensional certificate and exact norms

Use the harmonic operator lambda_n=n+1/2 on the actual infinite l2 space. It is already proved self-adjoint and genuinely unbounded. Let P be the first reflected coordinate projector from Block 12. Its only nonzero block is

\[
P=\frac1{25}\begin{pmatrix}9&12\\12&16\end{pmatrix}
\]

on coordinates zero and one; it vanishes on the remaining coordinates. Idempotence, Hermiticity and maximal-domain preservation are proved.

The explicit bounded extension of [H,P] is

\[
B=\frac{12}{25}(E_{10}-E_{01}),\qquad \|B\|=\frac{12}{25}.
\]

The general construction actually proves this finite-rank extension and its norm for every real diagonal sequence, with the eigenvalue difference retained. For the harmonic sequence that difference is exactly one.

For R_eta=(H-i eta)^{-1}, the exact operator-norm formula is

\[
\boxed{\|[R_\eta,P]\|=
\frac{12/25}{\sqrt{1/4+\eta^2}\sqrt{9/4+\eta^2}}.}
\]

The proof identifies the full bounded commutator as a complex scalar times E_01-E_10 and proves that this two-coordinate operator has norm exactly one. This is not a finite-cutoff approximation of the operator norm. It is valid for every real eta, including zero in this gapped model.

At eta=0,

    ||[R_0,P]||=16/25,
    [R_0,P] e_1 = (16/25)e_0.

At the genuinely nonreal parameter z=i,

\[
[R_1,P]e_1=\frac{-48+384i}{1625}\,e_0,
\qquad
\boxed{\|[R_1,P]\|^2=\frac{2304}{40625}.}
\]

The source bound gives ||[R_1,P]|| <= 12/25 for this same nonzero example. P is proved not to reduce H, and the commutator is proved nonzero for every real eta.

Exact opposite statements reject the positive sign in place of -RBR, omission of one resolvent factor, and extension of the inverse-square eta bound to eta=0. The model and generator are infinite-dimensional and unbounded; the chosen noncommutation is localized to two coordinates. It is not claimed to involve nonzero mixing throughout the infinite tail.

## 9. Verification and remaining boundaries

The new production verifier rebuilds 78 mathematical modules and the aggregate with one worker and warnings as errors. It audits all 1,502 inventoried names, including the certificate, range/domain lifts and every proof-bearing constructor. Only propext, Classical.choice and Quot.sound are allowed dependencies. Active sources contain no admissions, custom axioms, native evaluation or kernel-bypass options.

The 71 previous mathematical modules are checked against the new Block 13 preservation layer; all older layers remain active. The complete 1,173-theorem baseline was freshly verified before extending the cumulative inventory. New-module development was separate from that baseline inventory. Six new invalid controls test the sign, missing factor, zero eta, false reduction, false zero leakage and wrong squared norm. A timeout, import failure or nonzero batch exit alone never counts as a passed negative control. The negative batch uses `maxErrors=1000` so all 101 intended failures can be reported; the compiler default of 100 caused the first cumulative audit to fail and is documented in `BLOCK_14_FAILURES.md`. No mathematical source or false-control assertion was changed by that repair.

Lean is 4.34.0-rc2 and Mathlib is pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine clean dependency revisions are checked. The imported cache is reused, not rebuilt wholesale. Runtime restoration completed with all seven part hashes and the combined archive hash verified; runtime bytes remain external.

This block does not prove a general spectral representation or Stone theorem, abstract nonreal resolvent existence for every self-adjoint operator, differential-oscillator equivalence, compact/Hilbert–Schmidt reconstruction, product-domain ladder commutators, coherent-state factorial-lane weights, nonlinear/dissipative existence, density positivity preservation, continuum gravity, cosmology or empirical adequacy. A resolvent bound is not a claim that the physical model has been observationally validated.

**Next literal target:** Section 6.8, (6.57)–(6.67), infinite reconstruction for bounded, compact and Hilbert–Schmidt operators, plus the graph-domain generator limit. Use actual orthogonal contractive cutoffs (or another explicitly sufficient approximation hypothesis). The manuscript's displayed contraction estimate cannot be applied to arbitrary operators merely because they converge strongly. In particular, any compact right-compression argument must justify the needed adjoint/co-range control rather than infer it from strong convergence alone.
