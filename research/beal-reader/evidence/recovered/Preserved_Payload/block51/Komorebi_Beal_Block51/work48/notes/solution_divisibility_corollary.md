# A divisibility restriction from the quadratic twist

Status on 2026-09-19: written cross-route proof with checked local-type
and twisting implications, and independently audited norm-45 data and
finite comparison. No new irreducibility claim at primes three and five
is needed for this corollary. The external arithmetic and database
inputs are stated explicitly below.

## Statement

Let A,B,C be positive pairwise-coprime integers satisfying

\[
A^3+B^5=C^7.
\]

Subject to the declared, source-checked arithmetic and database inputs,

\[
\boxed{15\mid C\quad\Longrightarrow\quad3990\mid C.}
\]

In particular, C divisible by fifteen must also be divisible by two,
seven, and nineteen. This implies the initially proposed weaker
restriction 30|C ⇒ 3990|C. It does not exclude solutions with 3990|C,
or solutions with 15∤C, and is not a solution of the full signature
(3,5,7) equation.

The representation-theoretic intermediate statement is useful:
**if 15|C, the residual rank-two RM representation at seven is
absolutely reducible.** Here “absolutely reducible” means reducible
after extending the coefficient field to Fbar₇; it does not assert
splitting of an extension over its original coefficient field.

## Exact inputs

1. `level_lowering.md` proves that an absolutely irreducible residual
   RM representation attaches directly to a parallel-weight-two,
   trivial-character Hilbert newform over K=Q(√5), with the original
   Weil–Deligne types retained at (3) and (√5). Its seven-specific
   modularity, cyclotomic-restriction, finite-flat, coefficient-prime,
   weight and determinant hypotheses were separately checked. The
   original local conductor exponents belong to {2,3}.
2. PV arXiv:2512.17845v1, Proposition 7.4, printed pp.29–30, gives
   potentially multiplicative reduction when v_l(t−1)>3, for l=3,5.
   The source dictionary is (a,b,c,p)=(B,−C,A,7), with
   t=−B⁵/A³. Theorem 7.8, printed p.32, independently records exponent
   two in both branches used here: 3|ab and 5|bc.
   [Versioned primary source](https://arxiv.org/pdf/2512.17845v1).
3. `character_sieve.md` and its independent
   `bad7_character_sieve_audit.md` identify the totally even quadratic
   character ν of Q(ζ₁₅)⁺/K. It is tamely ramified at both (3) and
   (√5), unramified elsewhere at finite primes, and ν(Frob_(2))=−1.
   These character properties do not require that the residual RM
   representation be reducible: ν is an independently defined global
   character which can be used to twist any representation.
4. The same independently audited earlier result gives
   266∤C ⇒ absolute irreducibility. The stronger new result involving
   3990 is not an input here.
5. The complete norm-45 LMFDB space contains one orbit,
   `2.2.5.1-45.1-a`, with coefficient field Q and Hecke eigenvalue
   a_(2)=−3. The exact retained data and finite comparison are
   `source_records/candidate_lmfdb_45_search.html`,
   `source_records/candidate_lmfdb_45_a.html`, and
   `verification/candidate_twisted45.json`.
   [Primary form page](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-45.1-a).

The local factor and conductor arguments below are written proofs.
The small-space enumeration and Hecke value are imported exact
database data; they were not recomputed as a Hilbert modular form space.
Their independent parser and finite-polynomial audit is
`candidate_twisted45_audit.md`, with certificate
`verification/candidate_twisted45_independent.json`.

## Why both original local types are ramified quadratic special

Assume 15|C and suppose, for contradiction, that the residual RM
representation is absolutely irreducible. Primitivity makes A and B
units at three and five. Consequently

\[
t-1=-\frac{A^3+B^5}{A^3}=-\frac{C^7}{A^3},
\qquad v_l(t-1)=7v_l(C)>3\quad(l=3,5).
\]

The rational valuations in this application are the valuations used
in PV Proposition 7.4. Over K the valuation at (√5) is twice v₅;
this does not alter the asserted reduction type. Thus the full
Jacobian becomes totally multiplicative at both places. Its rank-four
Tate representation has monodromy rank two. The rank-two RM factor
therefore has monodromy rank one and Weil–Deligne type

\[
\eta_v\otimes\operatorname{Sp}_2,\qquad N\ne0.
\]

The characteristic-zero determinant is cyclotomic independently of
residual reducibility: this is BCDF arXiv:2205.15861v5, Theorem 2.8,
printed p.10, applied to the polarized RM abelian surface over the
totally real field K, as checked in `level_lowering.md`. It is not
inferred here from the weaker residual pairing argument in the
character sieve.
[Versioned primary source](https://arxiv.org/pdf/2205.15861v5).
Cyclotomic inertia is trivial at three and five, so η_v² is trivial
on inertia. The
quadratic inertia character is tame, since the residue characteristic
is odd. There is therefore no Swan term and the conductor is at most
two. Combining this with the already audited original conductor range
{2,3} forces the exponent to be exactly two. For a special type this
means η_v is ramified, since an unramified special type has exponent
one. Equivalently, the explicit branches of PV Theorem 7.8 give the
same answer immediately after substituting (B,−C,A).

This argument uses the original compatible-system conductor input.
The range {2,3} is the source-checked geometric conductor statement
recorded in the primes-three-and-five section of `level_lowering.md`;
it is used before constructing a modular lift. The conductor lower
bound is not inferred from choosing the desired level of a lift.
It does not infer an original conductor by pretending every residual
conductor is unchanged. In the particular type now established,
however, residual persistence is easy: choose an inertia element
on which η_v=−1. Its two residual eigenvalues are −1, so it has no
fixed vector in characteristic seven. The Swan term is still zero.
Thus the residual conductor is also exactly two, even if the
unipotent extension class disappears modulo seven.

The generic conductor tables alone contain ranges in some rows.
Also, the printed exception in PV Remark 3.12 is inconsistent with
the corresponding special rows of Table 3.3. Neither that exception
sentence nor a new use of Proposition 3.10 outside its stated
hypotheses is needed here: the argument uses the already audited
original range, potential multiplicative reduction, determinant,
and the exact branch statement of Theorem 7.8.

## Twisting the attached form

By the audited level-lowering theorem, choose a newform f with the
original types just established, so that its exact level is

\[
(3)^2(\sqrt5)^2=(45),\qquad N((45))=2025.
\]

Twist the attached automorphic representation by the quadratic Hecke
character ν. This is an ordinary automorphic twist, not a second
application of a lifting theorem. At the level of automorphic
functions it multiplies by ν(det g), preserving the cuspidal condition.
The character is totally even, so the holomorphic parallel weight
remains two. The central character is multiplied by ν²=1 and remains
trivial. The residual representation of the twisted newform is
directly congruent to barρ⊗ν at one fixed coefficient prime above
seven.

At either v=(3),(√5), there is a unique nontrivial quadratic character
of tame inertia. Both η_v and ν restrict to it. Hence η_vν is
unramified and the twisted local type is unramified special. Twisting
does not kill N. The local conductor is therefore exactly one, not
zero. At every other finite prime, ν is unramified and the attached
form is already unramified. In particular no level factor at seven
appears. Thus the twisted newform g has exact level

\[
\mathfrak n=(3)(\sqrt5)=(3\sqrt5),\qquad N(\mathfrak n)=45.
\]

No new finite-flat proof is needed for this twist of an existing
newform. If one instead twists the residual construction directly,
ν is unramified at seven, and finite flatness is preserved by
unramified descent; the resulting determinant is still cyclotomic.
That alternative is not used in the proof.

## The contradiction at two

The existing good- and semistable-reduction calculations give the
following possibilities for the original full J[7] at the prime
(2), of norm four:

| Parity of C | Full Frobenius polynomial before twisting |
|---|---|
| C odd | (T²+T+4)² or (T²+4)² |
| C even | (T+1)²(T+4)² |

These are characteristic-polynomial statements, so lattice
semisimplification suffices. Since ν(Frob_(2))=−1, twisting changes
the odd-C quadratic factors to Q₁=T²−T+4 or Q₀=T²+4, and changes
the even-C eigenvalues to 1 and 4.

The unique norm-45 form has factor R=T²+3T+4. It has no common root
with either Q₀ or Q₁ modulo seven: R−Q₀=3T and R−Q₁=4T, whereas
both Q_i have nonzero constant term. Nor can it supply either even-C
eigenvalue, since R(1)=1 and R(4)=4 modulo seven. Hence no rank-two
constituent of the twisted Jacobian representation can be the
residual representation of that form. Its rational coefficient field
eliminates any coefficient-prime ambiguity in this comparison.

This contradicts the existence of g. Therefore a primitive solution
with 15|C necessarily has an absolutely reducible residual RM
representation.

## The integer divisibility step and review boundary

The contrapositive of the independently audited theorem
266∤C ⇒ absolute irreducibility now forces 266|C. Since

\[
\gcd(15,266)=1,\qquad15\cdot266=3990,
\]

we obtain 3990|C. This logical step needs neither the new local
irreducibility strengthening at three and five nor elimination of
the other three original level spaces. Even the complete fourteen-form
norm-2025 elimination is unnecessary for this stronger twist proof.

The two level ideals must not be confused: the original level is the
rational ideal (45), of norm 2025; after twisting the level is
(3√5), of norm 45. The result remains a branch restriction on integer
solutions. It is not an unrestricted irreducibility theorem, an
elimination of the 3990|C branch, or a proof of Beal's conjecture.

Pins checked in preparing this proof:

| Input | SHA-256 |
|---|---|
| `level_lowering.md` | `ff74504680f23207c1fae030708582fa622f6699dfdf1057df9ec536f6d8ea63` |
| `bad7_character_sieve_audit.md` | `32a402832b37053600ab245ff5f0b58296dcebeef65df915b8c4f0682e8dc2ae` |
| `candidate_lmfdb_45_a.html` | `22342a7f424ec537125ef50970fadfb6f7dfe2c6d1f1f97f9239fb6d65872e09` |
| `candidate_lmfdb_45_search.html` | `78dca07dbc4e6db4dadc0bafcfbfd3e436461a3c55ae9e3535f3794a76b7f3c7` |
| `candidate_twisted45_audit.md` | `f371c6d1570b69037f37880fa22c6337dda0d691faa20de8eb8dffdde765e41b` |

This is a written arithmetic corollary with named external inputs,
not a formalized modularity or Diophantine theorem.
