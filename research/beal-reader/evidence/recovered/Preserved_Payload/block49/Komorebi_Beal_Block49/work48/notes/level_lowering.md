# Level lowering at seven: hypothesis audit

Checked 2026-09-19. Primary verdict: **proved as written**, for the conditional
level-lowering theorem below. This is a written arithmetic argument using the
named external results. It is not a Lean modularity theorem and does not
eliminate a newform or a Diophantine solution.

## Exact conclusion

Let positive pairwise-coprime integers satisfy
\(A^3+B^5=C^7\). Let \(K=\mathbf Q(\sqrt5)\), and let \(\bar\rho\)
be the residual RM representation of the Jacobian used in Block 47, in the
weight-two Tate-module normalization. **If \(\bar\rho\) is absolutely
irreducible**, there are a Hilbert newform \(f/K\) of parallel weight two
and trivial character, and a prime \(\mathfrak P\mid7\) of its coefficient
field, such that

\[
\bar\rho\otimes\overline{\mathbf F}_7
 \simeq\bar\rho_{f,\mathfrak P}\otimes\overline{\mathbf F}_7,
\qquad
\operatorname{level}(f)=(3)^{\varepsilon_3}(\sqrt5)^{\varepsilon_5},
\quad\varepsilon_3,\varepsilon_5\in\{2,3\}.
\]

Moreover, the newform can be chosen with the same Weil–Deligne types as
the original seven-adic representation at \((3)\) and \((\sqrt5)\).
Thus the four spaces are valid targets at seven. Combining this theorem
with Block 47 makes the conclusion unconditional for \(14\nmid C\).
Absolute irreducibility remains a separate input when \(14\mid C\).

This theorem does not assert that the coefficient field of \(f\) is
\(K\), that it has a preferred prime above seven, or that a form identified
only by a transcript index has been eliminated. One fixed form, prime and
residual embedding must be retained in subsequent comparisons.

## Normalization and source dictionary

The curve is
\[
y^2+(x^3+B)y=2Bx^3+3Ax+B^2.
\]
Its Jacobian is a polarized abelian surface with RM by \(K\) over \(K\),
as in the inherited source contract. The variable dictionary for Pacetti–
Villagra Torcomian (PV), arXiv:2512.17845v1, is
\[
(a,b,c,p)=(B,-C,A,7),\qquad t_{\rm PV}=-B^5/A^3.
\]
PV's raw hypergeometric normalization requires the Tate twist of Remark
2.2 to reach weight two. All determinant, finite-flat, Hodge–Tate and
newform comparisons in this note use the resulting geometric rank-two
representation. Mixing its trace with the unnormalized hypergeometric
trace would introduce a norm factor.

The coefficient prime \((7)\) is inert: \(x^2-x-1\) is irreducible modulo
seven because its discriminant is the nonsquare 5. Consequently the
coefficient residue field is \(\mathbf F_{49}\), and the local base field
at seven is the unramified quadratic extension of \(\mathbf Q_7\).
Neither Breuil–Diamond's theorem nor the arguments below require seven to
split in the coefficient field or in the base field.

The determinant is the cyclotomic character, not merely a character with
the same norm. The directly checked version of Billerey–Chen–Dieulefait–
Freitas (BCDF), arXiv:2205.15861v5, Theorem 2.8, applies to a polarized
\(\mathrm{GL}_2(F)\)-type abelian variety over a totally real field when
\(F\) is totally real. Here both fields are \(K\). It gives
\(\det\rho=\chi_7\), hence \(\det\bar\rho=\bar\chi_7\).
This is an additional source input beyond the weaker norm identity used
in the predecessor's irreducibility proof. The longer v5 manuscript has
different numbering from the shorter published paper cited by PV as
Theorem 3.13; no equality of those theorem numbers is assumed.

## Modularity and the corrected source locator

PV Theorem 2.4 points to Golfieri Madriaga–Pacetti (GP),
arXiv:2412.08804. The version available before PV v1 is **v2, 17 December
2025**. Its applicable plus-motive modularity result is **Theorem 6.2**,
printed p.21, not Theorem 6.3. The latter treats a minus motive and has
an \(r\ge11\) restriction.

In GP's family \((3,p,r)\), use exponent \(r=5\), equation coefficients
\((A_{\rm coeff},B_{\rm coeff},C_{\rm coeff})=(1,1,1)\), and variables
\((\alpha,\beta,\gamma)=(A,-C,B)\). Its parameter is
\(-A^3/B^5=t_{\rm PV}^{-1}\). Interchanging the parameter pairs and
inverting the parameter gives the same plus motive, up to the already
fixed geometric normalization. The condition \(r\nmid A_{\rm coeff}\)
is \(5\nmid1\), not a condition on the integer base \(A\).
Theorem 6.2 therefore establishes modularity here; it does not use
irreducibility at seven. This repairs the locator mismatch without
importing either PV main theorem that excludes seven.

## Irreducibility over the cyclotomic extension

Breuil–Diamond (BD), arXiv:1208.5367v3, Theorem 3.2.2, requires
irreducibility after restricting to \(G_{K(\zeta_7)}\).
Absolute irreducibility over \(K\) alone is not a formal substitute.
The missing implication is now proved in
`level_restricted_irred_review.md`.

The argument uses that the Jacobian has good reduction at seven if
\(7\nmid C\), and totally toric semistable reduction otherwise. If an
absolutely irreducible rank-two representation becomes reducible over
\(K(\zeta_7)\), normality supplies two lines interchanged by the quadratic
character \(\bar\chi_7^3\). Since the cyclotomic extension is totally
ramified of degree six locally, inertia interchanges them. Its tame
image then has projective order two.

For a common sufficiently divisible niveau \(n\), Raynaud's semistable
inertia weights write the two characters as \(\theta_n^u,\theta_n^v\)
with base-seven digits zero or one. Thus
\[
|u-v|\le(7^n-1)/6,
\]
whereas a quadratic quotient requires
\(u-v\equiv(7^n-1)/2\pmod{7^n-1}\), a contradiction.
This argument allows higher niveaux; the shorter list \(0,1,7,8\) from
the global-character argument would be insufficient here.
BCDF v5 Lemma 6.9 and the proof of Theorem 8.3 corroborate this exact
application. No determinant assumption is needed for this step.

## Finiteness and the local lift at seven

GP v2 Theorem 4.3, printed pp.17–18, gives a finite-flat model for the
residual representation when the residual prime does not divide twice
the three equation coefficients. Here the hypothesis is \(7\nmid2\),
including when \(7\mid C\). Its bad-reduction argument uses Mumford
uniformization; it does not assert that the Jacobian has good reduction.
The independent local construction in `bad7_torus_monodromy.md` supplies
a second route: the two node thicknesses are \(7v_7(C)\); the period
matrix's valuation part is a seventh power, leaving unit Kummer classes.
Those classes define a finite-flat model for the full \(J[7]\), and
finite-flat subquotients supply the residual RM constituent.

One must still turn finiteness into a **crystalline weight-two local
lift** before applying BD with level prime to seven. This follows here
from Fontaine–Laffaille in the unramified range, as follows. Let
\(F=K_{(7)}\) and \(k=\mathbf F_{49}\). Full faithfulness of the
finite-flat generic-fiber functor extends the \(k\)-action to its model.
The filtered module of its seven-torsion therefore has two coefficient
components for
\(\mathbf F_{49}\otimes_{\mathbf F_7}k\simeq k\times k\), each of rank
two, with filtration weights in \(\{0,1\}\). Denote their filtration-one
dimensions by \(d_0,d_1\in\{0,1,2\}\). In covariant Tate-module
conventions the determinant's inertia exponent is
\(d_0+7d_1\) modulo 48 (reversing both conventions gives the same
conclusion). Since the determinant is \(\bar\chi_7\),
\[
d_0+7d_1\equiv8\pmod{48},\qquad0\le d_0+7d_1\le16.
\]
Thus \(d_0=d_1=1\): the required Hodge types are genuinely parallel.

Choose a basis at each component whose first vector spans filtration
one. The two divided-Frobenius images of that vector and its complement
give an invertible matrix over \(k\). Lift the filtration and these
matrices over the unramified coefficient integer ring; set
\(\varphi_0(e_1)=7\varphi_1(e_1)\). This produces a strongly divisible
lattice lifting the entire residual module, including its extension
classes. The Fontaine–Laffaille functor gives a crystalline lift with
weights \(\{0,1\}\) at both embeddings. Its determinant differs from
\(\chi_7\) by an unramified character congruent to one; an unramified
square-root twist removes that factor. Such a square root exists by
Hensel's lemma since 2 is a seven-adic unit.

The source bridge is Fontaine–Laffaille, *Construction de représentations
p-adiques*, §§9.10–9.12 (finite-flat/filtered-module comparison),
Theorem 5.3 and Remark 6.13(b) (the determinant and its inertia weights),
§§7.12–7.15 (integral realization and reduction), and Theorem 8.4
(crystallinity). Apply their theory with its parameter \(E=\mathbf Q_7\)
to the underlying rank-four module, while retaining the commuting
\(W(\mathbf F_{49})\)-action. Their relative theory with parameter
\(E=F\) is not being used: it imposes a different filtration convention.
Divided Frobenius moves between the two coefficient components;
the lifted matrices do the same. The matrix lifting above is an application, not a
claim that the source states this particular rank-two lemma verbatim.
The weights lie in the safe interval \([0,1]\subset[0,7-2]\).

This handles the coefficient prime's inertness explicitly. It does not
discard the local extension and replace it by its semisimplification.
For \(7\nmid C\), the existing good-reduction seven-adic representation
already supplies a crystalline lift; the uniform argument also covers
the bad-seven branch.

## Removing two and the other variable primes

GP v2 Theorem 4.2, printed p.17, states unramifiedness away from the
fixed primes and explicitly includes the prime above two for the plus
motive. With coefficients one and exponents \((5,7,3)\), it gives
\[
\bar\rho\text{ unramified outside }(3),(\sqrt5),(7).
\]
There is no seven exception in its hypotheses. In particular, when
\(2\mid C\), **semistability at two alone would not establish this**:
it kills ramification on one-dimensional constituents but can leave a
nontrivial unipotent extension. The residual-unramifiedness theorem
supplies the stronger assertion actually required here.

At any prime away from seven where the residual representation is
unramified, an unramified characteristic-zero lift with determinant
\(\chi_7\) exists: lift its Frobenius matrix invertibly and adjust the
determinant without changing its reduction. The cyclotomic character is
unramified there. These are the local types that remove all variable
primes, including two. Alternatively, take BD's set \(S\) to consist
only of the three retained primes: its conclusion is unramified outside
\(S\).

## The primes three and five

At \((3)\) and \((\sqrt5)\), select the **original** local seven-adic
representations as the local lifts in BD. They already have the correct
residual representation and determinant. PV's local computations
(Corollaries 3.6 and 3.11, Remarks 3.7 and 3.12, Lemma 7.3 and
Proposition 7.4) give conductor exponents two or three in this family;
the piecewise rules are collected in Theorem 7.8. Retaining these
Weil–Deligne types gives exactly one of the four stated levels.

This prescribed-type application does not require an unproved assertion
that the residual conductor equals the original conductor. Nevertheless,
there is a useful direct check at seven. In a potentially good branch,
the finite inertia image on the full Tate module lies in
\(\mathrm{GL}_4(\mathbf Q_7)\). It has order prime to seven: an element
of order seven would require a nontrivial factor of the degree-six
polynomial \(\Phi_7\), which is irreducible over \(\mathbf Q_7\), in a
degree-four characteristic polynomial. For a group of order prime to
seven, averaging idempotents preserve all inertia and ramification-group
invariant dimensions under reduction. Its Artin conductor therefore
does not drop modulo seven. In a ramified-quadratic special branch,
scalar inertia \(-1\) persists modulo seven, so its conductor-two
conclusion also persists even if the unipotent part disappears.

This also explains why reduction modulo seven preserves a nonquadratic
finite inertial type at these primes. It does not by itself determine
which branch a proposed integer triple occupies. The full modulo-25
recipe in PV was source-checked, not recomputed in Magma in this task;
the uniform four-level theorem uses only the displayed local conductor
range and compatible original lifts.

## Applying the actual BD theorem

BD Theorem 3.2.2, printed pp.36–37 of arXiv v3, is an existence theorem
for modular lifts with specified Weil–Deligne types. Its hypotheses and
their dispositions here are:

| Obligation | Disposition |
|---|---|
| Residual modularity | GP v2 Theorem 6.2, with the dictionary above. |
| \(p>2\) | \(p=7\). |
| Cyclotomic restriction irreducible | Proved in the accompanying restriction audit. |
| Extra projective-image condition if \(p=5\) | Inapplicable at seven. |
| Determinant lift \(\psi\), with \(\psi\chi_7^{-1}\) finite | Choose \(\psi=\chi_7\), using BCDF Theorem 2.8. |
| Weight \((0,1)\) at each seven-adic embedding | Crystalline local lift constructed above. |
| Specified ordinary subset \(T\) and ordinary character | Choose \(T\) according to that lift; an ordinary crystalline weight-two lift has the required cyclotomic-times-unramified subcharacter. |
| Local Weil–Deligne types at three and five | Use the original lifts. |
| Character required at a retained special type | Its special subcharacter is cyclotomic times a finite-inertia character; reduce it to define BD's \(\mu_v\). |
| Agreement of local determinants on inertia | All chosen lifts have determinant \(\chi_7\). |
| No other retained ramification | The residual representation is unramified outside the three chosen primes. |

BD yields a modular characteristic-zero lift with determinant
\(\chi_7\), trivial Weil–Deligne type at seven, and the original types
at three and five. Local–global compatibility gives a cuspidal Hilbert
newform of the asserted weight, character and level. This proves the
conditional theorem.

## Sources, limits and next implication

Exact versions, primary links, source-byte hashes where available, and
the locator correction are recorded in
`../source_records/level_sources.json` and
`../source_records/level_source_audit.md`.
No novelty claim is made. The search scope was PV's cited dependency
chain, the precise cyclotomic restriction lemma, and the local
finite-flat-to-crystalline bridge.

The seven-specific level-lowering hypotheses are now supplied. What is
still absent for a complete signature proof is absolute irreducibility
on any branch not subsequently closed, followed by an actual correlated
elimination of every attached form and prime. PV Theorems A and B,
whose ranges exclude seven, are not used to perform that elimination.

Final self-review applied the conservative mathematical-proofreading
workflow to this note and its source records. No unresolved notation or
local mathematical-token issue remained. The Fontaine–Laffaille bridge
also received a separate adversarial review, appended to
`level_restricted_irred_review.md`. No numerical experiment is needed
for the two exact exponent inequalities used here.
