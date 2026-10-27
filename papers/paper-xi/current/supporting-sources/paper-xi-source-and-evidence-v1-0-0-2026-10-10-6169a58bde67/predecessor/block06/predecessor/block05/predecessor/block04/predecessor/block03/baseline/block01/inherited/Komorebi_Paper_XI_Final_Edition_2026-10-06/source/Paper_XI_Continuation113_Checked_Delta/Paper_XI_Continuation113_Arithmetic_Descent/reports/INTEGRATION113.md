# Continuation113: checked progress and the remaining attachment

**Original Paper XI Claim 16.2 remains open; the count is still 65/66.** This
continuation proves the missing finite equivariance statements under explicit
full-action and coprimality hypotheses, executes a characteristic-zero
arithmetic test, rejects its first proposed simple character, and constructs a
different character that removes the detected cubic self-twist obstruction.
It does not establish the original arithmetic attachment or change H5.

## 1. What the additional ideas produced

| Route | Result | Evidence and scope |
| --- | --- | --- |
| Equivariant scalar correction | Proved, including the character and norm identities needed for the correction | Four new Lean modules, fresh compile and kernel replay; actual full automorphisms are inputs |
| Canonical cyclic normalization | Proved for coprime cyclic order and carrier dimension | Lean; identifies a unique normalized action under its hypotheses, not the original kappa automatically |
| Actual cubic arithmetic realization | Explicit fields, character, lattice, simple character, Heisenberg quotient and monomial supercuspidal constructed | Ordinary source-backed proofs and exact rational calculations |
| Tame descent | Actual unramified quadratic occurrence equivalence and canonical trace sign obtained | BH1996/BH1999 hypotheses checked; occurrence transport does not create occurrence |
| First wild attachment | Disproved for the displayed theta_0 | Full central-type scalar is zeta_3; all extensions and global intertwiners are excluded |
| Wild-unit correction | Different theta_1 cancels that scalar and retains the central character | Full cubic self-twist passes; occurrence in the original AI(chi_0) remains unproved |
| Source wild image | Entire projective wild image has order27 and is nonabelian | Exhaustive character quotient plus finite-to-Weil argument, independently recomputed |
| Dyadic retained group | Quotient data alone still insufficient | D8/Q8 negative control; no raw finite-center lift has been supplied |

## 2. The finite bridge now proved

`CyclicDefect113.lean` starts from two honest scalar-fixing extension actions
covering the same cyclic action beta on a quotient of exponent m. Their
periods divide n, and gcd(n,m)=1. From the actual actions it derives a
multiplicative defect r and its orbit-norm identity. For

\[
T(a)=\prod_{i=0}^{n-1}r(\beta^i a)^i,
\]

the shift identity is T(beta a)/T(a)=r(a)^n. A Bezout power gives a character
chi with chi(beta a)/chi(a)=r(a). Dividing the previous scalar cochain by chi
preserves its cocycle equation and makes the scalar-pushout bridge equivariant.
The defect, its multiplicativity, and its norm are conclusions, not newly
assumed attachment data.

`ActualScalarLift113.lean` derives those scalar-pushout actions from actual
group automorphisms, exact quotient maps, normalized sections and invariant
original characters. The period on the pushout follows from the period on
the actual group. No surjectivity of the actual group into all complex
scalars is asserted.

`EquivariantRepresentation113.lean` composes the bridge with the original
packet representation. Its endpoint constructs an irreducible actual group
action Xi on the same carrier, with the exact prescribed theta restriction,
and preserves the supplied packet operator U:

\[
U\,\Xi(g)=\Xi(\alpha(g))\,U.
\]

This covariance does not imply U^n=1 or det(U)=1. Such properties are retained
if the original U has them; its normalization is not silently changed.

`CyclicNormalization113.lean` separately proves that an implementer of an
irreducible complex representation has scalar nth power, corrects its order,
and uses gcd(n,dim V)=1 to obtain the unique determinant-one honest cyclic
action. It derives an initial implementer from actual character/profile or
commutator data. Applying this theorem to the prescribed kappa still requires
proving that kappa has the stated normalization. These results concern
complex scalar pushouts and representations; they do not manufacture a
missing center-preserving automorphism of a retained dyadic group.

The four modules contain **76 named exports: 61 theorems, 14 definitions and
one structure**. This is a count of local formal declarations, unrelated to
the original 66-claim count. All four freshly compiled with warnings treated
as errors, all named exports were axiom-audited, and all four passed
leanchecker. The only reported axioms were Classical.choice, Quot.sound and
propext. An independent audit also compiled and kernel-checked all four.
The 140 inherited modules were hash-authenticated; the external Mathlib
revision was checked. Both were reused, not rebuilt. The replay does not hash
every Mathlib source/object or assert a clean Mathlib working tree. No
local-field arithmetic in the following sections is claimed to have been
formalized in Lean.

## 3. The arithmetic test is now decisive about the first candidate

Use

\[
F=\mathbb Q_3(\zeta_3),\quad L=\mathbb Q_3(\zeta_9),\quad
\varpi=\zeta_9-1,\quad \beta=\varpi^{-10}.
\]

The additive convention is PLUS:
psi_F(x)=psi_Q3(Tr_F/Q3(x)/3), and psi_L=psi_F composed with Tr_L/F.
Define chi_0 on U_L^1 by psi_L(beta log u), with chi_0(varpi)=chi_0(-1)=1.
Its conductor is7; the induced Weil representation has dimension3,
conductor13 and Swan conductor10. The regular cyclic monomial construction
provides the actual supercuspidal pi^0=AI_L/F(chi_0), independently of an
arbitrary type choice under LLC.

For the principal lattice-chain order a, set

\[
H^1=U_L^1U_a^6,\qquad J^1=U_L^1U_a^5,
\qquad
\theta_0(uy)=\chi_0(u)\psi_F(\operatorname{tr}(\beta(y-1))).
\]

The actual quotient is J^1/H^1=F3^3/diag(F3), with character-valued
commutator zeta_3^{2B}; its Heisenberg representation eta has dimension3.
The matching dimension and conductor of the two constructions never implied
that theta_0 occurred in pi^0.

Let omega be the specified cubic norm character of F^x for L/F and
Omega=omega composed with determinant. The candidate pi^0 has an Omega
self-twist. With Pi the multiplication matrix of varpi, the actual matrix
g=1+diag(0,1,2)Pi^4 normalizes H^1, J^1 and N=L^x J^1. The exact calculations
and their generator reductions prove theta_0^g=theta_0 Omega and, on the
same carrier, eta^g=eta Omega. Thus all intertwiners at the eta stage are
scalar. But

\[
h=g^{-1}\Pi g\Pi^{-1}\in H^1,\qquad\theta_0(h)=\zeta_3.
\]

Every central-type extension Lambda of eta therefore satisfies
Lambda^g(Pi)=zeta_3 Lambda(Pi), while (Lambda Omega)(Pi)=Lambda(Pi).
Neither changing the extension nor rescaling an intertwiner removes this
factor. The actual simple-character intertwining theorem and compact
induction eliminate every global intertwiner, not only the matrices tested
in a finite search. Consequently

\[
\operatorname{Hom}_{H^1}
 (\theta_0,\operatorname{AI}_{L/F}(\chi_0))=0.
\]

This is an independently audited rejection of this proposed attachment.
It is not a counterexample to original Claim 16.2: the complete original
packet, phase and H5 hypotheses were never instantiated on theta_0.

## 4. A concrete correction, with a precise limit

The scalar obstruction suggests the wild character

\[
\nu(u)=\psi_L(\varpi^{-8}\log u)\quad(u\in U_L^1),\qquad
\nu(\varpi)=\zeta_9,\quad\nu(-1)=1.
\]

It has conductor5 and is trivial on F^x. The value at varpi matters: choosing
it to be1 would fail to retain the central character. Define the different
simple characters

\[
\theta_a(uy)=\chi_0(u)\nu(u)^a
 \psi_F(\operatorname{tr}(\beta(y-1))).
\]

They retain beta, the deep matrix-trace character and the compatible central
character. The exact full central-type test gives:

| a | theta_a(h) | Cubic central-type self-twist |
| --- | --- | --- |
| 0 | zeta_3 | Excluded |
| 1 | 1 | Passes |
| 2 | zeta_3^2 | Excluded |

All relevant unit and eta generators were rechecked for the correction.
For theta_1, every central-type extension has the cubic self-twist. This
is more than a correction to an abstract matrix scalar. Nevertheless,

\[
\operatorname{Hom}_{H^1}
 (\theta_1,\operatorname{AI}_{L/F}(\chi_0))\ne0
\]

**has not been proved**. The table gives uniqueness only among the three
displayed powers of nu. It does not classify all possible corrections,
select among the three central-type extensions with the fixed central
character, or identify theta_1 with the prescribed original packet. The
source chi_0 remains fixed in this open assertion; replacing it by chi_0 nu
would be a different attachment question.

## 5. What tame descent and the source image add

For the actual unramified quadratic extension K/F and M=KL, define
chi_M=chi_0 composed with Norm_M/L and pi_K=AI_M/K(chi_M). The supplied
BH1996/BH1999 results give occurrence transport for theta_0 and its norm
lift theta_K after their actual central-character hypotheses are checked.
Both occurrences are false by the exclusion above. This equivalence does
not supply existence for a corrected type.

The restriction of theta_K to H_F^1 is theta_0^2; eta_K has dimension9.
Glauberman correspondence and the canonical determinant-one C2 extension
give the actual trace identity

\[
\operatorname{tr}\widehat\eta_K(\tau j)
 =-\operatorname{tr}\eta(\theta_0^2)(j),\qquad j\in J_F^1.
\]

In particular tr(eta-hat_K(tau))=-3. The exact finite F9/F3 model independently
checks this sign. The Weil source stays three-dimensional on restriction
to K, so its whole carrier cannot be identified with eta_K. This finding
also preserves the separate whole-carrier obstruction from continuation112.

Downstairs, the complete projective wild image of the original induced Weil
representation is the nonabelian group (C3 x C3) semidirect C3 of order27.
This follows from the six generators of U_L^1/U_L^7 and the induced cyclic
permutation, not from a sample of wild inertia. A separate exact calculation
reproduces all18 conjugate-character values. By contrast, the projective
image of the actual eta is abelian of order9. A valid comparison must specify
the proper Heisenberg subgroup or Clifford stage and retain the extra wild
action. Choosing an abstract subgroup does not identify the intrinsic packet.

One actual diagonal operator is diag(zeta_9^4,zeta_9^4,zeta_9). It has
determinant1 and cube zeta_3 I. Its projective class admits no lift with both
order3 and determinant1. Thus the coprime cyclic normalization theorem cannot
be applied to this wild order3 action on a three-dimensional carrier. Its
hypothesis fails exactly where this explicit obstruction occurs.

## 6. Route decisions and the next bounded attempt

The first theta_0-to-AI(chi_0) route is closed negatively for this test. The
finite coprime correction route is completed at its stated hypotheses. The
corrected theta_1 attachment route is open. Tame descent and finite models
are usable supporting results, not substitutes for the wild attachment.

The next discriminating task is to determine the inducing character of the
actual theta_1 central types, keeping chi_0 and the central character fixed.
A viable analytic route must transfer the theta_1 test function in the
**twisted** automorphic-induction identity with its specified intertwiner
and transfer normalization. The bare ordinary character sum of conjugates
of chi_0 does not justify that step. A complementary route is to compute the
actual intrinsic Clifford stages of this source and identify their wild
extension data with the corrected type. Neither route was completed here.

Even success for this example would still leave the original general
attachment, exact prescribed kappa normalization, retained dyadic group
actions where required, and the original same-completion H5 verification.
No new epsilon tests, new twist family, or broadened H5 have been added.
There is no claim of global novelty or a completed theorem66.

## 7. Verification and retained failures

The authoritative final Lean receipt is
`evidence/final_replay_corrected/replay/RESULT.json`; its encompassing v2
manifest pins inputs before and after execution. The arithmetic final replay
is `evidence/arithmetic/bounded_final113/manifest.json`. Lattice, exact finite
model and projective wild-image runs have separate contracts and manifests.
Independent reports cover all four formal modules, the arithmetic correction,
the all-intertwiner exclusion and the full projective wild-image reduction.
`STATUS113.json` indexes these records and pins their current hashes.

Development failures are retained. In particular, the initial lattice report
used the opposite additive-character sign; it was substantively corrected
and the old snapshot retained. The first root replay failed in the export
parser, not the Lean proof; its script snapshot and receipt remain distinct
from the passing replay. An early arithmetic v1 receipt was overwritten
before archival and is not recoverable; the final v2 record is a fresh run,
not a reconstruction. See `ROOT_VERIFICATION_FAILURES113.md`,
`evidence/arithmetic/FAILURES113.md`, and `REVIEW_NOTES113.md`, including the
explicit conductor-ideal wording correction.

The delivered archive contains this continuation's sources, computations,
audits, failure records and final four module objects. Baseline archives and
the runtime remain separately pinned dependencies. No inherited proof object
or prior receipt is silently promoted to a new113 proof.
