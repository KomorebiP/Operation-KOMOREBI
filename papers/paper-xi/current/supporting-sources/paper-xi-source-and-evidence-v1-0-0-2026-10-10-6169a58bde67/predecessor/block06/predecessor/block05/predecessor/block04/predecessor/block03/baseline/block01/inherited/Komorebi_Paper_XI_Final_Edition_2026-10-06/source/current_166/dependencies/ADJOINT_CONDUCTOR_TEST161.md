# The original rank-nine source selects critical level4 in the proposed period9 family

Status: ordinary conditional calculation from the actual type-order certificate
specified below; an exact necessary source comparison, not a proof of H5.
This note does not prove the existence of the proposed corrected stratum.

## 1. Source invariant: ordinary self-pair conductor232

Keep the original source of TWO_CUBIC_PACKETS_OBSTRUCTION127, without replacing
either factor. Thus F=F3((t)) and rho=A1 tensor A2, where Ah is the rank3
Heisenberg representation with projective equation

\[
 x_h^9+x_h=t^{-h},\qquad h=1,2.
\]

After the retained unramified splitting extension, each projective quotient
Vh has order9 and every nontrivial character of Vh has break h. This also
follows directly from these equations: for each nonzero constant v with
v^9=-v, the element y_v=v^3 x_h^3+v x_h satisfies

\[
 y_v^3-y_v=-v t^{-h}.
\]

These are the eight distinct nontrivial quotient characters. Indeed their
restriction to the translation group is a nonzero polynomial of degree3
on a set of nine elements, and different v give different restrictions.
Since h=1 or2 is prime to3, each displayed Artin--Schreier character has
break h. This is consistent with the retained primary ramification
calculation of Tsushima, Lemma3.14; no new break assignment is imposed.

For an irreducible Heisenberg representation Ah with nontrivial central
character, End(Ah), under conjugation, contains each character of Vh once.
For example, conjugation on the nine Weyl operators gives the nine
distinct characters through the nondegenerate commutator form. Hence

\[
 \operatorname{End}(\rho)=
 \operatorname{End}(A_1)\otimes\operatorname{End}(A_2)
\]

has one trivial character, eight characters of break1, and72 of break2
after that unramified extension. Distinctness follows from the original
independent projective quotients; a product of characters of distinct
breaks has the larger break. Consequently

\[
 \operatorname{Sw}(\operatorname{End}\rho)=8+72\cdot2=152.
 \tag{1}
\]

Unramified restriction preserves Swan conductor. The original rho is
irreducible on wild inertia, so Schur's lemma gives
dim End(rho)^I=1 already over F. There is no need for Frobenius to fix
each of the81 characters separately. Thus its ordinary Artin conductor is

\[
 a(\operatorname{End}\rho)=81-1+152=232.
 \tag{2}
\]

The scalar summand of End(rho) is unramified, so the same conductor is
obtained for its trace-zero adjoint summand.

## 2. Exact certificate being tested

The proposed family is over F with residue cardinality q=3. For clarity
retain q in the volume calculation. Assume an actual maximal simple type
in GL9(F) has the following certified data:

* A is a complete principal hereditary order of period9, with radical P.
* Its final parameter field K is totally ramified of degree9.
* After conjugating by an actual order unit if needed, beta=gamma+d,
  where gamma is a minimal defining approximation of level24 and
  d belongs to P^(-c). Its degree3 field is E, with B=End_E(E^3),
  B-order BcapA and radical Q. Thus Q^j=BcapP^j and its graded pieces
  have dimension3 over k_F. Those of P have dimension9.
* The defining sequence has leading native level24 and lower even
  critical level c=2a. Its actual simple-character orders are

\[
 \mathfrak J=\mathcal O_K+\mathfrak Q^a+\mathfrak P^{12},
 \qquad
 \mathfrak H=\mathcal O_K+\mathfrak Q^{a+1}+\mathfrak P^{13}.
 \tag{3}
\]

Here a=5 is the first proposed period9 repair (critical10), whereas a=2
is the deeper near-identity repair (critical4). Equation(3) is an input
from the actual defining-sequence construction, not an inference from
the mere values of the leading and critical levels. An order computation
is required before applying this note to a proposed beta.

The required graded compatibility follows from the defining approximation.
Write N_j(gamma)={u in A:[gamma,u] in P^j}. Minimality gives k0(gamma,A)=-24,
so N_-23(gamma)=B-order+P: one inclusion follows from the definition of
k0, and the other from the level24 valuation. Iterating BK1.4.9 from
j=-23 gives

\[
 N_{-c}(\gamma)=\mathfrak B+\mathfrak P^{24-c}.
\]

For every u in O_K, [gamma,u]=-[d,u] belongs to P^(-c). Hence

\[
 \mathcal O_K\subseteq\mathfrak B+\mathfrak P^{24-c}.
 \tag{3a}
\]

Since 24-c is14 or20 in the two cases considered, both are greater
than13. Intersecting(3a) with P^j for 1<=j<=13 proves
p_K^j subset Q^j+P^(24-c). Thus the K contribution cannot add an extra
direction outside the B-grade in the count below. The K-grade itself
has dimension1 because K/F is totally ramified of full degree9.

Let Iplus=1+P, J1=1+(J-order cap P), and H1=1+(H-order cap P).
Below grade a, J1 contributes only the
one-dimensional K-grade. At grades a through11, it contributes the
three-dimensional B-grade; at grade12 and above it is full. Hence

\[
 [I^{+}:J^1]=q^{8(a-1)+6(12-a)}=q^{2a+64}.
 \tag{4}
\]

The J1/H1 quotient has dimension2 at grade a (B modulo K), and dimension6
at grade12 (A modulo B). Thus

\[
 [J^1:H^1]=q^8,\qquad \dim\eta=q^4.
 \tag{5}
\]

Because K has full degree and residue degree1, J/J1=k_F^times. The residue
representation is therefore a character and dim lambda=dim eta=q^4.
BK6.2.5, printed pp204--205, states the *exact* group of unramified
self twists: its order is n/e(K/F), so here the torsion number is1.
This uses the exact theorem, not just the subgroup proved in
UNRAMIFIED_SELF_TWIST_OBSTRUCTION161.md.

## 3. Formal degree and pair conductor, without an HII assumption

Use Haar measure with vol(GL9(O_F))=1 and central measure
vol(O_F^times)=1. The reduction of Iplus is the maximal unipotent group
of GL9(k_F), so

\[
 \operatorname{vol}(I^+)=\frac1{\prod_{j=1}^{9}(q^j-1)},
 \qquad
 \operatorname{vol}(J)=(q-1)q^{-(2a+64)}\operatorname{vol}(I^+).
\]

For a unitary supercuspidal compactly induced from N=K^times J,
the usual compact-induction formal-degree formula gives

\[
 d(\pi)=\frac{\dim\lambda}{9\operatorname{vol}(J)}.
\]

The factor9 is [K^times J:F^times J]. Equivalently this is the special
case of Aubert--Plymen formula(29), printed p26, derived there from
BK7.7.11. Their formula(17), printed p19, gives

\[
 d(\mathrm{St}_9)=\frac1{9}\prod_{j=1}^{8}(q^j-1).
\]

Combining these equations yields the exact ratio

\[
 \frac{d(\pi)}{d(\mathrm{St}_9)}
 =\frac{q^9-1}{q-1}\,q^{2a+68}.
 \tag{6}
\]

If the prescribed unramified scalar is not unitary, use an unramified
twist to unitarize solely for this calculation. The pair pi^vee times pi,
its conductor, J, and lambda are unchanged. This does not replace the
scalar in the constructed representation.

The primary all-characteristic formula of Aubert--Plymen, Theorem6.5,
printed pp27--28, says for a unitary supercuspidal of GL_n with torsion
number r that

\[
 \frac{d(\pi)}{d(\mathrm{St}_n)}
 =r\frac{q^n-1}{q^r-1}q^{(r-n+\delta)/2}.
\]

Their Theorem6.9, printed p28, then identifies its ordinary pair conductor:

\[
 f(\pi^\vee\times\pi)=\delta+n^2-r.
 \tag{7}
\]

The paper assumes a nonarchimedean local field, with no characteristic-zero
restriction on these theorems; Remark6.7 expressly distinguishes earlier
restricted formulas from this general case. We do not use the later
characteristic-zero arguments of BHK1998, nor a conjectural formal-degree
identity.

With n=9 and r=1, comparison with(6) gives

\[
 \delta=4a+144=2c+144,
 \qquad
 f(\pi^\vee\times\pi)=4a+224=2c+224.
 \tag{8}
\]

Their Section4, formula(5), printed p8, fixes an additive character of
conductor O_F and defines f by the epsilon-factor ratio at0 and1.
The conductor convention in(7) is therefore the ordinary pair conductor, so its
comparison is with(2), not with the native conductor24 of the original
rank9 representation itself.

## 4. Decision for the two repairs

| Certified candidate | Critical c | log_q[Iplus:J1] | log_q dim eta | delta | Ordinary self-pair conductor |
|---|---:|---:|---:|---:|---:|
| First period9 repair | 10 | 74 | 4 | 164 | 244 |
| Deeper period9 repair | 4 | 68 | 4 | 152 | 232 |
| Original source | -- | -- | -- | Swan End rho=152 | 232 |

The established local Langlands correspondence over function fields
preserves contragredients and epsilon factors for pairs (Li-Huerta,
TheoremD(iii)--(iv)). Therefore any candidate actually corresponding to
the unchanged original rho must have self-pair conductor232.

The first period9 repair is excluded by244!=232, conditional only on its
stated actual-order certificate. The deeper critical4 repair passes this
necessary comparison. In this precise two-stage family, equation(8)
forces c=4; this is not a universal theorem about every possible
realization of the source.

Passing the leading conductor, exact self-twist count, and self-pair
conductor still does not identify the source parameter, its endo-class,
all native packet maps, or the full same-completion epsilon profile.
No H5 conclusion and no original16.2 closure follows from these invariants.

## 5. Primary-source record and scope

* Aubert--Plymen, *Plancherel measure for GL(n,F) and GL(m,D): Explicit
  formulas and Bernstein decomposition*, arXiv:math/0302169v4,
  4 October2004; published J.NumberTheory112(2005),26--66,
  DOI10.1016/j.jnt.2005.01.005. Local full PDF and extracted text are
  retained in input_cache. Used: introduction (field and measure
  conventions, torsion number), Section4 formula(5), (17), (29), Theorems6.5 and6.9,
  Remark6.7. Source URL: https://arxiv.org/pdf/math/0302169.
* BK1993, authorized project-local source:6.2.5, printed pp204--205;
  its compact-type formal-degree formula7.7.11 is also cited explicitly
  in Aubert--Plymen's derivation.
* Tsushima2024, authorized project-local source, Lemma3.14 and the retained
  original fixture127. The projective quotient calculation above is
  additionally shown explicitly.
* Li-Huerta, *The local Langlands correspondence for GL_n over function
  fields*, author-hosted primary PDF https://math.mit.edu/~sdlh/papers/llc.pdf,
  TheoremD(iii)--(iv), printed p4. Used only for an established necessary
  comparison with a proposed correspondence atom.

Search scope was the exact formal-degree/self-pair-conductor formula and
its characteristic hypothesis. The successful full Aubert--Plymen source
resolves that question. No claim of global novelty or search completeness
is made. No symbolic experiment, compiler, or theorem prover was run for
this derivation. Exact source bytes are recorded in ADJOINT_INPUT_PINS161.json.
