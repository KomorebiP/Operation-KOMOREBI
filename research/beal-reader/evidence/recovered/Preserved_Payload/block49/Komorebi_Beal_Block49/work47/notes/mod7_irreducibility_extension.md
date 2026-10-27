# Block 47: the seven-divides-AB irreducibility extension

Status: written proof using the explicitly named arithmetic inputs below.
It is not a Lean theorem, an exclusion of integer solutions, or a claim of
novelty. The elementary coefficient algebra is separately formalized.

## Statement

Let A,B,C be positive pairwise-coprime integers with A^3+B^5=C^7. Let J be
the Jacobian of

\[
y^2+(x^3+B)y=2Bx^3+3Ax+B^2,
\]

and let K=Q(sqrt(5)). The residual rank-two real-multiplication
representation at the inert prime (7) is absolutely irreducible if 7|AB.
Together with the earlier odd-C theorem, this proves irreducibility whenever

\[
\boxed{C\text{ is odd, or }7\mid AB.}
\]

The branch still unhandled by these two arguments is C even and 7 not
dividing AB. This includes both good ordinary reduction at seven and the
separate case 7|C. The claim is about a representation attached to a
hypothetical solution; irreducibility is not nonexistence of that solution.

## Dependency contract

The source dictionary and rank-two realization, and conductor bounds at
(3) and (sqrt(5)) of at most three, are exactly those retained in
`predecessor/mod7_oddC_written_proof.md`. They come from
[Pacetti–Villagra Torcomian, arXiv:2512.17845v1, §7.1, Corollary 3.6 and
Proposition 3.14](https://arxiv.org/html/2512.17845v1), with
(a,b,c,p)=(B,-C,A,7). No assertion of a maximal integral endomorphism order
at seven is needed: use a stable lattice in the rational RM representation
and lattice independence of residual semisimplification.

The local weight input is [Larson–Vaintrob, arXiv:1110.0255v4,
Lemma 4.10](https://arxiv.org/pdf/1110.0255v4): a degree-one associated
character at an unramified semistable prime over seven has weights zero or
one. For K_(7), the resulting inertia exponents are 0,1,7,8, up to the
common reciprocity sign. Semistable inertia is unipotent away from the
residual characteristic. The Weil pairing, local/global reciprocity, and
residual semisimplification are used as in the predecessor proof.

New geometric inputs have full written derivations in
`notes/evenC_semistability_at2.md` and
`notes/cartier_independent_audit.md`. The latter invokes Raynaud's
finite-flat uniqueness theorem under the verified hypothesis e=1<7-1.
These arithmetic theorems are not added as Lean axioms.

## Proof

Since 7|AB, primitivity implies 7 does not divide C. The discriminant
2^12 3^6 5^5 C^14 proves good reduction at seven. The Cartier computation

\[
M=\begin{pmatrix}0&A^2B\\A&0\end{pmatrix},\qquad M^2=A^3B I_2
\]

then gives geometric 7-rank zero. This holds over the unramified quadratic
extension K_(7)/Q_7 as well.

Suppose the rank-two representation is reducible over the algebraic closure
of F7, and write its semisimplification as lambda plus mu. The underlying
four-dimensional residual semisimplification is that of J[7]. If delta is
the rank-two determinant and chi the mod-seven cyclotomic character, the
Weil pairing gives

\[
(\lambda\mu)^8=\delta^8=\chi^2.
\]

At primes other than 2,3,5,7, semistability of the displayed model, proved
in the predecessor, makes lambda and mu unramified. At two, good reduction
does the same when C is odd. When C is even, the new stable model has two
ordinary nodes and gives semistability, which is enough for the same
unramified-character conclusion.

At (3) and (sqrt(5)), the determinant is trivial on wild inertia: its eighth
power is trivial there, and raising to the eighth power is injective on
the finite 3-group or 5-group image of a character. If lambda were wild,
mu would also be wild. Each would have conductor exponent at least two,
contradicting the total conductor bound of three. Thus both are tame.
Local reciprocity, or Frobenius conjugation of tame inertia, shows that
their inertia orders divide 8 at (3) and 4 at (sqrt(5)). Consequently
lambda^8 and mu^8 are unramified away from seven and trivial at real places.

Let phi=(1+sqrt(5))/2. Its reduction has order sixteen in F49^*.
Write the inertia exponent of lambda at seven as e in {0,1,7,8}.
Global reciprocity applied to the principal idele phi and lambda^8 gives

\[
\bar\phi^{8e}=1.
\]

All other local factors are one because phi is a unit and the character
is unramified there. Thus e is 0 or 8. The same reasoning for mu gives
f in {0,8}. A fundamental character at this inert prime has order 48,
and chi has exponent 8. The determinant relation yields

\[
8(e+f)\equiv16\pmod{48}.
\]

Of the four possible pairs, only (0,8) and (8,0) satisfy this relation.
Hence one constituent is unramified at seven.

This contradicts the local theorem in `cartier_independent_audit.md`: a
good-reduction abelian variety of 7-rank zero over an unramified 7-adic
field has no nonzero unramified subquotient of its 7-torsion. The theorem
handles arbitrary finite coefficient extension by passing to a power of
J, and therefore handles a constituent over the algebraic closure of F7.
Lattice independence transfers the associated constituent to J[7] without
assuming an integral F49 action on that particular torsion lattice.

This contradiction proves absolute irreducibility. No class-number step
and no Frobenius-at-two calculation are needed for this new conclusion.

## Boundary of the advance

The even-C semistability result permits the global character argument for
all parities. The last local contradiction requires 7|AB. If 7 does not
divide ABC, the reduction is ordinary and can have an unramified
constituent. If 7|C, the good-reduction Raynaud argument does not apply.
Neither remaining branch is silently covered by the proof.

Even where irreducibility is now available, one still needs the complete
level-lowering hypotheses at seven and elimination of all attached forms.
Full Beal also requires the other exponent signatures; success for (3,5,7)
alone would not settle it.
