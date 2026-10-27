# An actual dimension-correct two-transition Weil fixture

This is a by-hand construction of actual local fields, upper ramification groups, and an irreducible Weil representation. It is not an actual simple-character/type construction, not a counterexample to H1–H5, and not a Lean theorem. The construction was proposed by the delegated source-realization reader `/root/lattice_route/weil_realization112`; `/root/lattice_route` independently checked the equations, coefficient independence, group law, representation, descent, and cited ramification hypotheses. No source in continuation111 was modified.

## 1. Fields and torsors

Take

\[
F=\mathbf F_5((t)),\qquad K=\mathbf F_{625}((t)),\qquad
c^4=2,\quad d=c^{-1}.
\]

Such a c has order16, and the order of5 modulo16 is4, so c has degree4 over F5. In particular K/F is the unramified degree4 extension. We have c^5=2c and d^5=3d. The coefficients c,d are F5-independent: their ratio c² cannot belong to F5, because its square would be the nonsquare2.

For m1=2 and m2=3, define

\[
a_j=c t^{-m_j},\qquad b_j=d t^{-m_j},\qquad
L_j=K(x_j,y_j,z_j),
\]

\[
x_j^5-x_j=a_j,\qquad y_j^5-y_j=b_j,
\qquad z_j^5-z_j=a_jy_j.
\]

Write wp(s)=s^5-s. A Laurent series wp(s) with a pole has pole order divisible by5, because its s^5 term has strictly greater pole order than s. Every nonzero F5-combination of a_j,b_j has pole m_j, prime to5. Their Artin–Schreier classes are therefore independent, and K(x_j,y_j)/K has degree25.

The last equation gives an additional degree5 extension. If z_j already belonged to K(x_j,y_j), let alpha and beta be its commuting automorphisms translating x_j and y_j respectively by1. The equations imply

\[
\alpha(z_j)-z_j\in\mathbf F_5,
\qquad\beta(z_j)-z_j-x_j\in\mathbf F_5.
\]

Then alpha beta(z_j)-beta alpha(z_j)=1, contradicting commutativity. Thus [L_j:K]=125. Its automorphisms are

\[
h(u,v,w):(x,y,z)\longmapsto(x+u,y+v,z+vx+w),
\qquad u,v,w\in\mathbf F_5,
\]

with group law

\[
h(u,v,w)h(u',v',w')
=h(u+u',v+v',w+w'+uv').
\]

Hence H_j=Gal(L_j/K) is the order125 Heisenberg group, with center Z_j={h(0,0,w)}. These formulas verify normality and all125 automorphisms directly.

Every degree5 subextension is represented by a nonzero AS class in the span of a_j,b_j, and is ramified. A nontrivial unramified quotient of this5-group would yield a degree5 unramified subextension. Therefore L_j/K is totally ramified.

The two fields are linearly disjoint. A nontrivial common Galois subextension would have a cyclic degree5 subextension, because a nontrivial finite5-group has such a quotient. That would give a nonzero AS class in the intersection of the two coefficient spans. A combination with the distinct pole orders2 and3 has a largest pole prime to5, so cannot lie in wp(K). The intersection is zero. Consequently

\[
\operatorname{Gal}(L_1L_2/K)=H_1\times H_2.
\]

## 2. Ramification input and its checked hypotheses

The specialized source input is Koto Imai, *Ramification groups of some finite Galois extensions of maximal nilpotency class over local fields of positive characteristic*, manuscripta mathematica176, article66 (2025), DOI [10.1007/s00229-025-01664-5](https://link.springer.com/article/10.1007/s00229-025-01664-5). The primary published HTML was read on2026-10-01. Relevant exact locations are Lemma3.2, Lemma3.1, Example3.8(1), equations(3.53)–(3.56), and the differential valuation before Lemma2.1.

Apply that formula with its nilpotency parameter n=2, its p=5, a=a_j, b1=b_j, b2=0. The residue field is perfect; total ramification was proved above; both positive pole orders are m_j and prime to5; their leading coefficients c,d are F5-independent. The b2 pole condition is vacuous. The source uses the logarithmic differential valuation, so

\[
-a_j\,db_j=m_jcd\,t^{-2m_j}\frac{dt}{t}
=m_jt^{-2m_j}\frac{dt}{t}.
\]

Its final-break formula therefore gives

\[
r_j=\max(2m_j,m_j/5+m_j,m_j+m_j/5)=2m_j.
\]

The abelianization has its one break m_j; the terminal group is the center. Thus H1 has breaks2,4 and H2 has breaks3,6. This is the only specialized literature leaf; the remaining field/group/representation arguments here are derived directly.

For the compositum, projection compatibility by itself would not prove a product filtration. The following additional argument does. Nontrivial linear irreducibles of H_j have slope m_j; nonlinear irreducibles have nontrivial central character and slope2m_j. Every irreducible of H1×H2 is a tensor of factor irreducibles. Their possible positive slopes belong to the disjoint sets {2,4} and {3,6}. Its slope is the larger: between the slopes the lower factor is trivial on the actual upper ramification subgroup, by quotient compatibility, while the higher factor has no invariants; beyond both slopes both are trivial. Irreducibility and normality make the invariant space either zero or the whole space.

A normal subgroup of a finite group is the intersection of kernels of the irreducibles factoring through its quotient. Therefore the irreducibles trivial on the actual group at u determine that group and give H1^u×H2^u. Away from the endpoints the actual filtration is

| Range | Group |
|---|---|
| 0<u<2 | H1×H2 |
| 2<u<3 | Z1×H2 |
| 3<u<4 | Z1×Z2 |
| 4<u<6 | 1×Z2 |
| u>6 | 1 |

The distinct slope sets are essential to this proof. It is not asserted for arbitrary composita with coincident factor breaks.

## 3. The same25-dimensional carrier and actual Clifford data

Fix a primitive fifth root zeta. On complex functions F5→C put

\[
(\tau_j(u,v,w)f)(s)=\zeta^{w+vs}f(s+u).
\]

The group law above gives an honest representation. Modulation has five distinct eigenspaces, and translation permutes them transitively; hence tau_j is irreducible of dimension5. Its center acts by chi(w)=zeta^w.

The tensor R0=tau1⊗tau2 is irreducible of dimension25. An operator tau_j(h) is scalar only if u=v=0. If a tensor of two invertible operators is the identity, both factors are inverse scalars. Hence its kernel is exactly

\[
D=\{(z(w),z(-w)):w\in\mathbf F_5\}.
\]

Set M0=(L1L2)^D. Its group G'=(H1×H2)/D is a rank4 Heisenberg group of order5^5, and R0 is faithful on G'. Upper quotient compatibility collapses the transition at4: the images of Z1×Z2 and1×Z2 are equal. The actual positive filtration becomes

\[
G'\supset G_1'=(Z_1\times H_2)/D\simeq H_2
\supset G_2'=(Z_1\times Z_2)/D\simeq\mathbf F_5
\supset1,
\]

at2,3,6 respectively. The central identification is by addition of coordinates; no extra power of chi is introduced.

The first restricted representation R0|G1' is tau2-isotypic with multiplicity5. The restriction tau2|G2' is chi-isotypic with multiplicity5. Constituents are stable under their corresponding ambient groups: elements of H1 commute with H2, elements of H2 conjugate its representation by inner intertwiners, and G2' is central. Each quotient is F5² and each projective multiplicity commutator is

\[
\zeta^{uv'-u'v}.
\]

Thus these are two actual Definition9.1 data at the distinct quotient breaks2 and3, not artificially labeled planes. Their packet dimensions multiply exactly to the ambient25, with terminal constituent dimension1. The full finite source envelope is their literal orthogonal sum F5⁴.

## 4. Descent to the stated residue field and whole Weil parameter

Arithmetic Frobenius on K/F extends to an order4 automorphism sigma by

\[
\sigma(x_j)=2x_j,\quad\sigma(y_j)=3y_j,
\quad\sigma(z_j)=z_j.
\]

It preserves the equations because sigma(a_j)=2a_j, sigma(b_j)=3b_j, and2·3=1 inF5. Its fourth power is the identity on the field generators. It follows that L1L2/F is Galois with group (H1×H2)⋊C4. The central subgroup D is preserved, so M0/F is also Galois, with group G'⋊C4.

Conjugation by sigma takes (u,v,w) to (3u,2v,w). The operator S f(s)=f(2s) has S^4=1 and satisfies

\[
S\tau_j(u,v,w)S^{-1}=\tau_j(3u,2v,w).
\]

Therefore R0 extends to this finite Galois group with sigma represented by S⊗S. Call the resulting Weil representation rho, inflated through W_F. It is irreducible because its restriction to the wild group G' is irreducible, on the same25-dimensional carrier. This is the whole Weil parameter, not just a chosen constituent of a larger induced representation. Geometric Frobenius is the inverse of the arithmetic sigma convention and is represented by S^{-1}⊗S^{-1}.

The positive ramification filtration is unchanged by the unramified extension K/F. The sole ordinary slope of rho is6, since the nontrivial scalar center acts up to the terminal break. Its two nondegenerate projective Clifford transitions remain2 and3. The residue field of F is now F5, so packet dimensions5,5 pass the elementary residue-cardinality test.

The image of inertia is the5-group G'; the tame-inertia quotient acts trivially. Thus the actual tame stabilizer can be C=1. The displayed nontrivial C4 is an unramified Frobenius complement, not tame inertia. If a source dictionary also requires its Frobenius action, that action is explicit and must be retained; it cannot be silently reinterpreted as a subgroup of an actual compact type quotient. This construction does not claim that rho is primitive in the stronger sense of not induced from any proper subgroup; the original irreducibility conditions do not assert that stronger property.

## 5. Precisely what has not been supplied

No actual maximal simple character in GL25(F), no actual groups H1_theta,J1_theta, no arithmetic parameter field, and no canonical kappa action have been constructed here. In particular neither per-break H2 nor global assembled-type attachment is discharged. Numerical residue compatibility is necessary but not sufficient. The earlier variant over F25((t)) with coefficients1,epsilon and the same m_j is also genuine, but its5-dimensional packets fail the elementary type dimension requirement25^r; it is only a diagnostic, not a full counterexample.

The fixture makes the next test concrete: determine the actual Heisenberg dimension spectrum for maximal simple characters in GL25(F5((t))), first for a packet of degree5 and then for the assembled degree25, together with the required action. A dimension obstruction to a local packet would put this fixture outside H2; a proof of compatible actual realizations would permit a genuine attachment test. Either outcome is mathematically useful. H5 for the same completion and the original twist family is untouched.
