# Komorebi Transport Geometry (KTG)

## 0. Purpose

KTG is an abstract calculus for comparing objects that live in distinct ambient structures without silently identifying them. It is motivated by recurring Komorebi transfer-block ideas and by the architecture visible in IUT's multiradial constructions.

The guiding principle is:

> A cross-representation theorem must expose the exact transport, obstruction, normalization, enclosure, witness, and observable certificates that carry the conclusion.

---

## 1. Ambient contexts

Let \(\mathsf A\) be a collection/category of ambient structures. For every \(A\in\mathsf A\), attach a class/category \(\mathcal C_A\) of objects meaningful relative to \(A\).

Write

\[
x@A
\]

for an object \(x\in\mathcal C_A\).

**Typing axiom.** Even if underlying presentations look identical,

\[
x@A \not\equiv x@B
\]

unless an explicit identification or transport certificate has been supplied.

---

## 2. Transport as a common-container span

For an admissible context change \(f:A\to B\), introduce a transport carrier \(\mathcal K_f\) and representation maps/functors

\[
L_f:\mathcal C_A\to\mathcal K_f,
\qquad
R_f:\mathcal C_B\to\mathcal K_f.
\]

Together with an admissible relation \(\sim_f\) on the carrier, define the set-valued transport

\[
T_f(x)
=
\{y@B : L_f(x)\sim_f R_f(y)\}.
\]

This includes ordinary functions as the special case where \(T_f(x)\) is canonically singleton-valued.

---

## 3. Obstruction bundle

Every transport carries an explicit obstruction object

\[
\Omega_f.
\]

It may decompose into named channels such as

\[
\Omega_f
=
\Omega_f^{\rm perm}
\times
\Omega_f^{\rm aut}
\times
\Omega_f^{\rm shift}
\times
\Omega_f^{\rm norm}
\times
\Omega_f^{\rm desc}
\times\cdots.
\]

Exact transport is the limiting case in which the relevant obstruction object is trivial.

No obstruction channel may be declared harmless unless a theorem proves that the downstream observable is invariant under that channel or is controlled by an explicit one-sided estimate.

---

## 4. Coricity / invariance signatures

For a transformation family \(\Gamma\) acting on objects, call \(x\) **\(\Gamma\)-coric** when

\[
\forall\gamma\in\Gamma,\qquad \gamma x\cong x.
\]

With multiple generator families \(\Gamma_1,\dots,\Gamma_r\), attach the signature

\[
\Sigma_{\rm cor}(x)
=
(\Gamma_1:b_1,\ldots,\Gamma_r:b_r),
\qquad b_i\in\{0,1\}.
\]

Bi-coricity is the two-generator special case with both entries equal to one.

---

## 5. Lax transport composition

For

\[
A\xrightarrow{f}B\xrightarrow{g}C,
\]

define relational composition

\[
(T_g\star T_f)(x)
=
\bigcup_{y\in T_f(x)}T_g(y).
\]

Do not require strict equality with \(T_{g\circ f}\). Instead record a comparison

\[
\alpha_{g,f}:
T_g\star T_f
\Longrightarrow
T_{g\circ f},
\]

whose strength may be equality, isomorphism, inclusion, or a weaker certified relation.

This yields a hierarchy of transport modes:

\[
\text{strict}
\Rightarrow
\text{pseudo}
\Rightarrow
\text{equivariant}
\Rightarrow
\text{lax}
\Rightarrow
\text{enclosive}
\Rightarrow
\text{scalar-only}.
\]

---

## 6. Transport curvature

Given a square of context changes, compare the two path transports. The **transport curvature** is the obstruction

\[
\mathcal K_\square
=
\operatorname{Obs}(T_hT_f,T_kT_g).
\]

In a linear setting this reduces naturally to a commutator such as

\[
\mathcal K=[T_H,T_V]=T_HT_V-T_VT_H.
\]

Thus

\[
\boxed{\text{curvature} = \text{obstruction to commuting transport}.}
\]

---

## 7. Transport chart vs measurement chart

For each context \(A\), distinguish

\[
\mathcal T_A
=\text{transport representation},
\qquad
\mathcal M_A
=\text{measurement representation}.
\]

Connect them by

\[
\rho_A:\mathcal T_A\rightsquigarrow\mathcal M_A.
\]

The representation that makes transport exact or rigid need not be the representation in which the desired scalar invariant is easiest to compute.

---

## 8. Hull / closure operators

Let \((\mathcal M_A,\preceq)\) be an ordered measurement space. A hull operator

\[
H_A:\mathcal M_A\to\mathcal M_A
\]

satisfies:

1. **Extensive:** \(x\preceq H_A(x)\).
2. **Monotone:** \(x\preceq y\Rightarrow H_A(x)\preceq H_A(y)\).
3. **Idempotent:** \(H_A(H_A(x))=H_A(x)\).

The point of a hull is not to preserve exact equality. It creates a canonical comparison object large enough to contain a difficult or noncanonical transported object.

---

## 9. Monotone observables

Let \((\Lambda,\le)\) be an ordered codomain. An observable

\[
\Phi_A:\mathcal M_A\to\Lambda
\]

is monotone if

\[
x\preceq y\implies \Phi_A(x)\le \Phi_A(y).
\]

Typical examples include volume, degree, norm, energy, entropy, occupancy, defect, spectral radius, or certified error.

---

## 10. Obstruction compression

Suppose the obstruction bundle decomposes as

\[
\Omega_f=\Omega_f^0\times\Omega_f^+,
\]

where \(\Omega_f^0\) acts invisibly on the observable and \(\Omega_f^+\) acts only by monotone enlargement.

Then \(\Phi\) compresses a high-dimensional structural ambiguity into lower-dimensional ordered uncertainty:

\[
\Omega_f\xrightarrow{\Phi}\Omega_f^\Phi.
\]

This is a general abstraction of the pattern in which some structural indeterminacies disappear after passing to an invariant scalar, while another becomes a one-sided bound.

---

## 11. Witness preservation

For a reference object \(q@B\), define the completed transported enclosure

\[
\widehat T_f(x)
=
H_B\!\left(\bigvee_{y\in T_f(x)}\rho_B(y)\right).
\]

Then define

\[
W_f(x,q)
:\Longleftrightarrow
\rho_B(q)\preceq\widehat T_f(x).
\]

This is the **witness-preservation certificate**.

It may not be inferred solely from:

- functoriality,
- structural relatedness,
- common-carrier representation,
- simultaneous definability,
- equivariance,
- or invariance of the input context.

### Certified Transport Bound

If \(W_f(x,q)\) and \(\Phi_B\) is monotone, then

\[
\boxed{
\Phi_B(\rho_B(q))
\le
\Phi_B(\widehat T_f(x)).
}
\]

The inequality is trivial once the witness is proved. The witness is the load-bearing theorem.

---

## 12. Grade and normalization transport

Every measurable object may carry a grade

\[
\nu_A(x)\in G_A,
\]

encoding multiplicity, tensor power, scale, degree, packet weight, valuation normalization, or similar data.

For each transport \(f:A\to B\), specify

\[
\sigma_f:G_A\to G_B.
\]

A normalization-preserving transport must prove

\[
\nu_B(y)=\sigma_f(\nu_A(x)),
\]

or expose a defect

\[
\delta_f(x,y).
\]

Composition should satisfy a cocycle law when exact:

\[
\sigma_{g\circ f}=\sigma_g\circ\sigma_f.
\]

Failure defines normalization curvature/defect.

This prevents factors such as tensor powers, multiplicities, or \(j^2\)-type weights from silently disappearing during transport.

---

## 13. Safe abstraction / hidden internal structures

Let an implementation carry internal state \(z\in Z\), and let

\[
q:Z\to\bar Z
\]

be the public abstraction.

An observable \(\Phi\) is safe with respect to hiding the internal state exactly when it factors through \(q\):

\[
\Phi=\bar\Phi\circ q.
\]

Equivalently,

\[
q(z_1)=q(z_2)
\implies
\Phi(z_1)=\Phi(z_2).
\]

Any hidden datum that violates this condition is **load-bearing** and may not be abstracted away in a proof that uses \(\Phi\).

---

## 14. Canonical weighting from overlap compatibility

Let primitive labels be \(P\), with packets \(C_i\subseteq P\). Define an overlap graph whose vertices are packets and whose edges connect packets that share a primitive contribution required to have the same normalization in both.

If compatibility forces equal weight across every overlap edge and the overlap graph is connected, then all packet weights are equal. After normalization, the average is canonical.

This abstracts the idea that refinement/procession compatibility may force an averaging rule rather than leave weights arbitrary.

---

## 15. Standard proof pipeline

The complete KTG proof pattern is

\[
\boxed{
\text{TYPE}
\to
\text{TRANSPORT}
\to
\text{OBSTRUCTION}
\to
\text{NORMALIZATION}
\to
\text{HULL}
\to
\text{WITNESS}
\to
\text{OBSERVABLE}.
}
\]

No arrow is optional if the conclusion depends on it.

This is intended as a reusable proof-audit framework for Komorebi mathematics, not only for IUT.
